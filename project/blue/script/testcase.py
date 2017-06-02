import os
import io
import sys
import time
import fnmatch
import random
import threading
from Queue import Queue

import cv2
from PIL import Image
import numpy as np

from alize.exception import *
from alize.cmd import run

from blue.utility import *
from blue.utility import LOG as L
from blue.minicap import MinicapProc
from blue.script import testcase_adb

DEBUG=True

class TestCase_Base(testcase_adb.TestCase_Android):
    def __init__(self, *args, **kwargs):
        super(TestCase_Base, self).__init__(*args, **kwargs)
        self.minicap_proc = MinicapProc(self, DEBUG)

    def minicap_start(self):
        self.adb.forward("tcp:%s localabstract:minicap" % self.get("minicap.port"))
        self.minicap_proc.start()

    def minicap_finish(self):
        self.minicap_proc.finish()

    def minicap_screenshot(self, filename=None):
        if filename == None: filename = "capture.png"
        return self.minicap_proc.capture_image(filename)

    def minicap_create_video(self):
        self.minicap_proc.create_video(TMP_EVIDENCE_DIR, TMP_VIDEO_DIR)

    def minicap_search_pattern(self, reference, box=None):
        return self.minicap_proc.search_pattern(self.get_reference(reference), box)

    def sleep(self, base=1):
        sleep_time = (0.5 + base * random.random())
        L.debug("sleep time : %s" % sleep_time)
        time.sleep(sleep_time)

    def get_reference(self, reference):
        try:
            return os.path.join(TMP_DIR, "reference", self.adb.get().SERIAL, reference)
        except Exception as e:
            L.warning(e); raise e

    def get_target(self, target):
        try:
            return os.path.join(TMP_DIR, target)
        except Exception as e:
            L.warning(e); raise e

    def tap(self, reference, box=None, threshold=0.2):
        result = self.minicap_proc.search_pattern(self.get_reference(reference), box)
        if not result == None:
            L.info(self._tap(result, threshold))
            return True
        else: return False

    def _tap(self, result, threshold=0.2):
        if self.adb.get().ROTATE == "90":
            x = int(result.x) + random.randint(int(int(result.width) * threshold) , int(int(result.width) * (1.0 - threshold)))
            y = int(result.y) + random.randint(int(int(result.height) * threshold) , int(int(result.height) * (1.0 - threshold)))
        else:
            x = int(result.y) + random.randint(int(int(result.height) * threshold) , int(int(result.height) * (1.0 - threshold)))
            y = int(self.adb.get().WIDTH) - (int(result.x) + random.randint(int(int(result.width) * threshold) , int(int(result.width) * (1.0 - threshold))))
        return self.adb.tap(x, y)

    def enable(self, reference, box=None):
        L.debug("reference : %s" % reference)
        return (self.minicap_proc.search_pattern(self.get_reference(reference), box) != None)

    def find(self, reference, box=None):
        L.debug("reference : %s " % reference)
        result = self.minicap_proc_search_pattern(self.get_reference(reference), box)
        if not result == None: return result
        else: return None

    def enable_timeout(self, reference, box=None, loop=3, timeout=0.5):
        result = False
        for _ in range(loop):
            if self.enable(reference, box): result = True; break
            time.sleep(timeout)
        if result == False: self.minicap_screenshot("failed.png")
        return result

    def tap_timeout(self, reference, box=None, loop=3, timeout=0.5, threshold=0.2):
        if not self.enable_timeout(reference, box, loop, timeout):
            return False
        return self.tap(reference, box, threshold)

    def enable_pattern_timeout(self, pattern, loop=3, timeout=0.5):
        targets = self.__search_pattern(pattern)
        for target in targets:
            if self.enable_timeout(target, loop=loop, timeout=timeout):
                return True
        return False

    def tap_pattern_timeout(self, pattern, loop=3, timeout=0.5):
        targets = self.__search_pattern(pattern)
        for target in targets:
            if self.tap_timeout(target, loop=loop, timeout=timeout):
                return True
        return False

    def __search_pattern(self, pattern, host=""):
        result = []
        if host == "":
            host = os.path.join(TMP_DIR, self.adb.get().SERIAL)
        files = os.listdir(host)
        return fnmatch.filter(files, pattern)

    def tap_timeout_crop(self, reference, point, filename=None, loop=5, timeout=5):
        if filename == None:
            filename = self.adb_screenshot(self.adb.get().TMP_PICTURE)
        target = self.picture_crop(filename, point,
            self.get_target("crop_%s" % self.adb.get().TMP_PICTURE))
        return self.tap_crop_inside(reference, target, point)

    def tap_crop_inside(self, reference, target, point):
        if target == None:
            return False
        result = self.picture_find_pattern(
            self.get_target(target), self.get_reference(reference))
        if not result == None:
            result.x = int(result.x) + int(point.x)
            result.y = int(result.y) + int(point.y)
            L.info("Target Point : %s" % result)
            L.info(self._tap(result))
            return True
        else:
            return False

    def enable_timeout_crop(self, reference, point, filename=None, loop=3, timeout=0.5):
        if filename == None:
            filename = self.adb_screenshot(self.adb.get().TMP_PICTURE)
        target = self.picture_crop(filename, point,
            self.get_target("crop_%s" % self.adb.get().TMP_PICTURE))
        return self.enable_timeout(reference, target, loop, timeout)

    def enable_pattern_crop_timeout(self, pattern, point, filename=None, loop=3, timeout=0.5):
        targets = self.__search_pattern(pattern)
        for target in targets:
            if self.enable_timeout_crop(target, point, filename, loop=loop, timeout=timeout):
                return True
        return False

    def tap_pattern_crop_timeout(self, pattern, point, filename=None, loop=3, timeout=0.5):
        targets = self.__search_pattern(pattern)
        for target in targets:
            if self.tap_timeout_crop(target, point, filename, loop=loop, timeout=timeout):
                return True
        return False

    def tap_pattern_check_timeout(self, pattern, check, loop=3, timeout=0.5):
        filename = self.adb_screenshot(self.adb.get().TMP_PICTURE)
        targets = self.__search_pattern(pattern)
        for target in targets:
            result = self.find(target, self.adb.get().TMP_PICTURE)
            L.info("reference : %s : %s" % (target, str(result)))
            if result == None:
                pass
            elif not self.enable_timeout_crop(check, result, loop=loop, timeout=timeout):
                return self.tap(target, self.adb.get().TMP_PICTURE)
        return False
