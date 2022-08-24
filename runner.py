import time
import importlib
import tests.test_login
from search import collect_tests
from process import Process

processes = []


def process_func(test_list):
    for test in test_list:
        i = importlib.import_module('tests')
        p = Process(target=eval(test), args="x")
        p.start()
        processes.append(p)
  
    for process in processes:
        process.join()
        if process.exception:
            error, traceback = process.exception
            print(traceback)


def main():
    # test_list = ['tests.test_login.' + test_name for test_name in dir(tests.test_login) if test_name.startswith('test')]
    test_list = collect_tests()
    print(test_list)

    start = time.perf_counter()
    process_func(test_list)
    end = time.perf_counter()

    print(f'Finished in {round(end-start, 2)} second(s)')

if __name__ == "__main__":
    main()


class Runner(object):

    def collect_tests():
        pass


    def run_tests():
        pass