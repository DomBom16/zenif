from __future__ import annotations
from typing import Callable, Generic, TypeVar

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
            self.err = f"{err}{"" if err.endswith(".") else "."}"
        else:
            self.err = ""

    def __call__(self, value: any) -> any:
        self.validate(value=value)

    def validate(self, value: any):
        try:
            self._validate(value)
        except ValueError as e:
            if self.err:
                raise ValueError(self.err)
            else:
                raise e
            raise e

    def _validate(self, value: any):
        raise NotImplementedError()


class SchemaField(Generic[T]):
    def __init__(self):
        self._name: str | None = None
        self._default: any | None = None

        self.validators: list[Validator] = []

        self.is_required: bool = True

        self.condition: Condition | None = None
        self.pre_transform: Callable[[any], any] | None = None
        self.post_transform: Callable[[T], any] | None = None

    def name(self, name: str) -> SchemaField[T]:
        self._name = name
        return self

    def has(self, validator: Validator) -> SchemaField[T]:
        self.validators.append(validator)
        return self

    def when(
        self, condition: Callable[[dict], bool], error_message: str
    ) -> "SchemaField[T]":
        self.condition = Condition(condition, error_message)
        return self

    def default(self, value: T | Callable[[], T]) -> SchemaField[T]:
        self._default = value
        self.is_required = False
        return self

    def optional(self) -> SchemaField[T]:
        self.is_required = False
        return self

    def pre(self, func: Callable[[any], any]) -> "SchemaField[T]":
        self.pre_transform = func
        return self

    def post(self, func: Callable[[T], any]) -> "SchemaField[T]":
        self.post_transform = func
        return self

    def coerce(self, value: any) -> T:
        return value  # Default implementation, subclasses should override if needed


class Schema:
    def __init__(self, **fields: SchemaField):
        """A class for validating and coercing data based on a schema."""

        self.fields = fields
        self._strict = False
        self._all_optional = False

    def strict(self, value: bool = True) -> Schema:
        """Set strict mode to True or False."""
        self._strict = value
        return self

    def all_optional(self) -> Schema:
        """Mark all fields as optional."""
        self._all_optional = True
        return self

    def validate(self, data: dict) -> tuple[bool, dict[str, list[str]], dict]:
        """Validate data against the schema.

        Args:
            data (dict): The data to validate.

        Raises:
            SyntaxError: If a field name does not end with "F".

        Returns:
            tuple[bool, dict[str, list[str]], dict]: A tuple containing a boolean indicating whether the data is valid, a dictionary of field errors, and finally a dictionary of coerced data.
        """
        is_valid = True
        errors: dict[str, list[str]] = {}
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
                if field.is_required and not self._all_optional:
                    is_valid = False
                    errors[field_name] = ["This field is required."]
                elif field._default is not None:
                    coerced_data[field_name] = (
                        field._default() if callable(field._default) else field._default
                    )
            else:
                try:
                    value = data[field_name]

                    if not self._strict:
                        value = field.coerce(value)

                    if field.pre_transform:
                        value = field.pre_transform(value)

                    field_errors = []
                    for validator in field.validators:
                        try:
                            validator(value)
                        except ValueError as e:
                            is_valid = False
                            field_errors.append(str(e))

                    if field.post_transform:
                        value = field.post_transform(value)

                    if field_errors:
                        errors[field_name] = field_errors
                    else:
                        coerced_data[field_name] = value
                except Exception as e:
                    is_valid = False
                    errors[field_name] = [str(e)]

        if self._strict:
            extra_fields = set(data.keys()) - set(self.fields.keys())
            if extra_fields:
                is_valid = False
                errors["__extra__"] = [f"Unexpected fields: {', '.join(extra_fields)}"]

        return is_valid, errors, coerced_data
