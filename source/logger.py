import os
import logging

from utils import get_time
from logging import (FileHandler,
                     StreamHandler,
                     Formatter,
                     Logger)


date_format = '%Y-%m-%d %H:%M:%S'
text_format = '%(asctime)s [%(levelname)-5s] ' \
              'line:%(lineno)-2s of %(filename)-15s >> %(message)s'


class FileHandler(FileHandler):

    def __init__(self,
                 test_name: str,
                 session_date: str,
                 # filename: str = 'logs/log.log',
                 mode: str = 'a',
                 encoding: str | None = None,
                 delay: int = 0
                 ) -> None:

        filename = self.create_path(session_date, test_name)
        formatter = Formatter(text_format, date_format)
        super(FileHandler, self).__init__(filename, mode, encoding, delay)
        self.setFormatter(formatter)

    def create_path(self, session_date, test_name):
        # path, extension = os.path.splitext(filename)
        # return '{0}-{1}{2}'.format(path, test_name, extension)
        file_path = os.path.join('logs', f'test_session_{session_date}', f'{test_name}.log')
        if not os.path.exists(file_path):
            with open(file_path, 'w+') as f:
                f.write("file is opened for business")
        return file_path


class NewStreamHandler(StreamHandler):

    def __init__(self) -> None:
        StreamHandler.__init__(self)
        formatter = Formatter(text_format, date_format)
        self.setFormatter(formatter)


class NewLogger(Logger):

    def __init__(self, test_name: str, log_name: str = 'main') -> None:
        self.logger = logging.getLogger(log_name)
        self.logger.setLevel(logging.DEBUG)

        self.start_time = get_time()

        self.logger.addHandler(NewStreamHandler())
        self.logger.addHandler(FileHandler(test_name, self.start_time))

    @classmethod
    def get_logger(cls) -> logging.Logger:
        logger = logging.getLogger('main')
        return logger
