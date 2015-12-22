# coding=utf-8

import os
import sys
#from jinja2 import Environment, PackageLoader, FileSystemLoader
from .router import Map, Rule
from .local import LocalStack
from .http import RequestBase, ResponseBase
from ._reloader import Reloader


def render(template_name, **context):
    pass

class Request(RequestBase):
    def __init__(self, environ):
        RequestBase.__init__(self, environ)
        self.endpoint = None
        self.view_args = None


class Response(ResponseBase):
    pass


class _RequestContext(object):

    def __init__(self, app, environ):
        self.app = app
        self.url_adapter = app.url_map.bind_to_environ(environ)
        self.request = app.request_class(environ)

    def __enter__(self):
        _request_ctx_stack.push(self)

    def __exit__(self, exc_type, exc_value, tb):
        if tb is None or not self.app.debug:
            _request_ctx_stack.pop()


class Toy(object):

    static_path = '/static'
    secret_key = None

    request_class = Request
    response_class = Response

    def __init__(self):
        self.debug = False

        self.view_functions = {}
        self.url_map = Map()

        self.before_request_funcs = []
        self.after_request_funcs = []

    def update_template_context(self, context):
        pass

    def run(self, host='127.0.0.1', port=5000, auto_reload=False):
        from wsgiref.simple_server import make_server
        httpd = make_server(host, int(port), self)
        httpd.serve_forever()

    def add_url_rule(self, rule, endpoint, **options):
        '''添加rule ''' 
        options[endpoint] = endpoint
        options.setdefault('methods', ('GET',))
        self.url_map.add(Rule(rule, **options))

    def route(self, rule, **option):
        ''' 路由装饰，用于添加url rule'''
        def wrapper(func):
            self.add_url_rule(rule, func.__name__, **options)
            self.view_functions[func.__name__] = func
            return func
        return wrapper

    def request_context(self, environ):
        pass

    def match_request(self):
        ''' 匹配请求 ''' 
        rv = self.url_map.match()
        request.endpoint, request.view_args = rv
        return rv

    def dispatch_request(self):
        try:
            endpoint, values = self.match_request()
            return self.view_functions[endpoint](**values)
        except:
            pass

    def make_response(self, rv):
        ''' 根据类型返回结果 '''
        if isinstance(rv, self.reponse_class):
            return rv
        if isinstance(rv, str):
            return self.response_class(rv)
        if isinstance(rv, tuple):
            return self.response_class(*rv)

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
            response = self.make_response(rv)
            response = self.process_response(response)
            return response(environ, start_response)

    def wsgi_app(self, environ, start_response):
        request = Request(environ)
        self._response = Response()
        response_headers = [('Content-type', 'text/plain')]
        start_response(self._response.status, response_headers)
        yield 'Hello wrold\n'

    def __call__(self, environ, start_response):
        ''' callable '''
        return self.wsgi_app(environ, start_response)

_request_ctx_stack = LocalStack()
request = _request_ctx_stack.top.request
