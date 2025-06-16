from __future__ import annotations

from enum import Enum
from re import match
from typing import Any

from .core import Validator
from .exceptions import (
    AlphanumericError,
    DateError,
    EmailError,
    EmptyValueError,
    LengthError,
    NotFalsyError,
    NotTruthyError,
    RegexError,
    URLError,
    ValueRangeError,
)

inf = float("inf")


class MinLength(Validator):
    """Validates that the value has at least the minimum length."""

    def __init__(self, min: int, err: str | None = None):
        super().__init__(err)
        self.min = min

    def _validate(self, value: Any):
        if value is None:
            raise LengthError("Value is of None type.")
        if len(value) < self.min:
            raise LengthError(f"Minimum length is {self.min}.")


class MaxLength(Validator):
    """Validates that the value has at most the maximum length."""

    def __init__(self, max: int, err: str | None = None):
        super().__init__(err)
        self.max = max

    def _validate(self, value: Any):
        if value is None:
            raise LengthError("Value is of None type.")
        if len(value) > self.max:
            raise LengthError(f"Maximum length is {self.max}.")


class ExactLength(Validator):
    """Validates that the value has exactly the specified length."""

    def __init__(self, length: int, err: str | None = None):
        super().__init__(err)
        self.length = length

    def _validate(self, value: Any):
        if value is None:
            raise LengthError("Value is of None type.")
        if len(value) != self.length:
            raise LengthError(f"Length must be exactly {self.length}.")


class Length(Validator):
    """Compares whether the length of the value is within the given range."""

    def __init__(
        self, min: int | None = None, max: int | None = None, err: str | None = None
    ):
        super().__init__(err)
        self.min = min if min is not None else -inf
        self.max = max if max is not None else inf

    def _validate(self, value: Any):
        if value is None:
            raise LengthError("Value is of None type.")
        if len(value) < self.min:
            raise LengthError(f"Minimum length is {self.min}.")
        if len(value) > self.max:
            raise LengthError(f"Maximum length is {self.max}.")


class Value(Validator):
    """Compares whether the value is within the given range."""

    def __init__(
        self, min: int | None = None, max: int | None = None, err: str | None = None
    ):
        super().__init__(err)
        self.min = min if min is not None else -inf
        self.max = max if max is not None else inf

    def _validate(self, value: Any):
        if value is None:
            raise ValueRangeError("Value is of None type.")
        if value < self.min:
            raise ValueRangeError(f"Minimum value is {self.min}.")
        if value > self.max:
            raise ValueRangeError(f"Maximum value is {self.max}.")


class MinValue(Validator):
    """Validates that the value is at least the minimum value."""

    def __init__(self, min: int, err: str | None = None):
        super().__init__(err)
        self.min = min

    def _validate(self, value: Any):
        if value is None:
            raise ValueRangeError("Value is of None type.")
        if value < self.min:
            raise ValueRangeError(f"Minimum value is {self.min}.")


class MaxValue(Validator):
    """Validates that the value is at most the maximum value."""

    def __init__(self, max: int, err: str | None = None):
        super().__init__(err)
        self.max = max

    def _validate(self, value: Any):
        if value is None:
            raise ValueRangeError("Value is of None type.")
        if value > self.max:
            raise ValueRangeError(f"Maximum value is {self.max}.")


class ExactValue(Validator):
    """Validates that the value is exactly the given value."""

    def __init__(self, value: Any, err: str | None = None):
        super().__init__(err)
        self.value = value

    def _validate(self, value: Any):
        if value is None:
            raise ValueRangeError("Value is of None type.")
        if value != self.value:
            raise ValueRangeError(f"Value must be exactly {self.value}.")


class Regex(Validator):
    """Matches the given pattern to the value."""

    def __init__(self, pattern: str, err: str | None = None):
        super().__init__(err)
        self.pattern = pattern

    def _validate(self, value: Any):
        if not match(self.pattern, str(value)):
            raise RegexError("Value does not match pattern.")


class Email(Regex):
    """Extends the Regex() validator with the official RFC 5322 email regular expression."""

    def __init__(self, err: str | None = None):
        if err is None:
            err = "Invalid email address."
        super().__init__(
            r"""(?:[a-z0-9!#$%&'*+/=?^_`{|}~-]+(?:\.[a-z0-9!#$%&'*+/=?^_`{|}~-]+)*|"(?:[\x01-\x08\x0b\x0c\x0e-\x1f\x21\x23-\x5b\x5d-\x7f]|\\[\x01-\x09\x0b\x0c\x0e-\x7f])*")@(?:(?:[a-z0-9](?:[a-z0-9-]*[a-z0-9])?\.)+[a-z0-9](?:[a-z0-9-]*[a-z0-9])?|\[(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?|[a-z0-9-]*[a-z0-9]:(?:[\x01-\x08\x0b\x0c\x0e-\x1f\x21-\x5a\x53-\x7f]|\\[\x01-\x09\x0b\x0c\x0e-\x7f])+)\])""",
            err,
        )

    def _validate(self, value: Any):
        if not match(self.pattern, str(value)):
            raise EmailError(self.err)


class Alphanumeric(Regex):
    """Ensures the value is alphanumeric."""

    def __init__(self, err: str | None = None):
        if err is None:
            err = "Value must be alphanumeric."
        super().__init__(r"^[a-zA-Z0-9]+$", err)

    def _validate(self, value: Any):
        if not match(self.pattern, str(value)):
            raise AlphanumericError("Value must be alphanumeric.")


class URLType(Enum):
    DEFAULT = (
        r"/^(?:https?:\/\/)?(?:www\.)?(?:[A-Za-z0-9-]+\.)+[A-Za-z]{2,6}(?:\/\S*)?$/"
    )
    FORCEHTTP = r"/^https?:\/\/(?:www\.)?(?:[A-Za-z0-9-]+\.)+[A-Za-z]{2,6}(?:\/\S*)?$/"
    RFC3986 = r"""/^[a-z](?:[-a-z0-9\+\.])*:(?:\/\/(?:(?:%[0-9a-f][0-9a-f]|[-a-z0-9\._~\x{A0}-\x{D7FF}\x{F900}-\x{FDCF}\x{FDF0}-\x{FFEF}\x{10000}-\x{1FFFD}\x{20000}-\x{2FFFD}\x{30000}-\x{3FFFD}\x{40000}-\x{4FFFD}\x{50000}-\x{5FFFD}\x{60000}-\x{6FFFD}\x{70000}-\x{7FFFD}\x{80000}-\x{8FFFD}\x{90000}-\x{9FFFD}\x{A0000}-\x{AFFFD}\x{B0000}-\x{BFFFD}\x{C0000}-\x{CFFFD}\x{D0000}-\x{DFFFD}\x{E1000}-\x{EFFFD}!\$&\'\(\)\*\+,;=:])*@)?(?:\[(?:(?:(?:[0-9a-f]{1,4}:){6}(?:[0-9a-f]{1,4}:[0-9a-f]{1,4}|(?:[0-9]|[1-9][0-9]|1[0-9][0-9]|2[0-4][0-9]|25[0-5])(?:\.(?:[0-9]|[1-9][0-9]|1[0-9][0-9]|2[0-4][0-9]|25[0-5])){3})|::(?:[0-9a-f]{1,4}:){5}(?:[0-9a-f]{1,4}:[0-9a-f]{1,4}|(?:[0-9]|[1-9][0-9]|1[0-9][0-9]|2[0-4][0-9]|25[0-5])(?:\.(?:[0-9]|[1-9][0-9]|1[0-9][0-9]|2[0-4][0-9]|25[0-5])){3})|(?:[0-9a-f]{1,4})?::(?:[0-9a-f]{1,4}:){4}(?:[0-9a-f]{1,4}:[0-9a-f]{1,4}|(?:[0-9]|[1-9][0-9]|1[0-9][0-9]|2[0-4][0-9]|25[0-5])(?:\.(?:[0-9]|[1-9][0-9]|1[0-9][0-9]|2[0-4][0-9]|25[0-5])){3})|(?:[0-9a-f]{1,4}:[0-9a-f]{1,4})?::(?:[0-9a-f]{1,4}:){3}(?:[0-9a-f]{1,4}:[0-9a-f]{1,4}|(?:[0-9]|[1-9][0-9]|1[0-9][0-9]|2[0-4][0-9]|25[0-5])(?:\.(?:[0-9]|[1-9][0-9]|1[0-9][0-9]|2[0-4][0-9]|25[0-5])){3})|(?:(?:[0-9a-f]{1,4}:){0,2}[0-9a-f]{1,4})?::(?:[0-9a-f]{1,4}:){2}(?:[0-9a-f]{1,4}:[0-9a-f]{1,4}|(?:[0-9]|[1-9][0-9]|1[0-9][0-9]|2[0-4][0-9]|25[0-5])(?:\.(?:[0-9]|[1-9][0-9]|1[0-9][0-9]|2[0-4][0-9]|25[0-5])){3})|(?:(?:[0-9a-f]{1,4}:){0,3}[0-9a-f]{1,4})?::[0-9a-f]{1,4}:(?:[0-9a-f]{1,4}:[0-9a-f]{1,4}|(?:[0-9]|[1-9][0-9]|1[0-9][0-9]|2[0-4][0-9]|25[0-5])(?:\.(?:[0-9]|[1-9][0-9]|1[0-9][0-9]|2[0-4][0-9]|25[0-5])){3})|(?:(?:[0-9a-f]{1,4}:){0,4}[0-9a-f]{1,4})?::(?:[0-9a-f]{1,4}:[0-9a-f]{1,4}|(?:[0-9]|[1-9][0-9]|1[0-9][0-9]|2[0-4][0-9]|25[0-5])(?:\.(?:[0-9]|[1-9][0-9]|1[0-9][0-9]|2[0-4][0-9]|25[0-5])){3})|(?:(?:[0-9a-f]{1,4}:){0,5}[0-9a-f]{1,4})?::[0-9a-f]{1,4}|(?:(?:[0-9a-f]{1,4}:){0,6}[0-9a-f]{1,4})?::)|v[0-9a-f]+[-a-z0-9\._~!\$&\'\(\)\*\+,;=:]+)\]|(?:[0-9]|[1-9][0-9]|1[0-9][0-9]|2[0-4][0-9]|25[0-5])(?:\.(?:[0-9]|[1-9][0-9]|1[0-9][0-9]|2[0-4][0-9]|25[0-5])){3}|(?:%[0-9a-f][0-9a-f]|[-a-z0-9\._~\x{A0}-\x{D7FF}\x{F900}-\x{FDCF}\x{FDF0}-\x{FFEF}\x{10000}-\x{1FFFD}\x{20000}-\x{2FFFD}\x{30000}-\x{3FFFD}\x{40000}-\x{4FFFD}\x{50000}-\x{5FFFD}\x{60000}-\x{6FFFD}\x{70000}-\x{7FFFD}\x{80000}-\x{8FFFD}\x{90000}-\x{9FFFD}\x{A0000}-\x{AFFFD}\x{B0000}-\x{BFFFD}\x{C0000}-\x{CFFFD}\x{D0000}-\x{DFFFD}\x{E1000}-\x{EFFFD}!\$&\'\(\)\*\+,;=@])*)(?::[0-9]*)?(?:\/(?:(?:%[0-9a-f][0-9a-f]|[-a-z0-9\._~\x{A0}-\x{D7FF}\x{F900}-\x{FDCF}\x{FDF0}-\x{FFEF}\x{10000}-\x{1FFFD}\x{20000}-\x{2FFFD}\x{30000}-\x{3FFFD}\x{40000}-\x{4FFFD}\x{50000}-\x{5FFFD}\x{60000}-\x{6FFFD}\x{70000}-\x{7FFFD}\x{80000}-\x{8FFFD}\x{90000}-\x{9FFFD}\x{A0000}-\x{AFFFD}\x{B0000}-\x{BFFFD}\x{C0000}-\x{CFFFD}\x{D0000}-\x{DFFFD}\x{E1000}-\x{EFFFD}!\$&\'\(\)\*\+,;=:@]))*)*|\/(?:(?:(?:(?:%[0-9a-f][0-9a-f]|[-a-z0-9\._~\x{A0}-\x{D7FF}\x{F900}-\x{FDCF}\x{FDF0}-\x{FFEF}\x{10000}-\x{1FFFD}\x{20000}-\x{2FFFD}\x{30000}-\x{3FFFD}\x{40000}-\x{4FFFD}\x{50000}-\x{5FFFD}\x{60000}-\x{6FFFD}\x{70000}-\x{7FFFD}\x{80000}-\x{8FFFD}\x{90000}-\x{9FFFD}\x{A0000}-\x{AFFFD}\x{B0000}-\x{BFFFD}\x{C0000}-\x{CFFFD}\x{D0000}-\x{DFFFD}\x{E1000}-\x{EFFFD}!\$&\'\(\)\*\+,;=:@]))+)(?:\/(?:(?:%[0-9a-f][0-9a-f]|[-a-z0-9\._~\x{A0}-\x{D7FF}\x{F900}-\x{FDCF}\x{FDF0}-\x{FFEF}\x{10000}-\x{1FFFD}\x{20000}-\x{2FFFD}\x{30000}-\x{3FFFD}\x{40000}-\x{4FFFD}\x{50000}-\x{5FFFD}\x{60000}-\x{6FFFD}\x{70000}-\x{7FFFD}\x{80000}-\x{8FFFD}\x{90000}-\x{9FFFD}\x{A0000}-\x{AFFFD}\x{B0000}-\x{BFFFD}\x{C0000}-\x{CFFFD}\x{D0000}-\x{DFFFD}\x{E1000}-\x{EFFFD}!\$&\'\(\)\*\+,;=:@]))*)*)?|(?:(?:(?:%[0-9a-f][0-9a-f]|[-a-z0-9\._~\x{A0}-\x{D7FF}\x{F900}-\x{FDCF}\x{FDF0}-\x{FFEF}\x{10000}-\x{1FFFD}\x{20000}-\x{2FFFD}\x{30000}-\x{3FFFD}\x{40000}-\x{4FFFD}\x{50000}-\x{5FFFD}\x{60000}-\x{6FFFD}\x{70000}-\x{7FFFD}\x{80000}-\x{8FFFD}\x{90000}-\x{9FFFD}\x{A0000}-\x{AFFFD}\x{B0000}-\x{BFFFD}\x{C0000}-\x{CFFFD}\x{D0000}-\x{DFFFD}\x{E1000}-\x{EFFFD}!\$&\'\(\)\*\+,;=:@]))+)(?:\/(?:(?:%[0-9a-f][0-9a-f]|[-a-z0-9\._~\x{A0}-\x{D7FF}\x{F900}-\x{FDCF}\x{FDF0}-\x{FFEF}\x{10000}-\x{1FFFD}\x{20000}-\x{2FFFD}\x{30000}-\x{3FFFD}\x{40000}-\x{4FFFD}\x{50000}-\x{5FFFD}\x{60000}-\x{6FFFD}\x{70000}-\x{7FFFD}\x{80000}-\x{8FFFD}\x{90000}-\x{9FFFD}\x{A0000}-\x{AFFFD}\x{B0000}-\x{BFFFD}\x{C0000}-\x{CFFFD}\x{D0000}-\x{DFFFD}\x{E1000}-\x{EFFFD}!\$&\'\(\)\*\+,;=:@]))*)*|(?!(?:%[0-9a-f][0-9a-f]|[-a-z0-9\._~\x{A0}-\x{D7FF}\x{F900}-\x{FDCF}\x{FDF0}-\x{FFEF}\x{10000}-\x{1FFFD}\x{20000}-\x{2FFFD}\x{30000}-\x{3FFFD}\x{40000}-\x{4FFFD}\x{50000}-\x{5FFFD}\x{60000}-\x{6FFFD}\x{70000}-\x{7FFFD}\x{80000}-\x{8FFFD}\x{90000}-\x{9FFFD}\x{A0000}-\x{AFFFD}\x{B0000}-\x{BFFFD}\x{C0000}-\x{CFFFD}\x{D0000}-\x{DFFFD}\x{E1000}-\x{EFFFD}!\$&\'\(\)\*\+,;=:@])))(?:\?(?:(?:%[0-9a-f][0-9a-f]|[-a-z0-9\._~\x{A0}-\x{D7FF}\x{F900}-\x{FDCF}\x{FDF0}-\x{FFEF}\x{10000}-\x{1FFFD}\x{20000}-\x{2FFFD}\x{30000}-\x{3FFFD}\x{40000}-\x{4FFFD}\x{50000}-\x{5FFFD}\x{60000}-\x{6FFFD}\x{70000}-\x{7FFFD}\x{80000}-\x{8FFFD}\x{90000}-\x{9FFFD}\x{A0000}-\x{AFFFD}\x{B0000}-\x{BFFFD}\x{C0000}-\x{CFFFD}\x{D0000}-\x{DFFFD}\x{E1000}-\x{EFFFD}!\$&\'\(\)\*\+,;=:@])|[\x{E000}-\x{F8FF}\x{F0000}-\x{FFFFD}|\x{100000}-\x{10FFFD}\/\?])*)?(?:\#(?:(?:%[0-9a-f][0-9a-f]|[-a-z0-9\._~\x{A0}-\x{D7FF}\x{F900}-\x{FDCF}\x{FDF0}-\x{FFEF}\x{10000}-\x{1FFFD}\x{20000}-\x{2FFFD}\x{30000}-\x{3FFFD}\x{40000}-\x{4FFFD}\x{50000}-\x{5FFFD}\x{60000}-\x{6FFFD}\x{70000}-\x{7FFFD}\x{80000}-\x{8FFFD}\x{90000}-\x{9FFFD}\x{A0000}-\x{AFFFD}\x{B0000}-\x{BFFFD}\x{C0000}-\x{CFFFD}\x{D0000}-\x{DFFFD}\x{E1000}-\x{EFFFD}!\$&\'\(\)\*\+,;=:@])|[\/\?])*)?$/iu"""


class Url(Regex):
    """Validates that the value is a valid URL."""

    def __init__(self, type: URLType | None = None, err: str | None = None):
        if err is None:
            err = "Invalid URL."
        if type is None:
            type = URLType.DEFAULT
        super().__init__(str(type), err)

    def _validate(self, value: Any):
        if not match(self.pattern, str(value)):
            raise URLError(self.err)


class DateType(Enum):
    # YYYY-MM-DD (ISO 8601) - Year: 1900-2099, Month: 01-12, Day: 01-31
    ISO = r"^(19|20)\d{2}-(0[1-9]|1[0-2])-(0[1-9]|[12]\d|3[01])$"
    SLASH_US = r"^(0[1-9]|1[0-2])/(0[1-9]|[12]\d|3[01])/(19|20)\d{2}$"
    SLASH = r"^(0[1-9]|[12]\d|3[01])/(0[1-9]|1[0-2])/(19|20)\d{2}$"
    DASH_US = r"^(0[1-9]|1[0-2])-(0[1-9]|[12]\d|3[01])-(19|20)\d{2}$"
    DASH = r"^(0[1-9]|[12]\d|3[01])-(0[1-9]|1[0-2])-(19|20)\d{2}$"
    DOTS_US = r"^(0[1-9]|1[0-2])\.(0[1-9]|[12]\d|3[01])\.(19|20)\d{2}$"
    DOTS = r"^(0[1-9]|[12]\d|3[01])\.(0[1-9]|1[0-2])\.(19|20)\d{2}$"
    COMPACT = r"^(19|20)\d{2}(0[1-9]|1[0-2])(0[1-9]|[12]\d|3[01])$"
    DATETIME_ISO = r"^(19|20)\d{2}-(0[1-9]|1[0-2])-(0[1-9]|[12]\d|3[01])T([01]\d|2[0-3]):([0-5]\d):([0-5]\d)$"
    DATETIME_SPACE = r"^(19|20)\d{2}-(0[1-9]|1[0-2])-(0[1-9]|[12]\d|3[01]) ([01]\d|2[0-3]):([0-5]\d):([0-5]\d)$"


class Date(Regex):
    """Validates that the value matches a specified date format with range validation."""

    def __init__(self, type: DateType | None = None, err: str | None = None):
        if err is None:
            err = "Invalid date format."
        if type is None:
            type = DateType.ISO
        super().__init__(type.value, err)

    def _validate(self, value: Any):
        if not match(self.pattern, str(value)):
            raise DateError(self.err)


class NotEmpty(Validator):
    """Validates that the value is not empty."""

    def __init__(self, err: str | None = None):
        super().__init__(err)

    def _validate(self, value: Any):
        if not value:
            raise EmptyValueError("Value cannot be empty.")


class Truthy(Validator):
    """Validates that the value is truthy."""

    def __init__(self, err: str | None = None):
        super().__init__(err)

    def _validate(self, value: Any):
        if not value:
            raise NotTruthyError("Value cannot be falsy.")


class Falsy(Validator):
    """Validates that the value is falsy."""

    def __init__(self, err: str | None = None):
        super().__init__(err)

    def _validate(self, value: Any):
        if value:
            raise NotFalsyError("Value cannot be truthy.")
