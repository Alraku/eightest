import os
import importlib

from ast import Module
from typing import Tuple
from multiprocess import Semaphore
from eightest.process import S_Process
from eightest.utilities import get_time
from eightest.searcher import create_tree
from eightest.testcase import (Results,
                               Status)

from eightest.utilities import (load_env_file,
                                set_cpu_count)


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
        set_cpu_count()
        load_env_file()
        self.processes: list = []
        self.test_tree: list[dict] = create_tree()
        self.test_results = Results()

    def collect_tests(self) -> None:
        """
        Method for future test selection.
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
        concurrency = None
        start_time = get_time()
        NO_SYSTEM_CPU = int(os.getenv('CPU_COUNT'))

        if concurrency is None:
            concurrency = max(NO_SYSTEM_CPU - 1, 1)
            if concurrency == 1:
                raise ValueError('Not enough cores to parallelise.')

        semaphore = Semaphore(concurrency)
        # For each module in test hierarchy.
        for module in self.test_tree:
            module, mod_name, mod_members = self.importer(module)

            # For each TestSuite in module.
            for test_class in mod_members:
                _class = getattr(module, next(iter(test_class.keys())))

                # For each test in given TestSuite.
                for test_name in test_class[next(iter(test_class.keys()))]:
                    _test_instance = _class(test_name)

                    semaphore.acquire()

                    process = S_Process(
                            target=getattr(_class, test_name),
                            args=(_test_instance,),
                            test_name=test_name,
                            start_time=start_time,
                            semaphore=semaphore
                    )
                    process.start()
                    self.processes.append((process, _test_instance))

        self.get_results()

    def terminate_process(self, process, instance):
        process.terminate()
        instance.status = Status.ERROR
        instance.duration = 10
        instance.reruns = 1
        self.test_results.add(instance)

    def get_results(self) -> None:
        """
        Wait untill all processes are finished
        and get the test session results.
        """
        TIMEOUT = int(os.getenv('PROCESS_TIMEOUT'))

        for process, instance in self.processes:
            process.join(TIMEOUT)

            if process.is_alive():
                self.terminate_process(process, instance)
                continue

            instance.status = process.result[1]
            instance.duration = process.result[2]
            instance.reruns = process.result[3]

            self.test_results.add(instance)

    def show_results(self) -> None:
        """
        Print out results.
        """
        for test in self.test_results.tests:
            print(f'{test.name: <15} \
                    {test.status: <15} \
                    {test.duration: <5} \
                    {test.reruns}')


def main():
    runner = Runner()
    # runner.collect_tests()
    runner.run_tests()
    runner.show_results()
