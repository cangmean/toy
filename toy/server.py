from wsgiref.simple_server import make_server
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath('.')))
from toy.web import Toy


class WSGIServer(object):

    def __init__(self, host, port, application):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.sock.setblocking(0)
        self.sock.bind((host, port))
        self.sock.listen(2)
        self.host = host
        self.port = port
        self.application = application

    def run(self):
        while True:
            self.client, address = self.sock.accept()
            request_data = self.client.recv(1024)
            print(request_data)
            env = self.get_environ(request_data)
            result = self.application(env, self.start_response)

    def get_environ(self, data):
        env = {}

        env['wsgi.version'] = (1, 0)
        env['wsgi.url_scheme'] = 'http'
        env['wsgi.input'] = StringIO.StringIO(data)
        env['wsgi.errors'] = sys.stderr
        env['wsgi.multithread'] = False
        env['wsgi.mutiprocess'] = False
        env['wsgi.run_once'] = False

        # Required CGI variable
        env['REQUEST_METHOD'] = self.request_method
        env['PATH_INFO'] = self.path
        env['SERVER_NAME'] = self.server_name
        env['SERVER_PORT'] = str(self.server_port)
        
        return env

    def start_response(self, status, response_headers, exc_info=None):
        server_headers = [
                ('Date', 'Tue, 31 Mar 2015 12:54:48 GMT'),
                ('Server', 'WSGIServer 0.2'),
                ]
        self.headers_set = [status, response_headers + server_headers]

    def finish_response(self, result):
        try:
            status, response_headers = self.headers_set
            response = 'HTTP/1.1 {status}\r\n'.format(status=status)
            for header in response_headers:
                response += '{0}: {1}\r\n'.format(*header)
            response += '\r\n'
            for data in result:
                response += data
            print(''.join(
                '> {line}\n'.format(line=line)
                for line in response.splitlines()))
            self.client_connection.sendall(response)
        finally:
            self.client_connection.close()

if __name__ == '__main__':
    app = Toy() 
    print(app)
    httpd = make_server('127.0.0.1', 5000, app)
    httpd.serve_forever()
