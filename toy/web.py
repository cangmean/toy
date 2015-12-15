# coding=utf-8

import os
import sys


class Toy(object):

    static_path = '/static'
    secret_key = None

    def __init__(self):
        self.debug = False
        self.view_functions = {}

    def run(self, host='127.0.0.1', port=5000, auto_reload=False):
        from wsgiref.simple_server import make_server
        httpd = make_server(host, int(port), self)
        httpd.serve_forever()

    def route(self, rule, **option):
        pass

    def request_context(self, environ):
        pass

    def wsgi_app(self, environ, start_response):
        with self.request_context(environ):
            pass

    def __call__(self, environ, start_response):
        ''' callable '''
        return self.wsgi_app(environ, start_response)


class Reloader(object):

    """ reload modify files. """

    if sys.platform.startswith('java'):
        SUFFIX = '$py.class'
    else:
        SUFFIX = '.pyc'

    def __init__(self):
        # modify times
        self.mtimes = {}

    def __call__(self):
        # check all modules 
        for mod in sys.modules.values():
            self.check(mod)

    def check(self, mod):

        if not(mod and hasattr(mod, '__file__') and mode.__file__):
            return

        try:
            # get file last modify time
            mtime = os.stat(mod.__file__).st_mtime
        except (OSError, IOError):
            return 

        if mod.__file__.endswith(self.__class__.SUFFIX) and os.path.exists(mod.__file__[:-1]):
            # get .pyc and .py file max modify time
            mtime = max(os.stat(mod.__file__[:-1]).st_mtime, mtime)

        # set mtime to mtimes if mtimes not this module. reload module if module not in mtimes.
        if mod not in self.mtimes:
            self.mtimes[mod] = mtime
        elif self.mtimes[mod] < mtime:
            try:
                reload(mod)
                self.mtimes[mod] = mtime
            except ImportError:
                pass
