import os
import time

from traceback import format_exc
from eightest.logger import eLogger
from eightest.testcase import Status
from multiprocess import (Semaphore,
                          Process,
                          Pipe)


class S_Process(Process):
    """
    Process class overrides standard multiprocess.Process
    This class is responsible for managing and running
    everything what is related with running tests in Process.
    """

    def __init__(self,
                 test_name: str,
                 session_time: str,
                 semaphore: Semaphore,
                 pipe_conn: Pipe,
                 *args,
                 **kwargs
                 ) -> None:
        """
        Initialization of Process instance.
        Creates multiprocess.Pipe which allows to
        communicate with parent and child processes.

        Args:
            test_name (str): From test module, starts with "test_*".
            start_time (str): Test Session start time.
            semaphore (Semaphore): Manages an internal counter
                                   of available processes.
        """
        Process.__init__(self, *args, **kwargs)
        self.__child_conn = pipe_conn
        self.__test_name = test_name
        self.__semaphore = semaphore
        self.__session_time = session_time
        self.__status = Status.NOTRUN

    def run(self) -> None:
        """
        Starts process along with logger. Sends
        response back to parent process through Pipe.
        """
        self.__semaphore.acquire()
        self.__child_conn.send(0)
        log = eLogger(self.__test_name, self.__session_time)
        MAX_RERUNS = int(os.getenv('MAX_RERUNS'))
        NO_RUN = 0

        while NO_RUN < MAX_RERUNS:
            start = time.perf_counter()
            NO_RUN += 1

            try:
                log.start()
                self.__status = Status.RUNNING
                Process.run(self)

            except Exception as e:
                log.exception(format_exc())
                if isinstance(e, AssertionError):
                    self.__status = Status.FAILED
                else:
                    self.__status = Status.ERROR
            else:
                self.__status = Status.PASSED
                break

            finally:
                duration = log.end(start, self.__status, NO_RUN)

        self.__child_conn.send((self.__test_name,
                               self.__status,
                               duration,
                               NO_RUN))
        self.__child_conn.close()
        self.__semaphore.release()

    def terminate(self) -> None:
        """
        Terminates process and releases semaphore.
        """
        self.__semaphore.release()
        super().terminate()

    @property
    def test_name(self) -> str:
        """
        Getter for test_name attribute.

        Returns:
            str: test name.
        """
        return self.__test_name
