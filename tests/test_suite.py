import time

from source.logger import S_Logger
from source.testcase import TestCase

logger = S_Logger.get_logger()


class TestSuite(TestCase):

    def before(self):
        logger.debug('BEFORE LOG')

    def after(self):
        logger.debug('AFTER LOG')

    def test_one(self):
        logger.debug('TEST_ONE LOG')
        time.sleep(1)
        assert 0 == 0

    def test_two(self):
        logger.debug('TEST_TWO LOG')
        time.sleep(2)
        assert 1 == 0
