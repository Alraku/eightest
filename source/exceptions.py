class Error(Exception):
    """
    Base class for other exceptions.
    """
    pass


class EmptyFileException(Error):
    """
    Raised when the opened file is empty.
    """
    def __init__(self, file_name) -> None:
        self.message = f"'{file_name}' file is empty."
        self.file_name = file_name

    def __str__(self) -> str:
        return self.message


class TestOutOfClassException(Error):
    """
    Raised when test function was discovered out of Test Class.
    """
    def __init__(self, test_name) -> None:
        self.message = f"'{test_name}' test function out of Test Class."
        self.test_name = test_name

    def __str__(self) -> str:
        return self.message
