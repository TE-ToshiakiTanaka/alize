from __future__ import print_function

import os
import re
import sys
import argparse

from alize.adbkit import Android
MINICAP_PATH = os.path.abspath(os.path.join(
    os.path.dirname(os.path.abspath(__file__)), "minicap"))
ROTATEW_PATH = os.path.abspath(os.path.join(
    os.path.dirname(os.path.abspath(__file__)), "RotationWatcher.apk", "mobile"))

def argument():
    parser = argparse.ArgumentParser(
        formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument("-s", "--serial", dest="serial", required=False, help="Android Serial.")

    results = parser.parse_args()
    for k, v in vars(results).items():
        print("%s : %s" % (k, v))
    return results

def __get_serial(args):
    serial = None
    for k, v in vars(args).items():
        if k in "serial":
            serial = v
    return serial

def size(handset):
    size = search(handset.shell("dumpsys window"), "init=\d+x\d+")
    if size == "":
        w = search(handset.shell("dumpsys window"), "DisplayWidth=\d+")
        h = search(handset.shell("dumpsys window"), "DisplayHeight=\d+")
        return "%sx%s" % (w, h)
    else:
        w = size[0].split("=")[1].split("x")[0]
        h = size[0].split("=")[1].split("x")[1]
        return "%sx%s" % (w, h)

def search(text, pattern):
    repatter = re.compile(pattern)
    return repatter.findall(text)

def install(serial):
    a = Android(serial)
    abi = a.getprop("ro.product.cpu.abi").replace("\r", "").replace("\n", "")
    sdk = a.getprop("ro.build.version.sdk").replace("\r", "").replace("\n", "")
    pre = a.getprop("ro.build.version.preview_sdk").replace("\r", "").replace("\n", "")
    rel = a.getprop("ro.build.version.release").replace("\r", "").replace("\n", "")

    if pre == 0: sdk = "%s%s" % (sdk, pre)
    binary = "minicap-nopie"
    if int(sdk) >= 16: binary = "minicap"

    dstdir = "//data//local//tmp//minicap-devel"
    a.shell("mkdir %s 2>/dev/null || true" % (dstdir))
    s = size(a); args = "-P %s@%s/0" % (s, s); print(args)
    srcdir = os.path.join(MINICAP_PATH, "libs", abi, binary)
    srcjnidir = os.path.join(MINICAP_PATH, "jni", "minicap-shared", "aosp", "libs", "android-%s" % sdk, abi, "minicap.so")
    a.push(srcdir, dstdir)
    a.push(srcjnidir, dstdir)
    print(a.shell("ls %s" % dstdir))
    a.shell("chmod +x %s//%s" % (dstdir, binary))

    #a.shell("LD_LIBRARY_PATH=%s %s/%s %s" %(dstdir, dstdir, binary, args))

if __name__ == "__main__":
    install(__get_serial(argument()))
