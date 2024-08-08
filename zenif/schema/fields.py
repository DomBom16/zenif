from typing import Any, List as ListType, TYPE_CHECKING
import re
from .validators import Validator

if TYPE_CHECKING:
    from .core import Schema


class Field:
    def __init__(self, validators: ListType[Validator] = None, required: bool = True):
        self.validators = validators or []
        self.required = required

    def validate(self, value: Any):
        for validator in self.validators:
            validator(value)
        self._validate(value)

    def _validate(self, value: Any):
        pass  # To be overridden by subclasses


class String(Field):
    def __init__(self, validators=None):
        super().__init__(validators)

    def _validate(self, value):
        if not isinstance(value, str):
            raise ValueError("Must be a string.")
        for validator in self.validators:
            validator(value)


class Integer(Field):
    def _validate(self, value: Any):
        if not isinstance(value, int):
            raise ValueError("Must be an integer.")


class Float(Field):
    def _validate(self, value: Any):
        if not isinstance(value, (float, int)):
            raise ValueError("Must be a float.")


class Boolean(Field):
    def _validate(self, value: Any):
        if not isinstance(value, bool):
            raise ValueError("Must be a boolean.")


class List(Field):
    def __init__(self, item_field: Field, **kwargs):
        super().__init__(**kwargs)
        self.item_field = item_field

    def _validate(self, value: Any):
        if not isinstance(value, list):
            raise ValueError("Must be a list.")
        for item in value:
            self.item_field.validate(item)


class Dict(Field):
    def __init__(self, schema: "Schema", **kwargs):
        super().__init__(**kwargs)
        self.schema = schema

    def _validate(self, value: Any):
        if not isinstance(value, dict):
            raise ValueError("Must be a dictionary.")
        result = self.schema.validate(value)
        if not result.is_valid:
            raise ValueError(f"Dict validation failed: {result.errors}")


class Email(Field):
    def _validate(self, value: Any):
        if not isinstance(value, str):
            raise ValueError("Must be a string.")
        email_regex = r"""(?:[a-z0-9!#$%&'*+/=?^_`{|}~-]+(?:\.[a-z0-9!#$%&'*+/=?^_`{|}~-]+)*|"(?:[\x01-\x08\x0b\x0c\x0e-\x1f\x21\x23-\x5b\x5d-\x7f]|\\[\x01-\x09\x0b\x0c\x0e-\x7f])*")@(?:(?:[a-z0-9](?:[a-z0-9-]*[a-z0-9])?\.)+[a-z0-9](?:[a-z0-9-]*[a-z0-9])?|\[(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?|[a-z0-9-]*[a-z0-9]:(?:[\x01-\x08\x0b\x0c\x0e-\x1f\x21-\x5a\x53-\x7f]|\\[\x01-\x09\x0b\x0c\x0e-\x7f])+)\])"""
        if not re.match(email_regex, value):
            raise ValueError("Must be a valid email address.")
