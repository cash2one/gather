#!/usr/bin/env python
#
# Copyright 2009 Facebook
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.

import datetime
import os
import logging
import random
import tornado.escape
import tornado.ioloop
import tornado.web
import os.path
import uuid

import django.core.handlers.wsgi
import tornado.wsgi
import tornado.httpserver
from tornado.concurrent import Future
from tornado import gen
from tornado.options import define, options, parse_command_line

from utils import gen_username

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "gather.settings")

define("port", default=8000, help="run on the given port", type=int)


class MessageBuffer(object):
    def __init__(self):
        self.waiters = set()
        self.cache = []
        self.cache_size = 200

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
        message = {
            "id": str(uuid.uuid4()),
            "word": self.get_argument("word"),
            "time": str(datetime.datetime.now())[:19],
            "username": gen_username(),
            "count": random.randint(1, 5),
        }
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


def main():
    parse_command_line()

    wsgi_app = tornado.wsgi.WSGIContainer(django.core.handlers.wsgi.WSGIHandler())

    app = tornado.web.Application(
        [
            (r"/chat", MainHandler),
            (r"/chat/message/new", MessageNewHandler),
            (r"/chat/message/updates", MessageUpdatesHandler),
            (r'.*', tornado.web.FallbackHandler, dict(fallback=wsgi_app)),
            ],
            template_path=os.path.join(os.path.dirname(__file__), "templates"),
            static_path=os.path.join(os.path.dirname(__file__), "static"),
            debug=True,
        )
    app.listen(options.port)
    tornado.ioloop.IOLoop.current().start()


if __name__ == "__main__":
    main()
