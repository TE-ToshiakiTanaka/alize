import os
import socket
import threading
from banner import Banner
from itsdangerous import bytes_to_int
from Queue import Queue

import io
import cv2
import numpy as np
from cv2 import cv
from PIL import Image

class MinicapStream(object):
    __instance = None
    __mutex = threading.Lock()

    def __init__(self, ip="127.0.0.1", port=1313, path=""):
        self.IP = ip
        self.PORT = port
        self.PATH = path
        self.PID = 0
        self.banner = Banner()
        self.minicap_socket = None
        self.read_image_stream_task = None
        self.push = None
        self.picture = Queue()
        self.__flag = True

    @staticmethod
    def get_builder(ip="127.0.0.1", port=1313, path=""):
        if (MinicapStream.__instance == None):
            MinicapStream.__mutex.acquire()
            if (MinicapStream.__instance == None):
                MinicapStream.__instance = MinicapStream(ip, port, path)
            MinicapStream.__mutex.release()
        return MinicapStream.__instance

    def get_queue(self):
        return self.picture

    def get_d(self):
        return self.picture.qsize()

    def start(self):
        self.minicap_socket = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
        self.minicap_socket.connect((self.IP, self.PORT))
        #return self.read_image_stream()
        self.read_image_stream_task = threading.Thread(target=self.read_image_stream).start()

    def finish(self):
        self.__flag = False

    def read_image_stream(self):
        read_banner_bytes = 0
        banner_length = 2
        read_frame_bytes = 0
        frame_body_length = 0
        data_body = ""
        counter = 0

        while self.__flag:
            reallen = self.minicap_socket.recv(4096)
            length = len(reallen)
            if not length: continue
            cursor = 0
            while cursor < length:
                if read_banner_bytes < banner_length:
                    if read_banner_bytes == 0:
                        self.banner.version = bytes_to_int(reallen[cursor])
                    elif read_banner_bytes == 1:
                        banner_length = bytes_to_int(reallen[cursor])
                        self.banner.length = banner_length
                    elif read_banner_bytes in [2, 3, 4, 5]:
                        self.banner.pid += (bytes_to_int(reallen[cursor]) << ((read_banner_bytes - 2) * 8)) >> 0;
                    elif read_banner_bytes in [6, 7, 8, 9]:
                        self.banner.real_width += (bytes_to_int(reallen[cursor]) << ((read_banner_bytes - 6) * 8)) >> 0;
                    elif read_banner_bytes in [10, 11, 12, 13]:
                        self.banner.real_height += (bytes_to_int(reallen[cursor]) << ((read_banner_bytes - 10) * 8)) >> 0;
                    elif read_banner_bytes in [14, 15, 16, 17]:
                        self.banner.virtual_width += (bytes_to_int(reallen[cursor]) << ((read_banner_bytes - 14) * 8)) >> 0;
                    elif read_banner_bytes in [18, 19, 20, 21]:
                        self.banner.virtual_height += (bytes_to_int(reallen[cursor]) << ((read_banner_bytes - 18) * 8)) >> 0;
                    elif read_banner_bytes == 22:
                        self.banner.orientation = bytes_to_int(reallen[cursor]) * 90
                    elif read_banner_bytes == 23:
                        self.banner.quirks = bytes_to_int(reallen[cursor])
                    cursor += 1
                    read_banner_bytes += 1
                    if read_banner_bytes == banner_length:
                        print self.banner.toString()
                elif read_frame_bytes < 4:
                    frame_body_length = frame_body_length + ((bytes_to_int(reallen[cursor])<<(read_frame_bytes * 8)) >> 0)
                    cursor += 1
                    read_frame_bytes += 1
                else:
                    if length - cursor >= frame_body_length:
                        data_body = data_body + reallen[cursor:(cursor+frame_body_length)]
                        if bytes_to_int(data_body[0]) != 0xFF or bytes_to_int(data_body[1]) != 0xD8:
                            return
                        #image_pil = Image.open(io.BytesIO(data_body))
                        #image_cv = cv2.cvtColor(np.asarray(image_pil), cv2.COLOR_RGB2BGR)
                        self.picture.put(data_body)
                        if self.get_d() > 60: self.picture.get()
                        """
                        if counter % 10 == 0:
                            #image_pil = Image.open(io.BytesIO(data_body))
                            #image_cv = cv2.cvtColor(np.asarray(image_pil), cv2.COLOR_RGB2BGR)
                            #cv2.imshow('android capture', image_cv)
                            #cv2.waitKey(0)
                            #cv2.destroyAllWindows()
                            number = counter / 10
                            if number < 10: number = "000%s" % str(number)
                            elif number < 100: number = "00%s" % str(number)
                            elif number < 1000: number = "0%s" % str(number)
                            else: number = str(number)
                            self.save_file(os.path.join(self.PATH, "image_%s.png" % number), data_body)
                        """
                        cursor += frame_body_length
                        frame_body_length = 0
                        read_frame_bytes = 0
                        data_body = ""
                        counter += 1
                    else:
                        data_body = data_body + reallen[cursor:length]
                        frame_body_length -= length - cursor
                        read_frame_bytes += length - cursor
                        cursor = length


# adb shell LD_LIBRARY_PATH=/data/local/tmp /data/local/tmp/minicap -P 1200x1920@1200x1920/0
#             adb forward tcp:1313 localabstract:minicap


    def save_file(self,file_name, data):
        file=open(file_name, "wb")
        file.write(data)
        file.flush()
        file.close()




if __name__ == '__main__':
    import time
    a = MinicapStream.get_builder()
    print id(a)
    a.start()
    print a.get_d()
    time.sleep(100)
    a.finish()
