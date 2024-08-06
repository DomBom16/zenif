from typing import Callable


def argument(*args, **kwargs):
    """Decorator to add an argument to a CLI command."""

    def decorator(func: Callable) -> Callable:
        if not hasattr(func, "_arguments"):
            func._arguments = []
        func._arguments.append((args, kwargs))
        return func

    return decorator


def option(*args, **kwargs):
    """Decorator to add an option to a CLI command."""
    kwargs["is_option"] = True
    return argument(*args, **kwargs)
