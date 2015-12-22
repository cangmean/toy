# coding=utf-8

import re

rule_re = re.compile(r'''
    (?P<static>[^<]*)                        # static别名的组
    <(?:
        (?P<type>[a-zA-Z_][a-zA-Z0-9_]*)     # 类型必须是以字符开头
        \:                                   # 类型跟变量的分隔,比如: route('/groups/<int:num>')
    )?                                       # 可以不设置类型默认为string
        (?P<variable>[a-zA-Z_][a-zA-Z0-9_]*) # 变量
    >                                        # 类型和变量为尖括号形式, <int: num>或<username>
''', re.VERBOSE)


def parse_rule(rule):
    '''循环解析rule, 并返回 
    比如 rule = '/index/<int:page>'
    分别表示　静态(不变的) 类型 变量
    会返回  /index None None 
            None int page 
    '''
    pos = 0
    end = len(rule)
    do_match = rule_re.match
    used_names = set()
    while pos < end:
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


class Rule(object):

    def __init__(self, rule, endpoint=None, methods=None):
        self.rule = rule
        self._map = None
        self.endpoint = endpoint

        if methods is None:
            self.methods = None
        else:
            self.methods = set([x.upper() for x in methods])
            if 'HEAD' not in self.methods and 'GET' in self.methods:
                self.methods.add('HEAD')
        self._trace = []
        self._regex = []
        self.build_regex()

    def bind(self, _map):
        self._map = _map
        self.build_regex()

    def build_regex(self):
        ''' 构建regex '''
        regex_parts = []
        for _static, _type, _variable in parse_rule(self.rule):
            if _static:
                regex_parts.append(re.escape(_static))
                self._trace.append((False, _static))
            elif _variable:
                if _type is None or _type == 'string':
                    regex_parts.append('(?P<%s>%s)' % (_variable, '[a-zA-Z0-9_]*'))
                    self._trace.append((True, _variable))
                elif _type == 'int':
                    regex_parts.append('(?P<%s>%s)' % (_variable, '[0-9]*'))
                    self._trace.append((True, _variable))
                else:
                    raise TypeError('Rule variable argument must be int or string. default is string.')

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


class Map(object):

    def __init__(self):
        self.rules = []
        self.rules_by_endpoint = {}

    def bind_to_environ(self, environ):
        self.method = environ.get('REQUEST_METHOD', 'GET')
        self.path_info = environ.get('PATH_INFO')
        self.query_string = environ.get('QUERY_STRING')

    def add(self, rulefactory):
        '''添加rule'''
        for rule in rulefactory.get_rules(self):
            rule.bind(self)
            self.rules.append(rule)
            self.rules_by_endpoint.setdefault(rule.endpoint, []).append(rule)

    def match(self):
        path = self.path_info
        method = self.method.upper()

        for rule in self.rules:
            rv = rule.match(path)

            ''' 验证url正确性 '''
            if rv is None:
                continue

            ''' 验证请求方法和url rule接受的方法'''
            if rule.methods is not None and method not in rule.methods:
                continue
            return rule.endpoint, rv
