import time

from source.testcase import TestCase


class TestStrings(TestCase):

    def test_upper(self):
        text = 'text'
        time.sleep(3)
        assert text.upper() == 'TEXT'
