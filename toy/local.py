# coding=utf-8


class LocalStack(object):

    def __init__(self):
        self._stack = []

    def empty(self):
        if not self._stack:
            return True
        return False

    def push(self, obj):
        self._stack.append(obj)

    def pop(self):
        if self.empty():
            return None
        else:
            return self._stack.pop()

    @property
    def top(self):
        if self.empty():
            return self._stack[-1]
        else:
            return None
