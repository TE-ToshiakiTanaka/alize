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
from blue.script import testcase_base

DEBUG=True

class MinicapProc(object):
    def __init__(self, testcase, debug=False):
        self.tc = testcase
        self._loop_flag = True
        self._debug = debug # Debug Flag

        self._pattern_match_flag = False # Pattern Match
        self._pattern_match_target = None
        self.patternmatch_result = Queue()

        self._capture_flag = False # Capture
        self._capture_target = None
        self.capture_result = Queue()

        self.counter = 0

    def start(self):
        self.tc.minicap.start()
        self.loop = threading.Thread(target=self.main_loop).start()

    def finish(self):
        self._loop_flag = False; time.sleep(2)
        self.tc.minicap.finish()

    def __save(self, filename, data):
        with open(filename, "wb") as f:
            f.write(data)
            f.flush()

    def __save_cv(self, filename, img_cv):
        return cv2.imwrite(filename, img_cv)

    def __save_evidence(self, number, data):
        if number < 10: number = "0000%s" % str(number)
        elif number < 100: number = "000%s" % str(number)
        elif number < 1000: number = "00%s" % str(number)
        elif number < 10000: number = "0%s" % str(number)
        else: number = str(number)
        self.__save_cv(os.path.join(TMP_EVIDENCE_DIR, "image_%s.png" % number), data)

    def search_pattern(self, target, count=3):
        self._pattern_match_target = target
        self._pattern_match_flag = True
        ok = 0
        while ok < count:
            result = self.patternmatch_result.get()
            if result != None:
                ok += 1
        self._pattern_match_target = None
        self._pattern_match_flag = False
        return result

    def capture_image(self, filename=None, timeout=1):
        if filename != None:
            self._capture_target = filename
        else: filename = "capture.png"
        self._capture_flag = True
        for i in xrange(timeout):
            result = self.capture_result.get()
            if result:
                break
        abspath = os.path.join(TMP_DIR, filename)
        self._capture_target = None
        self._capture_flag = False
        return abspath

    def create_video(self, src, dst, filename="output.avi"):
        output = os.path.join(dst, filename)
        if os.path.exists(output):
            os.remove(output)
        cmd = r'%s -r 3 -i %s -vcodec mjpeg %s' % (
            FFMPEG_BIN, os.path.join(src, "image_%05d.png"), os.path.join(dst, filename))
        L.debug(run(cmd)[0])

    def main_loop(self):
        if self._debug: cv2.namedWindow("debug")
        while self._loop_flag:
            data = self.tc.minicap.picture.get()

            image_pil = Image.open(io.BytesIO(data))
            image_cv = cv2.cvtColor(np.asarray(image_pil), cv2.COLOR_RGB2BGR)

            if self._capture_flag:
                if self._capture_target != None: outputfile = os.path.join(TMP_DIR, self._capture_target)
                else: outputfile = os.path.join(TMP_DIR, "capture.png")
                result = self.__save_cv(outputfile, image_cv)
                self.capture_result.put(result)

            if self._pattern_match_flag:
                if self._pattern_match_target == None:
                    self.result.put(None)
                result, image_cv = self.tc.pic.search_pattern(image_cv, self._pattern_match_target)
                self.patternmatch_result.put(result)

            if self.counter % 10 == 0:
                self.__save_evidence(self.counter / 10, image_cv)

            if self._debug:
                w = int(self.tc.adb.get().WIDTH) / 2
                h = int(self.tc.adb.get().HEIGHT) / 2
                if int(self.tc.adb.get().ROTATE) == 0:
                    resize_image_cv = cv2.resize(image_cv, (h, w))
                else:
                    resize_image_cv = cv2.resize(image_cv, (w, h))
                cv2.imshow('debug', resize_image_cv)
                key = cv2.waitKey(5)
                if key == 27: break
            self.counter += 1
        if self._debug: cv2.destroyAllWindows()

class TestCase_Base(testcase_base.TestCase_Unit):
    def __init__(self, *args, **kwargs):
        super(TestCase_Base, self).__init__(*args, **kwargs)
        self.minicap_proc = MinicapProc(self, DEBUG)

    def minicap_start(self):
        self.adb.forward("tcp:%s localabstract:minicap" % self.get("minicap.port"))
        self.minicap_proc.start()

    def minicap_finish(self):
        self.minicap_proc.finish()

    def screenshot(self, filename=None):
        return self.minicap_proc.capture_image(filename)

    def minicap_create_video(self):
        self.minicap_proc.create_video(TMP_EVIDENCE_DIR, TMP_VIDEO_DIR)

    def minicap_search_pattern(self, reference):
        return self.minicap_proc.search_pattern(self.get_reference(reference))

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

    def tap(self, reference, target=None, threshold=0.2):
        if target == None:
            self.adb_screenshot(self.adb.get().TMP_PICTURE)
            target = self.adb.get().TMP_PICTURE
        result = self.picture_find_pattern(
                self.get_target(target), self.get_reference(reference))
        if not result == None:
            L.info(self._tap(result, threshold))
            return True
        else: return False

    def _tap(self, result, threshold=0.2):
        if self.adb.get().LOCATE == "H":
            x = int(result.x) + random.randint(int(int(result.width) * threshold) , int(int(result.width) * (1.0 - threshold)))
            y = int(result.y) + random.randint(int(int(result.height) * threshold) , int(int(result.height) * (1.0 - threshold)))
        else:
            x = int(result.y) + random.randint(int(int(result.height) * threshold) , int(int(result.height) * (1.0 - threshold)))
            y = int(self.adb.get().WIDTH) - (int(result.x) + random.randint(int(int(result.width) * threshold) , int(int(result.width) * (1.0 - threshold))))
        return self.adb_tap(x, y)

    def enable(self, reference, target=None):
        L.debug("reference : %s" % reference)
        if target == None:
            self.adb_screenshot(self.adb.get().TMP_PICTURE)
            target = self.adb.get().TMP_PICTURE
        return self.picture_is_pattern(
            self.get_target(target), self.get_reference(reference))

    def find(self, reference, target=None):
        L.debug("reference : %s " % reference)
        if target == None:
            self.adb_screenshot(self.adb.get().TMP_PICTURE)
            target = self.adb.get().TMP_PICTURE
        result = self.picture_find_pattern(
            self.get_target(target), self.get_reference(reference))
        if not result == None: return result
        else: return None

    def enable_timeout(self, reference, target=None, loop=3, timeout=0.5):
        result = False
        for _ in range(loop):
            if self.enable(reference, target): result = True; break
            time.sleep(timeout)
        return result

    def tap_timeout(self, reference, target=None, loop=3, timeout=0.5, threshold=0.2):
        if not self.enable_timeout(reference, target, loop, timeout):
            return False
        target = self.adb.get().TMP_PICTURE
        return self.tap(reference, target, threshold)

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
