import time
import importlib

from search import create_tree
from source.process import Process


class Worker(object):
    pass
    # * for each test create worker instance and then
    # * in the worker instance run new process?


class Runner(object):

    def __init__(self) -> None:
        self.processes = []
        self.test_tree = create_tree()
        # ? pprint(self.test_tree)

    def collect_tests(self) -> None:
        pass

    def importer(self, module: dict) -> None:

        mod_name = list(module.keys())[0]
        mod_members = list(module.values())[0]
        mod = importlib.import_module(mod_name)
        print("MODULE_NAME = ", mod_name)
        print("MODULE_MEMBERS = ", mod_members)

        return mod, mod_name, mod_members

    def run_tests(self) -> None:
        for module in self.test_tree[2:]:

            module, mod_name, mod_members = self.importer(module)

            for test_class in mod_members:

                class_name = list(test_class.keys())[0]
                print('CLASS = ', class_name)
                klasa = getattr(module, class_name)
                object = klasa()

                for test_name in test_class[list(test_class.keys())[0]]:
                    print('TEST NAME:', test_name)
                    p = Process(target=getattr(klasa, test_name),args=(object,))
                    p.start()
                    self.processes.append(p)

        for process in self.processes:
            process.join()
            if process.exception:
                error, traceback = process.exception
                print(traceback)


if __name__ == "__main__":
    start = time.perf_counter()

    runner = Runner()
    runner.run_tests()

    end = time.perf_counter()
    print(f'\nFinished in {round(end-start, 2)} second(s)')
