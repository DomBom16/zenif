from datetime import datetime
from math import floor

from colorama import Back, Fore, Style

from ...constants import Cursor, Keys
from ...decorators import enforce_types
from ...schema import DateF, Schema
from .base import BasePrompt


class DatePrompt(BasePrompt):
    def __init__(
        self,
        message: str,
        schema: Schema | None = None,
        id: str | None = None,
    ):
        super().__init__(message, schema, id)
        self._default: tuple[int, int, int] | None = None
        self._month_first: bool = False  # day-month or month-day

        self._year_range: tuple[int, int] = (1900, 2100)

        self._sep: str = "/"

        self._show_words: bool = False

        self.current_field_idx = 0

        self.day: str = ""
        self.month: str = ""
        self.year: str = ""

        # Check if the field is a DateF
        if schema and not isinstance(self.field, DateF):
            field_type = type(self.field).__name__
            error_message = f"DatePrompt requires a DateF field, but got {field_type}"
            raise TypeError(error_message)

    def default(self, value: tuple[int, int, int]) -> "DatePrompt":
        """Set the default value for the prompt."""
        self._default = value
        self.day, self.month, self.year = map(str, self._default)
        return self

    def month_first(self) -> "DatePrompt":
        """Use month-day-year instead of day-month-year."""
        self._month_first = True
        return self

    @enforce_types
    def year_range(self, start: int, end: int) -> "DatePrompt":
        """Set the minimum and maximum years for the prompt. Any values that exceed the range will be capped."""
        self._year_range = (max(0, start), end)
        return self

    def separator(self, sep: str) -> "DatePrompt":
        """Set the separator between the day, month, and year fields."""
        self._sep = sep
        return self

    def show_words(self) -> "DatePrompt":
        """On submit, display the submitted date in words. Ex: 1/1/2014 -> January 1, 2014"""
        self._show_words = True
        return self

    def ask(self) -> datetime:
        """Prompt the user for input."""
        field_order = (
            ["month", "day", "year"] if self._month_first else ["day", "month", "year"]
        )

        print("\n\n")

        fresh = False

        while True:
            controls = "←/→ to navigate, Tab to highlight, Enter to confirm"

            error = self.validate(
                datetime(
                    int(self.year or -1), int(self.month or -1), int(self.day or -1)
                )
                if self.year and self.month and self.day
                else None
            )

            for _ in range(3):
                print(Cursor.up(1) + Cursor.lclear(), end="")
            self._print_prompt(self.message, error=error)
            print(f"\n{Fore.RESET}{Style.DIM}  {controls}")

            formatted_value = f"  {Fore.YELLOW}{Back.RESET}{'' if self.current_field_idx == 0 else Style.DIM}{f'{Fore.BLACK}{Back.YELLOW}' if self.current_field_idx == 0 and fresh else ''}"

            formatted_value += (
                (self.month or "MM").rjust(2, "0")
                if self._month_first
                else (self.day or "DD").rjust(2, "0")
            )

            formatted_value += f"{Fore.YELLOW}{Back.RESET}{Style.DIM}{self._sep}{Style.NORMAL if self.current_field_idx == 1 else ''}{f'{Fore.BLACK}{Back.YELLOW}' if self.current_field_idx == 1 and fresh else ''}"

            formatted_value += (
                (self.day or "DD").rjust(2, "0")
                if self._month_first
                else (self.month or "MM").rjust(2, "0")
            )

            formatted_value += f"{Fore.YELLOW}{Back.RESET}{Style.DIM}{self._sep}{Style.NORMAL if self.current_field_idx == 2 else ''}{f'{Fore.BLACK}{Back.YELLOW}' if self.current_field_idx == 2 and fresh else ''}"

            formatted_value += (self.year or "YYYY").rjust(4, "0")

            formatted_value += f"{Style.RESET_ALL}"

            print(f"{formatted_value}")

            char = self._get_key()
            if char == Keys.TAB or char == Keys.RIGHT:  # Tab
                # move to next field
                self.current_field_idx = (self.current_field_idx + 1) % 3
                if int(self.year or 0) < self._year_range[0] and self.year:
                    self.year = str(self._year_range[0])
                fresh = char == Keys.TAB
            elif char == Keys.STAB or char == Keys.LEFT:  # Shift+Tab or Left arrow
                # move to previous field
                self.current_field_idx = (self.current_field_idx - 1) % 3
                if int(self.year or 0) < self._year_range[0] and self.year:
                    self.year = str(self._year_range[0])
                fresh = char == Keys.STAB
            elif char == Keys.ENTER:  # Enter key
                # check if all fields are filled and valid
                if (
                    1 <= int(self.day or -1) <= 31
                    and 1 <= int(self.month or -1) <= 12
                    and (
                        self._year_range[0]
                        <= int(self.year or -1)
                        <= self._year_range[1]
                    )
                    and not error
                ):
                    months = [
                        "January",
                        "February",
                        "March",
                        "April",
                        "May",
                        "June",
                        "July",
                        "August",
                        "September",
                        "October",
                        "November",
                        "December",
                    ]

                    for _ in range(3):
                        print(Cursor.up(1) + Cursor.lclear(), end="")
                    self._print_prompt(
                        self.message,
                        (
                            f"{months[int(self.month or 0) - 1]} {self.day or ''}, {self.year or ''}"
                            if self._show_words
                            else f"{int(self.month if self._month_first else self.day)}{self._sep}{int(self.day if self._month_first else self.month)}{self._sep}{int(self.year)}"
                        ),
                    )
                    print()
                    return datetime(int(self.year), int(self.month), int(self.day))
            elif char == Keys.BACKSPACE:  # Backspace
                if field_order[self.current_field_idx] == "day":
                    self.day = self.day[:-1]
                    if self.day == "0" or fresh:
                        self.day = ""
                elif field_order[self.current_field_idx] == "month":
                    self.month = self.month[:-1]
                    if self.month == "0" or fresh:
                        self.month = ""
                elif field_order[self.current_field_idx] == "year":
                    self.year = self.year[:-1]
                    if self.year == "0" or fresh:
                        self.year = ""
                fresh = False
            elif char == Keys.UP:  # Up arrow
                if field_order[self.current_field_idx] == "day":
                    self.day = str((int(self.day or 0) + 1) % 32)
                elif field_order[self.current_field_idx] == "month":
                    self.month = str((int(self.month or 0) + 1) % 13)
                elif field_order[self.current_field_idx] == "year":
                    self.year = str(int(self.year or str(datetime.now().year)) + 1)
                    if int(self.year) > self._year_range[1]:
                        self.year = str(self._year_range[0])  # Wrap around
                fresh = False
            elif char == Keys.DOWN:  # Down arrow
                if field_order[self.current_field_idx] == "day":
                    self.day = str((int(self.day or 0) - 1) % 32)
                elif field_order[self.current_field_idx] == "month":
                    self.month = str((int(self.month or 0) - 1) % 13)
                elif field_order[self.current_field_idx] == "year":
                    self.year = str(int(self.year or str(datetime.now().year)) - 1)
                    if int(self.year) < self._year_range[0]:
                        self.year = str(self._year_range[1])  # Wrap around
                fresh = False
            elif char.isdigit():
                fprev = fresh
                fresh = False
                if field_order[self.current_field_idx] == "day":
                    if fprev:
                        self.day = ""
                    if len(self.day.lstrip("0")) < 2:
                        self.day = self.day.lstrip("0") + char
                    if int(self.day) > 31:
                        self.day = "31"
                    if len(self.day) == 2 or int(self.day) > 3:
                        self.current_field_idx = (self.current_field_idx + 1) % 3
                        fresh = True
                elif field_order[self.current_field_idx] == "month":
                    if fprev:
                        self.month = ""
                    if len(self.month.lstrip("0")) < 2:
                        self.month = self.month.lstrip("0") + char
                    if int(self.month) > 12:
                        self.month = "12"
                    if len(self.month) == 2 or int(self.month) > 1:
                        self.current_field_idx = (self.current_field_idx + 1) % 3
                        fresh = True
                elif field_order[self.current_field_idx] == "year":
                    if fprev:
                        self.year = ""
                    if len(self.year.lstrip("0")) < 4:
                        self.year = self.year.lstrip("0") + char
                    if int(self.year) > self._year_range[1]:
                        self.year = str(self._year_range[1])
                    # Check if the year is valid
                    # If the year is reaching the point where adding more digits will overflow the max, go to the next field
                    # For example, if the cap was 3000 skip to the next field if the year is >300.
                    # If the cap was 2500, skip to the next field if the year is >250
                    if len(self.year) == 4 or int(self.year) > floor(
                        self._year_range[1] / 10
                    ):
                        self.current_field_idx = (self.current_field_idx + 1) % 3
                        fresh = True
