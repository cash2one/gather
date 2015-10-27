#!/usr/bin/env python

import os
import tornado.escape
import tornado.ioloop
import tornado.web
import os.path

import django.core.handlers.wsgi
import tornado.wsgi
import tornado.httpserver
from tornado.options import define, options, parse_command_line

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "gather.settings")

#from chatting.chat import MainHandler, MessageNewHandler, MessageUpdatesHandler

define("port", default=8000, help="run on the given port", type=int)


def main():
    parse_command_line()

    wsgi_app = tornado.wsgi.WSGIContainer(django.core.handlers.wsgi.WSGIHandler())

    app = tornado.web.Application(
        [
            #(r"/chat", MainHandler),
            #(r"/chat/message/new", MessageNewHandler),
            #(r"/chat/message/updates", MessageUpdatesHandler),
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
