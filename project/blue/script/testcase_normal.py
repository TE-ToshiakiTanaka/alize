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
        if not self.enable_timeout("home.png"):
            self.login(); time.sleep(5)
            while self.expedition_result(): self.sleep()
        self.tap_timeout("action_formation.png"); self.sleep()
        if form == None: return self.home()
        else: return self.formation(form)

    def login(self):
        self.adb.stop(self.get("kancolle.app")); time.sleep(5)
        self.adb.invoke(self.get("kancolle.app"));
        time.sleep(5); self.sleep()
        self.tap_timeout("start_music_off.png")
        time.sleep(5); self.sleep()
        self.tap_timeout("start_game.png")
        time.sleep(5); self.sleep()
        return True

    def expedition_result(self):
        if self.enable_timeout("expedition_result.png", loop=3, timeout=0.5):
            self.tap_timeout("expedition_result.png"); time.sleep(7)
            if self.enable_timeout("expedition_success.png", loop=2, timeout=1): pass
            elif self.enable_timeout("expedition_failed.png", loop=2, timeout=1): pass
            self.tap_timeout("next.png"); time.sleep(1)
            self.tap_timeout("next.png"); time.sleep(1)
            return self.enable_timeout("expedition_result.png", loop=3, timeout=0.5)
        else:
            return False

    def formation(self, formation):
        self.tap_timeout("formation_change.png"); self.sleep()
        if not self.enable_timeout("formation_deploy.png", loop=3, timeout=0.5):
            return False
        if formation == None: return False
        fleet = int(formation) % 3
        if self.adb.get().ROTATE == "0":
            p = POINT(self.normalize_w(int(self.adb.get().FORMATION_X) - (self.normalize_w(int(self.adb.get().FORMATION_WIDTH)) * fleet)),
                      self.normalize_h(int(self.adb.get().FORMATION_Y)),
                      self.normalize_w(int(self.adb.get().FORMATION_WIDTH)),
                      self.normalize_h(int(self.adb.get().FORMATION_HEIGHT)))
        else:
            p = POINT(self.normalize_w(int(self.adb.get().FORMATION_X)),
                      self.normalize_h(int(self.adb.get().FORMATION_Y) + (self.normalize_h(int(self.adb.get().FORMATION_HEIGHT)) * fleet)),
                      self.normalize_w(int(self.adb.get().FORMATION_WIDTH)),
                      self.normalize_h(int(self.adb.get().FORMATION_HEIGHT)))
        L.info(p);
        if not self.enable_timeout("form_fleet_1_focus.png", loop=2, timeout=0.2):
            self.tap_timeout("form_fleet_1.png"); self.sleep()
        self.tap_timeout("formation_select.png", p); self.sleep()
        time.sleep(2)
        return self.home()

    def home(self):
        self.tap_timeout("action_home.png"); time.sleep(3)
        return self.enable_timeout("home.png")
