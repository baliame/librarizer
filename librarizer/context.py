from __future__ import print_function
import sys
import time
import json
import os
from os.path import join as pathjoin
from os.path import expanduser as pathexpanduser

verbosity_quiet = -1
verbosity_normal = 0
verbosity_loud = 1


class Context:
    def __init__(self):
        self.libjson = {"mapping": {}}
        try:
            with open(pathjoin(pathexpanduser("~"), '.config', 'librarizer.json')) as f:
                self.libjson = json.loads(f.read())
        except Exception:
            pass
        self.options = {}
        self.verbosity = verbosity_normal
        self.log_destination = sys.stdout
        self.storage = {}

    def write(self):
        confdir = pathjoin(pathexpanduser("~"), '.config')
        try:
            os.stat(confdir)
        except Exception:
            os.mkdir(confdir)
        with open(pathjoin(confdir, 'librarizer.json'), 'w') as f:
            f.write(json.dumps(self.libjson, sort_keys=True, indent=4))

    def merge(self, kwargs, include=None, exclude=[]):
        for k, v in kwargs.items():
            key = k.replace("_", "-")
            if (include is not None and key not in include) or key in exclude:
                continue
            if v is not None:
                self.options[key] = v

    def log(self, message, min_verbosity=verbosity_normal):
        if self.verbosity >= min_verbosity:
            ts = time.strftime("%Y-%m-%d %H:%M:%S%z")
            print("{0} {1}".format(ts, message), file=self.log_destination)
            self.log_destination.flush()

    def __len__(self):
        return len(self.options)

    def __getitem__(self, optname):
        return self.options[optname]

    def __setitem__(self, optname, value):
        self.options[optname] = value

    def __call__(self, which):
        if which in self.libjson["mapping"]:
            return self.libjson["mapping"][which]
        return None

    def rename(self, src, dest):
        self.libjson["mapping"][src] = dest
        self.write()
