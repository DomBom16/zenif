from typing import Callable


def arg(*args, **kwargs):
    """Decorator to add an argument to a CLI command."""

    def decorator(func: Callable) -> Callable:
        if not hasattr(func, "_arguments"):
            func._arguments = []
        func._arguments.append((args, kwargs))
        return func

    return decorator


def kwarg(*args, **kwargs):
    """Decorator to add a keyword argument to a CLI command."""
    kwargs["is_option"] = True
    return arg(*args, **kwargs)
