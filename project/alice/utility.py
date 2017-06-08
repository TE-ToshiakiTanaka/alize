import os
import sys
import logging

from alize import log

DEBUG = True

WORK_DIR = os.path.normpath(os.path.dirname(__file__))
TMP_DIR = os.path.normpath(os.path.join(WORK_DIR, "tmp"))
TMP_REFERENCE_DIR = os.path.join(os.path.join(TMP_DIR, "reference"))
TMP_EVIDENCE_DIR = os.path.normpath(os.path.join(TMP_DIR, "evidence"))
TMP_VIDEO_DIR = os.path.normpath(os.path.join(TMP_DIR, "video"))
LOG_DIR = os.path.normpath(os.path.join(WORK_DIR, "log"))
BIN_DIR = os.path.normpath(os.path.join(WORK_DIR, "bin"))

PROFILE_DIR = os.path.normpath(os.path.join(WORK_DIR, "conf", "profile"))
FFMPEG_BIN = os.path.normpath(os.path.join(BIN_DIR, "ffmpeg", "bin", "ffmpeg.exe"))

LOG = log.Log("Alice.Project.ALIZE")
if not os.path.exists(LOG_DIR):
    os.mkdir(LOG_DIR)
logfile = os.path.join(LOG_DIR, "system.log")
if not os.path.exists(logfile):
    with open(logfile, 'a') as f:
        os.utime(logfile, None)

LOG.addHandler(log.Log.fileHandler(logfile, log.BASE_FORMAT, logging.DEBUG))

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
