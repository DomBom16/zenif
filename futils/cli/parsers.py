from typing import List, Dict, Any, Callable
import argparse
from .exceptions import CLIError


class ArgumentParser(argparse.ArgumentParser):
    def error(self, message):
        raise CLIError(message)


class CommandParser:
    def __init__(self, command: Callable):
        self.command = command
        self.parser = ArgumentParser(description=command.__doc__)
        self._add_arguments()

    def _add_arguments(self):
        if hasattr(self.command, "_arguments"):
            for args, kwargs in self.command._arguments:
                self._add_argument(*args, **kwargs)

    def _add_argument(self, *args, **kwargs):
        # Remove custom parameters that argparse doesn't understand
        is_flag = kwargs.pop("is_flag", False)
        is_option = kwargs.pop("is_option", False)

        if is_flag:
            kwargs["action"] = "store_true"
            kwargs.setdefault("default", False)

        if is_option and not args[0].startswith("-"):
            args = (f"--{args[0]}",) + args[1:]

        self.parser.add_argument(*args, **kwargs)

    def parse_args(self, args: List[str]) -> Dict[str, Any]:
        try:
            parsed_args = self.parser.parse_args(args)
            return vars(parsed_args)
        except CLIError as e:
            print(f"Error: {str(e)}")
            self.parser.print_help()
            return {}


def parse_command_args(command: Callable, args: List[str]) -> Dict[str, Any]:
    parser = CommandParser(command)
    return parser.parse_args(args)
