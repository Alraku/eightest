import inspect
import functools

from typing import Any, Callable


class Template(object):
    """
    Template for specific decorator creation.
    """

    def __init__(self, object) -> None:

        self.__object = object
        functools.update_wrapper(self, object)

    def __call__(self, *args: Any, **kwargs: Any) -> Callable:
        """
        When decorator is being called check if is used
        on whole class or single method. If class then
        decorate all methods, otherwise function.

        Returns:
            Callable: Decorated function or method.
        """
        if inspect.isclass(self.__object):
            for name, method in inspect.getmembers(self.__object):
                if not inspect.isfunction(method) or inspect.isbuiltin(method):
                    continue

                if not inspect.ismethod(method) and not name.startswith(
                    "test_"
                ):
                    continue

                setattr(self.__object, name, self.decorate_method(method))
            return self.__object(*args, **kwargs)

        else:
            self.__object(*args, **kwargs)

    def decorate_method(self, original_func: Callable) -> Callable:
        """
        Helper function for decorating particular class method.

        Args:
            original_func (Callable): _description_

        Returns:
            Callable: Decorated method.
        """

        @functools.wraps(original_func)
        def decorator(*args, **kwargs):
            return original_func(self, *args, **kwargs)

        return decorator


SMOKE_TEST = Template
REGRESSION_TEST = Template
