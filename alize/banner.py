class Banner(object):

    def __init__(self):
        self.version = 0
        self.length = 0
        self.pid = 0
        self.real_width = 0
        self.real_height = 0
        self.virtual_width = 0
        self.virtual_height = 0
        self.orientation = 0
        self.quirks = 0

    def toString(self):
        return "Banner [ Version = " + str(self.version) + \
                      ", Length = " + str(self.length) + \
                      ", PID = " + str(self.pid) + \
                      ", RealWidth = " + str(self.real_width) + \
                      ", RealHeight = " + str(self.real_height) + \
                      ", VirthalWidth = " + str(self.virtual_width) + \
                      ", VirthalHeight = " + str(self.virtual_height) + \
                      ", Orientation = " + str(self.orientation) + \
                      ", Quirks = " + str(self.qrirks) + "]"
