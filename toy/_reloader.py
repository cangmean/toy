# coding=utf-8

import os
import sys

class Reloader(object):

    """ reload modify files. """

    if sys.platform.startswith('java'):
        SUFFIX = '$py.class'
    else:
        SUFFIX = '.pyc'

    def __init__(self):
        # modify times
        self.mtimes = {}

    def __call__(self):
        # check all modules 
        for mod in sys.modules.values():
            self.check(mod)

    def check(self, mod):

        if not(mod and hasattr(mod, '__file__') and mod.__file__):
            return

        try:
            # get file last modify time
            mtime = os.stat(mod.__file__).st_mtime
        except (OSError, IOError):
            return 

        if mod.__file__.endswith(self.__class__.SUFFIX) and os.path.exists(mod.__file__[:-1]):
            # get .pyc and .py file max modify time
            mtime = max(os.stat(mod.__file__[:-1]).st_mtime, mtime)

        # set mtime to mtimes if mtimes not this module. reload module if module not in mtimes.
        if mod not in self.mtimes:
            self.mtimes[mod] = mtime
        elif self.mtimes[mod] < mtime:
            try:
                reload(mod)
                self.mtimes[mod] = mtime
            except ImportError:
                pass
 
