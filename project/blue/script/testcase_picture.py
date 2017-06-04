import os
import sys

from blue.utility import *
from blue.utility import LOG as L
from blue.script import testcase_base

class TestCase_Picture(testcase_base.TestCase_Unit):

    def picture_crop(self, filepath, point="", rename=""):
        try:
            pic = self.pic.open(filepath)
            if point == "":
                width, height = pic.size
                point = POINT(0, 0, width, height)
            crop_pic = self.pic.crop(pic, point)
            if rename == "": rename = filepath
            return self.pic.save(crop_pic, rename)
        except Exception as e:
            L.warning(e)

    def picture_rotate(self, filepath, rotate, rename=""):
        try:
            pic = self.pic.open(filepath)
            rotate_pic = self.pic.rotate(pic, rotate)
            if rename == "": rename = filepath
            return self.pic.save(rotate_pic, rename)
        except Exception as e:
            L.warning(e)

    def picture_resize(self, filepath, resize, rename=""):
        try:
            pic = self.pic.open(filepath)
            resize_pic = self.pic.resize(pic, resize)
            if rename == "": rename = filepath
            return self.pic.save(resize_pic, rename)
        except Exception as e:
            L.warning(e)

    def picture_get_rgb(self, filepath, point=""):
        try:
            pic = self.pic.open(filepath)
            return self.pic.get_rgb(pic, point)
        except Exception as e:
            L.warning(e)
