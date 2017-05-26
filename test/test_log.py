import os
import logging
try:
    from StringIO import StringIO
except ImportError:
    from io import StringIO
from nose.tools import with_setup, raises, ok_, eq_

from alize import log
from alize.exception import *

class TestLog(object):
    @classmethod
    def setup(cls):
        cls.LOG = log.Log("TEST.ALIZE")
        cls.original_logger = cls.LOG.logger
        cls.stream = StringIO()
        cls.log_handler = logging.StreamHandler(cls.stream)
        for handler in cls.original_logger.handlers:
            cls.original_logger.removeHandler(handler)
        cls.original_logger.addHandler(cls.log_handler)

    @classmethod
    def teardown(cls):
        cls.original_logger.removeHandler(cls.log_handler)
        cls.log_handler.close()

    @with_setup(setup, teardown)
    def test_log_success(self):
        self.LOG.debug("test sentence.")
        self.log_handler.flush()
        ok_("test sentence." in self.stream.getvalue())

    @with_setup(setup, teardown)
    def test_log_debug_success(self):
        self.LOG.debug("test sentence.")
        self.log_handler.flush()
        ok_("\033[92m" in self.stream.getvalue())

    @with_setup(setup, teardown)
    def test_log_info_success(self):
        self.LOG.info("test sentence.")
        self.log_handler.flush()
        ok_("\033[94m" in self.stream.getvalue())

    @with_setup(setup, teardown)
    def test_log_warning_success(self):
        self.LOG.warning("test sentence.")
        self.log_handler.flush()
        ok_("\033[93m" in self.stream.getvalue())

    @with_setup(setup, teardown)
    def test_log_error_success(self):
        self.LOG.error("test sentence.")
        self.log_handler.flush()
        ok_("\033[91m" in self.stream.getvalue())

    @with_setup(setup, teardown)
    def test_log_critical_success(self):
        self.LOG.critical("test sentence.")
        self.log_handler.flush()
        ok_("\033[95m" in self.stream.getvalue())

    @with_setup(setup, teardown)
    def test_log_failed(self):
        self.LOG.log('debug', "test sentence.")
        self.log_handler.flush()
        ok_("\033[95m" in self.stream.getvalue())
