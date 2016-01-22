# coding=utf-8

class Toy(object):

    def __init__(self):
        self.debug = False

    def route():
        pass

    def run(self, host='127.0.0.1', port=5000):
        from wsgiref.simple_server import make_server
        server = make_server(host, int(port), self)
        server.serve_forever()

    def wsgi_app(self, environ, start_response):
        status = '200 OK'
        headers = [('Content-type', 'text/plain')]
        start_response(status, headers)
        return ['Hello World!\n']

    def __call__(self, environ, start_response):
        return self.wsgi_app(environ, start_response)
