import os
import sys
import time
import unittest
import argparse
import importlib
import traceback

from alize.log import LOG as L
from alize.define import *
from alize.exception import *


class AlizeTestCase(unittest.TestCase):
    config = {}
    service = {}

    def __init__(self, *args, **kwargs):
        global service
        super(AlizeTestCase, self).__init__(*args, **kwargs)
        self.register(ALIZE_LIB)
        self.__parse()

    @classmethod
    def register(cls, host):
        if not os.path.exists(host):
            raise LibraryError("%s is not exists." % (host))
        sys.path.append(host)
        for fdn in os.listdir(host):
            try:
                if fdn.endswith(".pyc") or fdn.endswith(".py"): pass
                elif fdn.endswith("__pycache__"): pass
                else:
                    module = importlib.import_module("%s.service" % fdn)
                    cls.service[module.NAME] = module.FACTORY
            except Exception as e:
                L.warning(traceback.print_exc())
                L.warning(type(e).__name__ + ": " + str(e))

    @classmethod
    def set(cls, name, value):
        cls.config[name] = value

    @classmethod
    def get(cls, name):
        return cls.config[name]

    def __parse(self):
        parser = argparse.ArgumentParser()

        parser = self.arg_parse(parser)

        results = parser.parse_args()
        for k, v in vars(results).items():
            self.set("args.%s" % k, v)

    def arg_parse(self, parser):
        parser.add_argument(action='store', dest="testcase",
                            help='TestCase Name.')
        return parser

    @classmethod
    def get_service(cls, settings):
        pass
