from re import match


class Validator:
    def __call__(self, value: any):
        self.validate(value)

    def validate(self, value: any):
        raise NotImplementedError()


class MinLength:
    def __init__(self, min_length):
        self.min_length = min_length

    def __call__(self, value):
        if len(value or "") < self.min_length:
            raise ValueError(f"Minimum length is {self.min_length}.")


class MaxLength:
    def __init__(self, max_length):
        self.max_length = max_length

    def __call__(self, value):
        if len(value or "") > self.max_length:
            raise ValueError(f"Maximum length is {self.max_length}.")


class MinValue(Validator):
    def __init__(self, min_value: float):
        self.min_value = min_value

    def validate(self, value: any):
        if value < self.min_value:
            raise ValueError(f"Minimum value is {self.min_value}.")


class MaxValue(Validator):
    def __init__(self, max_value: float):
        self.max_value = max_value

    def validate(self, value: any):
        if value > self.max_value:
            raise ValueError(f"Maximum value is {self.max_value}.")


class Regex(Validator):
    def __init__(self, pattern: str):
        self.pattern = pattern

    def validate(self, value: any):
        if not match(self.pattern, value):
            raise ValueError(f"Value does not match pattern.")
