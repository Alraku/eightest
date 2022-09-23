import inspect
import functools

from typing import Any, Callable


class Template(object):
    """
    Template for specific decorator creation.
    """
    def __init__(self, object) -> None:

        self.object = object
        functools.update_wrapper(self, object)

    def __call__(self, *args: Any, **kwargs: Any) -> Callable:
        """
        When decorator is being called check if is used
        on whole class or single method. If class then
        decorate all methods, otherwise function.

        Returns:
            Callable: Decorated function or method.
        """
        if inspect.isclass(self.object):
            for name, method in inspect.getmembers(self.object):
                if not inspect.isfunction(method) \
                   or inspect.isbuiltin(method):
                    continue

                if not inspect.ismethod(method) and \
                   not name.startswith('test_'):
                    continue

                setattr(self.object, name, self.decorate_method(method))
            return self.object(*args, **kwargs)

        else:
            self.object(*args, **kwargs)

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
