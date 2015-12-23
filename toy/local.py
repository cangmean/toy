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
        try:
            return self._stack[-1]
        except (AttributeError, IndexError):
            return None

    def __len__(self):
        return len(self._stack)


if __name__ == '__main__':
    _stack = LocalStack()
    print _statck.top
