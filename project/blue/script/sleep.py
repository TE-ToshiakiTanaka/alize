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

    def test_sleep(self):
        userid = self.get("args.userid"); token = self.get("args.token")
        url = self.get("args.url"); job = self.get("args.job")
        if self.sleep_get_status(userid, token, url, job):
            timeout = int(self.get("args.timeout"))
            L.debug("Timeout : %d " % timeout); time.sleep(timeout)
        else:
            L.debug("Retry.")
        self.assertTrue(self.sleep_invoke_job(userid, token, url, job))

    @classmethod
    def tearDownClass(cls):
        L.info("*** End TestCase   : %s *** " % __file__)
