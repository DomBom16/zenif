from __future__ import annotations

from ast import literal_eval
from datetime import datetime
from enum import Enum
from typing import Any

from .core import SchemaField


class StringF(SchemaField[str]):
    def coerce(self, value: Any) -> str:
        try:
            return str(value)
        except Exception:
            # Fallback: return an empty string on conversion failure
            return ""


class IntegerF(SchemaField[int]):
    def coerce(self, value: Any) -> int:
        try:
            # Attempt to convert to float first to handle numeric strings
            return int(float(value))
        except Exception:
            # Fallback: return 0 on conversion failure
            return 0


class FloatF(SchemaField[float]):
    def coerce(self, value: Any) -> float:
        try:
            return float(value)
        except Exception:
            # Fallback: return 0.0 on conversion failure
            return 0.0


class BooleanF(SchemaField[bool]):
    def coerce(self, value: Any) -> bool:
        try:
            if isinstance(value, str):
                if value.lower() in ("true", "1", "yes"):
                    return True
                else:
                    return False
            return bool(value)
        except Exception:
            # Fallback: return False on conversion failure
            return False


class DateF(SchemaField[datetime]):
    def coerce(self, value: Any) -> datetime | None:
        try:
            if isinstance(value, str):
                return datetime.fromisoformat(value)
            if isinstance(value, (int, float)):
                return datetime.fromtimestamp(value)
            if isinstance(value, list):
                return datetime(*value)
            if isinstance(value, tuple):
                return datetime(*value)
            if isinstance(value, datetime):
                return value
            # Fallback: return None if no valid conversion is possible
            return None
        except Exception:
            # Fallback: return None on conversion failure
            return None


class EnumF(SchemaField[Enum]):
    def __init__(self):
        super().__init__()
        self._enum_class: type[Enum] | None = None

    def enum(self, enum_class: type[Enum]) -> EnumF:
        self._enum_class = enum_class
        return self

    def coerce(self, value: Any) -> Enum | None:
        if self._enum_class is None:
            return None
        try:
            if isinstance(value, str):
                return self._enum_class[value.upper()]
            return self._enum_class(value)
        except Exception:
            # Fallback: return None on conversion failure
            return None


class ListF(SchemaField[list]):
    def __init__(self):
        super().__init__()
        self._item_type: SchemaField | None = None

    def items(self, item_type: SchemaField) -> ListF:
        self._item_type = item_type
        return self

    def coerce(self, value: Any) -> list:
        try:
            if isinstance(value, str):
                value = literal_eval(value)
            if not isinstance(value, list):
                value = [value]
            if self._item_type:
                return [self._item_type.coerce(item) for item in value]
            return value
        except Exception:
            # Fallback: return an empty list on conversion failure
            return []


class DictF(SchemaField[dict]):
    def __init__(self):
        super().__init__()
        self._key_type: SchemaField | None = None
        self._value_type: SchemaField | None = None

    def keys(self, key_type: SchemaField) -> DictF:
        self._key_type = key_type
        return self

    def values(self, value_type: SchemaField) -> DictF:
        self._value_type = value_type
        return self

    def coerce(self, value: Any) -> dict:
        try:
            if isinstance(value, str):
                value = literal_eval(value)
            if not isinstance(value, dict):
                # Fallback: if value is not a dict, return an empty dict
                return {}
            if self._key_type and self._value_type:
                return {
                    self._key_type.coerce(k): self._value_type.coerce(v)
                    for k, v in value.items()
                }
            return value
        except Exception:
            # Fallback: return an empty dict on conversion failure
            return {}
