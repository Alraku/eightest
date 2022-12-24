from eightest import TestCase
import time
 
 
class TestString(TestCase):
 
    def before(self):
        self.text = 'text'
 
    def test_upper(self):
        expected = 'TEXT'
        time.sleep(4)
        assert self.text.upper() == expected
 
    def test_center(self):
        expected = ' text '
        assert self.text.center(6) == expected
 
    def test_capitalize(self):
        expected = 'Text'
        time.sleep(3)
        assert self.text.capitalize() == expected
 
    def test_upper_failed(self):
        expected = 'TEXT'
        assert self.text.upper() == 'xdd'
 
    def test_center_errored(self):
        expected = ' text '
        1/0
        assert self.text.center(6) == expected
 
    def test_capitalize_failed(self):
        expected = 'Text'
        assert self.text.capitalize() == 'xdd'
 
    def after(self):
        del self.text

