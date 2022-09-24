import time

from traceback import format_exc
from source.logger import S_Logger
from source.testcase import Status
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
                 start_time: str,
                 semaphore: Semaphore,
                 *args,
                 **kwargs) -> None:
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
        self._parent_conn, self._child_conn = Pipe()
        self._duration: float = 0
        self.test_name = test_name
        self.semaphore = semaphore
        self.start_time = start_time
        self.status = Status.PASS

    def run(self) -> None:
        """
        Starts process along with logger. Sends
        response back to parent process through Pipe.
        """
        log = S_Logger(self.test_name, self.start_time)
        NO_RUN = 0
        MAX_RUNS = 3 # TODO Make that a config value

        while NO_RUN < MAX_RUNS:
            start = time.perf_counter()
            NO_RUN += 1

            try:
                log.start()
                Process.run(self)

            except Exception as e:
                log.exception(format_exc())
                if isinstance(e, AssertionError):
                    self.status = Status.FAIL
                else:
                    self.status = Status.ERROR
            else:
                break

            finally:
                duration = log.end(start)
                self._child_conn.send((self.test_name,
                                       self.status,
                                       duration,
                                       NO_RUN))
                self.semaphore.release()

    @property
    def result(self) -> None:
        """
        Result getter for parent process.
        """
        if self._parent_conn.poll():
            self._result = self._parent_conn.recv()
        return self._result
