import os
import io
import sys
import time
import threading
from Queue import Queue

import cv2
from PIL import Image
import numpy as np

from alize.exception import *
from alize.cmd import run

from blue.utility import *
from blue.utility import LOG as L


class PatternMatchObject(object):
    def __init__(self, _target, _box):
        self.target = _target
        self.box = _box

    def __repr__(self):
        return "PatternMatchObject()"

    def __str__(self):
        return "Target, Box : %s, %s" % (self.target, self.box)

class MinicapProc(object):
    def __init__(self, parent, debug=False):
        self.base = parent
        self._loop_flag = True
        self._debug = debug # Debug Flag

        self._pattern_match = None
        self.patternmatch_result = Queue()

        self._capture = None
        self.capture_result = Queue()

        self.counter = 0

    def start(self):
        self.base.minicap.start()
        self.loop = threading.Thread(target=self.main_loop).start()

    def finish(self):
        self._loop_flag = False; time.sleep(2)
        self.base.minicap.finish()

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

    def search_pattern(self, target, box=None, timeout=5):
        self._pattern_match = PatternMatchObject(target, box)
        for _ in xrange(timeout):
            result = self.patternmatch_result.get()
            #if result != None: break;
        self._pattern_match = None
        return result

    def capture_image(self, filename, timeout=1):
        self._capture = filename
        for _ in xrange(timeout):
            result = self.capture_result.get()
            if result: break
        abspath = os.path.join(TMP_DIR, filename)
        self._capture = None
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
            data = self.base.minicap.picture.get()

            image_pil = Image.open(io.BytesIO(data))
            image_cv = cv2.cvtColor(np.asarray(image_pil), cv2.COLOR_RGB2BGR)

            if self._capture != None:
                outputfile = os.path.join(TMP_DIR, self._capture)
                result = self.__save_cv(outputfile, image_cv)
                self.capture_result.put(result)

            if self._pattern_match != None:
                result, image_cv = self.base.pic.search_pattern(
                    image_cv, self._pattern_match.target, self._pattern_match.box, TMP_DIR)
                self.patternmatch_result.put(result)

            if self.counter % 10 == 0:
                self.__save_evidence(self.counter / 10, image_cv)

            if self._debug:
                w = int(self.base.adb.get().MINICAP_WIDTH) / 2
                h = int(self.base.adb.get().MINICAP_HEIGHT) / 2
                if int(self.base.adb.get().ROTATE) == 0:
                    resize_image_cv = cv2.resize(image_cv, (h, w))
                else:
                    resize_image_cv = cv2.resize(image_cv, (w, h))
                cv2.imshow('debug', resize_image_cv)
                key = cv2.waitKey(5)
                if key == 27: break
            self.counter += 1
        if self._debug: cv2.destroyAllWindows()
