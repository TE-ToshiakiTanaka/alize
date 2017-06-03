import os
import sys
import json
from urlparse import urlparse

from utility import *

class Parser(object):
    def __init__(self):
        pass

    def search(self, target):
        print(os.path.join(TMP_DIR, target))


if __name__ == "__main__":
    p = Parser()
    p.search("kancolle\home\quest")
