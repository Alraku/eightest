import time

from eightest import eLogger, TestCase

log = eLogger.get_logger()


class TestSuite(TestCase):

    def before(self):
        log.debug('Before Test')

    def after(self):
        log.debug('After Test')

    # def test_one(self):
    #     log.debug('TEST_ONE LOG')
    #     time.sleep(1)
    #     assert 0 == 0

    # def test_two(self):
    #     log.debug('TEST_TWO LOG')
    #     time.sleep(2)
    #     assert 1 == 0

    # def test_three(self):
    #     log.debug('TEST_THREE LOG')
    #     1/0
    #     assert 0 == 0
