import time

from eightest import TestCase


class TestStrings(TestCase):

    def test_upper(self):
        text = 'text'
        time.sleep(10)
        assert text.upper() == 'TEXT'
