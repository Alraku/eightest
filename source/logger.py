import os
import logging

from source.utils import get_time
from pathlib import Path
from logging import (FileHandler,
                     StreamHandler,
                     Formatter,
                     Logger)


date_format = '%Y-%m-%d %H:%M:%S'
text_format = '%(asctime)s [%(levelname)-5s] ' \
              'line:%(lineno)-2s of %(filename)-15s >> %(message)s'


class S_FileHandler(FileHandler):
    """
    Class that overrides standard Logging FileHanlder.
    """

    def __init__(self,
                 test_name: str,
                 session_date: str,
                 mode: str = 'a',
                 encoding: str | None = None,
                 delay: int = 0
                 ) -> None:
        """
        Initialization of FileHandler instance.

        Args:
            test_name (str): From test module, starts with "test_*".
            session_date (str): Start date of whole test session.
            mode (str, optional): File read/write/append. Defaults to 'a'.
            encoding (str | None, optional): Type of file encoding.
            delay (int, optional): If true, file deferred until first call.
        """

        filename = self.create_path(session_date, test_name)
        super(S_FileHandler, self).__init__(filename, mode, encoding, delay)
        self.setFormatter(Formatter(text_format, date_format))

    def create_path(self, session_date: str, test_name: str) -> Path:
        """
        Creates both test session and log file paths.

        Args:
            session_date (str): Start date of whole test session.
            test_name (str): From test module, starts with "test_*".

        Returns:
            Path: Full path of log file.
        """
        folder_path = os.path.join('logs', f'test_session_{session_date}')
        file_path = os.path.join(folder_path, f'{test_name}.log')

        if not os.path.exists(folder_path):
            os.makedirs(folder_path)

        if not os.path.exists(file_path):
            with open(file_path, 'w+'):
                pass

        return file_path


class S_StreamHandler(StreamHandler):
    """
    Class that overrides standard Logging StreamHanlder.
    """

    def __init__(self) -> None:
        """
        Initialization of StreamHandler instance.
        """
        StreamHandler.__init__(self)
        formatter = Formatter(text_format, date_format)
        self.setFormatter(formatter)


class S_Logger(Logger):
    """
    Class that overrides standard Logging library.
    """

    def __init__(self, test_name: str, log_name: str = 'main') -> None:
        """
        Initialization of Logger instance.

        Args:
            test_name (str): From test module, starts with "test_*".
            log_name (str, optional): Logger name. Defaults to 'main'.
        """
        self.logger = logging.getLogger(log_name)
        self.logger.setLevel(logging.DEBUG)

        # Used for creating test_session folder.
        self.start_time = get_time()

        self.logger.addHandler(S_StreamHandler())
        self.logger.addHandler(S_FileHandler(test_name, self.start_time))

    @classmethod
    def get_logger(cls) -> logging.Logger:
        """
        Getter for Logger instance.

        Returns:
            logging.Logger: Logger instance.
        """
        logger = logging.getLogger('main')
        return logger
