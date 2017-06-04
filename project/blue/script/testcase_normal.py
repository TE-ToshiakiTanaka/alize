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

    def __upload(self, name=None):
        if name == None: name = self.adb.get().TMP_PICTURE
        fname = self.adb_screenshot(name)
        if self.adb.get().LOCATE == "V": self.picture_rotate(fname, "90")
        self.picture_resize(fname, "360P")
        self.slack_upload(fname)

    def initialize(self, form=None):
        if self.adb.rotate() == 0 or (not self.search("home")):
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
        time.sleep(3)
        self.__upload("formation_%s.png" % self.adb.get().SERIAL)
        return self.home()

    def supply(self, fleet):
        if not self.search("home"):
            return False
        self.tap("home/supply"); self.sleep()
        if not self.search(self.__fleet_focus(fleet)):
            self.tap(self.__fleet(fleet)); self.sleep()
        self.slack_message(self.get("bot.supply") % fleet)
        self.tap("supply"); self.sleep()
        return True

    def expedition(self, fleet, id):
        if not self.search("home"):
            return False
        self.tap("home/attack"); self.sleep()
        self.tap("expedition"); time.sleep(2); self.sleep()
        self.__expedition_stage(id); self.sleep()
        self.__expedition_id(id); self.sleep()
        if self.search("expedition/done"):
            self.slack_message(self.get("bot.expedition_done") % self.get("args.fleet"))
            return True
        self.tap("expedition/decide"); self.sleep()
        if not self.search("expedition/fleet_focus", _id=fleet):
            self.tap("expedition/fleet", _id=fleet); self.sleep()
        if self.search("expedition/unable"):
            self.slack_message(self.get("bot.expedition_unable") % self.get("args.fleet"))
            self.home()
            return False
        self.tap("expedition/start"); time.sleep(3); self.sleep()
        if self.search("expedition/done"):
            self.slack_message(self.get("bot.expedition_start") % self.get("args.fleet"))
            time.sleep(5); self.__upload()
            return True
        else:
            self.slack_message(self.get("bot.expedition_unable") % self.get("args.fleet"))
            self.home()
            return False

    def __expedition_stage(self, id):
        if int(id) > 32: self.tap("expedition/stage", _id="5"); self.sleep()
        elif int(id) > 24: self.tap("expedition/stage", _id="4"); self.sleep()
        elif int(id) > 16: self.tap("expedition/stage", _id="3"); self.sleep()
        elif int(id) > 8: self.tap("expedition/stage", _id="2"); self.sleep()
        else: pass

    def __expedition_id(self, id):
        self.tap("expedition/id", _id=id); self.sleep()

    def __fleet(self, fleet):
        return "basic/fleet/%s" % fleet

    def __fleet_focus(self, fleet):
        return "basic/fleet_focus/%s" % fleet
