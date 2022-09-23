from functools import wraps

dec_funcs = []


def template(function):
    @wraps(function)
    def nested(*args, **kwargs):
        return function(*args, **kwargs)

    dec_funcs.append(function)
    return nested


REGRESSION_TEST = template
SMOKE_TEST = template


# def decorate(function):
#     @wraps(function)
#     def inner():
#         print("Some stuff 1")
#         function()
#         print("Some stuff 2")

#     dec_funcs.append(function)
#     return inner
