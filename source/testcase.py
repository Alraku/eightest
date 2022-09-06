from enum import Enum, auto
from typing import Optional, Tuple


class MetaTestCase(type):
    """
    Metaclass for changing behaviour of
    TestCase class in order to add before/after
    functionalities during test execution.
    """

    def __new__(cls, name: str, bases: Tuple, attrs: dict):
        """
        When creating a new object of that class
        we create a new TestCase class with
        modified properties.

        Args:
            name (str): Class name that invokation came from
            bases (Tuple): Base classes that were inherited
            attrs (dict): Attributes of invoking class
        """
        def replaced_func(fn):
            def new_test(*args, **kwargs):
                args[0].before()
                result = fn(*args, **kwargs)
                args[0].after()
                return result

            return new_test

        # If method is found and its name starts with test, replace it
        for i in attrs:
            if callable(attrs[i]) and attrs[i].__name__.startswith('test'):
                attrs[i] = replaced_func(attrs[i])

        return (super(MetaTestCase, cls).__new__(cls, name, bases, attrs))


class Status(Enum):
    """
    The status of a given test or test session.
    """

    PASS = auto()
    FAIL = auto()
    ERROR = auto()


class TestCase(metaclass=MetaTestCase):
    """
    An individual Test Case.
    """

    def __init__(self, name) -> None:
        self.name = name
        self.status: Status = Status.PASS
        self.message: Optional[str]

    def before(self) -> None:
        """
        Overridable, execute before test part.
        """
        pass

    def after(self) -> None:
        """
        Overridable, execute after test part.
        """
        pass

    def run(self) -> None:
        """
        Execute test part.
        """
        pass

    def _update(self, status: Status) -> None:
        """
        Internal, update status property.
        """
        self.status = status

    def fail(self, message: str | None) -> None:
        """
        Indicate this test failed.
        """
        self._update(Status.FAIL, message)

    def error(self, message: str | None) -> None:
        """
        Indicate this test has encountered an error.
        """
        self._update(Status.ERROR, message)


class Results(object):
    """
    Overall results of a test run.
    """

    def __init__(self,
                 status: Status = Status.PASS,
                 message: str | None = None
                 ) -> None:
        self.status = status
        self.message = message

    def add(self, test: TestCase) -> None:
        """
        Add a Test to the list of tests.
        """
        if test.status is Status.FAIL:
            self.fail()

        self.tests.append(test)

    def fail(self) -> None:
        """
        Indicate the test run had at least one failure.
        """
        self.status = Status.FAIL

    def error(self, message: str | None = None) -> None:
        """
        Indicate the test run fatally errored.
        """
        self.status = Status.ERROR
        self.message = message