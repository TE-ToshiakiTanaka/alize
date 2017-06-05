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
        self.tap("basic/home"); self.sleep(4)
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
            self.tap("home/expedition"); time.sleep(9)
            if self.search("home/expedition/success"): pass
            elif self.search("home/expedition/failed"): pass
            while self.tap("basic/next"):
                time.sleep(1)
            return self.search("home/expedition")
        else:
            return False

    def formation(self, formation):v
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

    def attack(self, fleet, id):
        if not self.search("home"): return False
        self.tap("home/attack"); self.sleep()
        self.tap("attack"); time.sleep(2)
        self.__attack_stage(id)
        self.__attack_id(id)
        self.tap("attack/decide"); self.sleep()
        if not self.search(self.__fleet_focus(fleet)):
            self.tap(self.__fleet(fleet)); self.sleep(2)
        if self.search("attack/rack"):
            self.slack_message(self.get("bot.attack_rack")); self.home(); return True
        if self.search("attack/damage"):
            self.slack_message(self.get("bot.attack_damage")); self.home(); return True
        self.tap("attack/start"); self.sleep(4)
        if self.search("attack/unable"):
            self.slack_message(self.get("bot.attack_failed"))
            self.home(); return False
        self.slack_message(self.get("bot.attack_success"))
        return self.search("attack/compass")

    def __attack_stage(self, id):
        if int(id) > 30: self.tap("attack/stage", _id="6"); self.sleep()
        elif int(id) > 24: self.tap("attack/stage", _id="5"); self.sleep()
        elif int(id) > 18: self.tap("attack/stage", _id="4"); self.sleep()
        elif int(id) > 12: self.tap("attack/stage", _id="3"); self.sleep()
        elif int(id) > 6: self.tap("attack/stage", _id="2"); self.sleep()
        else: pass

    def __attack_id(self, id):
        self.tap("attack/id", _id=id); self.sleep()

    def battle(self):
        if not self.search("attack/compass"):
            if self.search("home"): return True
            else: return False
        self.tap("attack/compass")
        while not self.search("basic/next"):
            if self.tap_timeout("attack/formation/1"): self.sleep(10)
            if self.tap_timeout("attack/night_battle/stop"): self.sleep(5)
            self.sleep(10)
        while self.tap("basic/next"): self.sleep(2)
        while self.search("attack/withdrawal"):
            if self.search("basic/next"):
                self.__upload("drop_%s.png" % self.adb.get().SERIAL)
                self.tap("basic/next")
        self.tap("attack/withdrawal"); time.sleep(5)
        self.slack_message(self.get("bot.attack_return"))
        return self.search("home")

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

    def exercises(self):
        if not self.search("home"):
            return False
        self.tap("home/attack"); self.sleep()
        self.tap("exercises"); self.sleep(4)
        if not self.search("exercises/select"):
            self.home(); return False
        p = POINT(self.conversion_w(int(self.adb.get().EXERCISES_X)),
                  self.conversion_h(int(self.adb.get().EXERCISES_Y)),
                  self.conversion_w(int(self.adb.get().EXERCISES_WIDTH)),
                  self.conversion_h(int(self.adb.get().EXERCISES_HEIGHT)))
        flag = True
        for _ in xrange(5):
            if self.search("exercises/win", p):
                L.info("I'm already fighting. I won.")
            elif self.search("exercises/lose", p):
                L.info("I'm already fighting. I lost.")
            else:
                L.info(p);
                self._tap(p, threshold=0.49); self.sleep(3)
                fname = self.adb_screenshot("exercises_%s.png" % self.adb.get().SERIAL)
                if self.adb.get().LOCATE == "V":
                    self.picture_rotate(fname, "90")
                self.picture_resize(fname, "360P")
                self.tap("exercises/decide"); self.sleep()
                if self.search("exercises/unable"):
                    self.tap("exercises/return"); self.sleep()
                    self.tap("exercises/x"); self.sleep()
                    self.home(); return False
                self.slack_upload(fname)
                if self.tap("exercises/start"):
                    self.slack_message(self.get("bot.exercises_start")); self.sleep(5)
                    while not self.search("basic/next"):
                        if self.tap("attack/formation/1"): self.sleep(10)
                        if self.tap("attack/night_battle/start"):
                            self.slack_message(self.get("bot.night_battle_start"))
                            self.sleep()
                        time.sleep(10)
                    if self.search("attack/result/d"): self.slack_message(self.get("bot.result_d"))
                    elif self.search("attack/result/c"): self.slack_message(self.get("bot.result_c"))
                    elif self.search("attack/result/b"): self.slack_message(self.get("bot.result_b"))
                    elif self.search("attack/result/a"): self.slack_message(self.get("bot.result_a"))
                    else: self.slack_message(self.get("bot.result_s"))
                    while self.tap("basic/next"): time.sleep(5)
                    flag = False
                    break
            self.sleep(1)
            if self.adb.get().LOCATE == "V":
                p.x = int(p.x) - int(p.width); L.info("Point : %s" % str(p))
            else:
                p.y = int(p.y) + int(p.height); L.info("Point : %s" % str(p))
        if flag:
            self.slack_message(self.get("bot.exercises_result"))
            self.__upload()
            self.home(); return False
        self.sleep(3)
        return self.home()

    def quest(self, exercises=False):
        if not self.search("home"):
            return False
        self.tap("home/quest"); self.sleep()
        self.tap("quest"); self.sleep()
        self.slack_message(self.get("bot.quest_done"))
        self.quest_done(); self.sleep()
        self.slack_message(self.get("bot.quest_check"))
        self.quest_daily(exercises); self.sleep()
        self.quest_weekly(exercises); self.sleep()
        if not self.search("quest/mission"):
            return False
        self.tap("quest/perform"); self.sleep()
        self.__upload("quest_%s" % self.adb.get().TMP_PICTURE)
        self.tap("quest/return"); self.sleep()
        return True

    def quest_done(self):
        if not self.search("quest/mission"):
            return False
        self.tap("quest/perform"); self.sleep(3)
        while self.tap("quest/done"):
            self.sleep(2)
            self.tap("quest/close"); time.sleep(4)
        return True

    def quest_daily(self, exercises=False):
        if not self.search("quest/mission"):
            return False
        self.tap("quest/daily"); self.sleep(); time.sleep(4)
        self.tap_crop("quest/acceptance", "quest/daily/attack"); self.sleep()
        self.tap_crop("quest/acceptance", "quest/daily/expedition"); self.sleep()
        self.tap_crop("quest/acceptance", "quest/daily/supply"); self.sleep()
        if exercises:
            self.tap_crop("quest/acceptance", "quest/daily/exercises"); self.sleep()
        return True

    def quest_weekly(self, exercises=False):
        if not self.search("quest/mission"):
            return False
        self.tap("quest/weekly"); self.sleep(); time.sleep(4)
        self.tap_crop("quest/acceptance", "quest/weekly/attack"); self.sleep()
        self.tap_crop("quest/acceptance", "quest/weekly/expedition"); self.sleep()
        if exercises:
            self.tap_crop("quest/acceptance", "quest/weekly/exercises"); self.sleep()
        return True
