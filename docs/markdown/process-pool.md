### This file contains another example of implementation if multiprocessing parallel execution. For the moment being I have no time to try adjust that idea and test it.

    import time
    import multiprocess

    from functools import partial
    from eightest.process import Process
    from multiprocess.pool import Pool
    from eightest.searcher import create_tree


    class Runner(object):

    # TODO
    # ! 1. How to create pool of independent processes with different names?
    # ! 2. Pass different functions to pool

    def __init__(self) -> None:
        """
        Initialization of processes list
        and generating tests' hierarchy.
        """
        self.processes: list = []
        self.test_results: list = []
        self.test_tree: list[dict] = create_tree()

    def _Process(self, ctx, *args, **kwds):
        return ctx.MyProcess(*args, **kwds)

    def run_tests(self):
        ctx = multiprocess.get_context()
        ctx.MyProcess = Process

        Pool.Process = partial(self._Process)

        def worker(x):
            print(x**2)
            time.sleep(1)

        with ctx.Pool(processes=2, maxtasksperchild=1) as pool:

            nums = range(10)
            pool.map(worker, nums)


    if __name__ == "__main__":
        # runner = Runner().run_tests()
        from eightest.testcase import Status
        print(Status.ERROR.name)