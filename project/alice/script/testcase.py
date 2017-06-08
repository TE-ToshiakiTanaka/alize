import os
import sys
import time
import glob
import random
import fnmatch

from alice.utility import *
from alice.utility import LOG as L
from alice.minicap import MinicapProc
from alice.parser import Parser as P

from alice.script import testcase_base


DEBUG=True

class TestCase_Base(testcase_base.TestCase_Unit):
    def __init__(self, *args, **kwargs):
        super(TestCase_Base, self).__init__(*args, **kwargs)
        self.proc = MinicapProc(self, DEBUG)

    def minicap_start(self):
        self.adb.forward("tcp:%s localabstract:minicap" % self.get("minicap.port"))
        self.proc.start()

    def minicap_finish(self):
        self.proc.finish()

    def minicap_screenshot(self, filename=None):
        if filename == None: filename = "capture.png"
        return self.proc.capture_image(filename)

    def minicap_create_video(self):
        self.proc.create_video(TMP_EVIDENCE_DIR, TMP_VIDEO_DIR)

    def minicap_search_pattern(self, reference, box=None, count=30):
        return self.proc.search_pattern(self.get_reference(reference), box, count)

    def sleep(self, base=1):
        sleep_time = (base - 0.5 * random.random())
        L.debug("sleep time : %s" % sleep_time)
        time.sleep(sleep_time)

    def __box(self, width, height, bounds):
        x = int((width * int(bounds["s_x"])) / 100.00)
        y = int((height * int(bounds["s_y"])) / 100.00)
        width = int((width * int(bounds["f_x"])) / 100.00) - x
        height = int((height * int(bounds["f_y"])) / 100.00) - y
        return POINT(x, y, width, height)

    def tap_crop(self, target, crop_target, threshold=0.2, count=10, _id=None):
        box_result = self.find_all(crop_target, None, count, id=None)
        if len(box_result) == 0: return False
        for r in box_result:
            L.info(r)
            result = self.find(target, r, count, id=_id)
            if result == None: L.info(self._tap(r, threshold))
        return True

    def tap(self, target, box=None, threshold=0.2, count=10, _id=None):
        result = self.find(target, box, count, id=_id)
        if result != None:
            L.info(self._tap(result, threshold))
            return True
        else: return False

    def find_all(self, target, box=None, count=10, id=None):
        name, bounds = P.search(self.get_base(target))
        if id != None: name = name % str(id)
        if self.adb.get().ROTATE == "0":
            w = int(self.adb.get().MINICAP_HEIGHT)
            h = int(self.adb.get().MINICAP_WIDTH)
        else:
            w = int(self.adb.get().MINICAP_WIDTH)
            h = int(self.adb.get().MINICAP_HEIGHT)
        if box == None: box = self.__box(w, h, bounds)
        res = []
        for f in glob.glob(os.path.join(self.get_base(target), name)):
            result = self.proc.search_pattern(os.path.join(self.get_base(target), f), box, count)
            if result != None: res.append(result)
        return res

    def find(self, target, box=None, count=10, id=None):
        name, bounds = P.search(self.get_base(target))
        if id != None: name = name % str(id)
        if self.adb.get().ROTATE == "0":
            w = int(self.adb.get().MINICAP_HEIGHT)
            h = int(self.adb.get().MINICAP_WIDTH)
        else:
            w = int(self.adb.get().MINICAP_WIDTH)
            h = int(self.adb.get().MINICAP_HEIGHT)
        if box == None: box = self.__box(w, h, bounds)
        for f in glob.glob(os.path.join(self.get_base(target), name)):
            result = self.proc.search_pattern(os.path.join(self.get_base(target), f), box, count)
            if result != None: return result
        return None

    def search(self, target, box=None, count=10, _id=None):
        result = self.find(target, box, count, id=_id)
        if result != None: return True
        return False

    def search_timeout(self, target, box=None, loop=3, timeout=0.1):
        result = False
        for _ in range(loop):
            if self.search(target, box, 10): result = True; break
            time.sleep(timeout)
        if result == False: self.minicap_screenshot("failed.png")
        return result

    def get_base(self, target):
        try:
            return os.path.join(TMP_REFERENCE_DIR, "sinoalice", target)
        except Exception as e:
            L.warning(e); raise e

    def _tap(self, result, random=True, threshold=0.2):
        if random:
            x = self.normalize_w(result.x) + self.randomize(result.width, threshold)
            y = self.normalize_h(result.y) + self.randomize(result.height, threshold)
        else:
            x = self.normalize_w(result.x)
            y = self.normalize_h(result.y)
        return self.adb.tap(x, y)

    def normalize(self, base, real, virtual):
        return int(base * real / virtual)

    def normalize_w(self, base):
        return self.normalize(base, int(self.adb.get().WIDTH), int(self.adb.get().MINICAP_WIDTH))

    def conversion_w(self, base):
        return self.normalize(base, int(self.adb.get().MINICAP_WIDTH), int(self.adb.get().WIDTH))

    def normalize_h(self, base):
        return self.normalize(base, int(self.adb.get().HEIGHT), int(self.adb.get().MINICAP_HEIGHT))

    def conversion_h(self, base):
        return self.normalize(base, int(self.adb.get().MINICAP_HEIGHT), int(self.adb.get().HEIGHT))

    def randomize(self, base, threshold):
        return random.randint(int(int(base) * threshold) , int(int(base) * (1.0 - threshold)))
