from typing import Callable


def req(*args, **kwargs):
    """Decorator to add a required argument to a CLI command."""

    # for each arg and kwarg, set the help to lowercase
    kwargs["help"] = kwargs.get("help", "").lower()

    def decorator(func: Callable) -> Callable:
        if not hasattr(func, "_arguments"):
            func._arguments = []
        func._arguments.append((args, kwargs))
        return func

    return decorator


def opt(*args, **kwargs):
    """Decorator to add an optional argument or flag to a CLI command."""
    kwargs["is_option"] = True
    return req(*args, **kwargs)
