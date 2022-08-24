import os
import ast


def get_test_folder_path() -> str:
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

    for root, _, files in os.walk(get_test_folder_path()):
        for file_name in files:

            if file_name.endswith('pyc'):
                continue

            if file_name.startswith('test_'):
                file_path = os.path.join(root, file_name)
                test_files.append(file_path.replace('.\\', ''))

    return test_files


def show_info(function_node):
    """
    Prints out information about given function
    and its parameters.

    Args:
        function_node (_type_): _description_
    """
    print(f"Function name: {function_node.name}")
    # if function_node.args.args:
    #     print("Args:")
    #     for arg in function_node.args.args:
    #         print(f"\tParameter name: {arg.arg}")


def collect_tests() -> list[str]:
    """
    Searches for test functions in given test modules.

    Returns:
        list[str]: List of combined tests and their module paths.
    """
    collected_tests = [] 
    file_paths = get_test_modules()
    for file_path in file_paths:

        with open(file_path, encoding='utf-8') as file:
            node = ast.parse(file.read())

        module_path = file_path.replace('\\', '.')
        print(module_path)

        functions = [n for n in node.body if isinstance(n, ast.FunctionDef)]
        classes = [n for n in node.body if isinstance(n, ast.ClassDef)]

        for function in functions:
            show_info(function)
            collected_tests.append(module_path.replace('py', function.name))

        for class_ in classes:
            print("Class name:", class_.name)
            methods = [n for n in class_.body if isinstance(n, ast.FunctionDef)]
            for method in methods:
                show_info(method)

    return collected_tests

# TODO: Filter only those functions which have 'test' in their name.
# test_list = [test_folder + '.' + if test_name.startswith('test')]

