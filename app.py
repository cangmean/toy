# coding=utf-8

'''
一个玩具框架，用于理解python 框架机制。
查看了flask源码和werkzeug源码, 并简化，解耦和。
'''
import re
import os
import sys
import httplib
import logging
from pprint import pprint

logger = logging.getLogger('toy')
handler = logging.StreamHandler()
fomatter = logging.Formatter('[line: %(lineno)d] %(levelname)s: %(message)s')
handler.setFormatter(fomatter)
logger.setLevel(logging.DEBUG)
logger.addHandler(handler)

__all__ = ['Toy']

mtimes = {}

rule_re = re.compile(r'''
    (?P<static>[^<]*)
    <(?:
        (?P<type>[a-zA-Z_][a-zA-Z0-9_]*)
        \:
    )?
        (?P<variable>[a-zA-Z_][a-zA-Z0-9_]*)
    >
''', re.VERBOSE)


def _get_package_path(name):
    """Returns the path to a package or cwd if that cannot be found."""
    try:
        return os.path.abspath(os.path.dirname(sys.modules[name].__file__))
    except (KeyError, AttributeError):
        return os.getcwd()


def get_content_type(mimetype, charset):

    if mimetype.startswith('text/') or \
       mimetype == 'application/xml' or \
       (mimetype.startswith('application/') and
               mimetype.endswith('+xml')):
        mimetype += '; charset=' + charset
    return mimetype


def parse_rule(rule):
    '''循环解析rule 并返回。
    比如 rule = '/index/<int:page>'
    分别表示 静态(不变的) 类型 变量
    会返回 /index None None
           None   int  page
    '''
    pos = 0
    end = len(rule)
    do_match = rule_re.match
    used_names = set()
    while pos < end:
        # pos 开始匹配的位置
        m = do_match(rule, pos)
        if m is None:
            break
        data = m.groupdict()
        if data['static']:
            yield data['static'], None, None
        _type = data['type']
        _variable = data['variable']
        if _variable in used_names:
            raise ValueError('variable name %r used twice.' % variable)
        used_names.add(_variable)
        yield None, _type, _variable
        pos = m.end()

    if pos < end:
        remaining = rule[pos:]
        if '>' in remaining or '<' in remaining:
            raise ValueError('malformed url rule: %r' % rule)
        yield remaining, None, None


class Headers(object):

    def __init__(self, defaults=None):
        self._list = []
        if defaults is not None:
            if isinstance(defaults, (list, Headers)):
                self._list.extend(defaults)
            else:
                self.extend(defaults)

    def __getitem__(self, key, _get_mode=False):

        if not _get_mode:
            if isinstance(key, int):
                return self._list[key]
            elif isinstance(key, slice):
                return self.__class__(self._list[key])

        if not isinstance(key, str):
            raise TypeError('key type must be string.')
        ikey = key.lower()
        for k, v in self._list:
            if k.lower() == ikey:
                return v

        if _get_mode:
            raise KeyError()
        raise KeyError('key not exists.')

    def get(self, key, default=None, _type=None):
        try:
            rv = self.__getitem__(key, _get_mode=True)
        except KeyError:
            return default

        if _type is None:
            return rv

        try:
            return _type(rv)
        except ValueError:
            return default

    def add(self, key, value):
        self._list.append((key, value))

    def __setitem__(self, key, value):
        self.add(key, value)

    def to_wsgi_list(self):
        return list(self)

    def __iter__(self):
        return iter(self._list)

    def __len__(self):
        return len(self._list)

    def clear(self):
        del self._list[:]

    def __repr__(self):
        return '%s(%r)' % (self.__class__.__name__, list(self))


class BaseRequest(object):

    charset = 'utf-8'
    max_content_length = None
    max_form_memory_size = None

    def __init__(self, environ):
        self.environ = environ

    def bind_to_environ(self, environ):
        self.environ = environ

    @property
    def url_charset(self):
        return self.charset

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
    def http_user_agent(self):
        return self.environ.get('HTTP_USER_AGENT')

    def __repr__(self):
        return self.environ


class BaseResponse(object):

    charset = 'utf-8'
    default_status = 200
    default_mimetype = 'text/plain'

    def __init__(self, response=None, status=None,
                 headers=None, content_type=None, mimetype=None):
        if isinstance(headers, Headers):
            self.headers = header
        elif not headers:
            self.headers = Headers()
        else:
            self.headers = Headers(header)

        if content_type is None:
            if mimetype is None and 'content-type' not in self.headers:
                mimetype = self.default_mimetype
            if mimetype is not None:
                mimetype = get_content_type(mimetype, self.charset)
            content_type = mimetype
        if content_type is not None:
            self.headers['Content-Type'] = content_type

        if status is None:
            status = self.default_status
        if isinstance(status, int):
            self.status_code = status
        else:
            self.status = status

        if response is None:
            self.response = []
        elif isinstance(response, str):
            self.set_data(response)
        else:
            self.response = response

    @classmethod
    def force_type(cls, response, environ=None):
        # 强制转换成response 类型, 这里有错误
        if not isinstance(response, BaseResponse):
            response = BaseRequest(response)
        response.__class__ = cls
        return response

    def _get_status_code(self):
        return self._status_code

    def _set_status_code(self, code):
        self._status_code = code
        try:
            self._status = '%d %s' % (code, httplib.responses.get(code))
        except KeyError:
            self._status = '%d UNKOWN' % code

    status_code = property(_get_status_code, _set_status_code,
                           doc='The HTTP Status code as number.')
    del _get_status_code, _set_status_code

    def _get_status(self):
        return self._status

    def _set_status(self, value):
        self._status = value
        try:
            self._status_code = int(self._status.split(None, 1)[0])
        except ValueError:
            self._status_code = 0
            self._status = '0 %s' % self._status

    status = property(_get_status, _set_status, doc='The HTTP Status code')
    del _get_status, _set_status

    def get_data(self):
        return self.response

    def set_data(self, value):
        if isinstance(value, str):
            value = value.encode(self.charset)
        self.response = [value]
        self.headers['Content-Length'] = str(len(value))

    data = property(get_data, set_data, doc='''get and set response data''')

    def close(self):
        if hasattr(self.response, 'close'):
            self.response.close()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, tb):
        self.close()

    def get_wsgi_headers(self, environ):
        headers = Headers(self.headers)
        content_length = None
        status = self.status_code

        for key, value in headers:
            ikey = key.lower()
            if ikey == 'content-length':
                content_length = value

        if 100 <= status < 200 or status == 204:
            headers['Content-Length'] = content_length = u'0'

        return headers

    def get_app_iter(self, environ):
        status = self.status_code
        return self.response

    def get_wsgi_response(self, environ):
        headers = self.get_wsgi_headers(environ)
        app_iter = self.get_app_iter(environ)
        return app_iter, self.status, headers.to_wsgi_list()

    def __call__(self, environ, start_response):
        app_iter, status, headers = self.get_wsgi_response(environ)
        start_response(status, headers)
        return app_iter


class Request(BaseRequest):

    def __init__(self, environ):
        BaseRequest.__init__(self, environ)


class Response(BaseResponse):

    default_mimetype = 'text/html'


class _Rule(object):

    def __init__(self, rule, handler=None, methods=None):
        self.rule = rule
        self._map = None
        self.handler = handler

        if methods is None:
            self.methods = None
        else:
            self.methods = set([x.upper() for x in methods])
            if 'HEAD' not in self.methods and 'GET' in self.methods:
                self.methods.add('HEAD')

        self._regex = []
        self.build_regex()

    def bind(self, _map):
        self._map = _map
        self.build_regex()

    def build_regex(self):
        '''构建url regex '''
        regex_parts = []
        for _static, _type, _variable in parse_rule(self.rule):
            if _static:
                regex_parts.append(re.escape(_static))
            elif _variable:
                if _type is None or _type == 'string':
                    regex_parts.append('(?P<%s>%s)' % (_variable, '[a-zA-Z0-9_]*'))
                elif _type == 'int':
                    regex_parts.append('(?P<%s>%s)' % (_variable, '[0-9]*'))
                else:
                    raise TypeError('Rule variable argument must be int or string. The argument default is string.')
        regex = r'^%s$' % (u''.join(regex_parts))
        self._regex = re.compile(regex, re.UNICODE)

    def get_rules(self, _map):
        yield self

    def match(self, path):
        m = self._regex.search(path)
        if m is not None:
            groups = m.groupdict()
            result = {}
            for name, value in groups.iteritems():
                result[str(name)] = value

            return result


class _Map(object):

    def __init__(self):
        self.rules = []
        self.rules_by_handler = {}

    def bind_to_environ(self, environ):
        self.method = environ.get('REQUEST_METHOD', 'GET')
        self.path_info = environ.get('PATH_INFO')
        self.query_stirng = environ.get('QUERY_STRING')

    def add(self, rulefactory):
        '''添加rule '''
        for rule in rulefactory.get_rules(self):
            rule.bind(self)
            self.rules.append(rule)
            self.rules_by_handler.setdefault(rule.handler, []).append(rule)

    def match(self):
        path = self.path_info
        method = self.method.upper()

        for rule in self.rules:
            rv = rule.match(path)

            if rv is None:
                continue
            if rule.methods is not None and method not in rule.methods:
                continue
            return rule.handler, rv


class _RequestContext(object):

    def __init__(self, app, environ):
        self.app = app
        self.url_adapter = app.url_map.bind_to_environ(environ)
        self.request = app.request_class(environ)

    def __enter__(self):
        pass

    def __exit__(self, exc_type, exc_value, tb):
        if tb is None or not self.app.debug:
            pass


class Toy(object):

    static_path = '/static'
    secret_key = None

    request_class = Request
    response_class = Response

    def __init__(self, name=None):
        self.name = _get_package_path(name)
        self.debug = False
        self.view_funcs = {}
        self.url_map = _Map()
        self.error_handlers = {}

    def add_route(self, rule, handler, **options):
        options['handler'] = handler
        options.setdefault('methods', ('GET',))
        self.url_map.add(_Rule(rule, **options))

    def route(self, rule, **options):
        def decorator(func):
            self.add_route(rule, func.__name__, **options)
            self.view_funcs[func.__name__] = func
            return func
        return decorator

    def errorhandler(self, code):
        def decorator(func):
            self.error_handlers[code] = func
            return func
        return decorator

    def match_request(self):
        rv = self.url_map.match()
        return rv

    def dispatch_request(self):
        try:
            handler, params = self.match_request()
            return self.view_funcs[handler](**params)
        except Exception as e:
            handler = self.error_handlers.get(500)
            # debug 状态为True 或者 没有自定义错误信息
            if self.debug or handler is None:
                raise
            return handler(e)

    def run(self, host='127.0.0.1', port=5000):
        from wsgiref.simple_server import make_server
        server = make_server(host, int(port), self)
        server.serve_forever()

    def auto_reload(self):
        main_module = sys.modules['__main__']
        filename = os.path.splitext(os.path.basename(main_module.__file__))[0]
        try:
            __import__(filename)
        except ImportError:
            pass

        for module in sys.modules.values():
            filename = getattr(module, '__file__', None)
            if not (filename and os.path.isfile(filename)):
                continue

            if filename[-4:] in ('.pyc', '.pyo', '.pyd'):
                filename = filename[:-1] # get the '.py' file

            # get the time of most recent content modification
            try:
                mtime = os.stat(filename).st_mtime
            except OSError as e:
                logger.error(e)
                continue
            # set mtime to mtimes if mtimes not this module. reload module if module not in mtimes.
            old_time = mtimes.get(module)
            if old_time is None: # the first time in this function, just record mtime
                mtimes[module] = mtime
            elif old_time < mtime: # `module` is modified
                try:
                    reload(module)
                    mtimes[module] = mtime
                except ImportError:
                    pass

    def make_response(self, rv):
        if isinstance(rv, self.response_class):
            return rv
        elif isinstance(rv, str):
            return self.response_class(rv)
        elif isinstance(rv, tuple):
            return self.response_class(*rv)

    def request_context(self, environ):
        return _RequestContext(self, environ)

    def wsgi_app(self, environ, start_response):
        with self.request_context(environ):
            rv = self.dispatch_request()
            response = self.make_response(rv)
            return response(environ, start_response)

    def __call__(self, environ, start_response):
        return self.wsgi_app(environ, start_response)
