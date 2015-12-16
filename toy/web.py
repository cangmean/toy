# coding=utf-8

import os
import sys
#from jinja2 import Environment, PackageLoader, FileSystemLoader
from .router import Router
from .http import Request, Response
from ._reloader import Reloader


def render(template_name, **context):
    pass


class Toy(object):

    static_path = '/static'
    secret_key = None

    def __init__(self):
        self.debug = False
        self.view_functions = {}
        self._router = Router()

        self.before_request_funcs = []
        self.after_request_funcs = []

    def update_template_context(self, context):
        pass

    def run(self, host='127.0.0.1', port=5000, auto_reload=False):
        from wsgiref.simple_server import make_server
        httpd = make_server(host, int(port), self)
        httpd.serve_forever()

    def route(self, rule, **option):
        if 'methods' in option:
            methods = [m.upper() for m in methods]
        else:
            methods = ['GET']

        def wrapper(func):
            self._router.register(rule, func, methods)
            return func

        return wrapper

    def request_context(self, environ):
        pass

    def dispatch_request(self):
        pass

    def preprocess_request(self):
        for func in self.before_request_funcs:
            rv = func()
            if rv is not None:
                return rv

    def dev_wsgi_app(self, environ, start_response):
        with self.request_context(environ):
            rv = self.preprocess_request()
            if rv is None:
                rv = self.dispatch_request()

    def wsgi_app(self, environ, start_response):
        request = Request(environ)
        self._response = Response()
        response_headers = [('Content-type', 'text/plain')]
        start_response(self._response.status, response_headers)
        yield 'Hello wrold\n'

    def __call__(self, environ, start_response):
        ''' callable '''
        return self.wsgi_app(environ, start_response)

