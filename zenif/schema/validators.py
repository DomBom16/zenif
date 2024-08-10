from __future__ import annotations
from typing import Any
from re import match
from .core import Validator

inf = float("inf")


class Length(Validator):
    """Compares whether the length of the value is within the given range."""
    def __init__(self, min: int | None = None, max: int | None = None):
        self.min = min if min is not None else -inf
        self.max = max if max is not None else inf

    def validate(self, value: Any):
        if value is None:
            raise ValueError(f"Value is of None type.")
        if len(value) < self.min:
            raise ValueError(f"Minimum length is {self.min}.")
        if len(value) > self.max:
            raise ValueError(f"Maximum length is {self.max}.")


class Value(Validator):
    """Compares whether the value is within the given range."""
    def __init__(self, min: int | None = None, max: int | None = None):
        self.min = min if min is not None else -inf
        self.max = max if max is not None else inf

    def validate(self, value: Any):
        if value is None:
            raise ValueError(f"Value is of None type.")
        if value < self.min:
            raise ValueError(f"Minimum value is {self.min}.")
        if value > self.max:
            raise ValueError(f"Maximum value is {self.max}.")


class Regex(Validator):
    """Matches the given pattern to the value."""
    def __init__(self, pattern: str):
        self.pattern = pattern

    def validate(self, value: Any):
        if not match(self.pattern, str(value)):
            raise ValueError(f"Value does not match pattern.")


class EmailValidator(Validator):
    """Mimics the built-in Regex() validator with the official RFC 5322 email regular expression."""
    def validate(self, value: Any):
        if not match(
            r"""(?:[a-z0-9!#$%&'*+/=?^_`{|}~-]+(?:\.[a-z0-9!#$%&'*+/=?^_`{|}~-]+)*|"(?:[\x01-\x08\x0b\x0c\x0e-\x1f\x21\x23-\x5b\x5d-\x7f]|\\[\x01-\x09\x0b\x0c\x0e-\x7f])*")@(?:(?:[a-z0-9](?:[a-z0-9-]*[a-z0-9])?\.)+[a-z0-9](?:[a-z0-9-]*[a-z0-9])?|\[(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?|[a-z0-9-]*[a-z0-9]:(?:[\x01-\x08\x0b\x0c\x0e-\x1f\x21-\x5a\x53-\x7f]|\\[\x01-\x09\x0b\x0c\x0e-\x7f])+)\])""",
            str(value),
        ):
            raise ValueError("Invalid email format.")
