import os
import sys
import time
import argparse
try:
    import configparser
except:
    import ConfigParser as configparser

from alize.script import AlizeTestCase

from alice.server import MinicapService
from alice.utility import *
from alice.utility import LOG as L

class TestCase_Unit(AlizeTestCase):
    def __init__(self, *args, **kwargs):
        super(TestCase_Unit, self).__init__(*args, **kwargs)
        self.get_config()
        self.get_service()
        self.service = MinicapService("minicap", self.get("args.serial"),
            self.adb.get().HEIGHT, self.adb.get().WIDTH,
            self.adb.get().MINICAP_HEIGHT, self.adb.get().MINICAP_WIDTH, self.adb.get().ROTATE)
        self.service.start(); time.sleep(1)

    def __del__(self):
        if self.service != None:
            self.service.stop()

    def arg_parse(self, parser):
        parser.add_argument(action='store', dest='testcase',
                            help='TestCase Name.')
        parser.add_argument('-s', action='store', dest='serial',
                            help='Mobile (Android) Serial ID.')
        return parser

    @classmethod
    def get_service(cls):
        cls.adb = cls.service["alize.android"].get(cls.get("args.serial"), PROFILE_DIR)
        cls.minicap = cls.service["alize.minicap"].get(cls.get("minicap.ip"), int(cls.get("minicap.port")))
        cls.pic = cls.service["alize.picture"].get()

    def get_config(cls, conf=None):
        if conf == None:
            conf = os.path.join(SCRIPT_DIR, "config.ini")
        try:
            config = configparser.RawConfigParser()
            cfp = open(conf, 'r')
            config.readfp(cfp)
            for section in config.sections():
                for option in config.options(section):
                    cls.set("%s.%s" % (section, option), config.get(section, option))
        except Exception as e:
            L.warning('error: could not read config file: %s' % str(e))
