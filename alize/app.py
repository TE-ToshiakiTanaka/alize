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
from alize.workspace import Workspace
from alize.picture import Picture
from alize.stream import MinicapStream

PATH = os.path.abspath(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "tmp"))
TEMPLATE = os.path.abspath(os.path.join(PATH, "GAAZCY05D1882F9"))


class Alize(object):
    def __init__(self, ip="127.0.0.1", port=1313, path=""):
        self.workspace = Workspace(path)
        self.stream = MinicapStream.get_builder(ip, port, path)
        self.path = path
        self.__flag = True
        self._debug = True
        self._pattern_match = False
        self.counter = 0
        self.result = Queue()

    def main_loop(self):
        if self._debug: cv2.namedWindow("debug")
        while self.__flag:
            data = self.stream.picture.get()

            if self.counter % 10 == 0:
                number = self.counter / 10
                if number < 10: number = "0000%s" % str(number)
                elif number < 100: number = "000%s" % str(number)
                elif number < 1000: number = "00%s" % str(number)
                elif number < 10000: number = "0%s" % str(number)
                else: number = str(number)
                self.__save(os.path.join(self.path, "image_%s.png" % number), data)

            image_pil = Image.open(io.BytesIO(data))
            image_cv = cv2.cvtColor(np.asarray(image_pil), cv2.COLOR_RGB2BGR)

            if self._pattern_match:
                if self._pattern_match_target == None:
                    self.result.put(None)
                result, image_cv = Picture.search_pattern(image_cv, self._pattern_match_target)
                self.result.put(result)

            if self._debug:
                resize_image_cv = cv2.resize(image_cv, (640, 360))
                cv2.imshow('debug', resize_image_cv)
                key = cv2.waitKey(5)
                if key == 27: break
            self.counter += 1

        if self._debug: cv2.destroyAllWindows()

    def start(self):
        self.stream.start()
        self.loop = threading.Thread(target=self.main_loop).start()

    def finish(self):
        self.__flag = False; time.sleep(2)
        self.stream.finish()

    def __save(self, filename, data):
        with open(filename, "wb") as f:
            f.write(data)
            f.flush()

    def search_pattern(self, target):
        self._pattern_match_target = target
        self._pattern_match = True
        result = self.result.get()
        self._pattern_match_target = None
        self._pattern_match = False
        return result

    def is_pattern(self, target):
        result = self.search_pattern(target)
        if result == None: return False
        else: return True

if __name__ == "__main__":
    import time
    a = Alize(ip="127.0.0.1", port=1313, path=PATH)
    a.start()
    time.sleep(5)
    print("template matching start.")
    print(a.search_pattern(os.path.join(PATH, "YT911C1ZCP", "action_sortie.png")))
    print(a.search_pattern(os.path.join(PATH, "YT911C1ZCP", "action_supply.png")))
    print(a.search_pattern(os.path.join(PATH, "YT911C1ZCP", "action_docking.png")))
    print(a.search_pattern(os.path.join(PATH, "YT911C1ZCP", "action_home.png")))
    time.sleep(5)
    #a.capture_picture("sample01.png", PATH)
    a.finish()
    #a.create_video()
    #cv2.destroyAllWindows()
