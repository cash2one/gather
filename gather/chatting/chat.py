#!/usr/bin/env python
#! -*- coding: utf-8 -*-

import datetime
import logging
import tornadoredis
import tornado.escape
import tornado.ioloop
import tornado.web
import uuid

import tornado.wsgi
import tornado.httpserver
from tornado.concurrent import Future
from tornado import gen

from chatting.models import ChatInfo

from utils import gen_username


class MessageBuffer(object):
    def __init__(self):
        self.waiters = set()
        self.cache = self.get_top_50_info()
        self.cache_size = 50

    def wait_for_messages(self, cursor=None):
        # Construct a Future to return to our caller.  This allows
        # wait_for_messages to be yielded from a coroutine even though
        # it is not a coroutine itself.  We will set the result of the
        # Future when results are available.
        result_future = Future()
        if cursor:
            new_count = 0
            for msg in reversed(self.cache):
                if msg["id"] == cursor:
                    break
                new_count += 1
            if new_count:
                result_future.set_result(self.cache[-new_count:])
                return result_future
        self.waiters.add(result_future)
        return result_future

    def get_top_50_info(self):
        chats = ChatInfo.objects.all().order_by('-created')[:50]
        _cache = []
        for chat in chats:
            _cache.append({
                'id': chat.uuid,
                'word': chat.content,
                'time': str(chat.created)[:19],
                'username': chat.nickname,
                'count': int(chat.photo)
            })
        return _cache

    def cancel_wait(self, future):
        self.waiters.remove(future)
        # Set an empty result to unblock any coroutines waiting.
        future.set_result([])

    def new_messages(self, messages):
        logging.info("Sending new message to %r listeners", len(self.waiters))
        for future in self.waiters:
            future.set_result(messages)
        self.waiters = set()
        self.cache.extend(messages)
        if len(self.cache) > self.cache_size:
            self.cache = self.cache[-self.cache_size:]


# Making this a non-singleton is left as an exercise for the reader.
global_message_buffer = MessageBuffer()


class MainHandler(tornado.web.RequestHandler):
    def get(self):
        self.render("chat/chat.html", messages=global_message_buffer.cache)


class MessageNewHandler(tornado.web.RequestHandler):
    def post(self):
        word = self.get_argument("word")
        message = {
            "id": str(uuid.uuid4()),
            "word": word,
            "time": str(datetime.datetime.now())[:19],
            "username": gen_username(),
            "count": hash(word) % 4 + 1,
        }
        ChatInfo(
            uuid=message['id'],
            nickname=message['username'],
            content=message['word'],
            photo=message['count'],
        ).save()
        # to_basestring is necessary for Python 3's json encoder,
        # which doesn't accept byte strings.
        if self.get_argument("next", None):
            self.redirect(self.get_argument("next"))
        else:
            self.write(message)
        global_message_buffer.new_messages([message])


class MessageUpdatesHandler(tornado.web.RequestHandler):
    @gen.coroutine
    def get(self):
        cursor = self.get_argument("cursor", None)
        # Save the future returned by wait_for_messages so we can cancel
        # it in wait_for_messages
        self.future = global_message_buffer.wait_for_messages(cursor=cursor)
        messages = yield self.future
        if self.request.connection.stream.closed():
            return
        self.write(dict(messages=messages))

    def on_connection_close(self):
        global_message_buffer.cancel_wait(self.future)
