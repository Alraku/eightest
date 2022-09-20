import os
import ast

from source.exceptions import TestOutOfClassException


def find_folder_path() -> str:
    """
    Searches for main test folder path.

    Returns:
        str: path to test folder
    """
    for root, dirs, _ in os.walk(".", topdown=True):
        for dirname in dirs:
            if dirname in ('tests', 'test'):
                return os.path.join(root, dirname)


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
            if file_name.endswith('pyc'):
                continue

            # Look only for those that start with:
            if file_name.startswith('test_'):
                file_path = os.path.join(root, file_name)
                test_files.append(file_path.replace('.\\', ''))

    return test_files


def show_info(function_node: ast.FunctionDef) -> None:
    """
    Prints out information about given function
    and its parameters.

    Args:
        function_node (ast.FunctionDef): Function definition.
    """
    print(f"Function name: {function_node.name}")
    if function_node.args.args:
        print("Args:")
        for arg in function_node.args.args:
            print(f"\tParameter name: {arg.arg}")


def create_tree() -> list[dict]:
    """
    Searches for test functions in given test modules.

    Returns:
        list[str]: List of module names along
                    with their test functions.
    """
    test_tree = []

    for module in get_test_modules():

        with open(module, encoding='utf-8') as file:
            node = ast.parse(file.read())

        # Get all functions and classes from module.
        functions = [n for n in node.body if isinstance(n, ast.FunctionDef)]
        classes = [n for n in node.body if isinstance(n, ast.ClassDef)]

        module = module.replace('\\', '.').replace('.py', '')
        dict = {}
        dict[module] = []

        # If test function detected raise exception.
        for function in functions:
            if function.name.startswith('test_'):
                # dict[module].append(function.name)
                raise TestOutOfClassException(function.name)

        # Search for tests in test classes.
        for class_ in classes:
            dict[module].append({class_.name: []})
            methods = [n for n in class_.body if isinstance(n, ast.FunctionDef)]

            # Add methods to nested dictionary.
            for method in methods:
                if method.name.startswith('test_'):
                    dict[module][-1][class_.name].append(method.name)

        test_tree.append(dict)

    return test_tree
