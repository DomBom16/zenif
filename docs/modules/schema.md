# Schema Module

The Zenif Schema module provides a powerful and flexible way to define data structures and validate input. It allows you to create schemas for your data, validate inputs against these schemas, and integrate with other Zenif modules for robust data handling.

## Table of Contents

- [Schema Module](#schema-module)
  - [Table of Contents](#table-of-contents)
  - [Basic Usage](#basic-usage)
  - [Available Field Types](#available-field-types)
  - [Validators](#validators)
  - [Integration with CLI Module](#integration-with-cli-module)
  - [More Usage](#more-usage)
    - [List Validation](#list-validation)
    - [Optional Fields and Default Values](#optional-fields-and-default-values)
    - [Enum Fields](#enum-fields)
  - [Error Handling](#error-handling)
  - [SchemaField Methods](#schemafield-methods)
    - [`.has(validator)`](#hasvalidator)
    - [`.default(value)`](#defaultvalue)
    - [`.when(condition, error_message)`](#whencondition-error_message)
    - [`.pre(func)`](#prefunc)
    - [`.post(func)`](#postfunc)
    - [Method Chaining](#method-chaining)
    - [Complete Example](#complete-example)
  - [Coercion](#coercion)

## Basic Usage

Here's a simple example of how to create and use a schema:

```python
from zenif.schema import Schema, StringF, IntegerF, ListF, Length, Value

user_schema = Schema({
    "name": StringF().has(Length(min=3, max=50)),
    "age": IntegerF().has(Value(min=18, max=120)),
    "interests": ListF().items(StringF()).has(Length(min=1))
})

# Validating data
valid_data = {
    'name': 'John Doe',
    'age': 30,
    'interests': ['coding', 'reading']
}

is_valid, errors, coerced_data = user_schema.validate(valid_data)
print(is_valid)
# True
print(errors)
# {}

invalid_data = {
    'name': 'Jo',
    'age': 246,
    'interests': []
}

is_valid, errors, coerced_data = user_schema.validate(invalid_data)
print(is_valid)
# False
print(errors)
# {'name': [('LengthError', 'Minimum length is 3.')], 'age': [('ValueRangeError', 'Maximum value is 120.')], 'interests': [('LengthError', 'Minimum length is 1.')]}
```

## Available Field Types

- `StringF`: For text data
- `IntegerF`: For whole numbers
- `FloatF`: For decimal numbers
- `BooleanF`: For true/false values
- `ListF`: For lists of items
- `DictF`: For nested structures
- `DateF`: For date/time values
- `EnumF`: For enumerated values

Although you should avoid it, if you ever need to create a new field type, simply extend the SchemaField class:

```python
from zenif.schema import SchemaField

class MyTypeF(SchemaField[MyType]):
    ...

    def coerce(self, value: any) -> MyType:
        return ...
```

When creating a field, your class name should be in the `{type}F` format, where the type name is followed by the letter "F".

## Validators

Validators are used to apply specific rules to fields. Zenif's built-in validators include:

- `Length(min=None, max=None)`: Ensures a minimum and maximum length for strings or lists
- `MinLength(min)`: Ensures a minimum length for strings or lists
- `MaxLength(max)`: Ensures a maximum length for strings or lists
- `ExactLength(length)`: Ensures the field is exactly the specified length for strings or lists
- `Value(min=None, max=None)`: Ensures a minimum and maximum value for numbers
- `MinValue(min)`: Ensures a minimum value for numbers
- `MaxValue(max)`: Ensures a maximum value for numbers
- `ExactValue(value)`: Ensures the field is exactly the specified value for numbers
- `Regex(pattern)`: Validates strings against a regular expression
- `Email()`: Validates email addresses
- `Date()`: Ensures the field is in the format YYYY-MM-DD
- `Alphanumeric()`: Ensures the field only contains letters and numbers
- `Url()`: Validates URL addresses
- `NotEmpty()`: Ensures the field is not empty
- `Truthy()`: Ensures a value is truthy
- `Falsy()`: Ensures a value is falsy

The `Url` validator supports different validation types through the `URLType` enum:

- `URLType.DEFAULT`: Basic URL validation (allows with or without protocol)
- `URLType.FORCEHTTP`: Requires http:// or https:// protocol
- `URLType.RFC3986`: Full RFC 3986 compliant validation

```python
from zenif.schema import Url, URLType

# Basic URL validation
url_field = StringF().has(Url())

# Force HTTP/HTTPS protocol
strict_url_field = StringF().has(Url(type=URLType.FORCEHTTP))

# RFC 3986 compliant validation
rfc_url_field = StringF().has(Url(type=URLType.RFC3986))
```

You can also create custom validators by extending the base `Validator` class.

> [!NOTE]
> When your custom validator extends the `Validator` class, its `__call__` method automatically wraps any exceptions thrown in the `validate` method. This ensures that any error raised is an instance of `ValidationError` or one of its subclasses, which maintains consistent error handling across the schema. For example:

```python
from zenif.schema import Validator

class OddOrEven(Validator):
    def __init__(self, parity: str = "even", err: str | None = None):
        super().__init__(err)
        self.parity = 1 if parity.lower() == "odd" else 0

    def validate(self, value):
        if value % 2 != self.parity:
            # Even if a different type of error is raised, the base Validator wraps it as a ValidationError
            raise ValueError(f"Must be an {'even' if self.parity == 0 else 'odd'} number.")
```

In addition, Zenif also provides more specific exceptions that extend `ValidationError`, such as:

- `LengthError`
- `ValueRangeError`
- `RegexError`
- `EmailError`
- `AlphanumericError`
- `URLError`
- `DateError`
- `EmptyValueError`
- `NotTruthyError`
- `NotFalsyError`

These exceptions allow for more granular error handling and clearer messages.

## Integration with CLI Module

The Schema module integrates seamlessly with Zenif's CLI module, allowing for robust input validation in interactive prompts.

```python
from zenif.cli import Prompt
from zenif.schema import Schema, StringF, IntegerF, Length, Value

user_schema = Schema({
    "name": StringF().has(Length(min=3, max=50)),
    "age": IntegerF().has(Value(min=18, max=120))
})

name = Prompt.text("Enter your name", schema=user_schema, id="name").ask()
age = Prompt.number("Enter your age", schema=user_schema, id="age").ask()

print(f"Name: {name}")
print(f"Age: {age}")
```

In this example, the prompts will enforce the schema rules, ensuring that the name is between 3 and 50 characters, and the age is between 18 and 120.

## More Usage

### List Validation

You can validate lists of items:

```python
tags_schema = Schema({ "tags": ListF().items(StringF()).has(Length(min=3)) })
```

This schema ensures that 'tags' is a list of strings with at least 3 items.

### Optional Fields and Default Values

You can make fields optional or provide default values:

```python
user_schema = Schema(
    name=StringF().name("name"),
    age=IntegerF().name("age").default(),
    is_active=BooleanF().name("is_active").default(True)
)
```

### Enum Fields

You can use enumerated values:

```python
from enum import Enum

class UserRole(Enum):
    USER = "user"
    ADMIN = "admin"

user_schema = Schema(
    name=StringF().name("name"),
    role=EnumF().name("role").enum(UserRole).default(UserRole.USER)
)
```

## Error Handling

When validation fails, the `validate` method returns a tuple `(is_valid, errors, coerced_data)`:

- **`is_valid`**: A boolean indicating whether the validation passed.
- **`errors`**: A dictionary containing detailed error messages for each invalid field. Errors are now returned as tuples in the form `(ErrorClass, message)`, ensuring that you can programmatically distinguish between different types of validation errors.
- **`coerced_data`**: A dictionary containing the validated and coerced data.

For example, if a field fails a length check, the error might look like `('LengthError', 'Minimum length is 3')`.

## SchemaField Methods

All field types inherit from the `SchemaField` base class, which provides several methods for configuring field behavior:

### `.has(validator)`

Adds a validator to the field. Validators are applied in the order they are added.

```python
from zenif.schema import StringF, Length, Email

email_field = StringF().has(Length(min=5)).has(Email())
```

### `.default(value)`

Sets a default value for the field and makes it optional. The value can be a static value or a callable that returns a value.

```python
from zenif.schema import StringF, IntegerF
from datetime import datetime

# Static default value
name_field = StringF().default("Anonymous")

# Callable default value
timestamp_field = IntegerF().default(lambda: int(datetime.now().timestamp()))

# No default (None)
optional_field = StringF().default(None)
```

### `.when(condition, error_message)`

Adds a conditional requirement based on other fields in the schema. The field is only validated if the condition returns `True`.

```python
from zenif.schema import Schema, StringF, BooleanF

user_schema = Schema({
    "is_admin": BooleanF(),
    "admin_code": StringF().when(
        lambda data: data.get("is_admin", False),
        "Admin code is required when is_admin is True"
    )
})
```

### `.pre(func)`

Adds a pre-transformation function that modifies the value before validation. This is useful for normalizing input data.

```python
from zenif.schema import StringF

# Convert to lowercase before validation
username_field = StringF().pre(lambda x: x.lower() if isinstance(x, str) else x)

# Strip whitespace
text_field = StringF().pre(lambda x: x.strip() if isinstance(x, str) else x)
```

### `.post(func)`

Adds a post-transformation function that modifies the value after validation. This is useful for formatting output data.

```python
from zenif.schema import StringF

# Convert to title case after validation
name_field = StringF().post(lambda x: x.title())

# Add prefix to the value
code_field = StringF().post(lambda x: f"CODE_{x}")
```

### Method Chaining

All SchemaField methods return the field instance, allowing for method chaining:

```python
from zenif.schema import StringF, Length, Email

email_field = (StringF()
    .pre(lambda x: x.lower().strip())
    .has(Length(min=5, max=100))
    .has(Email())
    .default("user@example.com")
    .post(lambda x: x.lower()))
```

### Complete Example

Here's a comprehensive example using multiple SchemaField methods:

```python
from datetime import datetime

from zenif.schema import (
    BooleanF,
    Email,
    IntegerF,
    Length,
    Regex,
    Schema,
    StringF,
    Value,
)

user_schema = Schema(
    {
        "username": (
            StringF()
            .pre(lambda x: x.strip().lower())
            .has(Length(min=3, max=20))
            .post(lambda x: x if x.startswith("@") else f"@{x}")
        ),
        "email": (
            StringF()
            .pre(lambda x: x.strip().lower())
            .has(Email())
            .default("user@example.com")
        ),
        "age": IntegerF().has(Value(min=0, max=120)).default(18),
        "is_premium": BooleanF().default(False),
        "premium_code": (
            StringF()
            .pre(lambda x: x.strip().lower().replace("-", ""))
            .when(
                lambda data: data.get("is_premium", False),
                "Premium code required for premium users",
            )
            .default("")
            .has(Regex(r"^[a-z]{4}[a-z]{4}[a-z]{4}$", err="Invalid format."))
        ),
        "created_at": IntegerF().default(lambda: int(datetime.now().timestamp())),
    }
)

# Validate data
data = {
    "username": "  JohnDoe  ",
    "email": "  JOHN@EXAMPLE.COM  ",
    "age": 25,
    "is_premium": True,
    "premium_code": "JGUI-PYBF-WSMN",
}

is_valid, errors, coerced_data = user_schema.validate(data)
print(coerced_data)
# Output: {
#     'username': '@johndoe',
#     'email': 'john@example.com',
#     'age': 25,
#     'is_premium': True,
#     'premium_code': "jguipybfwsmn",
#     'created_at': 1640995200
# }
```

## Coercion

By default, the Schema module attempts to coerce input data to the correct types. You can disable this behavior by setting the schema to strict mode:

```python
is_valid, errors, coerced_data = user_schema.strict().validate(data)
```

In strict mode, type mismatches will result in validation errors instead of attempting coercion.
