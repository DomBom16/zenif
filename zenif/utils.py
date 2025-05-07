import re
import signal
import sys

from colorama import Back, Fore

from .constants import Keys


def wrap(text: str, width: int) -> list:
    """Wraps text to the desired width.

    Args:
        text (str): Text to wrap.
        width (int): Width to wrap text to.

    Returns:
        list: A list of lines as they appear in the block of wrapped text.
    """
    result = []

    lines = text.split("\n")

    for line in lines:
        if line.strip() == "":
            # Preserve empty lines (including lines with only whitespace)
            result.append("")
            continue

        current_line = ""
        current_line_visible_length = 0
        words = re.findall(r"\S+\s*", line)

        for word in words:
            word_visible_length = len(strip_ansi(word))

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


def strip_ansi(text: str) -> str:
    """
    Remove ANSI escape sequences from a string.

    This function removes all ANSI escape sequences, including color codes,
    cursor movements, and other control sequences.

    Args:
        text (str): The input string containing ANSI escape sequences.

    Returns:
        str: The input string with all ANSI escape sequences removed.
    """
    ansi_escape = re.compile(
        r"""\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])""",
        re.VERBOSE,
    )
    return ansi_escape.sub("", text)


def rgb_to_ansi(r: int = 255, g: int = 255, b: int = 255, fg: bool = True) -> str:
    color_code = 16 + 36 * int(r / 255 * 5) + 6 * int(g / 255 * 5) + int(b / 255 * 5)
    return f"\x1b[{'38' if fg else '48'};5;{color_code}m"


def colorize(string: str, color: dict[str, tuple | str]) -> str:
    """Applied certain ANSI escape codes that apply color.

    Args:
        string (str): String to color.
        color (dict[str, tuple  |  str]): A dictionary that contains keys 'foreground' and 'background' with values for colors in either RGB as a tuple or a color string recognized by the colorama library.

    Returns:
        str: The inputted string with color formatting.
    """

    fg_color = color.get("foreground")
    bg_color = color.get("background")

    fg_code = (
        rgb_to_ansi(*fg_color, fg=True)
        if isinstance(fg_color, tuple) and len(fg_color) == 3
        else (getattr(Fore, fg_color.upper(), "") if isinstance(fg_color, str) else "")
    )
    bg_code = (
        rgb_to_ansi(*bg_color, fg=False)
        if isinstance(bg_color, tuple) and len(bg_color) == 3
        else (getattr(Back, bg_color.upper(), "") if isinstance(bg_color, str) else "")
    )

    return f"{fg_code}{bg_code}{string}\x1b[0m"


def strip_unsafe_objs(
    object: any, repr_id: str
) -> str | int | bool | float | list | dict | tuple:
    """Sanitizes objects for unsafe objects.

    Args:
        object (any): Object to sanitize.
        repr_id (str): An ID that identifies canonically altered strings.

    Returns:
        str | int | bool | float | list | dict | tuple: A sanitized object.
    """
    if isinstance(object, (str, int, float, bool)):
        return object
    elif isinstance(object, list):
        return [strip_unsafe_objs(item, repr_id) for item in object]
    elif isinstance(object, dict):
        return {key: strip_unsafe_objs(value, repr_id) for key, value in object.items()}
    elif isinstance(object, tuple):
        return tuple(strip_unsafe_objs(item, repr_id) for item in object)
    else:
        return f"{repr_id}{repr(object)}"


def strip_repr_id(string: str, repr_id: str) -> str:
    """Removes repr IDs from strings.

    Args:
        string (str): String to operate on.
        repr_id (str): Repr ID to remove.

    Returns:
        str: String without repr IDs.
    """
    return re.sub(
        rf'"{repr_id}(.*?)"', r"\1", re.sub(rf"'{repr_id}(.*?)'", r"\1", string)
    )


def if_space(string: str, space: int = 0) -> str:
    """If space allows, return the given string.

    Args:
        string (str): String in question.
        space (int, optional): Space permitted. Defaults to 0.

    Returns:
        str: The original string if space permits, otherwise "".
    """
    return string if space >= len(string) else ""


def get_key() -> str:
    def handle_interrupt(signum, frame):
        raise KeyboardInterrupt()

    if sys.platform.startswith("win"):
        import msvcrt

        # Set up the interrupt handler
        signal.signal(signal.SIGINT, handle_interrupt)

        try:
            while True:
                if msvcrt.kbhit():
                    char = msvcrt.getch().decode("utf-8")
                    if char == Keys.CTRLC:  # Ctrl+C
                        raise KeyboardInterrupt()
                    return char
        finally:
            # Reset the interrupt handler
            signal.signal(signal.SIGINT, signal.SIG_DFL)

    else:
        import termios
        import tty

        fd = sys.stdin.fileno()
        old_settings = termios.tcgetattr(fd)
        try:
            tty.setraw(fd)
            # Set up the interrupt handler
            signal.signal(signal.SIGINT, handle_interrupt)

            while True:
                char = sys.stdin.read(1)
                if char == Keys.CTRLC:  # Ctrl+C
                    raise KeyboardInterrupt()
                if char == Keys.ESCAPE:
                    # Handle escape sequences (e.g., arrow keys)
                    next_char = sys.stdin.read(1)
                    if next_char == "[":
                        last_char = sys.stdin.read(1)
                        return f"\x1b[{last_char}"
                return char
        finally:
            # Reset terminal settings and interrupt handler
            termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
            signal.signal(signal.SIGINT, signal.SIG_DFL)
