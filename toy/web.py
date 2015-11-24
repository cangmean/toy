# coding=utf-8


class Request(object):

    def __init__(self, environ={}):
        self.environ = environ

    @property
    def path(self):
        print self.environ.get('PATH_INFO', '')

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


class Response(object):
    pass


class Toy(object):

    def __init__(self):
        pass

    def __call__(self, environ, start_response):
        ''' callable '''
        request = Request(environ)
        for k, v in environ.items():
            num = len(k)
            print 'key: {}.{}value: {}'.format(k, ' ' * (50 - num) , v)

        status = '200 OK'
        response_headers = [('Content-type', 'text/plain')]
        start_response(status, response_headers)
        yield 'Hello Wrold!\n'
