import os
import sys

import cv2
from PIL import Image
import numpy as np

PMC_THRESHOLD = 0.96

class POINT(object):
    def __init__(self, x, y, width, height):
        self.x = x
        self.y = y
        self.width = width
        self.height = height

    def __repr__(self):
        return "POINT()"

    def __str__(self):
        return "(X, Y) = (%s, %s), Width = %s, Height = %s" \
            % (self.x, self.y, self.width, self.height)


class Picture(object):
    @classmethod
    def _patternmatch(cls, reference, target):
        if not os.path.exists(reference):
            raise PictureError("it is not exists reference file. : %s" % reference)
        if not os.path.exists(target):
            raise PictureError("it is not exists target file. : %s" % target)
        reference_cv = cv2.imread(reference)
        target_cv = cv2.imread(target, 0)
        return cls.__patternmatch(reference_cv, target_cv)

    @classmethod
    def __patternmatch(cls, reference, target):
        img_gray = cv2.cvtColor(reference, cv2.COLOR_BGR2GRAY)
        template = target
        w, h = template.shape[::-1]
        res = cv2.matchTemplate(img_gray, template, cv2.TM_CCOEFF_NORMED)
        loc = np.where( res >= PMC_THRESHOLD)
        result = None
        for pt in zip(*loc[::-1]):
            result = POINT(pt[0], pt[1], w, h)
            cv2.rectangle(reference, pt, (pt[0] + w, pt[1] + h), (0, 0, 255), 5)
        return result, reference

    @classmethod
    def search_pattern(cls, reference, target):
        target_cv = cv2.imread(target, 0)
        return cls.__patternmatch(reference, target_cv)
