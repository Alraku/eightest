import os
import importlib

from ast import Module
from typing import Tuple
from multiprocess import Semaphore
from eightest.testcase import Status
from eightest.process import S_Process
from eightest.utilities import get_time
from eightest.searcher import create_tree

from eightest.utilities import (load_env_file,
                                set_cpu_count)


class TaskList(object):
    """
    Wraps independent Task objects into list.
    """

    class Result(object):
        """
        Overall result of a testcase.
        """
        def __init__(self,
                     status: Status = Status.NOTRUN,
                     message: str | None = None
                     ) -> None:
            self.status: Status = status
            self.message: str = message
            self.duration: float = None
            self.retries: int = 1

    class Task(object):
        """
        Single Task that contains several objects:
        - process object
        - test instance object
        - test result object

        Performs operations on process during test exec.
        """
        def __init__(self, process, instance, result) -> None:
            self.process = process
            self.instance = instance
            self.result = result

        def run(self) -> None:
            """
            Starts process if not running.
            """
            self.process.start()

        def join(self, timeout) -> None:
            """
            Blocks and waits until the process whose
            join() method is called terminates.
            If process is still alive after timeout,
            it is being terminated by force.

            Args:
                timeout (int): Time after which
                the process is to be terminated.
            """
            self.process.join(timeout)

            if self.process.is_alive():
                self.terminate(timeout)

        def terminate(self, timeout) -> None:
            """
            Terminates process by force.
            """
            self.process.terminate()
            self.result.status = Status.ERROR
            self.result.duration = f"TIMEOUT({timeout}s)"

        def set_result(self) -> None:
            """
            Gets result from process object of finished test
            and sets to internal results object.
            """
            if self.result.status == Status.ERROR:
                return

            self.result.status = self.process.result[1]
            self.result.duration = self.process.result[2]
            self.result.retries = self.process.result[3]

    def __init__(self) -> None:
        """
        List of task objects.
        """
        self.tasks = []

    def add(self, process, instance) -> None:
        """
        Adds a process with its associated
        instance to the list, sets Result object.

        Args:
            process (S_Process): Process object.
            instance (TestCase): Test instance.
        """
        self.tasks.append(self.Task(process, instance, self.Result()))

    def info(self, index) -> str:
        task = self.tasks[index]
        return f"<Process: {task.process}, Instance: {task.instance}, Result: {task.result.status}, {task.result.duration}, {task.result.retries}>"

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
        # self.processes: list = []
        self.tasks = TaskList()
        self.test_tree: list[dict] = create_tree()

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

    def dispatch_tasks(self) -> None:
        """
        Creates independent processes and appends
        them into the pool of processes.
        """
        start_time = get_time()
        concurrency = int(os.getenv('CONCURRENCY'))
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

                    process = S_Process(
                            target=getattr(_class, test_name),
                            args=(_test_instance,),
                            test_name=test_name,
                            start_time=start_time,
                            semaphore=semaphore
                    )

                    self.tasks.add(process, _test_instance)

    def run_tests(self) -> None:
        TIMEOUT = int(os.getenv('PROCESS_TIMEOUT'))

        for task in self.tasks.tasks:
            task.run()

        for task in self.tasks.tasks:
            task.join(TIMEOUT)
            task.set_result()

    def get_results(self) -> None:
        """
        Wait untill all processes are finished
        and get the test session results.
        """
        for index in range(len(self.tasks.tasks)):
            print(self.tasks.info(index))


def main():
    runner = Runner()
    runner.dispatch_tasks()
    runner.run_tests()
    runner.get_results()


if __name__ == "__main__":
    main()
