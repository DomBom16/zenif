import sys
from datetime import datetime, UTC
from inspect import getmodule, currentframe
from shutil import get_terminal_size as tsize
from threading import current_thread
from random import choice
from black import format_str, Mode
from io import StringIO
from re import sub

from pygments import highlight
from pygments.lexers import PythonLexer
from pygments.formatters import Terminal256Formatter as tformatter
from pygments.styles import get_style_by_name

from .utils import (
    strip_ansi,
    strip_unsafe_objs,
    strip_repr_id,
    wrap,
    if_space,
)
from .template import TemplateEngine


class Ruleset:
    def __init__(self, rules):
        self._rules = rules
        self.dict = self.Dict(rules)
        for category, settings in rules.items():
            setattr(
                self,
                category,
                type(f"{category.title().replace('_', '')}Rules", (), settings)(),
            )

    class Dict:
        def __init__(self, rules):
            self.all = rules
            for category, settings in rules.items():
                setattr(self, category, settings)


class StreamHandler:
    def __init__(self):
        self.output_streams = []
        self.stream_rulesets = {}

    def add(self, stream, ruleset=None):
        if stream not in self.output_streams:
            self.output_streams.append(stream)
            if ruleset:
                self.stream_rulesets[stream] = ruleset

    def remove(self, stream):
        if stream in self.output_streams:
            self.output_streams.remove(stream)
            if stream in self.stream_rulesets:
                del self.stream_rulesets[stream]

    def write(self, message, level=0):
        for stream in self.output_streams:
            ruleset = self.stream_rulesets.get(stream, None)
            if ruleset:
                # Apply filtering rules
                if level < ruleset.filtering.min_level:
                    continue
                if any(
                    substring in message
                    for substring in ruleset.filtering.exclude_messages
                ):
                    continue
                if ruleset.filtering.include_only_messages and not any(
                    substring in message
                    for substring in ruleset.filtering.include_only_messages
                ):
                    continue

                # Apply timestamp rules
                timestamp = ""
                if ruleset.timestamps.always_show or self._timestamp_changed():
                    now = (
                        datetime.now(UTC)
                        if ruleset.timestamps.use_utc
                        else datetime.now()
                    )
                    timestamp = now.strftime("%H:%M:%S")

                # Apply formatting rules
                if ruleset.formatting.pretty_print:
                    message = self._pretty_print(
                        message, ruleset.formatting.fixed_format_width
                    )

                formatted_message = f"{timestamp} {message}"
                stream.write(formatted_message)

            else:
                stream.write(message)

            stream.flush()

    def _timestamp_changed(self):
        # This function checks if the timestamp has changed
        # Implementation depends on how you want to track previous timestamps
        return True

    def _pretty_print(self, message, width):
        formatted_message = format_str(
            message, mode=Mode(line_length=width or tsize().columns)
        )
        return highlight(
            formatted_message,
            PythonLexer(),
            tformatter(style=get_style_by_name("one-dark")),
        )


class FileHandler:
    def __init__(self):
        self.file_streams = {}
        self.file_rulesets = {}

    def add(self, file_path, reset=False, ruleset=None):
        if file_path not in self.file_streams:
            mode = "w" if reset else "a"
            self.file_streams[file_path] = open(file_path, mode)
            self.file_streams[file_path].write("")
            self.file_streams[file_path].flush()
            if ruleset:
                self.file_rulesets[file_path] = ruleset

    def remove(self, file_path):
        if file_path in self.file_streams:
            self.file_streams[file_path].close()
            del self.file_streams[file_path]
            if file_path in self.file_rulesets:
                del self.file_rulesets[file_path]

    def write(self, message, level=0):
        for file_path, file_stream in self.file_streams.items():
            ruleset = self.file_rulesets.get(file_path, None)
            if ruleset:
                # Apply filtering rules
                if level < ruleset.filtering.min_level:
                    continue
                if any(
                    substring in message
                    for substring in ruleset.filtering.exclude_messages
                ):
                    continue
                if ruleset.filtering.include_only_messages and not any(
                    substring in message
                    for substring in ruleset.filtering.include_only_messages
                ):
                    continue

                # Apply timestamp rules
                timestamp = (
                    datetime.now(UTC) if ruleset.timestamps.use_utc else datetime.now()
                ).strftime("%H:%M:%S")

                # Apply formatting rules
                if ruleset.formatting.pretty_print:
                    message = self._pretty_print(
                        message, ruleset.formatting.fixed_format_width
                    )

                file_stream.write(
                    strip_ansi(
                        sub(
                            r"\033\[(\d+)C",
                            lambda m: " " * int(m.group(1)),
                            message,
                        )
                    )
                )

            else:
                file_stream.write(
                    strip_ansi(
                        sub(r"\033\[(\d+)C", lambda m: " " * int(m.group(1)), message)
                    )
                )
            file_stream.flush()

    def _timestamp_changed(self):
        # This function checks if the timestamp has changed
        # Implementation depends on how you want to track previous timestamps
        return True

    def _pretty_print(self, message, width):
        # formatted_message = format_str(
        #     message, mode=Mode(line_length=width or tsize().columns)
        # )
        # return highlight(
        #     formatted_message,
        #     PythonLexer(),
        #     tformatter(style=get_style_by_name("one-dark")),
        # )
        return message

    def reset(self, file_path):
        if file_path in self.file_streams:
            self.remove(file_path)
            self.add(file_path, reset=True)


class Streams:
    def __init__(self):
        self.file = FileHandler()
        self.normal = StreamHandler()


class Logger:
    """A class used to log messages with granular customizability.

    Args:
        rules (dict, optional): A ruleset that overrides the default rules. To view the default rules, view Logger().defaults. Defaults to {}.
    """

    def __init__(self, rules: dict = {}) -> None:

        self.__log_metadata: str = None
        self.__repr_id: str = ""

        self.__levels: dict[str, dict[str, str | int]] = {
            "debug": {
                "name": "debug",
                "level": 1,
                "color": "\033[34m",
            },
            "info": {
                "name": "info",
                "level": 0,
                "color": "\033[37m",
            },
            "success": {
                "name": "success",
                "level": 2,
                "color": "\033[32m",
            },
            "warning": {
                "name": "warning",
                "level": 3,
                "color": "\033[33m",
            },
            "error": {
                "name": "error",
                "level": 4,
                "color": "\033[31m",
            },
            "lethal": {
                "name": "lethal",
                "level": -1,
                "color": "\033[35m",
            },
        }

        self.defaults: dict[str, any] = {
            "timestamps": {
                "always_show": False,  # If False, only prints the time changes
                "use_utc": False,  # If True, use UTC for timestamps; otherwise, use local time
            },
            "stacking": {
                "enabled": True,  # If True, stacking is enabled; otherwise disabled
                # If False, messages will stack if if the capitalization isn't the same
                "case_sensitive": True,
            },
            "formatting": {
                # Determines if color should be part of the message; excludes log line
                "ansi": True,
                # If True, the One Dark theme will be applied to applicable data types (view Formatting > Only Highlight Data Structures)
                "highlighting": True,
                # If True, formats data structures with the Black formatter.
                "pretty_print": True,
                # Width to format syntax to. If 0, the width is set to the available space
                "fixed_format_width": 0,
            },
            "filtering": {
                "min_level": 0,  # The minimum log level to output; logs below this level are ignored. Can either be an integer, the level number, or a string, the level name
                # If a message contains any of the substrings in the list, it will not be logged
                "exclude_messages": [],
                # Only messages containing any of the substrings in the list will be logged; overridden by exclude_messages
                "include_only_messages": [],
            },
            "output": {
                "default_file_stream": None,  # Path to the log file
            },
            "metadata": {
                "show_metadata": False,  # Whether or not to show metadata
                "include_timestamp": False,  # If True, include the timestamp in metadata
                "include_level_name": False,  # If True, include the level name in metadata
                "include_thread_name": True,  # If True, include the thread name in metadata
                "include_file_name": False,  # If True, include the file name in metadata
                # If True, include the function that the called log method is inside of in metadata
                "include_wrapping_function": False,
                # If True, include the function name that was called in metadata
                "include_function": True,
                # If True, include the line number where the function was called in metadata
                "include_line_number": False,
                # If True, include the amount of values passed into the called function in metadata
                "include_value_count": True,
            },
            "log_line": {"format": "default"},
        }

        self.__rules: dict[str, any] = self.defaults.copy()
        if rules:
            for category, settings in rules.items():
                if category in self.__rules:
                    self.__rules[category].update(settings)
                else:
                    self.__rules[category] = settings

        self.ruleset = Ruleset(self.__rules)

        self.stream = Streams()

        # Add default stream (usually stdout)
        self.stream.normal.add(sys.stdout)

        if self.ruleset.output.default_file_stream:
            self.stream.file.add(self.ruleset.output.default_file_stream)

        self.__reset_timestamp()

        if self.ruleset.stacking.enabled:
            self.__log(
                "warning",
                "Stacking is currently not supported. You're seeing this message because you have the Stacking > Stacking Enabled rule set to True.",
            )
            self.__reset_timestamp()

    def __reset_timestamp(self) -> None:
        self.__previous_timestamp: str = None

    def __log(
        self,
        level: str,
        values: tuple,
        metadata: dict[str, any] = {},
        sep: str = "",
        pretty_print: bool = True,
    ) -> None:
        """Prints messages to the console. Lowest-level logging function.

        Args:
            level (str): The level to log at.
            values (tuple): The values to log.
            metadata (dict[str, any], optional): The metadata information to include in the log. Defaults to {}.
            sep (str, optional): The string that joins all values together. Defaults to "".
            pretty_print (bool, optional): Format with syntax highlighting and pprint.pformat(). Defaults to True.
        """

        ### CONDITIONS TO MEET ###

        if not metadata:
            # Retrieve the current frame
            frame = currentframe().f_back
            # Get the caller's function name and line number
            function_name = frame.f_code.co_name
            line_number = frame.f_lineno
            # Get the caller's module and file name
            module = getmodule(frame)
            file_name = frame.f_code.co_filename.split("/")[
                -1
            ]  # Extract file name from path
            value_count = len(values)

            metadata = {
                "module": module.__name__ if module else "",
                "function": function_name,
                "wrapping_func": frame.f_back.f_code.co_name if frame.f_back else "",
                "line_number": line_number,
                "file_name": file_name,
                "value_count": value_count,
            }

        min_level = self.ruleset.filtering.min_level
        try:
            current_level = self.__levels[level]["level"]
        except KeyError:
            self.__log("error", f"Level '{level}' does not exist.", metadata)
            return

        if self.__levels[level]["level"] != -1:
            if isinstance(min_level, str):
                if current_level < self.__levels[min_level]["level"]:
                    return
            else:
                if current_level < min_level:
                    return

        if any(
            sub in message.lower()
            for sub in [
                substring.lower()
                for substring in self.ruleset.filtering.exclude_messages
            ]
        ):
            return

        if self.ruleset.filtering.include_only_messages and not any(
            sub in message.lower()
            for sub in [
                substring.lower()
                for substring in self.ruleset.filtering.include_only_messages
            ]
        ):
            return

        ### MESSAGE ###

        terminal_width = tsize().columns

        context = {
            "timestamp": (self.__define_timestamp()),
            "filename": metadata.get("file_name", ""),
            "wrapfunc": metadata.get("wrapping_func", ""),
            "linenum": metadata.get("line_number", ""),
            "level": self.__levels[level]["name"],
        }

        te = TemplateEngine()
        log_line = te.process(self.ruleset.log_line.format, context, level)
        self.__message_space = terminal_width - te.processed.length
        self.__message_indent = te.processed.length

        self.__repr_id = "".join(
            choice("abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789")
            for _ in range(4)
        )
        message = sep.join(
            [
                (
                    self.__format_variable(value)
                    if pretty_print and isinstance(value, (list, dict, tuple))
                    else str(value)
                )
                for value in values
            ]
        )

        ### METADATA ###

        self.__log_metadata = ""

        if self.ruleset.metadata.show_metadata:
            message_length = (
                tsize().columns
                - te.processed.length
                - len(wrap(message, self.__message_space)[0])
            )

            if self.ruleset.metadata.include_timestamp:
                self.__log_metadata = (
                    if_space(
                        f"[tms: {self.__define_timestamp(no_blank=True)}]",
                        message_length - len(self.__log_metadata),
                    )
                    + self.__log_metadata
                )
            if self.ruleset.metadata.include_level_name:
                self.__log_metadata = (
                    if_space(
                        f"[lvl: {level}]", message_length - len(self.__log_metadata)
                    )
                    + self.__log_metadata
                )
            if self.ruleset.metadata.include_thread_name:
                self.__log_metadata = (
                    if_space(
                        f"[thr: {current_thread().name}]",
                        message_length - len(self.__log_metadata),
                    )
                    + self.__log_metadata
                )

            wrapping_func = metadata["wrapping_func"]
            function = metadata["function"]
            line_number = metadata["line_number"]
            file_name = metadata["file_name"]
            value_count = metadata["value_count"]

            if self.ruleset.metadata.include_file_name:
                self.__log_metadata = (
                    if_space(
                        f"[fl: {file_name}]", message_length - len(self.__log_metadata)
                    )
                    + self.__log_metadata
                )
            if self.ruleset.metadata.include_wrapping_function:
                self.__log_metadata = (
                    if_space(
                        f"[wfc: {wrapping_func}]",
                        message_length - len(self.__log_metadata),
                    )
                    + self.__log_metadata
                )
            if self.ruleset.metadata.include_function:
                self.__log_metadata = (
                    if_space(
                        f"[fnc: {function}]", message_length - len(self.__log_metadata)
                    )
                    + self.__log_metadata
                )
            if self.ruleset.metadata.include_line_number:
                self.__log_metadata = (
                    if_space(
                        f"[ln: {line_number}]",
                        message_length - len(self.__log_metadata),
                    )
                    + self.__log_metadata
                )
            if self.ruleset.metadata.include_value_count:
                self.__log_metadata = (
                    if_space(
                        f"[vlc: {value_count}]",
                        message_length - len(self.__log_metadata),
                    )
                    + self.__log_metadata
                )

            self.__log_metadata = (
                f"\033[0m\033[2m{self.__log_metadata.rjust(message_length)}\033[0m"
            )

        log_line += self.__log_metadata

        self.__previous_timestamp = datetime.now().strftime("%H:%M:%S")

        lines = wrap(message, self.__message_space)

        print(f"{log_line}\033[1A")
        log_output = StringIO()

        log_output.write(
            f"{log_line}{''.join([f'{self.__levels[level]["color"] if self.ruleset.formatting.ansi else ""}{line}\n' if i == 0 else f'\033[{self.__message_indent}C{self.__levels[level]["color"] if self.ruleset.formatting.ansi else ""}{line}\033[0m\n' for i, line in enumerate(lines)])}"
        )

        # Get the complete log message as a string
        log_message = log_output.getvalue()

        # Write to all output streams
        self.stream.normal.write(log_message)
        self.stream.file.write(log_message)

    def __format_variable(self, variable: list | dict) -> str:
        formatted_string = highlight(
            strip_repr_id(
                format_str(
                    str(strip_unsafe_objs(variable, self.__repr_id)),
                    mode=Mode(
                        line_length=(
                            self.ruleset.formatting.fixed_format_width
                            if self.ruleset.formatting.fixed_format_width > 0
                            else self.__message_space
                        )
                    ),
                ),
                self.__repr_id,
            ),
            PythonLexer(),
            tformatter(style=get_style_by_name("one-dark")),
        )
        if self.ruleset.formatting.ansi:
            return formatted_string
        else:
            return strip_ansi(formatted_string)

    def __define_timestamp(self, no_blank: bool = False) -> str:
        timestamp = datetime.now(
            datetime.UTC if self.ruleset.timestamps.use_utc else None
        ).strftime("%H:%M:%S")
        if no_blank:
            return timestamp
        if (
            datetime.now(
                datetime.UTC if self.ruleset.timestamps.use_utc else None
            ).strftime("%H:%M:%S")
            == self.__previous_timestamp
            and not self.ruleset.timestamps.always_show
        ):
            timestamp = f"\033[{len(datetime.now().strftime('%H:%M:%S'))}C"
        return timestamp

    # def __del__(self):
    #     """Cleanup method to close all file streams."""
    #     for file_stream in self.file_streams.values():
    #         file_stream.close()
