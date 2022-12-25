import os
import time
import logging

from pathlib import Path
from logging import (FileHandler,
                     StreamHandler,
                     Formatter,
                     Logger)

from eightest.testcase import Status


date_format = '%Y-%m-%d %H:%M:%S'
text_format = '%(asctime)s %(levelname)-8s ' \
              'line:%(lineno)-2s of %(filename)-15s >> %(message)s'


class S_FileHandler(FileHandler):
    """
    Class that overrides standard Logging FileHanlder.
    """
    def __init__(self,
                 test_name: str,
                 session_date: str,
                 mode: str = 'a',
                 encoding: str = None,
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


class eLogger(Logger):
    """
    Class that overrides standard Logging library.
    """
    INFO = 20
    ERROR = 40

    def __init__(self,
                 test_name: str,
                 start_time: str,
                 log_name: str = 'main',
                 *args, **kwargs) -> None:
        """
        Initialization of Logger instance.

        Args:
            test_name (str): From test module, starts with "test_*".
            start_time (str): Test Session start time.
            log_name (str, optional): Logger name. Defaults to 'main'.
        """
        Logger.__init__(self, log_name, *args, **kwargs)
        self.__logger = logging.getLogger(log_name)
        self.__logger.setLevel(logging.DEBUG)
        self.__logger.addHandler(S_StreamHandler())
        self.__logger.addHandler(S_FileHandler(test_name, start_time))

        self.__test_name = test_name
        self.setLevel(logging.DEBUG)
        self.addHandler(S_StreamHandler())
        self.addHandler(S_FileHandler(test_name, start_time))

    def start(self, *args) -> None:
        """
        Test start logging method.
        """
        if self.isEnabledFor(eLogger.INFO):
            self._log(eLogger.INFO,
                      f'THE EXECUTION OF {self.__test_name.upper()} ' +
                      'HAS STARTED.',
                      args)

    def end(self, start: time.time, status: Status, NO_RUN, *args) -> float:
        """
        Test end logging method. Computes duration
        of test execution.

        Args:
            start (time.time): Test start time.

        Returns:
            float: Test execution duration.
        """
        end = time.perf_counter()
        duration = round(end-start, 2)

        if self.isEnabledFor(eLogger.INFO):
            self._log(eLogger.INFO,
                      (f'THE EXECUTION OF {self.__test_name.upper()} ' +
                       f'HAS ENDED WITH RESULT: {status.name} ' +
                       f'RUN NUMBER: {NO_RUN}'),
                      args)

            self._log(eLogger.INFO,
                      f'FINISHED IN {duration} SECOND(S)',
                      args)

        return duration

    def exception(self, traceback: str, *args) -> None:
        """
        Test exception logging method.

        Args:
            traceback (str): Full exception traceback in string from.
        """
        if self.isEnabledFor(eLogger.ERROR):
            self._log(eLogger.ERROR,
                      f'AN EXCEPTION OCCURRED: {traceback}',
                      args)

    @classmethod
    def get_logger(cls) -> logging.Logger:
        """
        Getter for Logger instance.

        Returns:
            logging.Logger: Logger instance.
        """
        return logging.getLogger('main')
