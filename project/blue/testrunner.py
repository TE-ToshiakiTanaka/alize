import os
import sys
import alize

PATH = os.path.abspath(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if not PATH in sys.path:
    sys.path.insert(0, PATH)

if alize.__version__ < "0.1.0":
    sys.exit("alize version over 0.1.0. : %s " % (alize.__version__))

from alize.application import AlizeRunner
from alize.workspace import Workspace

from blue.utility import *
from blue.script.testcase_base import TestCase_Unit

class TestRunner(object):
    def __init__(self):
        self.runner = AlizeRunner()
        self.workspace = Workspace(WORK_DIR)

        self.lib = self.workspace.mkdir("lib")
        self.tmp = self.workspace.mkdir("tmp")
        self.log = self.workspace.mkdir("log")
        self.report = self.workspace.mkdir("report")

        self.tmp_video = self.workspace.mkdir("tmp/video")
        self.tmp_evidence = self.workspace.mkdir("tmp/evidence")

        TestCase_Unit.register(LIB_DIR)

    def execute(self, script):
        self.runner.execute(script, SCRIPT_DIR)

    def execute_with_report(self, script):
        self.runner.execute_with_report(script, SCRIPT_DIR, REPORT_DIR)

if __name__ == "__main__":
    if len(sys.argv[1:]) < 1:
        sys.exit("Usage: %s <filename>" % sys.argv[0])
    testcase = sys.argv[1]
    runner = TestRunner()
    runner.execute_with_report(testcase)
