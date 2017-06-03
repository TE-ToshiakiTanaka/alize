import os
import sys
import time
import json
import base64
import urllib2

from blue.utility import *
from blue.utility import LOG as L
from blue.script import testcase

class TestCase(testcase.TestCase_Base):

    def initialize(self, form=None):
        if self.search("home"): pass
        else:
            self.login(); time.sleep(3)
            while self.expedition_result(): self.sleep()
        self.tap("home/formation"); self.sleep()
        if form == None: return self.home()
        else: return self.formation(form)

    def home(self):
        self.tap("basic/home"); time.sleep(3)
        return self.search("home")

    def login(self):
        self.adb.stop(self.get("kancolle.app")); time.sleep(5)
        self.adb.invoke(self.get("kancolle.app"));
        time.sleep(5); self.sleep()
        self.tap("login/music"); time.sleep(5); self.sleep()
        self.tap("login"); time.sleep(5); self.sleep()
        return True

    def expedition_result(self):
        if self.search("home/expedition"):
            self.tap("home/expedition"); time.sleep(7)
            if self.search("home/expedition/success"): pass
            elif self.search("home/expedition/failed"): pass
            self.tap("basic/next"); time.sleep(1)
            self.tap("basic/next"); time.sleep(1)
            return self.search("home/expedition")
        else:
            return False

    def formation(self, formation):
        self.tap("formation/change"); self.sleep()
        if not self.search("formation/deploy"):
            return False
        if formation == None: return False
        fleet = int(formation) % 3
        if self.adb.get().ROTATE == "0":
            p = POINT(self.conversion_w(int(self.adb.get().FORMATION_X) - (self.conversion_w(int(self.adb.get().FORMATION_WIDTH)) * fleet)),
                      self.conversion_h(int(self.adb.get().FORMATION_Y)),
                      self.conversion_w(int(self.adb.get().FORMATION_WIDTH)),
                      self.conversion_h(int(self.adb.get().FORMATION_HEIGHT)))
        else:
            p = POINT(self.conversion_w(int(self.adb.get().FORMATION_X)),
                      self.conversion_h(int(self.adb.get().FORMATION_Y) + (self.conversion_h(int(self.adb.get().FORMATION_HEIGHT)) * fleet)),
                      self.conversion_w(int(self.adb.get().FORMATION_WIDTH)),
                      self.conversion_h(int(self.adb.get().FORMATION_HEIGHT)))
        L.info(p);
        if not self.search("formation/fleet_1_focus"):
            self.tap("formation/fleet_1"); self.sleep()
        self.tap("formation/select", p); self.sleep()
        return self.home()
