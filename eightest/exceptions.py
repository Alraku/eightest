class Error(Exception):
    """
    Base class for other exceptions.
    """
    def __init__(self) -> None:
        self.message = 'Base Custom Error Class'

    def __str__(self) -> str:
        return self.message


class EmptyFileError(Error):
    """
    Raised when the opened file is empty.
    """
    def __init__(self, file_name) -> None:
        self.message = f"'{file_name}' file is empty."


class NoTestsFoundError(Error):
    """
    Raised when no tests were found.
    """
    def __init__(self) -> None:
        self.message = "No tests found in the test folder."


class TestOutOfClassError(Error):
    """
    Raised when test function was discovered out of Test Class.
    """
    def __init__(self, test_name) -> None:
        self.message = f"'{test_name}' test function out of Test Class."
