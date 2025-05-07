class ValidationError(Exception):
    def __init__(self, message: str):
        """Base class for validation errors."""
        self.message = message
        super().__init__(message)


class StrictValidationError(ValidationError):
    """Base class for strict validation errors."""

    pass


class LengthError(ValidationError):
    """Base class for length errors."""

    pass


class ValueRangeError(ValidationError):
    """Base class for value range errors."""

    pass


class RegexError(ValidationError):
    """Base class for regex errors."""

    pass


class EmailError(RegexError):
    """Base class for email errors."""

    pass


class AlphanumericError(RegexError):
    """Base class for alphanumeric errors."""

    pass


class URLError(RegexError):
    """Base class for URL errors."""

    pass


class DateError(RegexError):
    """Base class for date errors."""

    pass


class EmptyValueError(ValidationError):
    """Base class for empty value errors."""

    pass


class NotTruthyError(ValidationError):
    """Base class for not truthy errors."""

    pass


class NotFalsyError(ValidationError):
    """Base class for not falsy errors."""

    pass
