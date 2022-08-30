import time
import importlib

from source.process import Process
from source.search import create_tree


class Worker(object):
    pass
    # * for each test create worker instance and then
    # * in the worker instance run new process?


class Runner(object):

    def __init__(self) -> None:
        self.processes = []
        self.test_tree = create_tree()

    def collect_tests(self) -> None:
        pass

    def run_tests(self) -> None:
        for module in self.test_tree:

            module_name = list(module.keys())[0]
            module_members = list(module.values())[0]

            module = importlib.import_module(module_name)

            for test in module_members:
                if isinstance(test, dict):
                    continue

                p = Process(target=getattr(module, test))
                p.start()
                self.processes.append(p)

        for process in self.processes:
            process.join()
            if process.exception:
                error, traceback = process.exception
                print(traceback)


def main():
    start = time.perf_counter()

    runner = Runner()
    runner.run_tests()

    end = time.perf_counter()
    print(f'\nFinished in {round(end-start, 2)} second(s)')


if __name__ == "__main__":
    main()
