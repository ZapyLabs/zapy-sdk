async def empty_function(*args):
    if len(args) == 0:
        return None
    elif len(args) == 1:
        return args[0]
    else:
        return args

def call_with_signature(function, *args, kwargs):
    import inspect

    sig = inspect.signature(function)
    my_args = list(args)
    my_kwargs = dict()
    args_tuples = list(sig.parameters.items())
    for k , v in args_tuples[len(my_args):]:
        cls = v.annotation
        if inspect.Signature.empty == cls:
            raise ValueError(f"Undefined type for '{k}' argument on method '{function.__name__}'")
        if cls not in kwargs:
            raise ValueError(f"Invalid type of {cls} for argument '{k}' on method '{function.__name__}'")
        value = kwargs.get(cls)
        my_kwargs[k] = value
    return function(*my_args, **my_kwargs)