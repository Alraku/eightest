import time
import importlib

from process import Process
from search import create_tree


processes = []



def process_func(test_list):
    for test in test_list:
        # tests = importlib.import_module('tests.test_login')
        p = Process(target=eval(test), args="x")
        p.start()
        processes.append(p)
  
    for process in processes:
        process.join()
        if process.exception:
            error, traceback = process.exception
            print(traceback)


def main():
    
    # test_list = ['tests.test_login.' + test_name for test_name in dir(tests) if test_name.startswith('test_')]
    # test_list = collect_tests()
    print(test_list)

    start = time.perf_counter()
    process_func(test_list)
    end = time.perf_counter()

    print(f'Finished in {round(end-start, 2)} second(s)')

def make_me():
    print('xd')

if __name__ == "__main__":
    # main()
    test_tree = create_tree()[0]
    key = list(test_tree.keys())[0]
    value = list(test_tree.values())
    
    print(key)
    print(value[0][5])

    test_module = importlib.import_module(key)

    p = Process(target=getattr(test_module, value[0][5]))
    p.start()
    p.join()


class Runner(object):

    def collect_tests():
        pass

    def run_tests():
        pass


"""
[{'tests.test_login': ['test_one',
                       'test_two',
                       'test_error',
                       'test_x',
                       'test_four',
                       'test_make',
                       {'TestSuite': ['test_krzys', 'test_krzys2']}]},
 {'tests.test_register': ['test_paka', {'Testing': ['test_hihi']}]},
 {'tests.api.test_api1': ['test_api_one']},
 {'tests.api.test_api2': []}]
"""
