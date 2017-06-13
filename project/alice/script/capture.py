import os
import sys
import time

from alice.utility import *
from alice.utility import LOG as L
from alice.script import testcase_normal

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
            flag = os.path.join(TMP_DIR, "flag.txt")
            #self.workspace.touch("flag.txt")
            while os.path.exists(flag):
                time.sleep(15)
            self.minicap_finish()
        except Exception as e:
            self.minicap_finish(); time.sleep(2)
            self.minicap_create_video()

    @classmethod
    def tearDownClass(cls):
        L.info("*** End TestCase     : %s *** " % __file__)
