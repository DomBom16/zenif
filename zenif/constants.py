import select
import termios
import tty


class Keys:
    """
    A set of common keys used in the terminal.

        - Up, Down, Right, Left
        - Backspace, Insert, Delete, Enter, Escape, Tab, Shift+Tab
        - Ctrl+A to Ctrl+Z
        - F1 to F12

    For more information, see https://en.wikipedia.org/wiki/ANSI_escape_code
    """

    # Arrow keys
    UP = "\x1b[A"
    DOWN = "\x1b[B"
    RIGHT = "\x1b[C"
    LEFT = "\x1b[D"

    # Special keys
    BACKSPACE = "\x7f"
    INSERT = "\x1b[2~"
    DELETE = "\x1b[3~"
    ENTER = "\r"
    ESCAPE = "\x1b"
    TAB = "\t"
    STAB = "\x1b[Z"  # Shift+Tab

    # Control keys
    CTRLA = "\x01"  # ASCII 1
    CTRLB = "\x02"  # ASCII 2
    CTRLC = "\x03"  # ASCII 3
    CTRLD = "\x04"  # ASCII 4
    CTRLE = "\x05"  # ASCII 5
    CTRLF = "\x06"  # ASCII 6
    CTRLG = "\x07"  # ASCII 7
    CTRLH = "\x08"  # ASCII 8 (\b)
    CTRLI = "\x09"  # ASCII 9 (\t)
    CTRLJ = "\x0a"  # ASCII 10 (\n)
    CTRLK = "\x0b"  # ASCII 11
    CTRLL = "\x0c"  # ASCII 12 (\f)
    CTRLM = "\x0d"  # ASCII 13 (\r)
    CTRLN = "\x0e"  # ASCII 14
    CTRLO = "\x0f"  # ASCII 15
    CTRLP = "\x10"  # ASCII 16
    CTRLQ = "\x11"  # ASCII 17
    CTRLR = "\x12"  # ASCII 18
    CTRLS = "\x13"  # ASCII 19
    CTRLT = "\x14"  # ASCII 20
    CTRLU = "\x15"  # ASCII 21
    CTRLV = "\x16"  # ASCII 22
    CTRLW = "\x17"  # ASCII 23
    CTRLX = "\x18"  # ASCII 24
    CTRLY = "\x19"  # ASCII 25
    CTRLZ = "\x1a"  # ASCII 26

    # Function keys
    F1 = "\x1bOP"
    F2 = "\x1bOQ"
    F3 = "\x1bOR"
    F4 = "\x1bOS"
    F5 = "\x1b[15~"
    F6 = "\x1b[17~"
    F7 = "\x1b[18~"
    F8 = "\x1b[19~"
    F9 = "\x1b[20~"
    F10 = "\x1b[21~"
    F11 = "\x1b[23~"
    F12 = "\x1b[24~"

    # Groups
    # Useful for elimatation of key detection,
    # e.g. "if key in Keys.ARROWS" vs. "if key in [Keys.UP, Keys.DOWN, Keys.RIGHT, Keys.LEFT]"

    ARROWS = (UP, DOWN, RIGHT, LEFT)
    CTRLKEYS = (
        CTRLA,
        CTRLB,
        CTRLC,
        CTRLD,
        CTRLE,
        CTRLF,
        CTRLG,
        CTRLH,
        CTRLI,
        CTRLJ,
        CTRLK,
        CTRLL,
        CTRLM,
        CTRLN,
        CTRLO,
        CTRLP,
        CTRLQ,
        CTRLR,
        CTRLS,
        CTRLT,
        CTRLU,
        CTRLV,
        CTRLW,
        CTRLX,
        CTRLY,
        CTRLZ,
    )
    FUNCKEYS = (F1, F2, F3, F4, F5, F6, F7, F8, F9, F10, F11, F12)


class Cursor:
    @staticmethod
    def sclear() -> str:
        """Clear the screen"""
        return "\x1b[2J"

    @staticmethod
    def lclear() -> str:
        """Clear the current line"""
        return "\x1b[2K"

    @staticmethod
    def move(dx: int, dy: int) -> str:
        """Move the cursor relative to the current position

        Args:
            dx (int): The number of columns to move right
            dy (int): The number of rows to move down

        Returns:
            str: Ansi code to move the cursor
        """
        return f"\x1b[{dy};{dx}H"

    @staticmethod
    def up(dy: int) -> str:
        """Move the cursor up

        Args:
            dy (int): The number of rows to move up

        Returns:
            str: Ansi code to move the cursor up
        """
        return f"\x1b[{dy}A"

    @staticmethod
    def down(dy: int) -> str:
        """Move the cursor down

        Args:
            dy (int): The number of rows to move down

        Returns:
            str: Ansi code to move the cursor down
        """
        return f"\x1b[{dy}B"

    @staticmethod
    def right(dx: int) -> str:
        """Move the cursor right

        Args:
            dx (int): The number of columns to move right

        Returns:
            str: Ansi code to move the cursor right
        """
        return f"\x1b[{dx}C"

    @staticmethod
    def cright(x: int, dx: int, w: int) -> str:
        """Move the cursor right continuously, advancing to the next line if necessary

        Args:
            x (int): The current position of the cursor
            dx (int): The number of columns to move right
            w (int): The width of the terminal

        Returns:
            str: Ansi code to move the cursor right
        """
        fx, fy = x, 0
        for _ in range(dx):
            fx += 1
            if fx >= w:
                fx = 0
                fy += 1
        return f"\x1b[{fx - x}C" + (f"\x1b[{fy}B" if fy > 0 else "")

    @staticmethod
    def left(x: int) -> str:
        """Move the cursor left

        Args:
            x (int): The number of columns to move left

        Returns:
            str: Ansi code to move the cursor left
        """
        return f"\x1b[{x}D"

    @staticmethod
    def set(x: int, y: int) -> str:
        """Set the cursor position on the screen

        Args:
            x (int): The number of columns to move right
            y (int): The number of rows to move down

        Returns:
            str: Ansi code to set the cursor
        """
        return f"\x1b[{y};{x}f"

    @staticmethod
    def get(timeout=1.0):
        """Get the cursor position on the screen

        Returns:
            tuple[int, int]: The cursor position on the screen
        """
        with open("/dev/tty", "rb+", buffering=0) as tty_fd:
            fd = tty_fd.fileno()
            old_settings = termios.tcgetattr(fd)
            try:
                # Set terminal to cbreak (raw) mode for character-by-character input
                tty.setcbreak(fd)

                # Send the ANSI query to get cursor position
                tty_fd.write(b"\x1b[6n")

                response = b""
                while True:
                    # Use select to avoid blocking indefinitely
                    r, _, _ = select.select([tty_fd], [], [], timeout)
                    if not r:
                        break  # Timeout reached, no more data
                    # Read one byte at a time
                    byte = tty_fd.read(1)
                    if not byte:
                        break
                    response += byte
                    if response.endswith(b"R"):
                        break  # End of response reached

                # Expected response is of the form b"\x1b[<rows>;<cols>R"
                if response.startswith(b"\x1b[") and response.endswith(b"R"):
                    try:
                        numbers = response[2:-1].split(b";")
                        if len(numbers) == 2:
                            row = int(numbers[0] or 1) - 1
                            col = int(numbers[1] or 1) - 1
                            return row, col
                    except ValueError:
                        pass  # Conversion failed if unexpected format
                return None  # Return None if the response was not as expected
            finally:
                # Restore the original terminal settings
                termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)

    @staticmethod
    def hide() -> str:
        """Hide the cursor

        Returns:
            str: Ansi code to hide the cursor
        """
        return "\x1b[?25l"

    @staticmethod
    def show() -> str:
        """Show the cursor

        Returns:
            str: Ansi code to show the cursor
        """
        return "\x1b[?25h"
