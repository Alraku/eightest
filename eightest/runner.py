import os
import time
import pprint
import psutil
import importlib
import itertools

from ast import Module
from typing import List, Tuple
from threading import Thread
from multiprocess import Semaphore, Pipe
from eightest.process import S_Process
from eightest.utilities import get_time
from eightest.searcher import create_tree
from eightest.testcase import Status, TestCase

from eightest.utilities import (load_env_file,
                                set_cpu_count)


class Result(object):
    """
    Overall result of a testcase.
    """
    def __init__(self,
                 status: Status = Status.NOTRUN,
                 message: str | None = None
                 ) -> None:
        self.status = status
        self.message = message
        self.test_name: str = None
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
    def __init__(self,
                 process: S_Process,
                 instance: TestCase,
                 pipe_conn: Pipe,
                 result: Result
                 ) -> None:
        self.process = process
        self.instance = instance
        self.pipe_conn = pipe_conn
        self.result = result
        self.duration = None

    def run(self) -> None:
        """
        Starts process if not running.
        """
        self.process.start()
        self.pipe_conn.recv()
        self.duration = time.perf_counter()
        self.result.status = Status.RUNNING
        self.result.test_name = self.process.test_name

    def join(self, timeout: int = 0) -> None:
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
            # log.debug('failed to join worker %s', self.process)
            self.process.kill()
        self.set_result()

    def terminate(self, timeout: int = 0) -> None:
        """
        Terminates process by force.
        """
        # TODO to mozna polaczyc jakos z test_result, niech process wysyla jednak pelna zwrotke
        self.process.terminate()
        self.result.status = Status.ERROR
        self.result.duration = f"TIMEOUT({timeout}s)"
        self.result.retries = 1

    def set_result(self) -> None:
        """
        Gets result from process object of finished test
        and sets to internal results object.
        """
        (self.result.test_name,
         self.result.status,
         self.result.duration,
         self.result.retries) = self.pipe_conn.recv()


class Tasks(object):
    """
    Wraps independent Task objects into list.
    """

    def __init__(self) -> None:
        """
        List of task objects.
        """
        self.all_tasks: List[Task] = []
        self.completed: List[Task] = []

    def add(self, process: S_Process, instance: TestCase, pipe_conn: Pipe) -> None:
        """
        Adds a process with its associated
        instance to the list, sets Result object.

        Args:
            process (S_Process): Process object.
            instance (TestCase): Test instance.
        """
        task = Task(process, instance, pipe_conn, Result())
        self.all_tasks.append(task)

    def complete(self, task: Task) -> None:
        self.completed.append(task)
        self.all_tasks.remove(task)

    def info(self) -> str:
        output = list()
        for task in self.completed:
            output.append(f"Test Name: {task.result.test_name} " +
                          f"Result: {task.result.status} " +
                          f"Duration: {task.result.duration} " +
                          f"Retries: {task.result.retries}")
        return output

    def __iter__(self) -> list[Task]:
        return itertools.cycle(self.all_tasks)


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
        self.tasks = Tasks()
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
                    parent_conn, child_conn = Pipe()

                    process = S_Process(
                            target=getattr(_class, test_name),
                            args=(_test_instance,),
                            test_name=test_name,
                            session_time=start_time,
                            semaphore=semaphore,
                            pipe_conn=child_conn
                    )
                    self.tasks.add(process, _test_instance, parent_conn)

    def run_tests(self) -> None:

        def runner(tasks):
            for task in tasks:
                task.run()
            # TODO SOME TRY/CATCH/ERROR EXCEPTION
            # log.info('Runned all available processes.')

        TIMEOUT = int(os.getenv('PROCESS_TIMEOUT'))

        try:
            runner = Thread(target=runner, args=(self.tasks.all_tasks,))
            runner.start()
            runner.join()

        except (KeyboardInterrupt, SystemExit):
            for task in self.tasks.all_tasks:
                if task.process.is_alive():
                    task.terminate(0)

        try:
            if not self.tasks.all_tasks:
                raise Exception

            while self.tasks.all_tasks:
                for task in self.tasks.all_tasks:

                    if not task.process.is_alive() and task.result.status.name == 'RUNNING':
                        task.join()
                        self.tasks.complete(task)

                    if task.result.status.name == "RUNNING":
                        check_time = time.perf_counter() - task.duration

                        if (check_time > TIMEOUT):
                            task.terminate(TIMEOUT)
                            self.tasks.complete(task)
                    else:
                        continue

                time.sleep(0.1)

        except (KeyboardInterrupt, SystemExit):
            # log.debug('parent received ctrl-c: stop all processes')
            for task in self.tasks.all_tasks:
                if task.process.is_alive():
                    task.terminate(0)

        except Exception:
            pass

    def pause_resume(self) -> None:
        for task in self.tasks.all_tasks:
            if task.process.is_alive():
                proc = psutil.Process(task.process.pid)

                if proc.is_running():
                    proc.suspend()
                else:
                    proc.resume()

    def get_results(self) -> None:
        """
        Wait untill all processes are finished
        and get the test session results.
        """
        pprint.pprint(self.tasks.info())


def main():
    runner = Runner()
    runner.dispatch_tasks()
    runner.run_tests()
    runner.get_results()


if __name__ == "__main__":
    main()
