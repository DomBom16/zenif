from __future__ import annotations

from .core import SchemaField

from enum import Enum
from datetime import datetime
from ast import literal_eval


class StringF(SchemaField[str]):
    def coerce(self, value: any) -> str:
        return str(value)


class IntegerF(SchemaField[int]):
    def coerce(self, value: any) -> int:
        return int(float(value))


class FloatF(SchemaField[float]):
    def coerce(self, value: any) -> float:
        return float(value)


class BooleanF(SchemaField[bool]):
    def coerce(self, value: any) -> bool:
        return bool(value)


class DateF(SchemaField[datetime]):
    def coerce(self, value: any) -> datetime:
        if isinstance(value, str):
            return datetime.fromisoformat(value)
        return value


class EnumF(SchemaField[Enum]):
    def __init__(self):
        super().__init__()
        self._enum_class: type[Enum] | None = None

    def enum_class(self, enum_class: type[Enum]) -> EnumF:
        self._enum_class = enum_class
        return self

    def coerce(self, value: any) -> Enum:
        if self._enum_class is None:
            raise ValueError("Enum class not set")
        if isinstance(value, str):
            return self._enum_class[value.upper()]
        return self._enum_class(value)


class ListF(SchemaField[list]):
    def __init__(self):
        super().__init__()
        self._item_type: SchemaField | None = None

    def item_type(self, item_type: SchemaField) -> ListF:
        self._item_type = item_type
        return self

    def coerce(self, value: any) -> list:
        if isinstance(value, str):
            value = literal_eval(value)
        if not isinstance(value, list):
            value = [value]
        if self._item_type:
            return [self._item_type.coerce(item) for item in value]
        return value


class DictF(SchemaField[dict]):
    def __init__(self):
        super().__init__()
        self._key_type: SchemaField | None = None
        self._value_type: SchemaField | None = None

    def key_type(self, key_type: SchemaField) -> DictF:
        self._key_type = key_type
        return self

    def value_type(self, value_type: SchemaField) -> DictF:
        self._value_type = value_type
        return self

    def coerce(self, value: any) -> dict:
        if isinstance(value, str):
            value = literal_eval(value)
        if not isinstance(value, dict):
            raise ValueError("Cannot coerce to dict")
        if self._key_type and self._value_type:
            return {
                self._key_type.coerce(k): self._value_type.coerce(v)
                for k, v in value.items()
            }
        return value
