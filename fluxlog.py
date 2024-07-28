import datetime
import inspect
import os
import re
import shutil
import threading
import random
import string
import black
from pygments import highlight
from pygments.lexers import PythonLexer
from pygments.formatters import Terminal256Formatter
from pygments.styles import get_style_by_name
from colorama import Fore, Back, Style, init
from copy import deepcopy

init(autoreset=True)


class FluxLogger:

    def __init__(self, rules: dict = {}):
        """A class used to log messages with granular customizability.

        Args:
            rules (dict, optional): A ruleset that overrides the default rules. To view the default rules, view FluxLogger().defaults. Defaults to {}.
        """

        self.__previous_message: any = ""
        self.__previous_level: str = None
        self.__log_count: int = 0
        self.__log_metadata: str = None
        self.__prompt_length: int = 0
        self.__last_line_length: int = 0
        self.__last_line_height: int = 0
        self.__repr_id: str = ""

        self.defaults: dict = {
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
                "highlighting_enabled": True,  # If True, the One Dark theme will be applied to applicable data types (view Formatting > Only Highlight Data Structures)
                "only_highlight_data_structures": True,  # If True, only lists, dictionaries, tuples, and other objects are highlighted
                "formatting_enabled": True,  # If True, formats data structures with the Black formatter.
                "prefix": "",  # String to add to the beginning of the log
                "suffix": "",  # String to add to the end of the log
                # If enabled, you can use predefined and custom placeholders using the .[placeholder] syntax in your messages
                "placeholders_enabled": False,
                "fixed_format_width": 0,  # Width to format syntax to. If 0, the width is set to the available space
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
                "format": [
                    {
                        "type": "template",
                        "value": "timestamp",
                        "parameters": [
                            {"color": {"foreground": "dynamic"}},
                        ],
                    },
                    {"type": "static", "value": " "},
                    {
                        "type": "template",
                        "value": "filename",
                        "parameters": [
                            {"color": {"foreground": "dynamic"}},
                            {
                                "visible": ">95",
                            },
                            {
                                "filter": {
                                    "items": ["fluxlog.py"],
                                    "replace": "internal",
                                }
                            },
                            {"align": {"alignment": "right"}},
                        ],
                    },
                    {
                        "type": "template",
                        "value": "wrapfunc",
                        "parameters": [
                            {"color": {"foreground": "dynamic"}},
                            {
                                "visible": False,
                            },
                            {
                                "truncate": {},
                            },
                            {
                                "filter": {
                                    "items": ["<module>"],
                                    "replace": "< module >",
                                },
                            },
                            {"visible": ">75"},
                            {
                                "if": {
                                    "condition": {
                                        "type": "breakpoint",
                                        "value": {"min": 95},
                                    },
                                    "action": {
                                        "type": "parameters",
                                        "value": {
                                            "align": {"alignment": "left"},
                                            "affix": {"prefix": ":"},
                                        },
                                    },
                                },
                            },
                            {
                                "if": {
                                    "condition": {
                                        "type": "breakpoint",
                                        "value": {"max": 95, "min": 75},
                                    },
                                    "action": {
                                        "type": "parameters",
                                        "value": {
                                            "truncate": {},
                                            "align": {"alignment": "right"},
                                        },
                                    },
                                },
                            },
                        ],
                    },
                    {
                        "type": "template",
                        "value": "linenum",
                        "parameters": [
                            {"color": {"foreground": "dynamic"}},
                            {"affix": {"prefix": Style.NORMAL}},
                            {
                                "if": {
                                    "condition": {
                                        "type": "breakpoint",
                                        "value": {"max": 75},
                                    },
                                    "action": {
                                        "type": "parameters",
                                        "value": {
                                            "align": {
                                                "alignment": "right",
                                                "width": 3,
                                                "fillchar": "⋅",
                                            },
                                            "affix": {"prefix": Style.DIM},
                                        },
                                    },
                                }
                            },
                            {
                                "if": {
                                    "condition": {
                                        "type": "breakpoint",
                                        "value": {"min": 75},
                                    },
                                    "action": {
                                        "type": "parameters",
                                        "value": {
                                            "align": {
                                                "alignment": "left",
                                                "width": 3,
                                                "fillchar": " ",
                                            },
                                            "affix": {"prefix": ":"},
                                        },
                                    },
                                }
                            },
                        ],
                    },
                    {"type": "static", "value": " "},
                    {
                        "type": "template",
                        "value": "level",
                        "parameters": [
                            {"color": {"foreground": "dynamic"}},
                            {
                                "align": {
                                    "alignment": "left",
                                    "width": 9,
                                },
                            },
                        ],
                    },
                ],
                # Format of line prompt info. The log message and metadata information (if Metadata > Show Metadata is set to True) will always be included at the end of the log line. The message and metadata segments are not editable until further notice.
                # Below are all () parameters that you can apply to .[] placeholders.
                # Parameters are applied in the order their listed, so left pad then prefix is different than prefix then left pad.
                # align:
                #   left align:            L_<width:int=10>_<fillchar:str=' '>
                #   right align:           R_<width:int=10>_<fillchar:str=' '>
                #   center align:          C_<width:int=10>_<fillchar:str=' '>
                # case:
                #   uppercase:             u_
                #   lowercase:             l_
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

        self.__levels = {
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

        self.rules: dict = self.defaults.copy()
        if rules:
            for category, settings in rules.items():
                if category in self.rules:
                    self.rules[category].update(settings)
                else:
                    self.rules[category] = settings

        for category, settings in self.rules.items():
            setattr(self, f"rs_{category}", settings)

        self.__reset_timestamp()

        if self.rs_formatting["placeholders_enabled"]:
            self.__log(
                "warning",
                "Placeholders are currently not supported. You're seeing this message because you have the Formatting > Placeholders Enabled rule set to True.",
            )
            self.__reset_timestamp()

        if self.rs_stacking["stacking_enabled"]:
            self.__log(
                "warning",
                "Stacking is currently not supported. You're seeing this message because you have the Stacking > Stacking Enabled rule set to True.",
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
        """Prints messages to the console. Lowest-level logging function.

        Args:
            level (str): The level to log at.
            values (tuple): The values to log.
            metadata (dict, optional): The metadata information to include in the log. Defaults to {}.
            sep (str, optional): The string that joins all values together. Defaults to "".
            pretty_print (bool, optional): Format with syntax highlighting and pprint.pformat(). Defaults to True.
        """

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
            "timestamp": (
                self.__define_timestamp()
                if terminal_width > 85
                else self.__define_timestamp(format="%H:%M:%S")
            ),
            "filename": metadata.get("file_name", ""),
            "wrapfunc": metadata.get("wrapping_func", ""),
            "linenum": metadata.get("line_number", ""),
            "level": (self.__levels[level]["name"]["display"].upper()),
        }

        log_line = self.__parse_log_line(context, level)
        self._message_space = terminal_width - self.__prompt_length
        self._message_indent = self.__prompt_length

        self.__repr_id = "".join(
            random.choice(string.ascii_letters + string.digits) for _ in range(4)
        )
        message = sep.join(
            [
                (
                    self.__format_variable(value)
                    if pretty_print and not isinstance(value, (str, int, float))
                    else str(value)
                )
                for value in values
            ]
        )

        ### METADATA ###

        self.__log_metadata = ""

        if self.rs_metadata["show_metadata"]:
            message_length = shutil.get_terminal_size().columns - len(
                self.__remove_ansi(
                    log_line.replace(
                        context["tms"], self.__define_timestamp(no_blank=True)
                    )
                )
            )

            if self.rs_metadata["include_timestamp"]:
                self.__log_metadata = (
                    self.__define_m_widget(
                        f"[tms: {self.__define_timestamp(
                    no_blank=True)}]",
                        message_length - len(self.__log_metadata),
                    )
                    + self.__log_metadata
                )
            if self.rs_metadata["include_level_name"]:
                self.__log_metadata = (
                    self.__define_m_widget(
                        f"[lvl: {level}]", message_length - len(self.__log_metadata)
                    )
                    + self.__log_metadata
                )
            if self.rs_metadata["include_thread_name"]:
                self.__log_metadata = (
                    self.__define_m_widget(
                        f"[thr: {threading.current_thread().name}]",
                        message_length - len(self.__log_metadata),
                    )
                    + self.__log_metadata
                )

            wrapping_func = metadata["wrapping_func"]
            function = metadata["function"]
            line_number = metadata["line_number"]
            file_name = metadata["file_name"]
            value_count = metadata["value_count"]

            if self.rs_metadata["include_file_name"]:
                self.__log_metadata = (
                    self.__define_m_widget(
                        f"[fl: {file_name}]", message_length - len(self.__log_metadata)
                    )
                    + self.__log_metadata
                )
            if self.rs_metadata["include_wrapping_function"]:
                self.__log_metadata = (
                    self.__define_m_widget(
                        f"[wfc: {wrapping_func}]",
                        message_length - len(self.__log_metadata),
                    )
                    + self.__log_metadata
                )
            if self.rs_metadata["include_function"]:
                self.__log_metadata = (
                    self.__define_m_widget(
                        f"[fnc: {function}]", message_length - len(self.__log_metadata)
                    )
                    + self.__log_metadata
                )
            if self.rs_metadata["include_line_number"]:
                self.__log_metadata = (
                    self.__define_m_widget(
                        f"[ln: {line_number}]",
                        message_length - len(self.__log_metadata),
                    )
                    + self.__log_metadata
                )
            if self.rs_metadata["include_value_count"]:
                self.__log_metadata = (
                    self.__define_m_widget(
                        f"[vlc: {value_count}]",
                        message_length - len(self.__log_metadata),
                    )
                    + self.__log_metadata
                )

            self.__log_metadata = f"{Style.RESET_ALL}{Style.DIM}{
                self.__log_metadata.rjust(message_length)}"

        log_line += self.__log_metadata

        ### STACKING CONDITIONALS & self._previous_... VARIABLES & LOGGING ###

        # if (
        #     f"{message if self.rs_stacking["case_sensitive"] else message.lower()}"
        #     == f"{
        #         self.__previous_message if self.rs_stacking["case_sensitive"] else self.__previous_message.lower()}"
        #     and level.lower() != "critical"
        #     and level.lower() == self.__previous_level
        #     and self.rs_stacking["stacking_enabled"]
        # ):
        #     self.__log_count += 1
        # else:
        self.__log_count = 1

        self.__previous_message = message
        self.__previous_level = level.lower()
        self._previous_timestamp = datetime.datetime.now().strftime(
            self.rs_timestamps["format"]
        )

        lines = self.__wrap_text(message, self._message_space)
        self.__last_line_height = len(lines)
        self.__last_line_length = len(lines[-1])

        print(f"{log_line}\033[1A")
        for line in lines:
            print(
                f"\033[{self._message_indent}C{self.__levels[level]["color"] if self.rs_formatting["color_enabled"] else ""}{line}"
            )

    def __close(self) -> None:
        terminal_width = shutil.get_terminal_size().columns
        timestamp = (
            self.__define_timestamp()
            if terminal_width > 85
            else self.__define_timestamp(format="%H:%M:%S")
        )
        self._previous_timestamp = self.__define_timestamp(no_blank=True)

        if self.__previous_message is not None and self.__log_count > 1:
            # print(
            #     f"\033[{self.__last_line_height}A{Fore.GREEN}{timestamp}{Style.RESET_ALL}\033[{self.__last_line_height - 1}B\033[{self.__last_line_length}C {Style.DIM}{Fore.WHITE}(x{self.__log_count}){Style.RESET_ALL}"
            # )
            pass

    def __sanitize_unsafe_objects(self, variable):
        if isinstance(variable, (str, int, float, bool)):
            return variable
        elif isinstance(variable, list):
            return [self.__sanitize_unsafe_objects(item) for item in variable]
        elif isinstance(variable, dict):
            return {
                key: self.__sanitize_unsafe_objects(value)
                for key, value in variable.items()
            }
        elif isinstance(variable, tuple):
            return tuple(self.__sanitize_unsafe_objects(item) for item in variable)
        else:
            return f"{self.__repr_id}{repr(variable)}"

    def __format_variable(self, variable) -> str:

        # Highlight the formatted string
        style = get_style_by_name("one-dark")

        highlighted_str = highlight(
            re.sub(
                rf'"{self.__repr_id}(.*?)"',
                r"\1",
                re.sub(
                    rf"'{self.__repr_id}(.*?)'",
                    r"\1",
                    black.format_str(
                        str(self.__sanitize_unsafe_objects(variable)),
                        mode=black.Mode(line_length=self._message_space),
                    ),
                ),
            ),
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

        for line in lines:
            current_line = ""
            current_line_visible_length = 0
            words = re.findall(r"\S+\s*", line)

            for word in words:
                word_visible_length = visible_length(word)

                if current_line_visible_length + word_visible_length > width:
                    if current_line:
                        result.append(current_line.rstrip())
                    current_line = ""
                    current_line_visible_length = 0

                current_line += word
                current_line_visible_length += word_visible_length

            if current_line:
                result.append(current_line.rstrip())

        return result

    def __parse_log_line(self, context, level):

        def return_values(value, default):
            if type(value) != type(default):
                raise Exception(f"Value {value} must be type {type(default)}.")
            if isinstance(value, dict):
                for dk, dv in default.items():
                    value.setdefault(dk, dv)
            if isinstance(value, str) and len(value) < 1:
                value = default
            return value

        # Get JSON
        log_line = self.rs_log_line["format"]
        if not log_line:
            raise Exception("The received log line format had no value.")
        # Get segement
        self.__prompt_length = 0
        formatted_log_line = ""
        for segment in log_line:
            value = ""

            visible = True
            color = {}
            style = []
            terminal_width = shutil.get_terminal_size().columns

            if segment["type"] != "template":
                value = str(segment["value"])
            else:
                value = str(context.get(segment["value"], ""))
                i = 0
                parameters = deepcopy(segment.get("parameters", []))
                for parameter in parameters:
                    if len(parameter) > 1:
                        raise Exception(
                            f"Parameter {parameter} is longer than length of 1."
                        )
                    pname = list(parameter.keys())[0]
                    pvalue = list(parameter.values())[0]
                    if pname == "align":
                        pvalue = return_values(
                            pvalue, {"alignment": "left", "width": 10, "fillchar": " "}
                        )
                        pvalue["width"] += +(
                            len(value) - len(self.__remove_ansi(value))
                        )
                        if pvalue["alignment"].lower() in ["left", "l"]:
                            value = value.ljust(pvalue["width"], pvalue["fillchar"])
                        if pvalue["alignment"].lower() in ["right", "r"]:
                            value = value.rjust(pvalue["width"], pvalue["fillchar"])
                        if pvalue["alignment"].lower() in ["center", "c"]:
                            value = value.center(pvalue["width"], pvalue["fillchar"])
                    if pname == "case":
                        pvalue = return_values(pvalue, "upper")
                        if pvalue.lower() in ["upper", "u"]:
                            value = value.upper()
                        if pvalue.lower() in ["lower", "l"]:
                            value = value.lower()
                        if pvalue.lower() in ["capitalize", "cap", "c"]:
                            value = value.capitalize()
                        if pvalue.lower() in ["swapcase", "swap", "s"]:
                            value = value.swapcase()
                        if pvalue.lower() in ["title", "t"]:
                            value = value.title()
                    if pname == "filter":
                        pvalue = return_values(
                            pvalue,
                            {
                                "mode": "exclude",
                                "items": [],
                                "replace": "",
                                "case_sensitive": False,
                            },
                        )
                        if pvalue["mode"].lower() in ["exclude", "e"]:
                            for item in pvalue["items"]:
                                if (
                                    item if pvalue["case_sensitive"] else item.lower()
                                ) in (
                                    value if pvalue["case_sensitive"] else value.lower()
                                ):
                                    value = pvalue["replace"]
                        if pvalue["mode"].lower() in ["include", "i"]:
                            for item in pvalue["items"]:
                                if (
                                    item if pvalue["case_sensitive"] else item.lower()
                                ) not in (
                                    value if pvalue["case_sensitive"] else value.lower()
                                ):
                                    value = pvalue["replace"]
                    if pname == "affix":
                        pvalue = return_values(pvalue, {"prefix": "", "suffix": ""})
                        if len(pvalue["prefix"]) > 0:
                            value = pvalue["prefix"] + value
                        if len(pvalue["suffix"]) > 0:
                            value = value + pvalue["suffix"]
                    if pname == "truncate":
                        pvalue = return_values(
                            pvalue, {"width": 10, "ending": "…", "position": "end"}
                        )
                        pvalue["width"] += +(
                            len(value) - len(self.__remove_ansi(value))
                        )
                        if len(value) > pvalue["width"]:
                            if pvalue["position"] in ["end", "right", "e", "r"]:
                                value = (
                                    value[: pvalue["width"] - len(pvalue["ending"])]
                                    + pvalue["ending"]
                                )
                            elif pvalue["position"] in [
                                "center",
                                "middle",
                                "mid",
                                "m",
                                "c",
                            ]:
                                left_width = (
                                    pvalue["width"] - len(pvalue["ending"])
                                ) // 2
                                right_width = (
                                    pvalue["width"] - len(pvalue["ending"]) - left_width
                                )
                                value = (
                                    value[:left_width]
                                    + pvalue["ending"]
                                    + value[-right_width:]
                                )
                            elif pvalue["position"] in [
                                "beginning",
                                "start",
                                "left",
                                "b",
                                "s",
                                "l",
                            ]:
                                value = (
                                    pvalue["ending"]
                                    + value[
                                        -(pvalue["width"] - len(pvalue["ending"])) :
                                    ]
                                )
                    if pname == "visible":
                        if isinstance(pvalue, bool):
                            visible = pvalue
                        elif isinstance(pvalue, str):
                            if pvalue.startswith(">"):
                                visible = terminal_width >= int(pvalue[1:])
                            if pvalue.startswith("<"):
                                visible = terminal_width < int(pvalue[1:])
                        elif isinstance(pvalue, int):
                            visible = terminal_width >= pvalue
                    if pname == "color":
                        color = return_values(
                            pvalue,
                            {"foreground": (), "background": ()},
                        )
                        lmap = {
                            "info": "white",
                            "debug": "blue",
                            "success": "green",
                            "warning": "yellow",
                            "error": "red",
                            "critical": "magenta",
                        }
                        cmap = {
                            "timestamp": "green",
                            "filename": "magenta",
                            "wrapfunc": "yellow",
                            "linenum": "cyan",
                            "level": lmap.get(level, "white"),
                        }
                        if color["foreground"] == "dynamic":
                            color["foreground"] = cmap[segment["value"]]
                    if pname == "style":
                        pvalue = return_values(
                            pvalue,
                            {
                                "bold": False,
                                "italic": False,
                                "underline": False,
                                "blink": False,
                                "reverse": False,
                            },
                        )
                        if pvalue["bold"]:
                            style.append("\033[1m")
                        if pvalue["italic"]:
                            style.append("\033[3m")
                        if pvalue["underline"]:
                            style.append("\033[4m")
                        if pvalue["blink"]:
                            style.append("\033[5m")
                        if pvalue["reverse"]:
                            style.append("\033[7m")
                    if pname == "pad":
                        pvalue = return_values(
                            pvalue, {"left": 0, "right": 0, "fillchar": " "}
                        )
                        value = f"{(pvalue["fillchar"] * pvalue["left"])}{value}{(pvalue["fillchar"] * pvalue["right"])}"
                    if pname == "repeat":
                        value = value * return_values(pvalue, {"count": 1})["count"]
                    if pname == "if":
                        pvalue = return_values(pvalue, {"condition": {}, "action": {}})
                        ready = False
                        if pvalue["condition"].get("type", "") == "breakpoint":
                            bp = pvalue["condition"].get("value", "")
                            bp = return_values(bp, {"min": 0, "max": 9999})
                            if (
                                terminal_width >= bp["min"]
                                and terminal_width < bp["max"]
                            ):
                                ready = True

                        if ready:
                            if pvalue["action"].get("type", "") == "parameters":
                                j = 0
                                for k, v in pvalue["action"].get("value", {}).items():
                                    parameters.insert(i + j + 1, {k: v})
                                    j += 1

                    i += 1

            if not visible:
                value = ""

            if segment["value"] == "timestamp":
                self.__prompt_length += len(
                    str(
                        self.__define_timestamp(no_blank=True)
                        if terminal_width > 85
                        else self.__define_timestamp(no_blank=True, format="%H:%M:%S")
                    )
                )
            else:
                self.__prompt_length += len(self.__remove_ansi(value))

            def rgb_to_ansi(r=255, g=255, b=255, fg=True):
                # 8-bit (256 color) system
                color_code = (
                    16 + 36 * int(r / 255 * 5) + 6 * int(g / 255 * 5) + int(b / 255 * 5)
                )
                return f'\033[{"38" if fg else "48"};5;{color_code}m'

            def colorize(value, color, style):
                # Determine foreground color
                fg_color = color.get("foreground")
                if isinstance(fg_color, tuple) and len(fg_color) == 3:
                    fg_code = rgb_to_ansi(*fg_color, fg=True)
                elif isinstance(fg_color, str):
                    fg_code = getattr(Fore, fg_color.upper(), "")
                else:
                    fg_code = ""

                # Determine background color
                bg_color = color.get("background")
                if isinstance(bg_color, tuple) and len(bg_color) == 3:
                    bg_code = rgb_to_ansi(*bg_color, fg=False)
                elif isinstance(bg_color, str):
                    bg_code = getattr(Back, bg_color.upper(), "")
                else:
                    bg_code = ""

                # Apply colors to value
                return f"{fg_code}{bg_code}{"".join(style)}{value}{Style.RESET_ALL}"

            value = colorize(value, color, style)

            formatted_log_line += value

        return formatted_log_line

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
            datetime.datetime.now(
                datetime.UTC if self.rs_timestamps["use_utc"] else None
            ).strftime(self.rs_timestamps["format"])
            == self._previous_timestamp
            and not self.rs_timestamps["always_show"]
        ):
            timestamp = f"\033[{len(datetime.datetime.now().strftime(format or self.rs_timestamps["format"]))}C"
        return timestamp

    def __log_method(self, values, level, sep, pretty_print):
        # Get current frame
        frame = inspect.currentframe()
        # Get the caller's frame
        caller_frame = frame.f_back.f_back

        module = caller_frame.f_globals["__name__"]
        function = caller_frame.f_code.co_name
        wrapping_func = caller_frame.f_code.co_name
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

    def info(self, *values, sep: str = None, rich: bool = True) -> None:
        """Logs the given values to the console with an "info" level.

        Args:
            sep (str, optional): String inserted between values. Defaults to None
            rich (bool, optional): Format values for easier readability with syntax highlighting. Defaults to True
        """

        self.__log_method(
            values=values,
            level=self.__levels["info"]["name"]["display"],
            sep=sep or "\n",
            pretty_print=rich,
        )

    def debug(self, *values, sep: str = None, rich: bool = True) -> None:
        """Logs the given values to the console with a "debug" level.

        Args:
            sep (str, optional): String inserted between values. Defaults to None
            rich (bool, optional): Format values for easier readability with syntax highlighting. Defaults to True
        """

        self.__log_method(
            values=values,
            level=self.__levels["debug"]["name"]["display"],
            sep=sep or "\n",
            pretty_print=rich,
        )

    def success(self, *values, sep: str = None, rich: bool = True) -> None:
        """Logs the given values to the console with a "success" level.

        Args:
            sep (str, optional): String inserted between values. Defaults to None
            rich (bool, optional): Format values for easier readability with syntax highlighting. Defaults to True
        """

        self.__log_method(
            values=values,
            level=self.__levels["success"]["name"]["display"],
            sep=sep or "\n",
            pretty_print=rich,
        )

    def warning(self, *values, sep: str = None, rich: bool = True) -> None:
        """Logs the given values to the console with a "warning" level.

        Args:
            sep (str, optional): String inserted between values. Defaults to None
            rich (bool, optional): Format values for easier readability with syntax highlighting. Defaults to True
        """

        self.__log_method(
            values=values,
            level=self.__levels["warning"]["name"]["display"],
            sep=sep or "\n",
            pretty_print=rich,
        )

    def error(self, *values, sep: str = None, rich: bool = True) -> None:
        """Logs the given values to the console with an "error" level.

        Args:
            sep (str, optional): String inserted between values. Defaults to None
            rich (bool, optional): Format values for easier readability with syntax highlighting. Defaults to True
        """

        self.__log_method(
            values=values,
            level=self.__levels["error"]["name"]["display"],
            sep=sep or "\n",
            pretty_print=rich,
        )

    def critical(self, *values, sep: str = None, rich: bool = True) -> None:
        """Logs the given values to the console with a "critical" level.

        Args:
            sep (str, optional): String inserted between values. Defaults to None
            rich (bool, optional): Format values for easier readability with syntax highlighting. Defaults to True
        """

        self.__log_method(
            values=values,
            level=self.__levels["critical"]["name"]["display"],
            sep=sep or "\n",
            pretty_print=rich,
        )
