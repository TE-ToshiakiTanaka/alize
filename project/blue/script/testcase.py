import os
import sys
import time
import fnmatch
import random

from alize.exception import *

from blue.utility import *
from blue.utility import LOG as L
from blue.script import testcase_base

class MinicapProc(object):
    def __init__(self, testcase, debug=False):
        self.tc = testcase
        self._loop_flag = True
        self._debug = debug # Debug Flag
        self._pattern_match_flag = False # Pattern Match
        self._pattern_match_target = None
        self._capture_flag = False # Capture
        self._capture_target = None
        self.counter = 0
        self.result = Queue()

    def start(self):
        self.tc.minicap.start()
        self.loop = threading.Thread(target=self.main_loop).start()

    def finish(self):
        self.__flag = False; time.sleep(2)
        self.tc.minicap.finish()

    def __save(self, filename, data):
        with open(filename, "wb") as f:
            f.write(data)
            f.flush()

    def __save_evidence(self, counter):
        if number < 10: number = "0000%s" % str(number)
        elif number < 100: number = "000%s" % str(number)
        elif number < 1000: number = "00%s" % str(number)
        elif number < 10000: number = "0%s" % str(number)
        else: number = str(number)
        self.__save(os.path.join(TMP_EVIDENCE_DIR, "image_%s.png" % number), data)

    def main_loop(self):
        if self._debug: cv2.namedWindow("debug")
        while self.__flag:
            data = self.tc.minicap.picture.get()

            if self.counter % 10 == 0:
                self.__save_evidence(self.counter / 10)

            if self._capture_flag:
                if self._capture_target != None:

            image_pil = Image.open(io.BytesIO(data))
            image_cv = cv2.cvtColor(np.asarray(image_pil), cv2.COLOR_RGB2BGR)

            if self._pattern_match_flag:
                if self._pattern_match_target == None:
                    self.result.put(None)
                result, image_cv = Picture.search_pattern(image_cv, self._pattern_match_target)
                self.result.put(result)

            if self._debug:
                w = int(self.tc.adb().get().WIDTH) / 2
                h = int(self.tc.adb().get().HEIGHT) / 2
                resize_image_cv = cv2.resize(image_cv, (w, h))
                cv2.imshow('debug', resize_image_cv)
                key = cv2.waitKey(5)
                if key == 27: break
            self.counter += 1
        if self._debug: cv2.destroyAllWindows()

class TestCase_Base(testcase_base.TestCase_Unit):
    def __init__(self, *args, **kwargs):
        super(TestCase_Base, self).__init__(*args, **kwargs)
        self.minicap = MinicapProc(self, DEBUG)

    def sleep(self, base=1):
        sleep_time = (0.5 + base * random.random())
        L.debug("sleep time : %s" % sleep_time)
        time.sleep(sleep_time)

    def get_reference(self, reference):
        try:
            return os.path.join(TMP_DIR, self.adb.get().SERIAL, reference)
        except Exception as e:
            L.warning(e); raise e

    def get_target(self, target):
        try:
            return os.path.join(TMP_DIR, target)
        except Exception as e:
            L.warning(e); raise e
