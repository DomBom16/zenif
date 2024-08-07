from inspect import currentframe, getmodule
from .handlers import Ruleset, Streams, FHGroup, SHGroup
import sys
from .utils import strip_unsafe_objs, strip_repr_id  # , strip_ansi
from black import format_str, Mode
from pygments import highlight
from pygments.lexers import PythonLexer
from pygments.formatters import Terminal256Formatter as tformatter
from pygments.styles import get_style_by_name
from random import choice
from io import StringIO
from copy import deepcopy

# import traceback
# from colorama import init, Fore, Style

# init(autoreset=False)

# > File "demo.py", line 21, in <module>
#     main(1, 2, z)  # Oops...
#     |          └ 0
#     └ <function main at 0x7ff810e63bf8>

#   File "demo.py", line 16, in main
#     x * y / z
#     |   |   └ 0
#     |   └ 2
#     └ 1

# ZeroDivisionError: division by zero


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
            return formatted
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

    def fhgroup(self, *items) -> FHGroup:
        group = FHGroup(self.stream.file)
        for item in [*items]:
            if isinstance(item, str):
                group.add(item)
            elif isinstance(item, FHGroup):
                group.add(*item.file_paths)
        return group

    def shgroup(self, *items) -> SHGroup:
        group = SHGroup(self.stream.normal)
        for item in [*items]:
            if isinstance(item, SHGroup):
                group.add(*item.streams)
            else:
                group.add(item)
        return group

    # def exception(self, exc_info=None):
    #     """
    #     Log an exception with a detailed traceback and variable callouts.

    #     :param exc_info: A tuple (type, value, traceback) as returned by sys.exc_info().
    #                      If not provided, it will use the current exception information.
    #     """
    #     if exc_info is None:
    #         exc_info = sys.exc_info()

    #     exc_type, exc_value, exc_traceback = exc_info

    #     # Format the traceback
    #     tb_lines = traceback.format_exception(exc_type, exc_value, exc_traceback)

    #     # Remove the first line which typically says "Traceback (most recent call last):"
    #     tb_lines = tb_lines[1:]
    #     tb_lines = "\n".join(tb_lines).split("\n")

    #     # Process each line of the traceback
    #     processed_lines = []
    #     frame = exc_traceback
    #     for lineno, line in enumerate(tb_lines):

    #         if "File" in tb_lines[lineno - 1]:
    #             code_line = line.split("\n")[-1]
    #             local_vars = frame.tb_frame.f_locals
    #             var_positions = self._get_var_positions(code_line, local_vars)
    #             processed_lines.append(
    #                 highlight(
    #                     code_line,
    #                     PythonLexer(),
    #                     tformatter(style=get_style_by_name("one-dark")),
    #                 ).rstrip()
    #             )

    #             if var_positions:
    #                 callout_lines = self._create_callout_lines(
    #                     var_positions, local_vars
    #                 )
    #                 processed_lines.extend(callout_lines)

    #             frame = frame.tb_next
    #         else:
    #             processed_lines.append(strip_ansi(line))

    #     # Join the processed lines
    #     full_tb = "\n".join(processed_lines)

    #     # Log the exception
    #     print(f"Exception occurred:\n{full_tb}")

    # def _get_var_positions(self, code_line, local_vars):
    #     """Find positions of variables in the code line."""
    #     var_positions = {}
    #     for var in local_vars:
    #         if var in code_line:
    #             var_positions[var] = code_line.index(var)
    #     return dict(sorted(var_positions.items(), key=lambda x: x[1]))

    # def _create_callout_lines(self, var_positions, local_vars):
    #     """Create callout lines for variables."""
    #     callout_lines = []
    #     var_count = len(var_positions)

    #     for i in range(var_count):
    #         line = ""
    #         for j, (var, pos) in enumerate(var_positions.items()):
    #             value = repr(local_vars[var])
    #             line += (
    #                 f"\r\033[{pos}C{Fore.BLUE}{Style.DIM}┃{Style.RESET_ALL}"
    #                 if ((var_count - 1) - i) > j
    #                 else ""
    #             )
    #             line += (
    #                 f"\r\033[{pos}C{Fore.BLUE}{Style.DIM}┗{Style.NORMAL} {value}{Style.RESET_ALL}"
    #                 if ((var_count - 1) - i) == j
    #                 else ""
    #             )
    #         callout_lines.append(line)

    #     return callout_lines

    def create_test_stream(self) -> tuple[StringIO, "SHGroup"]:
        stream = StringIO()
        group = self.shgroup(stream)
        return stream, group

    def clear_stream(self, stream: StringIO):
        stream.truncate(0)
        stream.seek(0)


class TestLogger:
    def __init__(self):
        self.logger = Logger()
        self.default_stream = sys.stdout
        self.default_ruleset = deepcopy(self.logger.defaults)
        self.test_streams = {
            "default": StringIO(),
            "no_ansi": StringIO(),
            "timestamp": StringIO(),
            "multi_stream": StringIO(),
        }

    def setup(self):
        print("\n--- Setting up test streams ---")
        self.logger.stream.normal.remove(self.default_stream)
        for _, stream in self.test_streams.items():
            self.logger.stream.normal.add(stream)
            self.logger.stream.normal.modify(
                stream, self.default_ruleset, use_original=True
            )

    def clear_test_streams(self):
        for stream in self.test_streams.values():
            stream.truncate(0)
            stream.seek(0)

    def test_default_stream(self):
        print("\n\033[35m--- Testing Default Stream ---\033[0m")
        self.clear_test_streams()
        self.logger.info("This is a default log message")
        print(self.test_streams["default"].getvalue(), end="")

    def test_no_ansi_stream(self):
        print("\n\033[35m--- Testing No ANSI Stream ---\033[0m")
        self.clear_test_streams()
        self.logger.stream.normal.modify(
            self.test_streams["no_ansi"], {"formatting": {"ansi": False}}
        )
        self.logger.info("This is a log message without ANSI formatting")
        print(self.test_streams["no_ansi"].getvalue(), end="")

    def test_timestamp_stream(self):
        print("\n\033[35m--- Testing Always Show Timestamp Stream ---\033[0m")
        self.clear_test_streams()
        self.logger.stream.normal.modify(
            self.test_streams["timestamp"], {"timestamps": {"always_show": True}}
        )
        self.logger.info("This log message should always show a timestamp")
        self.logger.info(
            "This log message should show a timestamp too, even if it's the same second"
        )
        print(self.test_streams["timestamp"].getvalue(), end="")

    def test_multiple_streams(self):
        print("\n\033[35m--- Testing Multiple Streams Simultaneously ---\033[0m")
        self.clear_test_streams()

        # Configure streams with different settings
        self.logger.stream.normal.modify(
            self.test_streams["default"], self.default_ruleset, use_original=True
        )
        self.logger.stream.normal.modify(
            self.test_streams["no_ansi"], {"formatting": {"ansi": False}}
        )
        self.logger.stream.normal.modify(
            self.test_streams["timestamp"], {"timestamps": {"always_show": True}}
        )
        self.logger.stream.normal.modify(
            self.test_streams["multi_stream"],
            {"formatting": {"ansi": False}, "timestamps": {"always_show": True}},
        )

        # Log messages to all streams
        self.logger.info(
            "This message should appear in all streams with different formatting"
        )
        self.logger.warning("This is a warning message to test multiple streams")

        # Print output from each stream
        for stream_name, stream in self.test_streams.items():
            print(f"\nOutput from {stream_name} stream:")
            print(stream.getvalue(), end="")

    def reset(self):
        print("\n\033[35m--- Resetting to default stream ---\033[0m")
        for stream in self.test_streams.values():
            self.logger.stream.normal.remove(stream)
        self.logger.stream.normal.add(self.default_stream)

    def run_tests(self):
        self.setup()
        self.test_default_stream()
        self.test_no_ansi_stream()
        self.test_timestamp_stream()
        self.test_multiple_streams()
        self.reset()


# len = 3
# (len - 1) - i

# == > C
# >  > Y
# <  > N

# 0
#   0   Y
#   1   Y
#   2   C
# 1
#   0   Y
#   1   C
#   2   N
# 2
#   0   C
#   1   N
#   2   N
