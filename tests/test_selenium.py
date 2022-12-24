import time
from selenium import webdriver
from selenium.webdriver.safari.options import Options as SafariOptions
   
from eightest import TestCase, eLogger

log = eLogger.get_logger()


class TestStrings(TestCase):

    def before(self) -> None:
        log.debug('Before Test')
        self.driver = webdriver.Safari()

    def after(self) -> None:
        log.debug('After Test')
        self.driver.quit()

    # def test_selenium(self) -> None:
    #     self.driver.get('https://www.onet.pl')
    #     log.info(self.driver.title)
    #     time.sleep(2)
    #     assert self.driver.title == 'Onet – Jesteś na bieżąco'

    # def test_selenium2(self) -> None:
    #     self.driver.get('https://www.github.com')
    #     log.info(self.driver.title)
    #     time.sleep(2)
    #     assert self.driver.title == 'GitHub: Where the world builds software · GitHub'