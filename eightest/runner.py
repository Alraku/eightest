import os
import time
import jsons
import pprint
import psutil
import importlib
import itertools
import traceback

from ast import Module
from threading import Thread
from typing import List, Tuple
from multiprocess import Semaphore, Pipe
from eightest.process import S_Process
from eightest.utilities import get_time
from eightest.searcher import TestMethod, create_tree
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
        """
        Args:
            status (Status, optional): Test status.
            message (str | None, optional): Additinoal message.
        """
        self.status = status
        self.message = message
        self.test_name: str = None
        self.duration: float = None
        self.retries: int = 1


class Task(object):
    """
    Single Task that wraps several objects.
    Performs operations on process during test exec.
    """
    def __init__(self,
                 process: S_Process,
                 instance: TestCase,
                 pipe_conn: Pipe,
                 result: Result
                 ) -> None:
        """
        Args:
            process (S_Process): Process object.
            instance (TestCase): Test instance object.
            pipe_conn (Pipe): Pipe child connection.
            result (Result): Test result object.
        """
        self.process = process
        self.instance = instance
        self.result = result
        self.duration = None
        self._pipe_conn = pipe_conn

    def run(self) -> None:
        """
        Starts process if not running, waits
        until receives message from child process
        that it had started execution through pipe.

        Raises:
            ChildProcessError: When process is already running.
            ValueError: When received wrong process response value.
            Exception: When process could not be started.
        """
        if self.process.is_alive():
            raise ChildProcessError('Process is already running.')

        try:
            self.process.start()
            if (resp := self._pipe_conn.recv()) != 0:
                raise ValueError(f'Wrong return value from process: {resp}')

            self.duration = time.perf_counter()
            self.result.status = Status.RUNNING
            self.result.test_name = self.process.test_name

        except Exception:
            message = f'Could not start process: {self.process}.'
            # log.error(message)
            raise Exception(message)

    def join(self, timeout: int = 0) -> None:
        """
        When process has finished its work, join it
        and call set result method.

        Args:
            timeout (int): Time after which
            the process is to be joined.
        """
        self.process.join(timeout)
        self._set_result()

    def terminate(self, timeout: int) -> None:
        """
        Terminates process by force.
        """
        self.process.terminate()
        self.result.status = Status.TIMEOUT
        self.result.duration = timeout
        self.result.retries = 1

    def _set_result(self) -> None:
        """
        Gets result from process object of finished test
        and sets to internal results object.

        Raises:
            ChildProcessError: When no response is available from process.
        """
        if not self._pipe_conn.poll():
            message = f'Could not get response from process: {self.process}.'
            # log.error(message)
            raise ChildProcessError(message)

        (self.result.test_name,
         self.result.status,
         self.result.duration,
         self.result.retries) = self._pipe_conn.recv()

    def __repr__(self):
        return json.dumps(self.__dict__)


class Tasks(object):
    """
    Wraps independent Task objects into list.
    """
    def __init__(self) -> None:
        self.remaining: List[Task] = []
        self.completed: List[Task] = []

    def add(self,
            process: S_Process,
            instance: TestCase,
            pipe_conn: Pipe
            ) -> None:
        """
        Adds a process with its associated
        instance to the list, sets Result object.

        Args:
            process (S_Process): Process object.
            instance (TestCase): Test instance.
            pipe_conn: (Pipe): Pipe child connection.
        """
        task = Task(process, instance, pipe_conn, Result())
        self.remaining.append(task)

    def complete(self, task: Task) -> None:
        """
        Adds task to completed task list and
        removes from the remaining.

        Args:
            task (Task): Particular Task object.
        """
        self.completed.append(task)
        self.remaining.remove(task)

    def info(self) -> List[str]:
        """
        Prints out overall test session info.

        Returns:
            List[str]: List of str outputs.
        """
        output: List[str] = []

        for task in self.completed:
            output.append(f"Test Name: {task.result.test_name} " +
                          f"Result: {task.result.status} " +
                          f"Duration: {task.result.duration} " +
                          f"Retries: {task.result.retries}")
        return output

    def __iter__(self) -> list[Task]:
        return itertools.cycle(self.remaining)

    def get_progress(self) -> None:
        passed = error = failed = notrun = 0

        for task in self.completed:
            if task.result.status.name == 'PASSED':
                passed += 1
            if task.result.status.name == 'FAILED':
                failed += 1
            if task.result.status.name == 'ERROR':
                error += 1
            if task.result.status.name == 'TIMEOUT':
                error += 1

        notrun = len(self.remaining)
        progress = {
            "passed": passed,
            "error": error,
            "failed": failed,
            "notrun": notrun,
            "list": jsons.dump(self.completed)
        }
        return progress

    def reset(self) -> None:
        self.remaining.clear()
        self.completed.clear()


class Runner(object):
    """
    Class responsible for creating processes in which
    each test is executed separately and independently.
    """
    def __init__(self, decor: str = None) -> None:
        """
        Initialization of processes list
        and generating tests' hierarchy.
        """
        set_cpu_count()
        load_env_file()
        self.tasks = Tasks()
        self.test_tree: List[TestMethod] = create_tree(decor)
        self.selected: List[TestMethod] = []
        self.decor = decor

    def collect_tests(self, list) -> None:
        """
        Method for future test selection.
        """
        self.selected.clear()
        for elem in self.test_tree:
            if elem.value in list:
                self.selected.append(elem)

    def importer(self, module_path: str) -> Module:
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
        # mod_name = next(iter(module.keys()))
        # mod_members = next(iter(module.values()))
        try:
            module = importlib.import_module(module_path)
        except ModuleNotFoundError as Error:
            raise Error

        return module

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

        if self.decor:
            for test_method in self.test_tree:
                if test_method.decorator:
                    self.selected.append(test_method)

        if not self.selected:
            self.selected = self.test_tree

        for test_method in self.selected:

            module = self.importer(test_method.module_path)

            _class = getattr(module, test_method.test_class)
            _test_instance = _class(test_method.test_name)
            parent_conn, child_conn = Pipe()

            process = S_Process(
                target=getattr(_class, test_method.test_name),
                args=(_test_instance,),
                test_name=test_method.test_name,
                session_time=start_time,
                semaphore=semaphore,
                pipe_conn=child_conn
            )
            self.tasks.add(process, _test_instance, parent_conn)

    def run_tests(self) -> None:
        """
        Runs all tests and gathers results.
        """
        def runner(tasks: List[Task]):
            """
            Helper method to run tasks in
            separate non-blocking Thread.

            Args:
                tasks (List[Task]): List of tasks.
            """
            try:
                for task in tasks:
                    # log.debug(f'Running task: {task}.')
                    task.run()

            except Exception:
                print(traceback.format_exc())
            # log.info('Runned all available tasks.')

        TIMEOUT = int(os.getenv('PROCESS_TIMEOUT'))

        try:
            runner = Thread(target=runner, args=(self.tasks.remaining.copy(),))
            runner.start()

        except (KeyboardInterrupt, SystemExit):
            for task in self.tasks.remaining:
                if task.process.is_alive():
                    task.terminate(0)

        try:
            if not self.tasks.remaining:
                raise IndexError('No tasks were found in remaining list.')

            while self.tasks.remaining:
                for task in self.tasks.remaining.copy():

                    if (not task.process.is_alive()
                       and task.result.status.name == 'RUNNING'):
                        # log.debug('Joining task: ', task)
                        task.join()
                        self.tasks.complete(task)

                    elif task.result.status.name == "RUNNING":
                        check_time = time.perf_counter() - task.duration

                        if (check_time > TIMEOUT):
                            # log.debug('Terminating task: ', task)
                            task.terminate(TIMEOUT)
                            self.tasks.complete(task)

                time.sleep(0.2)

        except (KeyboardInterrupt, SystemExit):
            # log.debug('Parent received CTRL-C: stopping all processes.')
            for task in self.tasks.remaining:
                if task.process.is_alive():
                    task.terminate(0)

        except Exception:
            raise Exception('Some error occurred during test exec.')

    def pause_resume(self) -> None:
        """
        Pauses or resumes test execution.
        """
        for task in self.tasks.remaining:
            # if task.process.is_alive():
            proc = psutil.Process(task.process.pid)
            print('jestem w funkcji:', proc.status())

            if str(proc.status()) == 'running':
                print('pauza')
                proc.suspend()
            else:
                print('resume')
                proc.resume()

    def get_results(self) -> None:
        """
        Prints test session results.
        """
        pprint.pprint(self.tasks.info())


def main():
    runner = Runner()
    runner.dispatch_tasks()
    runner.run_tests()
    runner.get_results()


def argsparser():
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument('-d', metavar='DECORATOR', type=str, default=None)

    args = parser.parse_args()

    runner = Runner(args.d)
    runner.dispatch_tasks()
    runner.run_tests()
    runner.get_results()

if __name__ == "__main__":
    # main()
    argsparser()
