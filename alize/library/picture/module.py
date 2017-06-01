import os
import sys

try:
    from PIL import Image
    from PIL import ImageOps
    from PIL import ImageDraw
    from PIL import ImageEnhance
    import cv2
    import numpy as np
except Exception as e:
    print(str(e))

from alize.log import Log
from alize.exception import *

SHARPNESS = 2.0
CONTRAST = 2.0

PMC_THRESHOLD = 0.96
L = Log("Picture.Library.ALIZE")

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
    def exists(cls, filename):
        if os.path.exists(filename): return True
        else:
            L.warning("%s is not exists." % filename)
            raise PictureError("%s is not exists." % filename)

    @classmethod
    def open(cls, filename):
        if cls.exists(filename):
            try:
                return Image.open(filename, 'r')
            except IOError as e:
                L.warning("I/O Error %s" % str(e))
                raise PictureError("it is not success of loading picture %s" % filename)

    @classmethod
    def to_opencv(cls, pic):
        if pic == None:
            raise PictureError("it is not create opencv_pic.")
        return np.asarray(pic)

    @classmethod
    def to_pil(cls, opencv_pic):
        try:
            return Image.fromarray(opencv_pic)
        except Exception as e:
            L.warning(str(e))
            raise PictureError("it is not exchange pic.")

    @classmethod
    def get_rgb(cls, pic, point=""):
        if point == "":
            point = POINT(0, 0, pic.size[0], pic.size[1])
        box = (point.x, point.y, point.x + point.width, point.y + point.height)
        rgbimg = pic.crop(box).convert("RGB")
        rgb = np.array(rgbimg.getdata())
        return [cls.__round(rgb[:,0]),
                cls.__round(rgb[:,1]),
                cls.__round(rgb[:,2])]

    @classmethod
    def __round(cls, array):
        return int(round(np.average(array)))

    @classmethod
    def resize(cls, pic, size):
        if size =="240P": sz = 240
        elif size == "360P": sz = 360
        elif size == "480P": sz = 480
        elif size == "720P": sz = 720
        elif size == "1080P": sz = 1080
        else: return
        #L.info("Base : %s" % str(pic.size))
        width = float((float(pic.size[0]) * sz)) / float(pic.size[1])
        res = (int(width), sz)
        #L.info("Resize : %s" % str(res))
        return pic.resize(res)

    @classmethod
    def info(cls, pic):
        L.info("File Format : %s " % pic.format)
        L.info("File Size   : %s " % str(pic.size))
        L.info("File Mode   : %s " % pic.mode)

    @classmethod
    def convert(cls, from_file, to_file, mode, width, height):
        rawdata = open(from_file,'rb').read()
        imgsize = (width, height)
        img = Image.frombytes(mode, imgsize, rawdata)
        img.save(to_file)

    @classmethod
    def save(cls, pic, filepath, q=100, opt=True):
        #cls.exists(filepath)
        if not os.path.exists(os.path.dirname(filepath)):
            raise PictureError("it is not exists parents directory. : %s" % os.path.dirname(filepath))
        pic.save(filepath, quality=q, optimize=opt)
        return filepath

    @classmethod
    def binary(cls, pic):
        if pic == None: raise PictureError("it is not exists.")
        opencv_pic = cls.to_opencv(pic)
        cv_pic_gray = cv2.cvtColor(opencv_pic, cv2.COLOR_BGR2GRAY)
        cv_pic = cv2.adaptiveThreshold(
            cv_pic_gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2)
        opencv_pic = cv2.cvtColor(cv_pic, cv2.COLOR_GRAY2RGB)
        pic = cls.to_pil(opencv_pic)
        pic.convert("RGB")
        return pic

    @classmethod
    def grayscale(cls, pic):
        if pic == None: raise PictureError("it is not exists.")
        try:
            return ImageOps.grayscale(pic).convert("RGB")
        except IOError as e:
            L.warning("I/O Error : %s" % str(e))
            raise PictureError("it is not success of converting grayscale. %s" % pic)

    @classmethod
    def brightness(cls, pic, level=1.0):
        if pic == None: raise PictureError("it is not exists.")
        try:
            brightness = ImageEnhance.Brightness(pic)
            return brightness.enhance(level)
        except IOError as e:
            L.warning("I/O Error : %s" % str(e))
            raise PictureError("it is not success of converting brightness. %s" % pic)

    @classmethod
    def contrast(cls, pic, threshold=CONTRAST):
        if pic == None: raise PictureError("it is not exists.")
        try:
            contrast_converter = ImageEnhance.Contrast(pic)
            return contrast_converter.enhance(threshold)
        except IOError as e:
            L.warning("I/O Error : %s" % str(e))
            raise PictureError("it is not success of converting contrast. %s" % pic)

    @classmethod
    def sharpness(cls, pic, threshold=SHARPNESS):
        if pic == None: raise PictureError("it is not exists.")
        try:
            sharpness_converter = ImageEnhance.Sharpness(pic)
            return sharpness_converter.enhance(threshold)
        except IOError as e:
            L.warning("I/O Error : %s" % str(e))
            raise PictureError("it is not success of converting sharpness. %s" % pic)

    @classmethod
    def crop(cls, pic, point):
        if point == None: raise PictureError("Point object is None.")
        box = (point.x, point.y, point.x + point.width, point.y + point.height)
        try:
            return pic.crop(box)
        except IOError as e:
            L.info("I/O error : %s" % str(e))
            raise PictureError("it is not succes of crop picture. %s" % pic)

    @classmethod
    def reload(cls, filename):
        try:
            cls.exists(filename)
            return Image.open(filename, 'r')
        except Error as e:
            L.warning("Error : %s" % str(e))
            raise PictureError("it is not success of loading picture %s" % filename)


    @classmethod
    def point(cls, pic, points, filename):
        draw = ImageDraw.Draw(pic)
        for point in points:
            p = (float(point.y), float(point.x))
            p1 = (float(point.y)+1.0, float(point.x))
            p2 = (float(point.y), float(point.x)+1.0)
            p3 = (float(point.y)+1.0, float(point.x)+1.0)
            draw.point(p, (0xff, 0x00, 0x00))
            draw.point(p1, (0xff, 0x00, 0x00))
            draw.point(p2, (0xff, 0x00, 0x00))
            draw.point(p3, (0xff, 0x00, 0x00))
        return cls.save(pic, filename)


    @classmethod
    def _patternmatch(cls, reference, target, box=None):
        if not os.path.exists(reference):
            raise PictureError("it is not exists reference file. : %s" % reference)
        if not os.path.exists(target):
            raise PictureError("it is not exists target file. : %s" % target)
        reference_cv = cv2.imread(reference)
        target_cv = cv2.imread(target, 0)
        return cls.__patternmatch(reference_cv, target_cv, box)

    @classmethod
    def __patternmatch(cls, reference, target, box=None, tmp=None):
        img_gray = cv2.cvtColor(reference, cv2.COLOR_BGR2GRAY)
        if len(img_gray.shape) == 3: height, width, channels = img_gray.shape[:3]
        else: height, width = img_gray.shape[:2]
        if box == None:
            box = POINT(0, 0, width, height)
        cv2.rectangle(reference,
                      (box.x, box.y),
                      (box.x + box.width, box.y + box.height), (0, 255, 0), 5)
        img_gray = img_gray[box.y:(box.y + box.height), box.x:(box.x + box.width)]
        cv2.imwrite(os.path.join(tmp, "crop.png"), img_gray)
        template = target
        w, h = template.shape[::-1]
        res = cv2.matchTemplate(img_gray, template, cv2.TM_CCOEFF_NORMED)
        loc = np.where( res >= PMC_THRESHOLD)
        result = None
        for pt in zip(*loc[::-1]):
            x = pt[0] + box.x
            y = pt[1] + box.y
            result = POINT(x, y, w, h)
            cv2.rectangle(reference, (x, y), (x + w, y + h), (0, 0, 255), 5)
        return result, reference

    @classmethod
    def search_pattern(cls, reference, target, box=None, tmp=None):
        if not os.path.exists(target):
            raise PictureError("it is not exists target file. : %s" % target)
        target_cv = cv2.imread(target, 0)
        return cls.__patternmatch(reference, target_cv, box, tmp)
