from __future__ import annotations

from typing import Any, Callable, Generic, TypeVar

from .exceptions import ValidationError

T = TypeVar("T")


class Condition:
    def __init__(self, condition: Callable[[dict], bool], error_message: str):
        self.condition = condition
        self.error_message = error_message

    def check(self, data: dict) -> bool:
        return self.condition(data)


class Validator:
    def __init__(self, err: str | None = None):
        if err:
            self.err = f"{err}{'' if err.endswith('.') else '.'}"
        else:
            self.err = ""

    def __call__(self, value: Any) -> Any:
        self.validate(value=value)

    def validate(self, value: Any):
        try:
            self._validate(value)
        except Exception as e:
            # If a custom error message was provided via err, use it
            if self.err:
                if isinstance(e, ValidationError):
                    raise type(e)(self.err) from e
                else:
                    raise ValidationError(self.err) from e
            else:
                if isinstance(e, ValidationError):
                    raise
                raise ValidationError(str(e)) from e

    def _validate(self, value: Any):
        raise NotImplementedError()


class SchemaField(Generic[T]):
    def __init__(self):
        self._default: Any | None = None
        self.validators: list[Validator] = []
        self.is_required: bool = True
        self.condition: Condition | None = None
        self.pre_transform: Callable[[Any], Any] | None = None
        self.post_transform: Callable[[T], Any] | None = None

    def has(self, validator: Validator) -> SchemaField[T]:
        self.validators.append(validator)
        return self

    def when(
        self, condition: Callable[[dict], bool], error_message: str
    ) -> "SchemaField[T]":
        self.condition = Condition(condition, error_message)
        return self

    def default(self, value: T | Callable[[], T] | None) -> SchemaField[T]:
        if value is not None:
            self._default = value if callable(value) else lambda: value
        self.is_required = False
        return self

    def pre(self, func: Callable[[Any], Any]) -> "SchemaField[T]":
        self.pre_transform = func
        return self

    def post(self, func: Callable[[T], Any]) -> "SchemaField[T]":
        self.post_transform = func
        return self

    def coerce(self, value: Any) -> T | None:
        return value  # Default implementation, subclasses should override if needed


class Schema:
    def __init__(self, fields: dict[str, SchemaField]):
        """A class for validating and coercing data based on a schema.

        The schema is initialized with a dictionary of fields.
        """
        self.fields = fields
        self._strict = False

    def strict(self, value: bool = True) -> Schema:
        """Set strict mode to True or False."""
        self._strict = value
        return self

    def validate(
        self, data: dict, partial: bool = False
    ) -> tuple[bool, dict[str, list[tuple[str, str]]], dict]:
        """Validate data against the schema.

        Args:
            data (dict): The data to validate.
            partial (bool): If True, only validate fields present in the data.

        Returns:
            tuple[bool, dict[str, list[tuple[str, str]]], dict]: A tuple containing a boolean indicating whether the data is valid, a dictionary of field errors, and a dictionary of coerced data.
        """
        is_valid = True
        errors: dict[str, list[tuple[str, str]]] = {}
        coerced_data = {}

        for field_name, field in self.fields.items():
            if not field.__class__.__name__.endswith("F"):
                raise SyntaxError(
                    f'Field {field.__class__.__name__} name must end with "F".'
                )
            if field.condition:
                if not field.condition.check(data):
                    continue  # Skip this field if the condition is not met
            if field_name not in data:
                if partial:
                    continue
                if field.is_required:
                    is_valid = False
                    errors[field_name] = [("ValidationError", "Field is required.")]
                elif field._default is not None:
                    coerced_data[field_name] = (
                        field._default() if callable(field._default) else field._default
                    )
                continue
            else:
                try:
                    value = data[field_name]

                    if not self._strict:
                        value = field.coerce(value)

                    if field.pre_transform:
                        value = field.pre_transform(value)

                    field_errors: list[tuple[str, str]] = []
                    for validator in field.validators:
                        try:
                            validator(value)
                        except ValidationError as e:
                            is_valid = False
                            field_errors.append((e.__class__.__name__, e.message))

                    if field.post_transform:
                        value = field.post_transform(value)

                    if field_errors:
                        errors[field_name] = field_errors
                    else:
                        coerced_data[field_name] = value
                except Exception as e:
                    is_valid = False
                    errors[field_name] = [("Exception", str(e))]

        if self._strict:
            extra_fields = set(data.keys()) - set(self.fields.keys())
            if extra_fields:
                is_valid = False
                errors["__extra__"] = [
                    (
                        "StrictValidationError",
                        f"Unexpected fields: {', '.join(extra_fields)}",
                    )
                ]

        return is_valid, errors, coerced_data
