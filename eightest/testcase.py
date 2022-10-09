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
    RUNNING = auto()
    NOTRUN = auto()
    PASSED = auto()
    FAILED = auto()
    ERROR = auto()


class TestCase(metaclass=MetaTestCase):
    """
    An individual Test Case.
    """

    def __init__(self, name) -> None:
        self.name = name
        self._duration: float = 0
        self.message: Optional[str]
        self._status: Status = Status.PASSED
        self._reruns: int = 0

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

    def _update(self, status: Status, message: str) -> None:
        """
        Internal, update status property.
        """
        self._status = status
        self.message = message

    def fail(self, message: str | None) -> None:
        """
        Indicate this test failed.
        """
        self._update(Status.FAILED, message)

    def error(self, message: str | None) -> None:
        """
        Indicate this test has encountered an error.
        """
        self._update(Status.ERROR, message)

    @property
    def status(self):
        return self._status

    @status.setter
    def status(self, status: Status):
        self._status = status

    @property
    def duration(self):
        return self._duration

    @duration.setter
    def duration(self, duration: float):
        self._duration = duration

    @property
    def reruns(self):
        return self._reruns

    @reruns.setter
    def reruns(self, reruns: float):
        self._reruns = reruns


class Results(object):
   
    def add(self, test: TestCase) -> None:
        """
        Add a Test to the list of tests.
        """
        if test.status is Status.FAILED:
            self.fail()

        self.tests.append(test)

    def fail(self) -> None:
        """
        Indicate the test run had at least one failure.
        """
        self.status = Status.FAILED

    def error(self, message: str | None = None) -> None:
        """
        Indicate the test run fatally errored.
        """
        self.status = Status.ERROR
        self.message = message
