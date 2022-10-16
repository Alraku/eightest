from time import sleep
from eightest import TestCase, eLogger

log = eLogger.get_logger()


class TestStrings(TestCase):

    def before(self) -> None:
        log.debug('Before Test')
        self.text = 'text'

    def test_upper(self) -> None:
        sleep(7)
        assert self.text.upper() == 'TEXT'

    def test_capitalize(self) -> None:
        sleep(2)
        assert self.text.capitalize() == 'Text'

    def test_center(self) -> None:
        sleep(4)
        assert self.text.center(6) == ' text '

    def test_endswith(self) -> None:
        sleep(6)
        assert self.text.endswith('xt')

    def test_isalpha(self) -> None:
        sleep(1)
        assert self.text.isalpha()

    def test_center2(self) -> None:
        sleep(1)
        1/0
        assert self.text.center(6) == ' text '

    def test_endswith2(self) -> None:
        sleep(6)
        assert self.text.endswith('xt')

    def test_isalpha2(self) -> None:
        sleep(1)
        assert self.text.isdecimal()
