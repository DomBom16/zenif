from __future__ import annotations
from typing import Any, Callable, Generic, TypeVar, Union

T = TypeVar("T")


class Validator:
    def __call__(self, value: Any):
        self.validate(value)

    def validate(self, value: Any):
        raise NotImplementedError()


class SchemaField(Generic[T]):
    def __init__(self):
        self._name: str | None = None
        self.validators: list[Validator] = []
        self._default: Any | None = None
        self.is_required: bool = True

    def name(self, name: str) -> SchemaField[T]:
        self._name = name
        return self

    def has(self, validator: Validator) -> SchemaField[T]:
        self.validators.append(validator)
        return self

    def default(self, value: Union[T, Callable[[], T]]) -> SchemaField[T]:
        self._default = value
        self.is_required = False
        return self

    def optional(self) -> SchemaField[T]:
        self.is_required = False
        return self

    def coerce(self, value: Any) -> T:
        return value  # Default implementation, subclasses should override if needed


class Schema:
    def __init__(self, **fields: SchemaField):
        self.fields = fields
        self._strict = False
        self._all_optional = False

    def strict(self, value: bool = True) -> Schema:
        self._strict = value
        return self

    def all_optional(self) -> Schema:
        self._all_optional = True
        return self

    def validate(self, data: dict) -> tuple[bool, dict[str, list[str]], dict]:
        is_valid = True
        errors: dict[str, list[str]] = {}
        coerced_data = {}

        for field_name, field in self.fields.items():
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

                    field_errors = []
                    for validator in field.validators:
                        try:
                            validator(value)
                        except ValueError as e:
                            is_valid = False
                            field_errors.append(str(e))

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
