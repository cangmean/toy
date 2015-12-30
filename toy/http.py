# coding=utf-8

import threading
import httplib


class BaseObject(threading.local):
    pass


class RequestBase(BaseObject):
    
    def __init__(self, environ={}):
        self.environ = environ

    def bind(self, environ):
        self.environ = environ

    @property
    def path(self):
        return self.environ.get('PATH_INFO', '')

    @property
    def method(self):
        return self.environ.get('REQUEST_METHOD', '')

    @property
    def query_string(self):
        return self.environ.get('QUERY_STRING', '')

    @property
    def content_type(self):
        return self.environ.get('CONTENT_TYPE', '')

    @property
    def http_user_agen(self):
        return self.environ.get('HTTP_USER_AGEN', '')

    def __repr__(self):
        return self.environ


class ResponseBase(object):
    
    def __init__(self, body=None, code=200, content_type='text/html'):
        self.code = code
        self.content_type = content_type
        self._body = body 

    @property
    def status(self):
        return ' '.join([str(self.code), httplib.responses.get(self.code)])

    def set_status(self, code):
        self.code = int(code)

    @property
    def body(self):
        return self._body

    def set_body(self, body):
        self._body = str(body)

    def __call__(self, environ, start_response):
        ''' 处理这个响应为wsgi application'''
        headers = [('Content-Type', self.content_type)]
        start_response('200 OK', headers)
        return self.body
