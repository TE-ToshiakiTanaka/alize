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

    def test_expedition(self):
        L.info("*** Expedition ***")
        try:
            self.minicap_start(); time.sleep(2)
            self.assertTrue(self.initialize())
            while self.expedition_result(): time.sleep(1)
            self.slack_message(self.get("bot.expedition") % self.get("args.fleet"))
            self.assertTrue(self.supply(self.get("args.fleet")))
            self.assertTrue(self.home())
            self.assertTrue(self.expedition(
                self.get("args.fleet"), self.get("args.expedition")))
            self.assertTrue(self.home())
            while self.expedition_result(): time.sleep(1)
            self.minicap_finish()
        except Exception as e:
            self.minicap_finish()
            time.sleep(2); self.minicap_create_video()
            self.fail()

    @classmethod
    def tearDownClass(cls):
        L.info("*** End TestCase     : %s *** " % __file__)
