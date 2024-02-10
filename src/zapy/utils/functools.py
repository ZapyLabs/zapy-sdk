from typing import Any, Callable


async def empty_function(*args: tuple[Any]) -> Any | None:
    if len(args) == 0:
        return None
    elif len(args) == 1:
        return args[0]
    else:
        return args


def call_with_signature(function: Callable, *args: tuple, kwargs: dict) -> Any:
    import inspect

    sig = inspect.signature(function)
    my_args = list(args)
    my_kwargs = {}
    args_tuples = list(sig.parameters.items())
    for k, v in args_tuples[len(my_args) :]:
        cls = v.annotation
        if inspect.Signature.empty == cls:
            err_msg = f"Undefined type for '{k}' argument on method '{function.__name__}'"
            raise ValueError(err_msg)
        if cls not in kwargs:
            err_msg = f"Missing type of {cls} for argument '{k}' on method '{function.__name__}'"
            raise ValueError(err_msg)
        value = kwargs.get(cls)
        my_kwargs[k] = value
    return function(*my_args, **my_kwargs)
