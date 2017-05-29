import os
import sys
import csv
import unittest
import importlib
import xmlrunner
import traceback

from alize.log import LOG as L
from alize.exception import *

class AlizeRunner(object):
    def __init__(self):
        pass

    def load(self, testcase, host):
        if testcase.find(".py") != -1:
            script = testcase
        else:
            script = testcase + ".py"
        path = os.path.join(host, script)
        if not os.path.exists(path):
            raise TestRunnerError("%s is not exists." % (path))
        name = script[:script.find(".")]
        L.debug("TestCase : %s" % path)
        try:
            if os.path.exists(path):
                return importlib.import_module(name)
            else:
                return False
        except ImportError as e:
            L.warning(traceback.print_exc())
            L.warning(type(e).__name__ + ": " + str(e))
            return False

    def execute(self, script, host, v=2):
        if not os.path.exists(host):
            raise TestRunnerError("%s is not exists." % (host))
        sys.path.append(host)

        suite = unittest.TestSuite()
        loader = unittest.TestLoader()
        module = self.load(script, host)
        L.debug("Module Name : " + str(module))
        if not module:
            L.warning("Not loaded module : %s" % script)
            raise TestRunnerError("%s is not extended AlizeTestCase." % script)
        else: suite.addTest(loader.loadTestsFromModule(module))
        unittest.TextTestRunner(verbosity=v).run(suite)
        sys.path.remove(host)

    def execute_with_report(self, script, host, output):
        if not os.path.exists(host):
            raise TestRunnerError("%s is not exists." % (host))
        sys.path.append(host)

        if not os.path.exists(output):
            raise TestRunnerError("%s is not exists." % (output))

        suite = unittest.TestSuite()
        loader = unittest.TestLoader()
        module = self.load(script, host)
        if not module:
            L.warning("Not loaded module : %s" % script)
            raise TestRunnerError("%s is not extended AlizeTestCase." % script)
        else: suite.addTest(loader.loadTestsFromModule(module))
        xmlrunner.XMLTestRunner(output=output).run(suite)
        sys.path.remove(host)
