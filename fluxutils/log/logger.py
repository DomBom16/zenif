from inspect import currentframe, getmodule
from .handlers import Ruleset, Streams, FHGroup, SHGroup
import sys
from .utils import strip_ansi, strip_unsafe_objs, strip_repr_id
from black import format_str, Mode
from pygments import highlight
from pygments.lexers import PythonLexer
from pygments.formatters import Terminal256Formatter as tformatter
from pygments.styles import get_style_by_name
from random import choice


class Logger:
    def __init__(self, ruleset: dict = {}):
        self.__levels = {
            "debug": {"name": "debug", "level": 1, "color": "\033[34m"},
            "info": {"name": "info", "level": 0, "color": "\033[37m"},
            "success": {"name": "success", "level": 2, "color": "\033[32m"},
            "warning": {"name": "warning", "level": 3, "color": "\033[33m"},
            "error": {"name": "error", "level": 4, "color": "\033[31m"},
            "lethal": {"name": "lethal", "level": 5, "color": "\033[35m"},
        }

        self.defaults = {
            "timestamps": {
                "always_show": False,
                "use_utc": False,
            },
            "stacking": {
                "enabled": True,
                "case_sensitive": True,
            },
            "formatting": {
                "ansi": True,
                "highlighting": True,
                "pretty_print": True,
                "fixed_format_width": 0,
            },
            "filtering": {
                "min_level": 0,
                "exclude_messages": [],
                "include_only_messages": [],
            },
            "output": {
                "default_file_stream": None,
            },
            "metadata": {
                "show_metadata": False,
                "include_timestamp": False,
                "include_level_name": False,
                "include_thread_name": True,
                "include_file_name": False,
                "include_wrapping_function": False,
                "include_function": True,
                "include_line_number": False,
                "include_value_count": True,
            },
            "log_line": {"format": "default"},
        }

        self.__rules = self.defaults.copy()
        if ruleset:
            for category, settings in ruleset.items():
                if category in self.__rules:
                    self.__rules[category].update(settings)
                else:
                    self.__rules[category] = settings

        self.ruleset = Ruleset(self.__rules, self.defaults)
        self.stream = Streams(self.defaults)

        if self.ruleset.output.default_file_stream:
            self.stream.file.add(
                self.ruleset.output.default_file_stream, ruleset=self.__rules
            )

        # Add default stdout stream
        self.stream.normal.add(sys.stdout, ruleset=self.__rules)

        if self.ruleset.stacking.enabled:
            self.warning(
                "Stacking is currently not supported. You're seeing this message because you have the Stacking > Stacking Enabled rule set to True."
            )

    def __format_value(self, value, ruleset):
        repr_id = "".join(
            choice("abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789")
            for _ in range(4)
        )
        if ruleset.formatting.pretty_print and isinstance(value, (list, dict, tuple)):
            formatted = highlight(
                strip_repr_id(
                    format_str(
                        str(strip_unsafe_objs(value, repr_id)),
                        mode=Mode(
                            line_length=(
                                ruleset.formatting.fixed_format_width
                                if ruleset.formatting.fixed_format_width > 0
                                else 80  # default width if not specified
                            )
                        ),
                    ),
                    repr_id,
                ),
                PythonLexer(),
                tformatter(style=get_style_by_name("one-dark")),
            )
            return formatted if ruleset.formatting.ansi else strip_ansi(formatted)
        return str(value)

    def __log(self, level: str, values: tuple, sep: str = " ", metadata: dict = None):
        if not metadata:
            frame = currentframe().f_back.f_back
            metadata = {
                "module": getmodule(frame).__name__ if getmodule(frame) else "n/a",
                "function": frame.f_code.co_name,
                "wrapping_func": frame.f_code.co_name if frame else "n/a",
                "line_number": frame.f_lineno,
                "file_name": frame.f_code.co_filename.split("/")[-1],
                "value_count": len(values),
                "level": level,
            }

        level_info = self.__levels[level]

        formatted_values = [
            self.__format_value(value, self.ruleset) for value in values
        ]

        # Join the formatted values
        message = sep.join(formatted_values)

        self.stream.normal.write(message, level_info, metadata)
        self.stream.file.write(message, level_info, metadata)

    def debug(self, *values, sep: str = " "):
        self.__log("debug", values, sep)

    def info(self, *values, sep: str = " "):
        self.__log("info", values, sep)

    def success(self, *values, sep: str = " "):
        self.__log("success", values, sep)

    def warning(self, *values, sep: str = " "):
        self.__log("warning", values, sep)

    def error(self, *values, sep: str = " "):
        self.__log("error", values, sep)

    def lethal(self, *values, sep: str = " "):
        self.__log("lethal", values, sep)

    def fhgroup(self, *file_paths: str) -> FHGroup:
        return FHGroup(self.stream.file, *file_paths)

    def shgroup(self, *streams: str | object) -> SHGroup:
        return SHGroup(self.stream.normal, *streams)
