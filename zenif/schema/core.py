from typing import Dict, Any, TYPE_CHECKING

if TYPE_CHECKING:
    from .fields import Field


class Schema:
    def __init__(self, fields: Dict[str, "Field"]):
        self.fields = fields

    def validate(self, data: Dict[str, Any]) -> "ValidationResult":
        errors = {}
        for field_name, field in self.fields.items():
            if field_name not in data:
                if field.required:
                    errors[field_name] = "This field is required."
            else:
                try:
                    field.validate(data[field_name])
                except ValueError as e:
                    errors[field_name] = str(e)
        return ValidationResult(not bool(errors), errors)


class ValidationResult:
    def __init__(self, is_valid: bool, errors: Dict[str, str] = None):
        self.is_valid = is_valid
        self.errors = errors or {}
