import traceback
import multiprocess
from logger import NewLogger


class Process(multiprocess.Process):

    def __init__(self, test_name, *args, **kwargs):
        multiprocess.Process.__init__(self, *args, **kwargs)
        self._parent_conn, self._child_conn = multiprocess.Pipe()
        self._exception = None
        self._test_name = test_name

    def run(self):
        try:
            logger = NewLogger(test_name=self._test_name).get_logger()
            logger.info('EXECUTION OF %s HAS STARTED.', self._test_name)
            multiprocess.Process.run(self)
            self._child_conn.send(None)

        except Exception as e:
            tb = traceback.format_exc()
            self._child_conn.send((e, tb))

    @property
    def exception(self):
        if self._parent_conn.poll():
            self._exception = self._parent_conn.recv()
        return self._exception
