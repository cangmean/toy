# coding=utf-8


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
