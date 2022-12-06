import os
import ast

from typing import Tuple
from eightest.utilities import ROOT_DIR
from eightest.exceptions import (NoTestsFoundError,
                                 TestOutOfClassError)


class TestMethod(object):

    def __init__(self,
                 module_path: str,
                 test_class: str,
                 test_name: str,
                 value: int,
                 decorator: str = None
                 ) -> None:
        self.module_path = module_path
        self.test_class = test_class
        self.test_name = test_name
        self.decorator = decorator
        self.selected = None
        self.value = value


def infinite_sequence():
    num = 0
    while True:
        yield str(num)
        num += 1


def find_folder_path() -> str:
    """
    Searches for main test folder path.

    Returns:
        str: path to test folder
    """
    for root, dirs, _ in os.walk(".", topdown=True):
        exclude = set(['.git', '.venv', '.vscode', '__pycache__'])
        dirs[:] = [d for d in dirs if d not in exclude]

        for dirname in dirs:
            if dirname in ('tests', 'test'):
                return os.path.join(root, dirname)

        raise FileNotFoundError('Could not find test(s) folder.')


def get_test_modules() -> list[str]:
    """
    Searches for test files recursively in given directory.
    Test file must start with "test_" to be recognized.

    Returns:
        list: list of test module names
    """
    test_files = []

    for root, _, files in os.walk(find_folder_path()):
        for file_name in files:

            # Ignore cache files
            if file_name.endswith('.pyc'):
                continue

            # Look only for those that starts with:
            if file_name.startswith('test_'):
                file_path = os.path.join(root[2:], file_name)
                test_files.append(file_path)

    if test_files:
        return test_files
    raise NoTestsFoundError


def show_info(function_node: ast.FunctionDef) -> None:
    """
    Prints out information about given function
    and its parameters.

    Args:
        function_node (ast.FunctionDef): Function definition.
    """
    if not isinstance(function_node, ast.FunctionDef):
        raise TypeError(f'{function_node} must be type of ast.FunctionDef')

    print(f"Function name: {function_node.name}")
    if function_node.args.args:
        print("Args:")

        for arg in function_node.args.args:
            print(f"\tParameter name: {arg.arg}")


def read_from_module(module: str) -> Tuple[ast.FunctionDef, ast.ClassDef]:
    """
    Opens module and gets all functions and classes.

    Returns:
        Tuple[ast.FunctionDef, ast.ClassDef]: Functions and classes.
    """
    with open(os.path.join(ROOT_DIR, module), encoding='utf-8') as file:
        node = ast.parse(file.read())

    functions = [n for n in node.body if isinstance(n, ast.FunctionDef)]
    classes = [n for n in node.body if isinstance(n, ast.ClassDef)]

    return functions, classes


def create_tree(decor: str) -> list[dict]:
    """
    Searches for test functions in given test modules.

    Returns:
        list[str]: List of module names along
                    with their test functions.
    """
    test_tree = []
    gen = infinite_sequence()

    for module in get_test_modules():

        functions, classes = read_from_module(module)

        module = module.replace(os.sep, '.').replace('.py', '')
        dict = {}
        dict[module] = []

        # If test function detected raise exception.
        for function in functions:
            if function.name.startswith('test_'):
                raise TestOutOfClassError(function.name)

        # Search for tests in test classes.
        for class_ in classes:
            methods = [n for n in class_.body if isinstance(n, ast.FunctionDef)]
            for method in methods:
                if not method.name.startswith('test_'):
                    continue

                tempdec = None
                if decor:
                    if method.decorator_list:
                        # print(method.decorator_list[0].id)
                        tempdec = method.decorator_list[0].id
                test_method = TestMethod(module, class_.name, method.name, next(gen), tempdec)
                test_tree.append(test_method)

    return test_tree
