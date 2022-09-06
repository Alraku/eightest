import importlib

from ast import Module
from typing import Tuple
from search import create_tree
from source.process import Process


class Runner(object):
    """
    Class responsible for creating processes in which
    each test is executed separately and independently.
    """

    def __init__(self) -> None:
        """
        Initialization of processes list
        and generating tests' hierarchy.
        """
        self.processes: list = []
        self.test_tree: list[dict] = create_tree()

    def collect_tests(self) -> None:
        """
        Method for future test discovery.
        """
        pass

    def importer(self, module: dict) -> Tuple[Module, str, str]:
        """
        Imports given module name.

        Args:
            module (dict): Module in form of dictionary
            with name and its class members.

        Raises:
            ModuleNotFoundError: When module was not found.

        Returns:
            Tuple[Module, str, str]: Imported module,
            its name and members.
        """
        mod_name = next(iter(module.keys()))
        mod_members = next(iter(module.values()))

        try:
            mod = importlib.import_module(mod_name)
        except ModuleNotFoundError as Error:
            raise Error

        return mod, mod_name, mod_members

    def run_tests(self) -> None:
        """
        Creates independent processes and appends
        them into the pool of processes.
        """
        # For each module in test hierarchy.
        for module in self.test_tree:
            module, mod_name, mod_members = self.importer(module)

            # For each TestSuite in module.
            for test_class in mod_members:
                _class = getattr(module, next(iter(test_class.keys())))

                # For each test in given TestSuite.
                for test_name in test_class[next(iter(test_class.keys()))]:
                    _class_instance = _class(test_name)

                    process = Process(
                            target=getattr(_class, test_name),
                            args=(_class_instance,),
                            test_name=test_name
                    )
                    process.start()
                    self.processes.append(process)

        # Wait untill all processes are finished and get exceptions.
        for process in self.processes:
            process.join()
            if process.exception:
                error, traceback = process.exception
                print(traceback)


if __name__ == "__main__":
    runner = Runner().run_tests()
