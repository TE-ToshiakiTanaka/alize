import os
import subprocess

import utility
from utility import *
from utility import LOG as L

APP_LOG = os.path.abspath(os.path.join(LOG_DIR, "bin"))

class MinicapService(object):
    def __init__(self, name, serial, width, height, rotate):
        if not os.path.exists(APP_LOG):
            os.mkdir(APP_LOG)
        self.serial = serial
        self.width = width
        self.height = height
        self.rotate = rotate # v: 0, h: 90

        self.name = name
        self.proc = None
        self.description = "Minicap Server Process."
        self.log = open(os.path.abspath(os.path.join(APP_LOG, "%s.log" % self.name)), 'w')

    def start(self):
        LD_LIB = "LD_LIBRARY_PATH=//data//local//tmp//minicap-devel"
        BIN = "//data//local//tmp//minicap-devel//minicap"
        ARGS = "%sx%s@%sx%s/%s" % (self.width, self.height, self.width, self.height, self.rotate)
        EXEC = "adb -s %s shell %s %s -P %s" % (self.serial, LD_LIB, BIN, ARGS)
        L.debug(EXEC)
        if self.proc is None:
            subprocess_args = { 'stdin'     : subprocess.PIPE,
                                'stdout'    : self.log,
                                'stderr'    : self.log }
                                #'shell'     : True }
            self.proc = subprocess.Popen(EXEC, **subprocess_args)
        else:
            pass

    def stop(self):
        if self.proc is not None:
            subprocess.Popen(
                "taskkill /F /T /PID %i" % self.proc.pid, shell=True)
            self.proc = None
        else:
            pass

    def name(self):
        return self.name

    def status(self):
        if self.proc is not None: return True
        else: return False

if __name__ == '__main__':
    import time
    proc = MinicapService("minicap", "BH9037HP5U", "720", "1280", "0")
    #proc = DartService("minicap")
    proc.start()
    time.sleep(5)
    proc.stop()
