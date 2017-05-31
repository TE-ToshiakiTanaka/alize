import os
import sys
import time

from blue.utility import *
from blue.utility import LOG as L
from blue.script import testcase_normal

class TestCase(testcase_normal.TestCase):
    def __init__(self, *args, **kwargs):
        super(TestCase, self).__init__(*args, **kwargs)

    @classmethod
    def setUpClass(cls):
        L.info("*** Start TestCase   : %s *** " % __file__)

    def test_1(self):
        L.info("*** Capture ***")
        self.minicap_start()
        time.sleep(10)
        L.debug(self.minicap_search_pattern("history.png"))
        time.sleep(10)
        L.info(self.screenshot("capture.png"))
        time.sleep(1)
        self.minicap_finish()
        time.sleep(2)
        self.minicap_create_video()

    @classmethod
    def tearDownClass(cls):
        L.info("*** End TestCase     : %s *** " % __file__)
