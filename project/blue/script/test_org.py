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
        try:
            self.minicap_start(); time.sleep(2)
            #self.login()
            #L.debug(self.search("home/expedition"))
            #L.debug(self.tap("home/attack")); time.sleep(2)
            L.debug(self.initialize())
            while self.expedition_result(): self.sleep()
            L.debug(self.supply(2))
            L.debug(self.home())
            while self.expedition_result(): self.sleep()
            L.debug(self.expedition(2, 2))
            L.debug(self.home())
            time.sleep(2)
            self.minicap_finish()
        except Exception as e:
            self.minicap_finish(); time.sleep(2)
            self.minicap_create_video()

    @classmethod
    def tearDownClass(cls):
        L.info("*** End TestCase     : %s *** " % __file__)
