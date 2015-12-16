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

    def build_regex(self):
        regex_parts = []
        for _static, _type, _variable in parse_rule(rule):
            if _type is None and _static:
                regex_parts.append(re.escape(_static))
                self._trace.append((False, _static))
            elif _variable:
                regex_parts.append('(?P<%s>%s)' % (_variable, '[a-zA-Z0-9_]*'))
                self._trace.append((True, _variable))
        regex = r'^%s$' % (u''.join(regex_parts))
        self._regex = re.compile(regex, re.UNICODE)


class Router(object):

    def __init__(self):
        self.maps = {}

    def register(self, rule, func, methods):

        r = Rule(rule, methods)
        self.maps[r] = func
