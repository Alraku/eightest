import os
import ast

from typing import Tuple
from source.exceptions import (NoTestsFoundError,
                               TestOutOfClassError)


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
            # FIXME Fix path filtering for UNIX.
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
    with open(module, encoding='utf-8') as file:
        node = ast.parse(file.read())

    functions = [n for n in node.body if isinstance(n, ast.FunctionDef)]
    classes = [n for n in node.body if isinstance(n, ast.ClassDef)]

    return functions, classes


def create_tree() -> list[dict]:
    """
    Searches for test functions in given test modules.

    Returns:
        list[str]: List of module names along
                    with their test functions.
    """
    test_tree = []

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
            dict[module].append({class_.name: []})
            methods = [n for n in class_.body if isinstance(n, ast.FunctionDef)]
            # TODO Create way of adding info about decorator to the dict.

            # Add methods to nested dictionary.
            for method in methods:
                if method.name.startswith('test_'):
                    if method.decorator_list:
                        pass
                        # print(method.decorator_list[0].id)
                    dict[module][-1][class_.name].append(method.name)

        test_tree.append(dict)

    return test_tree
