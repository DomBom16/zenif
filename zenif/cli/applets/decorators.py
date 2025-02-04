from dataclasses import dataclass
from typing import Callable


@dataclass
class AParam:
    """
    Represents metadata for a Applet parameter.

    Attributes:
        param_name: The name of the parameter as defined in the function signature.
        kind: One of "argument" (positional), "option" (named option), or "flag" (boolean switch).
        help: Help text describing the parameter.
        default: The default value (if any).
        cli_name: The name used on the command line (e.g. "--depth" or "path").
        alias: An optional shorthand alias (e.g. "-d").
    """

    param_name: str
    kind: str
    help: str = ""
    default: any = None
    cli_name: str = ""
    alias: str | None = None

    def __post_init__(self):
        if self.kind in ("option", "flag"):
            # If no explicit CLI name was given, build one from the parameter name.
            if not self.cli_name:
                self.cli_name = f"--{self.param_name}"
            elif not self.cli_name.startswith("-"):
                self.cli_name = f"--{self.cli_name}"
            if self.alias:
                # Use one dash for single-letter aliases, two for longer.
                self.alias = (
                    f"-{self.alias}" if len(self.alias) == 1 else f"--{self.alias}"
                )
        else:
            # For positional arguments, the CLI name is just the parameter name.
            self.cli_name = self.param_name


def _ensure_aparams(func: Callable) -> dict[str, AParam]:
    if not hasattr(func, "_cli_params"):
        func._cli_params = {}
    return func._cli_params


def arg(name: str, *, help: str = "") -> Callable:
    """
    Decorator for a required positional argument.

    Example:
        @arg("path", help="The folder path")
    """

    def decorator(func: Callable) -> Callable:
        cli_params = _ensure_aparams(func)
        cli_params[name] = AParam(
            param_name=name,
            kind="argument",
            help=help,
        )
        return func

    return decorator


def opt(name: str, *, default: any = None, help: str = "") -> Callable:
    """
    Decorator for an option (an optional parameter that takes a value).

    Example:
        @opt("depth", default=10, help="The depth to use")
    """

    def decorator(func: Callable) -> Callable:
        cli_params = _ensure_aparams(func)
        cli_params[name] = AParam(
            param_name=name,
            kind="option",
            help=help,
            default=default,
        )
        return func

    return decorator


def flag(name: str, *, help: str = "") -> Callable:
    """
    Decorator for a boolean flag.

    Example:
        @flag("all", help="Show all")
    """

    def decorator(func: Callable) -> Callable:
        cli_params = _ensure_aparams(func)
        cli_params[name] = AParam(
            param_name=name,
            kind="flag",
            help=help,
            default=False,
        )
        return func

    return decorator


def alias(name: str, alias: str) -> Callable:
    """
    Decorator to set a shorthand alias for an already defined option or flag.
    """

    def decorator(func: Callable) -> Callable:
        # Ensure the function has a place to store alias info.
        if not hasattr(func, "_cli_aliases"):
            func._cli_aliases = {}
        func._cli_aliases[name] = alias
        return func

    return decorator
