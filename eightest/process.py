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
        # self._parent_conn, self._child_conn = Pipe()
        self._child_conn = pipe_conn
        self._duration: float = 0
        self.test_name = test_name
        self.semaphore = semaphore
        self.session_time = session_time
        self.status = Status.NOTRUN

    def run(self) -> None:
        """
        Starts process along with logger. Sends
        response back to parent process through Pipe.
        """
        self.semaphore.acquire()
        self._child_conn.send(None)
        log = eLogger(self.test_name, self.session_time)
        MAX_RERUNS = int(os.getenv('MAX_RERUNS'))
        NO_RUN = 0

        while NO_RUN < MAX_RERUNS:
            start = time.perf_counter()
            NO_RUN += 1

            try:
                log.start()
                self.status = Status.RUNNING
                Process.run(self)

            except Exception as e:
                log.exception(format_exc())
                if isinstance(e, AssertionError):
                    self.status = Status.FAILED
                else:
                    self.status = Status.ERROR
            else:
                self.status = Status.PASSED
                break

            finally:
                duration = log.end(start, self.status, NO_RUN)
        self._child_conn.send((self.test_name,
                               self.status,
                               duration,
                               NO_RUN))
        self.semaphore.release()

    def terminate(self) -> None:
        self.semaphore.release()
        super().terminate()

    @property
    def result(self) -> None:
        """
        Result getter for parent process.
        """
        if self._parent_conn.poll():
            self._result = self._parent_conn.recv()
        return self._result
