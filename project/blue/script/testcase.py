import os
import sys
import time
import glob
import random

from blue.utility import *
from blue.utility import LOG as L
from blue.minicap import MinicapProc
from blue.script import testcase_adb
from blue.parser import Parser as P

DEBUG=True

class TestCase_Base(testcase_adb.TestCase_Android):
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
        sleep_time = (0.5 + base * random.random())
        L.debug("sleep time : %s" % sleep_time)
        time.sleep(sleep_time)

    def __box(self, width, height, bounds):
        x = int((width * int(bounds["s_x"])) / 100.00)
        y = int((height * int(bounds["s_y"])) / 100.00)
        width = int((width * int(bounds["f_x"])) / 100.00) - x
        height = int((height * int(bounds["f_y"])) / 100.00) - y
        return POINT(x, y, width, height)

    def tap(self, target, box=None, threshold=0.2, count=10):
        result = self.find(target, box, count)
        if result != None:
            L.info(self._tap(result, threshold))
            return True
        else: return False

    def find(self, target, box=None, count=10):
        name, bounds = P.search(self.get_base(target))
        w = int(self.adb.get().MINICAP_WIDTH)
        h = int(self.adb.get().MINICAP_HEIGHT)
        if box == None: box = self.__box(w, h, bounds)
        for f in glob.glob(os.path.join(self.get_base(target), name)):
            result = self.proc.search_pattern(os.path.join(self.get_base(target), f), box, count)
            if result != None: return result
        return None

    def search(self, target, box=None, count=10):
        result = self.find(target, box, count)
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
            return os.path.join(TMP_REFERENCE_DIR, "kancolle", target)
        except Exception as e:
            L.warning(e); raise e

    def _tap(self, result, threshold=0.2):
        if self.adb.get().ROTATE == "90":
            x = self.normalize_w(result.x) + self.randomize(result.width, threshold)
            y = self.normalize_h(result.y) + self.randomize(result.height, threshold)
        else:
            x = self.normalize_h(result.y) + self.randomize(result.height, threshold)
            y = int(self.adb.get().WIDTH) - (self.normalize_w(result.x) + self.randomize(result.width, threshold))
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
