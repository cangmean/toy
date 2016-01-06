# coding=utf-8

import httplib


def get_content_type(mimetype, charset):

    if mimetype.startswith('text/') or \
       mimetype == 'application/xml' or \
       (mimetype.startswith('application/') and
               mimetype.endswith('+xml')):
        mimetype += '; charset=' + charset
    return mimetype


def native_itermethods(names):
    ''' 为每一个类创建一个itermethod的实例方法
    比如: get 或创建处 iterget方法,并把原有的get方法返回iterget的列表.
    '''

    def setmethod(cls, name):
        itermethod = getattr(cls, name)
        setattr(cls, 'iter%s' % name, itermethod)
        listmethod = lambda self, *a, **kw: list(itermethod(self, *a, **kw))
        listmethod.__doc__ = \
                'Like :py:meth:`iter%s`, but returns a list.' % name
        setattr(cls, name, listmethod)

    def wrap(cls):
        for name in names:
            setmethod(cls, name)
        return cls
    return wrap


class Headers(object):

    def __init__(self, defaults=None):
        self._list = []
        if defaults is not None:
            if isinstance(defaults, (list, Headers)):
                self._list.extend(defaults)
            else:
                self.extend(defaults)

    def __getitem__(self, key, _get_mode=False):
        '''实例可以接受键, 如果_get_mode是True则想列表一样
           使用下标和切片, 否则只接受string类型 '''
        if not _get_mode:
            if isinstance(key, int):
                return self._list[key]
            elif isinstance(key, slice):
                return self.__class__(self._list[key])
        if not isinstance(key, str):
            raise TypeError(u'类型错误，键值必须为string类型.')
        ikey = key.lower()
        for k, v in self._list:
            if k.lower() == ikey:
                return v

        if _get_mode:
            raise KeyError()
        raise KeyError(u'到这里还报错，说明查询的key不存在')

    def get(self, key, default=None, _type=None):
        try:
            rv = self.__getitem__(key, _get_mode=True):
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

    def __iter__(self):
        return iter(self._list)

    def __len__(self):
        return len(self._list)

    def clear(self):
        del self._list[:]


class RequestBase(Object):
    
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

    charset = 'utf-8'

    default_status = 200

    default_mimetype = 'text/plain'
    
    def __init__(self, response=None, status=None,
                 headers=None, content_type=None, mimetype=None):
        if isinstance(headers, Headers):
            self.headers = header
        elif not header:
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

    def _get_status_code(self):
        return self._status_code

    def _set_status_code(self, code):
        self._status_code = code
        try:
            self._status = '%d %s' % (code, httplib.responses.get(code))
        except KeyError:
            self._status = '%d UNKNOWN' % code

    status_code = property(_get_status_code, _set_status_code,
                           doc='The HTTP Status code as number')

    def get_data(self):
        pass

    def set_data(self, value):
        if isinstance(value, str):
            value = value.encode(self.charset)
        self.response = [value]

    data = property(get_data, set_data, doc='''设置和获取响应数据 ''')


    def __call__(self, environ, start_response):
        ''' 处理这个响应为wsgi application'''
        headers = [('Content-Type', self.content_type)]
        start_response('200 OK', headers)
        return self.body
