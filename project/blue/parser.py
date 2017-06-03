import os
import sys
import json
from urlparse import urlparse

from utility import *

class Parser(object):
    def __init__(self):
        pass

    @classmethod
    def search(self, target):
        for f in os.listdir(target):
            if f.find(".json") != -1:
                with open(os.path.join(target, f), 'r') as jf:
                    data = json.load(jf)
                    return data["name"], data["bounds"]


if __name__ == "__main__":
    name, bounds = Parser.search(os.path.join(TMP_REFERENCE_DIR, "kancolle\home"))
    print(int(1280 * int(bounds["s_y"]) / 100.00))
