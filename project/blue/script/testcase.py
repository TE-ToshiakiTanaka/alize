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
        self._capture_flag = False # Capture
        self._capture_target = None
        self.counter = 0
        self.result = Queue()

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
        cv2.imwrite(filename, img_cv)

    def __save_evidence(self, number, data):
        if number < 10: number = "0000%s" % str(number)
        elif number < 100: number = "000%s" % str(number)
        elif number < 1000: number = "00%s" % str(number)
        elif number < 10000: number = "0%s" % str(number)
        else: number = str(number)
        self.__save_cv(os.path.join(TMP_EVIDENCE_DIR, "image_%s.png" % number), data)

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
            """
            if self._capture_flag:
                if self._capture_target != None:
            """
            image_pil = Image.open(io.BytesIO(data))
            image_cv = cv2.cvtColor(np.asarray(image_pil), cv2.COLOR_RGB2BGR)

            if self.counter % 10 == 0:
                self.__save_evidence(self.counter / 10, image_cv)

            if self._pattern_match_flag:
                if self._pattern_match_target == None:
                    self.result.put(None)
                result, image_cv = Picture.search_pattern(image_cv, self._pattern_match_target)
                self.result.put(result)

            if self._debug:
                w = int(self.tc.adb.get().WIDTH) / 2
                h = int(self.tc.adb.get().HEIGHT) / 2
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

    def minicap_create_video(self):
        self.minicap_proc.create_video(TMP_EVIDENCE_DIR, TMP_VIDEO_DIR)

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
