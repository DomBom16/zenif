from colorama import Fore, Style
from typing import Callable
import argparse

from .decorators import AParam
from .exceptions import AppletError
from .formatters import HelpFormatter


class ArgumentParser(argparse.ArgumentParser):
    def error(self, message):
        raise AppletError(message)


class CommandParser:
    def __init__(self, command: Callable):
        self.command = command
        self.parser = ArgumentParser(description=command.__doc__)
        self._add_arguments()

    def _add_arguments(self):
        # Get cli parameters; default to an empty dict if not defined.
        cli_params = getattr(self.command, "_cli_params", {})

        # Merge in alias info if available.
        cli_aliases = getattr(self.command, "_cli_aliases", {})
        for param_name, alias_name in cli_aliases.items():
            if param_name in cli_params:
                # Format alias if needed.
                if not alias_name.startswith("-"):
                    alias_name = (
                        f"-{alias_name}" if len(alias_name) == 1 else f"--{alias_name}"
                    )
                cli_params[param_name].alias = alias_name
            else:
                raise ValueError(
                    f"Parameter '{param_name}' not defined; cannot set alias."
                )

        # Iterate over CLI parameters and add them.
        for param in cli_params.values():
            self._add_argument(param)

    def _add_argument(self, param: AParam):
        args = []
        kwargs = {}
        if param.kind == "argument":
            # Positional argument: no dashes.
            args.append(param.cli_name)
        else:
            # For options and flags, add the main CLI name and any alias.
            args.append(param.cli_name)
            if param.alias:
                args.append(param.alias)
            # Ensure that the parsed variable name matches the function parameter.
            kwargs["dest"] = param.param_name

        kwargs["help"] = param.help
        if param.default is not None:
            kwargs["default"] = param.default

        if param.kind == "flag":
            kwargs["action"] = "store_true"
            kwargs.setdefault("default", False)

        self.parser.add_argument(*args, **kwargs)

    def parse_args(self, args: list[str]) -> dict[str, any]:
        try:
            parsed_args = self.parser.parse_args(args)
            return vars(parsed_args)
        except AppletError as e:
            print(
                f"{Fore.RED}During parsing, an error occurred\n> {str(e)}{Style.RESET_ALL}"
            )
            print(
                HelpFormatter.format_command_help(self.command.__name__, self.command)
            )
            return {}


def parse_command_args(command: Callable, args: list[str]) -> dict[str, any]:
    parser = CommandParser(command)
    return parser.parse_args(args)
