from zenif.schema import (
    Schema,
    String,
    Integer,
    List,
    Email,
    MinLength,
    MaxLength,
    MaxValue,
)

user_schema = Schema(
    {
        "username": String(validators=[MinLength(3)]),
        "email": Email(),
        "age": Integer(validators=[MaxValue(120)]),
        "interests": List(String(), validators=[MaxLength(5)]),
    }
)

data = {
    "username": "johndoe",
    "email": "john@example.com",
    "age": 30,
    "interests": ["coding", "hiking"],
}

result = user_schema.validate(data)
print(result.is_valid)  # True

invalid_data = {
    "username": "j",
    "email": "not-an-email",
    "age": 150,
    "interests": ["too", "many", "interests", "in", "this", "list"],
}

result = user_schema.validate(invalid_data)
print(result.is_valid)  # False
print(result.errors)  # Dictionary of validation errors
