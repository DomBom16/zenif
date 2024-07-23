import datetime
import inspect
import os
import re
import shutil
import threading
import pprint
from pygments import highlight
from pygments.lexers import PythonLexer
from pygments.formatters import Terminal256Formatter
from pygments.styles import get_style_by_name
from colorama import Fore, Style, init

init(autoreset=True)


class FluxLogger:
    """The primary class of the fluxlog library. Provides various functions to print messages to the console."""

    def __init__(self, rules: dict = {}):
        self._previous_message: any = ""
        self._previous_level: str = None
        self._log_count: int = 0
        self._previous_message_length: int = 0
        self._log_metadata: str = None
        self._prompt_length: int = 0
        self._first_log: bool = True
        self._last_line_length: int = 0
        self._last_line_height: int = 0

        self._default_rules: dict = {
            "timestamps": {
                "always_show": False,  # If False, only prints the time changes
                "use_utc": False,  # If True, use UTC for timestamps; otherwise, use local time
                "format": "%Y-%m-%d %H:%M:%S",  # Format to log timestamps in
            },
            "stacking": {
                "stacking_enabled": True,  # If True, stacking is enabled; otherwise disabled
                # If False, messages will stack if if the capitalization isn't the same
                "case_sensitive": True,
            },
            "formatting": {
                "color_enabled": True,  # Determines if color should be part of the message, including the c_ log parameter
                "prefix": "",  # String to add to the beginning of the log
                "suffix": "",  # String to add to the end of the log
                # If enabled, you can use predefined and custom placeholders using the .[placeholder] syntax in your messages
                "enable_placeholders": False,
            },
            "filtering": {
                "min_level": 0,  # The minimum log level to output; logs below this level are ignored. Can either be an integer, the level number, or a string, the level name
                # If a message contains any of the substrings in the list, it will not be logged
                "exclude_messages": [],
                # Only messages containing any of the substrings in the list will be logged; overridden by exclude_messages
                "include_only_messages": [],
            },
            "output": {
                "output_to_file": False,  # If True, logs are written to a file specified by file_path
                "file_path": "log.txt",  # Path to the log file
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
            "log_line": {
                "format": f".[tms] .[fl](>_85).[wfc](T_,W_<module>_< module >,L_,P_:,>_85).[wfc](T_,W_<module>_< module >,R_,<_85,>_75).[ln](L_3,P_:) .[lvl](L_{9 if shutil.get_terminal_size().columns > 75 else 4})"
                # Format of line prompt info. The log message and metadata information (if Metadata > Show Metadata is set to True) will always be included at the end of the log line. The message and metadata segments are not editable until further notice.
                # Below are all () parameters that you can apply to .[] placeholders.
                # Parameters are applied in the order their listed, so L,T_P_x is different than T_P_x,L
                # Z, zero-pad:              Z_<width:int=10>
                # L, left align:            L_<width:int=10>_<fillchar:str=' '>
                # R, right align:           R_<width:int=10>_<fillchar:str=' '>
                # C, center align:          C_<width:int=10>_<fillchar:str=' '>
                # u, uppercase:             u_
                # l, lowercase:             l_
                # X, exclude:               X_<exclude:str=''>
                # I, include:               I_<include:str=''>
                # W, when:                  W_<condition:str=''>_<replace:str=''>
                # P, prefix:                P_<prefix:str=''>
                # S, suffix:                S_<suffix:str=''>
                # >, show when > than:      >_<terminal_width:int=75>
                # <, show when <= than:     <_<terminal_width:int=75>
                # T, truncate:              T_<width:int=10>_<ending:str='…'>
                # c, color:                 c_<RED|YELLOW|GREEN|CYAN|BLUE|MAGENTA|BLACK|WHITE=WHITE>
                # AB*DEFGH*JK*MNO*Q***UV**Y*ab*defghjik*mnopqrst*vwxyz
            },
        }

        self.levels = {
            "debug": {
                "name": {"display": "debug", "short": "dbg"},
                "level": 1,
                "color": Fore.BLUE,
            },
            "info": {
                "name": {"display": "info", "short": "inf"},
                "level": 0,
                "color": Fore.WHITE,
            },
            "success": {
                "name": {"display": "success", "short": "scs"},
                "level": 2,
                "color": Fore.GREEN,
            },
            "warning": {
                "name": {"display": "warning", "short": "wrn"},
                "level": 3,
                "color": Fore.YELLOW,
            },
            "error": {
                "name": {"display": "error", "short": "err"},
                "level": 4,
                "color": Fore.RED,
            },
            "critical": {
                "name": {"display": "critical", "short": "crt"},
                "level": -1,
                "color": Fore.MAGENTA,
            },
        }

        self.rules: dict = self._default_rules.copy()
        if rules:
            for category, settings in rules.items():
                if category in self.rules:
                    self.rules[category].update(settings)
                else:
                    self.rules[category] = settings

        for category, settings in self.rules.items():
            setattr(self, f"rs_{category}", settings)

        self.__reset_timestamp()

        if self.rs_formatting["enable_placeholders"]:
            self.__log(
                "warning",
                "Placeholders are currently not supported. You're seeing this message because you have the Formatting > Enable Placeholders rule set to True.",
            )
            self.__reset_timestamp()

    def __reset_timestamp(self):
        self._blank_timestamp: str = (
            f"\033[{
            len(datetime.datetime.now().strftime(self.rs_timestamps["format"]))}C"
        )
        self._previous_timestamp: str = None

    def __log(
        self,
        level: str,
        values: tuple,
        metadata: dict = {},
        sep: str = "",
        pretty_print: bool = True,
    ):
        ### CONDITIONS TO MEET ###

        if not metadata:
            # Retrieve the current frame
            frame = inspect.currentframe().f_back
            # Get the caller's function name and line number
            function_name = frame.f_code.co_name
            line_number = frame.f_lineno
            # Get the caller's module and file name
            module = inspect.getmodule(frame)
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

        min_level = self.rs_filtering["min_level"]
        try:
            current_level = self.levels[level]["level"]
        except KeyError:
            self.__log("error", f"Level '{level}' does not exist.", metadata)
            return

        if self.levels[level]["level"] != -1:
            if isinstance(min_level, str):
                if current_level < self.levels[min_level]["level"]:
                    return
            else:
                if current_level < min_level:
                    return

        if any(
            sub in message.lower()
            for sub in [
                substring.lower() for substring in self.rs_filtering["exclude_messages"]
            ]
        ):
            return

        if self.rs_filtering["include_only_messages"] and not any(
            sub in message.lower()
            for sub in [
                substring.lower()
                for substring in self.rs_filtering["include_only_messages"]
            ]
        ):
            return

        ### MESSAGE ###

        terminal_width = shutil.get_terminal_size().columns

        context = {
            "tms": (
                self.__define_timestamp()
                if terminal_width > 75
                else self.__define_timestamp(format="%H:%M:%S")
            ),
            "fl": metadata.get("file_name", "") if terminal_width > 85 else "",
            "wfc": metadata.get("wrapping_func", "") if terminal_width > 75 else "",
            "ln": metadata.get("line_number", ""),
            "lvl": (
                self.levels[level]["name"]["display"].upper()
                if terminal_width > 75
                else self.levels[level]["name"]["short"][:3].upper()
            ),
        }

        log_line_format = self.rs_log_line["format"]
        log_line = self.__parse_placeholders(log_line_format, context, level)
        self._message_space = terminal_width - self._prompt_length
        self._message_indent = self._prompt_length

        # message = sep.join([pprint.pformat(value, indent=1, width=self._message_space) if pretty_print else str(value) for value in values])
        message = sep.join(
            [
                (self.__format_variable(value) if pretty_print else str(value))
                for value in values
            ]
        )

        ### METADATA ###

        self._log_metadata = ""

        if self.rs_metadata["show_metadata"]:
            message_length = shutil.get_terminal_size().columns - len(
                self.__remove_ansi(
                    log_line.replace(
                        context["tms"], self.__define_timestamp(no_blank=True)
                    )
                )
            )

            if self.rs_metadata["include_timestamp"]:
                self._log_metadata = (
                    self.__define_m_widget(
                        f"[tms: {self.__define_timestamp(
                    no_blank=True)}]",
                        message_length - len(self._log_metadata),
                    )
                    + self._log_metadata
                )
            if self.rs_metadata["include_level_name"]:
                self._log_metadata = (
                    self.__define_m_widget(
                        f"[lvl: {level}]", message_length - len(self._log_metadata)
                    )
                    + self._log_metadata
                )
            if self.rs_metadata["include_thread_name"]:
                self._log_metadata = (
                    self.__define_m_widget(
                        f"[thr: {threading.current_thread().name}]",
                        message_length - len(self._log_metadata),
                    )
                    + self._log_metadata
                )

            wrapping_func = metadata["wrapping_func"]
            function = metadata["function"]
            line_number = metadata["line_number"]
            file_name = metadata["file_name"]
            value_count = metadata["value_count"]

            if self.rs_metadata["include_file_name"]:
                self._log_metadata = (
                    self.__define_m_widget(
                        f"[fl: {file_name}]", message_length - len(self._log_metadata)
                    )
                    + self._log_metadata
                )
            if self.rs_metadata["include_wrapping_function"]:
                self._log_metadata = (
                    self.__define_m_widget(
                        f"[wfc: {wrapping_func}]",
                        message_length - len(self._log_metadata),
                    )
                    + self._log_metadata
                )
            if self.rs_metadata["include_function"]:
                self._log_metadata = (
                    self.__define_m_widget(
                        f"[fnc: {function}]", message_length - len(self._log_metadata)
                    )
                    + self._log_metadata
                )
            if self.rs_metadata["include_line_number"]:
                self._log_metadata = (
                    self.__define_m_widget(
                        f"[ln: {line_number}]", message_length - len(self._log_metadata)
                    )
                    + self._log_metadata
                )
            if self.rs_metadata["include_value_count"]:
                self._log_metadata = (
                    self.__define_m_widget(
                        f"[vlc: {value_count}]",
                        message_length - len(self._log_metadata),
                    )
                    + self._log_metadata
                )

            self._log_metadata = f"{Style.RESET_ALL}{Style.DIM}{
                self._log_metadata.rjust(message_length)}"

        log_line += self._log_metadata

        ### STACKING CONDITIONALS & self._previous_... VARIABLES & LOGGING ###

        if (
            f"{message if self.rs_stacking["case_sensitive"] else message.lower()}"
            == f"{
                self._previous_message if self.rs_stacking["case_sensitive"] else self._previous_message.lower()}"
            and level.lower() != "critical"
            and level.lower() == self._previous_level
            and self.rs_stacking["stacking_enabled"]
        ):
            self._log_count += 1
        else:
            self._log_count = 1

            self._previous_message = message
            self._previous_level = level.lower()
            self._previous_timestamp = datetime.datetime.now().strftime(
                self.rs_timestamps["format"]
            )

            lines = self.__wrap_text(message, self._message_space)
            self._last_line_height = len(lines)
            self._last_line_length = len(lines[-1])

            print(f"{log_line}\033[1A")
            for line in lines:
                print(
                    f"\033[{self._message_indent}C{self.levels[level]["color"] if self.rs_formatting["color_enabled"] else ""}{line}"
                )

    def __close(self) -> None:
        terminal_width = shutil.get_terminal_size().columns
        timestamp = (
            self.__define_timestamp()
            if terminal_width > 75
            else self.__define_timestamp(format="%H:%M:%S")
        )
        self._previous_timestamp = datetime.datetime.now().strftime(
            self.rs_timestamps["format"]
        )

        if self._previous_message is not None and self._log_count > 1:
            print(
                f"\033[{self._last_line_height}A{Fore.GREEN}{timestamp}{Style.RESET_ALL}\033[{self._last_line_height - 1}B\033[{self._last_line_length}C {Style.DIM}{Fore.WHITE}(x{self._log_count}){Style.RESET_ALL}"
            )

    def __format_variable(self, variable) -> str:

        # Highlight the formatted string
        style = get_style_by_name("one-dark")

        print([pprint.pformat(variable, width=self._message_space)])

        highlighted_str = highlight(
            pprint.pformat(variable, width=self._message_space),
            PythonLexer(),
            Terminal256Formatter(style=style),
        )

        return highlighted_str.rstrip()

    def __wrap_text(self, text, width):
        ansi_escape = re.compile(r"\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])")

        result = []

        def visible_length(s):
            return len(ansi_escape.sub("", s))

        lines = text.split("\n")
        print(f"Number of lines: {len(lines)}")  # Debug print

        for line_num, line in enumerate(lines, 1):
            print(f"Processing line {line_num}: {repr(line)}")  # Debug print
            current_line = ""
            current_line_visible_length = 0
            words = re.findall(r"\S+\s*", line)

            for word in words:
                word_visible_length = visible_length(word)

                if current_line_visible_length + word_visible_length > width:
                    if current_line:
                        result.append(current_line.rstrip())
                        print(
                            f"Added to result: {repr(current_line.rstrip())}"
                        )  # Debug print
                    current_line = ""
                    current_line_visible_length = 0

                current_line += word
                current_line_visible_length += word_visible_length

            if current_line:
                result.append(current_line.rstrip())
                print(f"Added to result: {repr(current_line.rstrip())}")  # Debug print

        return result

    def __parse_placeholders(self, format_str, context, level):

        def get_parts(param, defaults, split_char="_"):
            parts = param.split(split_char, len(defaults) - 1)
            return [
                parts[i] if i < len(parts) else defaults[i]
                for i in range(len(defaults))
            ]

        def to_str(value, default, param_name):
            try:
                return str(value or default)
            except:
                # self._log("warning", f"The {param_name} parameter couldn't be properly applied because the value couldn't be converted to a string.")
                print(
                    f"The {param_name} parameter couldn't be properly applied because the values of one of it's options couldn't be converted to an string. Instead, {default} will be supplied."
                )
                return default

        def to_int(value, default, param_name):
            try:
                return int(value or default)
            except:
                # self._log("warning", f"The {param_name} parameter couldn't be properly applied because the value couldn't be converted to an integer.")
                print(
                    f"The {param_name} parameter couldn't be properly applied because the values of one of it's options couldn't be converted to an integer. Instead, {default} will be supplied."
                )
                return default

        def apply_parameters(value, parameters):
            original_value = value
            stripped_value = self.__remove_ansi(value)

            terminal_width = shutil.get_terminal_size().columns
            default_pad_length = 10

            color = None

            for param in parameters:

                if param.startswith("Z_"):
                    pad_length = (
                        to_int(param[2:], default_pad_length, param)
                        if len(param) > 2
                        else default_pad_length
                    )
                    stripped_value = stripped_value.zfill(pad_length)

                elif param.startswith("L_"):
                    defaults = [default_pad_length, " "]
                    parts = get_parts(param[2:], defaults)
                    pad_length = to_int(parts[0], defaults[0], param)
                    fillchar = to_str(parts[1], defaults[1], param)
                    stripped_value = stripped_value.ljust(pad_length, fillchar)

                elif param.startswith("R_"):
                    defaults = [default_pad_length, " "]
                    parts = get_parts(param[2:], defaults)
                    pad_length = to_int(parts[0], defaults[0], param)
                    fillchar = to_str(parts[1], defaults[1], param)
                    stripped_value = stripped_value.rjust(pad_length, fillchar)

                elif param.startswith("C_") and not param.startswith("COLOR"):
                    defaults = [default_pad_length, " "]
                    parts = get_parts(param[2:], defaults)
                    pad_length = to_int(parts[0], defaults[0], param)
                    fillchar = to_str(parts[1], defaults[1], param)[0]
                    stripped_value = stripped_value.center(pad_length, fillchar)

                elif param == "u_":
                    stripped_value = stripped_value.upper()

                elif param == "l_":
                    stripped_value = stripped_value.lower()

                elif param.startswith("X_"):
                    exclude = to_str(param[2:], "", param) if len(param) > 2 else ""
                    if exclude in stripped_value:
                        stripped_value = ""

                elif param.startswith("I_"):
                    include = to_str(param[2:], "", param) if len(param) > 2 else ""
                    if include not in stripped_value:
                        stripped_value = ""

                elif param.startswith("W_"):
                    defaults = ["", ""]
                    parts = get_parts(param[2:], defaults)
                    when = to_str(parts[0], defaults[0], param)
                    show = to_str(parts[1], defaults[1], param)
                    if when in stripped_value:
                        stripped_value = show

                elif param.startswith("P_"):
                    prefix = to_str(param[2:], "", param) if len(param) > 2 else ""
                    stripped_value = prefix + stripped_value

                elif param.startswith("S_"):
                    suffix = to_str(param[2:], "", param) if len(param) > 2 else ""
                    stripped_value += suffix

                elif param.startswith(">_"):
                    width = to_int(param[2:], 75, param) if len(param) > 2 else 75
                    if width >= terminal_width:
                        stripped_value = ""

                elif param.startswith("<_"):
                    width = to_int(param[2:], 75, param) if len(param) > 2 else 75
                    if width < terminal_width:
                        stripped_value = ""

                elif param.startswith("T_"):
                    defaults = [10, "…"]
                    parts = get_parts(param[2:], defaults)

                    width = to_int(parts[0], defaults[0], param)
                    ending = to_str(parts[1], defaults[1], param)

                    stripped_value = (
                        stripped_value[: (width - len(ending))] + ending
                        if len(stripped_value) > width
                        else stripped_value
                    )

                elif param.startswith("c_") and self.rs_formatting["color_enabled"]:
                    color = param.split("_", 1)[1]

            if original_value == context.get("tms", ""):
                self._prompt_length += len(
                    str(
                        self.__define_timestamp(no_blank=True)
                        if terminal_width > 75
                        else self.__define_timestamp(format="%H:%M:%S", no_blank=True)
                    )
                )
            else:
                self._prompt_length += len(str(stripped_value))

            if color:
                stripped_value = f"{color}{stripped_value}{Style.RESET_ALL}"

            recolored_value = ""
            stripped_index = 0

            ansi_escape = re.compile(r"(?:\033[@-_][0-?]*[ -/]*[@-~])")
            for match in ansi_escape.finditer(original_value):
                start, end = match.span()
                recolored_value += stripped_value[
                    stripped_index : start - stripped_index
                ]
                recolored_value += original_value[start:end]
                stripped_index += start - stripped_index

            recolored_value += stripped_value[stripped_index:]

            return recolored_value

        def placeholder_replacer(match):
            placeholder = match.group(1)
            parameters = match.group(2).strip("()").split(",") if match.group(2) else []

            if placeholder == "ln" and not any(
                parameter.startswith("L_") for parameter in parameters
            ):
                parameters.append("L_3")

            value = context.get(placeholder, "")

            # BLACK, RED, GREEN, YELLOW, BLUE, MAGENTA, CYAN, WHITE

            c_map = {
                "BLACK": Fore.BLACK,
                "RED": Fore.RED,
                "GREEN": Fore.GREEN,
                "YELLOW": Fore.YELLOW,
                "BLUE": Fore.BLUE,
                "MAGENTA": Fore.MAGENTA,
                "CYAN": Fore.CYAN,
                "WHITE": Fore.WHITE,
            }

            for parameter in range(len(parameters)):
                if parameters[parameter].startswith("c_"):
                    parameters[parameter] = (
                        f"c_{c_map[parameters[parameter][2:] or -1]}"
                    )

            # Apply color based on the placeholder and level
            c_lvl_map = {
                "tms": Fore.GREEN,
                "fl": Fore.MAGENTA,
                "wfc": Fore.YELLOW,
                "ln": Fore.CYAN,
                "lvl": self.levels[level]["color"],
            }
            color = c_lvl_map.get(placeholder, "")
            if (
                color
                and not any(parameter.startswith("c_") for parameter in parameters)
                and self.rs_formatting["color_enabled"]
            ):
                parameters.append(f"c_{color}")

            return apply_parameters(str(value), parameters)

        placeholder_pattern = re.compile(r"\.\[([a-zA-Z0-9_]+)\](?:\((.*?)\))?")

        # Regex to match everything except placeholders
        inverse_pattern = re.compile(r"((?:\.\[[a-zA-Z0-9_]+\](?:\(.*?\))?)|.)+?")

        # Count unmatched characters
        self._prompt_length = sum(
            len(match.group())
            for match in inverse_pattern.finditer(str(format_str))
            if not placeholder_pattern.match(match.group())
        )

        return placeholder_pattern.sub(placeholder_replacer, str(format_str))

    # helper functions

    def __remove_ansi(self, text):
        ansi_escape = re.compile(r"\033[@-_][0-?]*[ -/]*[@-~]")
        return ansi_escape.sub("", text)

    def __define_m_widget(self, content: str, space: int = 0) -> str:
        return content if space >= len(content) else ""

    def __define_timestamp(self, no_blank: bool = False, format: str = None) -> str:
        timestamp = datetime.datetime.now(
            datetime.UTC if self.rs_timestamps["use_utc"] else None
        ).strftime(format or self.rs_timestamps["format"])
        if no_blank:
            return timestamp
        if (
            timestamp == self._previous_timestamp
            and not self.rs_timestamps["always_show"]
        ):
            timestamp = self._blank_timestamp
        return timestamp

    def __log_method(self, values, level, sep, pretty_print):
        # Get current frame
        frame = inspect.currentframe()
        # Get the caller's frame
        caller_frame = frame.f_back

        module = caller_frame.f_globals["__name__"]
        function = caller_frame.f_code.co_name
        wrapping_func = caller_frame.f_back.f_code.co_name
        line_number = caller_frame.f_lineno
        file_name = os.path.basename(caller_frame.f_code.co_filename)

        metadata = {
            "module": module,
            "function": function,
            "wrapping_func": wrapping_func,
            "line_number": line_number,
            "file_name": file_name,
            "value_count": len(values),
        }

        self.__log(
            level=level,
            values=values,
            metadata=metadata,
            sep=sep,
            pretty_print=pretty_print,
        )
        self.__close()

    def info(self, *values, sep: str = " ", rich: bool = True):
        """Logs the given values to the console with an "info" level.

        Args:
            sep (str, optional): String inserted between values. Defaults to " "
            rich (bool, optional): Format values for easier readability with syntax highlighting. Defaults to True
        """
        rich = (
            False
            if (
                all(isinstance(value, (str, int)) for value in values)
                and len(values) == 1
            )
            or sep not in ["", " "]
            else rich
        )
        self.__log_method(
            values=values,
            level=self.levels["info"]["name"]["display"],
            sep=sep,
            pretty_print=rich,
        )

    def debug(self, *values, sep: str = " ", rich: bool = True):
        """Logs the given values to the console with a "debug" level.

        Args:
            sep (str, optional): String inserted between values. Defaults to " "
            rich (bool, optional): Format values for easier readability with syntax highlighting. Defaults to True
        """
        rich = (
            False
            if (
                all(isinstance(value, (str, int)) for value in values)
                and len(values) == 1
            )
            or sep not in ["", " "]
            else rich
        )
        self.__log_method(
            values=values,
            level=self.levels["debug"]["name"]["display"],
            sep=sep,
            pretty_print=rich,
        )

    def success(self, *values, sep: str = " ", rich: bool = True):
        """Logs the given values to the console with a "success" level.

        Args:
            sep (str, optional): String inserted between values. Defaults to " "
            rich (bool, optional): Format values for easier readability with syntax highlighting. Defaults to True
        """
        rich = (
            False
            if (
                all(isinstance(value, (str, int)) for value in values)
                and len(values) == 1
            )
            or sep not in ["", " "]
            else rich
        )
        self.__log_method(
            values=values,
            level=self.levels["success"]["name"]["display"],
            sep=sep,
            pretty_print=rich,
        )

    def warning(self, *values, sep: str = " ", rich: bool = True):
        """Logs the given values to the console with a "warning" level.

        Args:
            sep (str, optional): String inserted between values. Defaults to " "
            rich (bool, optional): Format values for easier readability with syntax highlighting. Defaults to True
        """
        rich = (
            False
            if (
                all(isinstance(value, (str, int)) for value in values)
                and len(values) == 1
            )
            or sep not in ["", " "]
            else rich
        )
        self.__log_method(
            values=values,
            level=self.levels["warning"]["name"]["display"],
            sep=sep,
            pretty_print=rich,
        )

    def error(self, *values, sep: str = " ", rich: bool = True):
        """Logs the given values to the console with an "error" level.

        Args:
            sep (str, optional): String inserted between values. Defaults to " "
            rich (bool, optional): Format values for easier readability with syntax highlighting. Defaults to True
        """
        rich = (
            False
            if (
                all(isinstance(value, (str, int)) for value in values)
                and len(values) == 1
            )
            or sep not in ["", " "]
            else rich
        )
        self.__log_method(
            values=values,
            level=self.levels["error"]["name"]["display"],
            sep=sep,
            pretty_print=rich,
        )

    def critical(self, *values, sep: str = " ", rich: bool = True):
        """Logs the given values to the console with a "critical" level.

        Args:
            sep (str, optional): String inserted between values. Defaults to " "
            rich (bool, optional): Format values for easier readability with syntax highlighting. Defaults to True
        """
        rich = (
            False
            if (
                all(isinstance(value, (str, int)) for value in values)
                and len(values) == 1
            )
            or sep not in ["", " "]
            else rich
        )
        self.__log_method(
            values=values,
            level=self.levels["critical"]["name"]["display"],
            sep=sep,
            pretty_print=rich,
        )
