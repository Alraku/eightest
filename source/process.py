import time

from source.logger import S_Logger
from multiprocess import (Semaphore,
                          Process,
                          Pipe)

from traceback import (format_exc,
                       TracebackException)


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
            semaphore (Semaphore): Manages an internal counter
                                   of available processes.
        """
        Process.__init__(self, *args, **kwargs)
        self._parent_conn, self._child_conn = Pipe()
        self._exception = None
        self._test_name = test_name
        self._semaphore = semaphore
        self._start_time = start_time

    def run(self) -> None:
        """
        Starts process along with logger.
        """
        try:
            start = time.perf_counter()
            logger = S_Logger(self._test_name, self._start_time).get_logger()
            logger.info('EXECUTION OF %s HAS STARTED.', self._test_name)
            Process.run(self)
            self._child_conn.send(None)

        except Exception as e:
            tb = format_exc()
            logger.error(f'EXCEPTION OCCURRED: {tb}')
            self._child_conn.send((e, tb))

        finally:
            logger.info('EXECUTION OF %s HAS ENDED.', self._test_name)
            end = time.perf_counter()
            logger.info(f'FINISHED in {round(end-start, 2)} second(s)')
            self._semaphore.release()

    @property
    def exception(self) -> TracebackException:
        """
        Getter for catched exceptions during process execution.

        Returns:
            TracebackException: Exception in readable form.
        """
        if self._parent_conn.poll():
            self._exception = self._parent_conn.recv()
        return self._exception
