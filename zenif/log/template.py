from copy import deepcopy
from math import inf
from shutil import get_terminal_size as tsize
from typing import Any

from colorama import Style

from ..utils import colorize, strip_ansi


def shorthand(shorthand: str) -> list[dict]:
    shorthands: dict[str, list[dict]] = {
        "default": [
            {
                "type": "template",
                "value": "timestamp",
                "parameters": [{"color": {"foreground": "default"}}],
            },
            {"type": "static", "value": " "},
            {
                "type": "template",
                "value": "filename",
                "parameters": [
                    {"color": {"foreground": "default"}},
                    {"visible": ">95"},
                    {"truncate": {}},
                    {"align": {"alignment": "right"}},
                ],
            },
            {
                "type": "template",
                "value": "wrapfunc",
                "parameters": [
                    {"color": {"foreground": "default"}},
                    {"visible": False},
                    {
                        "if": {
                            "condition": {"type": "matches", "value": [""]},
                            "action": {"type": "set", "value": "source"},
                        }
                    },
                    {"truncate": {}},
                    {"visible": ">75"},
                    {
                        "if": {
                            "condition": {"type": "breakpoint", "value": {"min": 95}},
                            "action": {
                                "type": "parameters",
                                "value": [
                                    {"align": {"alignment": "left"}},
                                    {"affix": {"prefix": ":"}},
                                ],
                            },
                        }
                    },
                    {
                        "if": {
                            "condition": {
                                "type": "breakpoint",
                                "value": {"max": 95, "min": 75},
                            },
                            "action": {
                                "type": "parameters",
                                "value": [{"align": {"alignment": "right"}}],
                            },
                        }
                    },
                ],
            },
            {
                "type": "template",
                "value": "linenum",
                "parameters": [
                    {"color": {"foreground": "default"}},
                    {"affix": {"prefix": "\x1b[22m"}},
                    {
                        "if": {
                            "condition": {"type": "breakpoint", "value": {"max": 75}},
                            "action": {
                                "type": "parameters",
                                "value": [
                                    {
                                        "align": {
                                            "alignment": "right",
                                            "width": 3,
                                            "fillchar": "⋅",
                                        }
                                    },
                                    {"affix": {"prefix": "\x1b[2m"}},
                                ],
                            },
                        }
                    },
                    {
                        "if": {
                            "condition": {"type": "breakpoint", "value": {"min": 75}},
                            "action": {
                                "type": "parameters",
                                "value": [
                                    {
                                        "align": {
                                            "alignment": "right",
                                            "width": 4,
                                            "fillchar": "0",
                                        }
                                    },
                                    {"affix": {"prefix": ":\x1b[2m"}},
                                ],
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
                    {"color": {"foreground": "default"}},
                    {"case": "upper"},
                    {"align": {"alignment": "left", "width": 7}},
                ],
            },
            {"type": "static", "value": " "},
        ],
        "filled": [
            {
                "type": "template",
                "value": "timestamp",
                "parameters": [
                    {"color": {"foreground": "lightblack_ex"}},
                    {"affix": {"suffix": " "}},
                ],
            },
            {
                "type": "template",
                "value": "▐",
                "builtin": False,
                "parameters": [
                    {"color": {"foreground": "default", "fgcmap": "filename"}},
                    {"visible": ">95"},
                ],
            },
            {
                "type": "template",
                "value": "filename",
                "parameters": [
                    {"color": {"background": "default", "foreground": "black"}},
                    {"visible": ">95"},
                    {"truncate": {}},
                    {"align": {"alignment": "right"}},
                ],
            },
            {
                "type": "template",
                "value": "▐",
                "builtin": False,
                "parameters": [
                    {
                        "color": {
                            "foreground": "default",
                            "fgcmap": "wrapfunc",
                            "background": "default",
                            "bgcmap": "filename",
                        }
                    },
                    {
                        "if": {
                            "condition": {"type": "breakpoint", "value": {"max": 95}},
                            "action": {
                                "type": "parameters",
                                "value": [
                                    {
                                        "color": {
                                            "foreground": "default",
                                            "fgcmap": "wrapfunc",
                                        }
                                    }
                                ],
                            },
                        }
                    },
                    {"visible": ">75"},
                ],
            },
            {
                "type": "template",
                "value": "wrapfunc",
                "parameters": [
                    {"color": {"background": "default", "foreground": "black"}},
                    {"visible": False},
                    {
                        "if": {
                            "condition": {"type": "matches", "value": [""]},
                            "action": {"type": "set", "value": "source"},
                        }
                    },
                    {"truncate": {}},
                    {"visible": ">75"},
                    {
                        "if": {
                            "condition": {"type": "breakpoint", "value": {"min": 95}},
                            "action": {
                                "type": "parameters",
                                "value": [{"align": {"alignment": "left"}}],
                            },
                        }
                    },
                    {
                        "if": {
                            "condition": {
                                "type": "breakpoint",
                                "value": {"max": 95, "min": 75},
                            },
                            "action": {
                                "type": "parameters",
                                "value": [{"align": {"alignment": "right"}}],
                            },
                        }
                    },
                ],
            },
            {
                "type": "template",
                "value": "▐",
                "builtin": False,
                "parameters": [
                    {
                        "color": {
                            "background": "default",
                            "bgcmap": "wrapfunc",
                            "foreground": "default",
                            "fgcmap": "linenum",
                        }
                    },
                    {
                        "if": {
                            "condition": {"type": "breakpoint", "value": {"max": 75}},
                            "action": {
                                "type": "parameters",
                                "value": [
                                    {
                                        "color": {
                                            "foreground": "default",
                                            "fgcmap": "linenum",
                                        }
                                    }
                                ],
                            },
                        }
                    },
                ],
            },
            {
                "type": "template",
                "value": "linenum",
                "parameters": [
                    {"color": {"background": "default", "foreground": "black"}},
                    {"affix": {"prefix": "\x1b[22m"}},
                    {
                        "if": {
                            "condition": {"type": "breakpoint", "value": {"max": 75}},
                            "action": {
                                "type": "parameters",
                                "value": [
                                    {
                                        "align": {
                                            "alignment": "right",
                                            "width": 3,
                                            "fillchar": "⋅",
                                        }
                                    },
                                    {"affix": {"prefix": "\x1b[2m"}},
                                ],
                            },
                        }
                    },
                    {
                        "if": {
                            "condition": {"type": "breakpoint", "value": {"min": 75}},
                            "action": {
                                "type": "parameters",
                                "value": [
                                    {
                                        "align": {
                                            "alignment": "right",
                                            "width": 4,
                                            "fillchar": "0",
                                        }
                                    },
                                    {"affix": {"prefix": "\x1b[2m"}},
                                ],
                            },
                        }
                    },
                ],
            },
            {
                "type": "template",
                "value": "▌",
                "builtin": False,
                "parameters": [
                    {
                        "color": {
                            "background": "default",
                            "bgcmap": "level",
                            "foreground": "default",
                            "fgcmap": "linenum",
                        }
                    }
                ],
            },
            {
                "type": "template",
                "value": "level",
                "parameters": [
                    {"color": {"background": "default", "foreground": "black"}},
                    {"case": "upper"},
                    {"align": {"alignment": "left", "width": 7}},
                ],
            },
            {
                "type": "template",
                "value": "▌",
                "builtin": False,
                "parameters": [{"color": {"foreground": "default", "fgcmap": "level"}}],
            },
            {"type": "static", "value": " "},
        ],
        "noalign": [
            {
                "type": "template",
                "value": "timestamp",
                "parameters": [{"color": {"foreground": "default"}}],
            },
            {"type": "static", "value": " "},
            {
                "type": "template",
                "value": "filename",
                "parameters": [
                    {"color": {"foreground": "default"}},
                    {"visible": ">95"},
                    {"truncate": {}},
                ],
            },
            {
                "type": "template",
                "value": "wrapfunc",
                "parameters": [
                    {"color": {"foreground": "default"}},
                    {"visible": False},
                    {
                        "if": {
                            "condition": {"type": "matches", "value": [""]},
                            "action": {"type": "set", "value": "source"},
                        }
                    },
                    {"truncate": {}},
                    {"visible": ">75"},
                    {
                        "if": {
                            "condition": {"type": "breakpoint", "value": {"min": 95}},
                            "action": {
                                "type": "parameters",
                                "value": [
                                    {"affix": {"prefix": ":"}},
                                ],
                            },
                        }
                    },
                ],
            },
            {
                "type": "template",
                "value": "linenum",
                "parameters": [
                    {"color": {"foreground": "default"}},
                    {"affix": {"prefix": ":"}},
                ],
            },
            {"type": "static", "value": " "},
            {
                "type": "template",
                "value": "level",
                "parameters": [
                    {"color": {"foreground": "default"}},
                    {"case": "upper"},
                ],
            },
            {"type": "static", "value": " "},
        ],
        "simple": [
            {
                "type": "template",
                "value": "timestamp",
                "parameters": [{"color": {"foreground": "default"}}],
            },
            {"type": "static", "value": " "},
            {
                "type": "template",
                "value": "level",
                "parameters": [
                    {"color": {"foreground": "default"}},
                    {"case": "upper"},
                    {"align": {"alignment": "left", "width": 7}},
                ],
            },
            {"type": "static", "value": " "},
        ],
        "short": [
            {
                "type": "template",
                "value": "timestamp",
                "parameters": [{"color": {"foreground": "default"}}],
            },
            {"type": "static", "value": " "},
            {
                "type": "template",
                "value": "level",
                "parameters": [
                    {"color": {"foreground": "default"}},
                    {"case": "upper"},
                    {"align": {"alignment": "left", "width": 7}},
                    {"truncate": {"width": 3, "marker": ""}},
                    {
                        "if": {
                            "condition": {"type": "matches", "value": "WAR"},
                            "action": {"type": "set", "value": "WRN"},
                        }
                    },
                    {
                        "if": {
                            "condition": {"type": "matches", "value": "DEB"},
                            "action": {"type": "set", "value": "DBG"},
                        }
                    },
                    {
                        "if": {
                            "condition": {"type": "matches", "value": "SUC"},
                            "action": {"type": "set", "value": "SCS"},
                        }
                    },
                    {
                        "if": {
                            "condition": {"type": "matches", "value": "CRI"},
                            "action": {"type": "set", "value": "CRT"},
                        }
                    },
                ],
            },
            {"type": "static", "value": " "},
        ],
        "timestamp": [
            {
                "type": "template",
                "value": "timestamp",
                "parameters": [{"color": {"foreground": "default"}}],
            },
            {"type": "static", "value": " "},
        ],
        "level": [
            {
                "type": "template",
                "value": "level",
                "parameters": [
                    {"color": {"foreground": "default"}},
                    {"case": "upper"},
                    {"align": {"alignment": "left", "width": 7}},
                ],
            },
            {"type": "static", "value": " "},
        ],
        "levelshort": [
            {
                "type": "template",
                "value": "level",
                "parameters": [
                    {"color": {"foreground": "default"}},
                    {"case": "upper"},
                    {"align": {"alignment": "left", "width": 7}},
                    {"truncate": {"width": 3, "marker": ""}},
                    {
                        "if": {
                            "condition": {"type": "matches", "value": "WAR"},
                            "action": {"type": "set", "value": "WRN"},
                        }
                    },
                    {
                        "if": {
                            "condition": {"type": "matches", "value": "DEB"},
                            "action": {"type": "set", "value": "DBG"},
                        }
                    },
                    {
                        "if": {
                            "condition": {"type": "matches", "value": "SUC"},
                            "action": {"type": "set", "value": "SCS"},
                        }
                    },
                    {
                        "if": {
                            "condition": {"type": "matches", "value": "CRI"},
                            "action": {"type": "set", "value": "CRT"},
                        }
                    },
                ],
            },
            {"type": "static", "value": " "},
        ],
    }
    return shorthands.get(shorthand, "")


class LastProcessed:
    def __init__(self):
        self.length: int = 0
        self.level: str = ""


class TemplateEngine:
    def __init__(self):
        self.processors: dict[str, Any] = {
            # Main processors
            "align": self.__process_align,
            "case": self.__process_case,
            "affix": self.__process_affix,
            "truncate": self.__process_truncate,
            "mask": self.__process_mask,
            "pad": self.__process_pad,
            "repeat": self.__process_repeat,
            "style": self.__process_style,
            # If statement
            "if": self.__process_if,
            # Last processors
            "visible": self.__process_visible,
            "color": self.__process_color,
        }
        self.last_processors: list[str] = ["visible", "color"]
        self.__tempname: str = ""
        self.__level: str = ""
        self.__length: int = 0
        self.processed: LastProcessed = LastProcessed()

    def process(
        self, template: list[dict[str, Any]] | str, context: dict[str, Any], level: str
    ) -> str:
        if isinstance(template, str):
            template = shorthand(template)

        result = ""
        self.__level = level
        self.__length = 0
        for segment in template:
            if segment.get("builtin", True):
                value = self.__get_segment_value(segment, context)
            else:
                value = segment.get("value", "")
            parameters = deepcopy(segment.get("parameters", []))

            # Process all parameters, including 'if' statements
            value, last_parameters = self.__process_parameters(value, parameters)

            # Apply last processors in specific order, only if they were present
            for pname in self.last_processors:
                if last_parameters[pname] is not None:
                    value = str(self.processors[pname](value, last_parameters[pname]))

            result += value

            if segment.get("value", "") == "timestamp":
                self.__length += len(strip_ansi(value.replace("\x1b[8C", 8 * "#")))
            else:
                self.__length += len(strip_ansi(value))

        # Store the length and level in last_processed after processing
        self.processed.length = self.__length
        self.processed.level = self.__level

        return result

    def __process_parameters(
        self, value: str, parameters: list[dict[str, Any]]
    ) -> tuple[str, dict[str, Any]]:
        last_parameters = {k: None for k in self.last_processors}

        for parameter in parameters:
            pname, pvalue = next(iter(parameter.items()))
            if pname == "if":
                value, if_last_params = self.__process_if(value, pvalue)
                # Update last_parameters only if the condition was met
                for lp, lv in if_last_params.items():
                    if lv is not None:
                        last_parameters[lp] = lv
            elif pname in self.last_processors:
                last_parameters[pname] = pvalue
            elif pname in self.processors:
                value = str(self.processors[pname](value, pvalue))

        return value, last_parameters

    def __process_if(
        self, value: str, pvalue: dict[str, Any]
    ) -> tuple[str, dict[str, Any]]:
        pvalue = self.__process_pvalue(pvalue, {"condition": {}, "action": {}})
        condition_type = pvalue["condition"].get("type", None).lower()
        condition_value = pvalue["condition"].get("value", None)
        action_type = pvalue["action"].get("type", None).lower()
        action_value = pvalue["action"].get("value", None)

        # Process condition
        condition_met = self.__evaluate_condition(
            condition_type, condition_value, value
        )

        last_parameters = {k: None for k in self.last_processors}

        # Apply actions if condition is met
        if condition_met:
            if action_type == "parameters":
                for param in action_value or []:
                    param_name, param_value = next(iter(param.items()))
                    if param_name in self.last_processors:
                        last_parameters[param_name] = param_value
                    elif param_name in self.processors:
                        value = self.processors[param_name](value, param_value)
            elif action_type == "set":
                value = action_value
            elif action_type == "replace":
                action_value = self.__process_pvalue(
                    (action_value or {}), {"old": "", "new": ""}
                )
                value = value.replace(action_value["old"], action_value["new"])

        return value, last_parameters

    def __evaluate_condition(
        self, condition_type: str, condition_value: Any, value: str
    ) -> bool:
        if condition_type == "breakpoint":
            bp = self.__process_pvalue((condition_value or {}), {"min": 0, "max": inf})
            return bp["min"] <= tsize().columns < bp["max"]
        elif condition_type == "contains":
            return any(cv in value for cv in condition_value)
        elif condition_type == "matches":
            return value in condition_value
        elif condition_type == "excludes":
            return not any(cv in value for cv in condition_value)
        elif condition_type == "startswith":
            return any(value.startswith(cv) for cv in condition_value)
        elif condition_type == "endswith":
            return any(value.endswith(cv) for cv in condition_value)
        else:
            return False

    def __get_segment_value(
        self, segment: dict[str, Any], context: dict[str, Any]
    ) -> str:
        if segment["type"] != "template":
            self.__tempname = ""
            return str(segment["value"])
        self.__tempname = segment["value"]
        return str(context.get(segment["value"], ""))

    def __process_pvalue(self, value: Any, default: Any) -> Any:
        if not isinstance(value, type(default)):
            raise TypeError(f"Value {value} must be type {type(default)}")
        if isinstance(value, dict):
            for dk, dv in default.items():
                value.setdefault(dk, dv)
        if isinstance(value, str) and len(value) < 1:
            value = default
        return value

    def __process_align(self, value: str, pvalue: dict[str, Any]) -> str:
        pvalue = self.__process_pvalue(
            pvalue, {"alignment": "left", "width": 10, "fillchar": " "}
        )
        terminal_width = tsize().columns

        if isinstance(pvalue["width"], str) and pvalue["width"].endswith("%"):
            pvalue["width"] = int(terminal_width * (int(pvalue["width"][:-1]) / 100))

        pvalue["width"] += len(value) - len(strip_ansi(value))
        pvalue["fillchar"] = pvalue["fillchar"][0]

        if pvalue["alignment"].lower() == "left":
            return value.ljust(pvalue["width"], pvalue["fillchar"])
        elif pvalue["alignment"].lower() == "right":
            return value.rjust(pvalue["width"], pvalue["fillchar"])
        elif pvalue["alignment"].lower() == "center":
            return value.center(pvalue["width"], pvalue["fillchar"])
        else:
            raise ValueError("Invalid alignment value. Try 'left', 'right', 'center'")

    def __process_case(self, value: str, pvalue: str) -> str:
        pvalue = self.__process_pvalue(pvalue, "upper")
        case_functions = {
            "upper": str.upper,
            "lower": str.lower,
            "capitalize": str.capitalize,
            "swapcase": str.swapcase,
            "title": str.title,
        }
        if pvalue.lower() in case_functions:
            return case_functions[pvalue.lower()](value)
        else:
            raise ValueError(
                "Invalid case value. Try 'upper', 'lower', 'capitalize', 'swapcase', 'title'"
            )

    def __process_affix(self, value: str, pvalue: dict[str, Any]) -> str:
        pvalue = self.__process_pvalue(pvalue, {"prefix": "", "suffix": ""})
        return pvalue["prefix"] + value + pvalue["suffix"]

    def __process_truncate(self, value: str, pvalue: dict[str, Any]) -> str:
        pvalue = self.__process_pvalue(
            pvalue, {"width": 10, "marker": "…", "position": "end"}
        )
        pvalue["width"] += len(value) - len(strip_ansi(value))

        if len(value) > pvalue["width"]:
            if pvalue["position"] == "end":
                return (
                    value[: pvalue["width"] - len(pvalue["marker"])] + pvalue["marker"]
                )
            elif pvalue["position"] == "middle":
                left_width = (pvalue["width"] - len(pvalue["marker"])) // 2
                right_width = pvalue["width"] - len(pvalue["marker"]) - left_width
                return value[:left_width] + pvalue["marker"] + value[-right_width:]
            elif pvalue["position"] == "start":
                return (
                    pvalue["marker"]
                    + value[-(pvalue["width"] - len(pvalue["marker"])) :]
                )
            else:
                raise ValueError(
                    "Invalid truncate position. Try 'end', 'middle', 'start'"
                )

        return value

    def __process_mask(self, value: str, pvalue: dict[str, Any]) -> str:
        pvalue = self.__process_pvalue(
            pvalue, {"width": (10, 4), "masker": "*", "position": "end"}
        )
        masked_part = pvalue["masker"][0] * (pvalue["width"][0] - pvalue["width"][1])

        if pvalue["position"] == "end":
            return value.ljust(pvalue["width"][0])[: pvalue["width"][1]] + masked_part
        elif pvalue["position"] == "start":
            return masked_part + value.rjust(pvalue["width"][0])[-pvalue["width"][1] :]
        elif pvalue["position"] == "middle":
            start = (pvalue["width"][1] + 1) // 2
            return value[:start] + masked_part + value[-(pvalue["width"][1] - start) :]
        else:
            raise ValueError("Invalid mask position. Try 'end', 'middle', 'start'")

    def __process_pad(self, value: str, pvalue: dict[str, Any]) -> str:
        pvalue = self.__process_pvalue(pvalue, {"left": 0, "right": 0, "fillchar": " "})
        return f"{(pvalue['fillchar'][0] * pvalue['left'])}{value}{(pvalue['fillchar'][0] * pvalue['right'])}"

    def __process_repeat(self, value: str, pvalue: dict[str, int]) -> str:
        return value * self.__process_pvalue(pvalue, {"count": 1})["count"]

    def __process_visible(
        self,
        value: str,
        pvalue: bool | str | int,
    ) -> str:
        terminal_width = tsize().columns

        if isinstance(pvalue, bool):
            return value if pvalue else ""
        elif isinstance(pvalue, str):
            if pvalue.startswith(">"):
                return value if terminal_width >= int(pvalue[1:]) else ""
            if pvalue.startswith("<"):
                return value if terminal_width < int(pvalue[1:]) else ""
        elif isinstance(pvalue, int):
            return value if terminal_width >= pvalue else ""
        return ""

    def __process_style(self, value: str, pvalue: dict[str, bool]) -> str:
        pvalue = self.__process_pvalue(
            pvalue,
            {
                "bold": False,
                "italic": False,
                "underline": False,
                "blink": False,
                "reverse": False,
            },
        )
        style = []
        if pvalue["bold"]:
            style.append("\x1b[1m")
        if pvalue["italic"]:
            style.append("\x1b[3m")
        if pvalue["underline"]:
            style.append("\x1b[4m")
        if pvalue["blink"]:
            style.append("\x1b[5m")
        if pvalue["reverse"]:
            style.append("\x1b[7m")
        return f"{''.join(style)}{value}{Style.RESET_ALL}" if style else value

    def __process_color(self, value: str, pvalue: dict[str, Any]) -> str:
        pvalue = self.__process_pvalue(
            pvalue, {"foreground": (), "fgcmap": None, "background": (), "bgcmap": None}
        )
        lmap = {
            "info": "white",
            "debug": "blue",
            "success": "green",
            "warning": "yellow",
            "error": "red",
            "lethal": "magenta",
        }
        cmap = {
            "timestamp": "green",
            "filename": "magenta",
            "wrapfunc": "yellow",
            "linenum": "cyan",
            "level": lmap.get(self.__level, "white"),
        }

        def case_insensitive_compare(value, target):
            if isinstance(value, str):
                return value.lower() == target.lower()
            elif isinstance(value, tuple):
                return any(
                    item.lower() == target.lower()
                    for item in value
                    if isinstance(item, str)
                )
            return False

        if case_insensitive_compare(pvalue["foreground"], "default"):
            pvalue["foreground"] = cmap.get(
                pvalue["fgcmap"] or self.__tempname, "white"
            )
        if case_insensitive_compare(pvalue["background"], "default"):
            pvalue["background"] = cmap.get(
                pvalue["bgcmap"] or self.__tempname, "white"
            )

        return colorize(value, pvalue)
