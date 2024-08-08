from zenif.cli import CLI, arg, kwarg, Prompt
from zenif.schema import (
    Schema,
    String,
    Integer,
    Email,
    List,
    MinLength,
    MinValue,
    MaxLength,
    MaxValue,
)

cli = CLI()


@cli.command
@arg("name", help="Name to greet")
@kwarg("--greeting", default="Hello", help="Greeting to use")
@kwarg("--shout", is_flag=True, help="Print in uppercase")
def greet(name: str, greeting: str, shout: bool = False):
    """Greet a person."""
    message = f"{greeting}, {name}!"
    if shout:
        message = message.upper()
    return message


@cli.command
def test_prompts():
    """Test all available prompts"""

    # _ = Prompt.text("What's your name?").ask()
    # _ = (
    #     Prompt.text("What's your favorite programming language?")
    #     .default("Python")
    #     .ask()
    # )
    # _ = Prompt.password("Enter a password").ask()
    # _ = Prompt.confirm("Do you like pizza?").ask()
    # _ = Prompt.confirm("Do you want dessert?").default(True).ask()
    # _ = Prompt.choice(
    #     "What's your favorite color?", choices=["Red", "Green", "Blue", "Yellow"]
    # ).ask()
    # _ = Prompt.checkbox(
    #     "Select your hobbies",
    #     choices=["Reading", "Gaming", "Sports", "Cooking", "Traveling"],
    # ).ask()
    # _ = Prompt.number("How old are you?").ask()
    # _ = Prompt.number("Rate your experience").min(1).max(5).ask()

    # cli.echo("All prompts completed successfully!")

    class EvenNumber:
        def __call__(self, value):
            if value % 2 != 0:
                raise ValueError("Must be an even number.")

    user_schema = Schema(
        {
            "enter_your_name": String(validators=[MinLength(3), MaxLength(50)]),
            "enter_your_age": Integer(
                validators=[MinValue(18), MaxValue(120), EvenNumber()]
            ),
            "select_your_interests": List(
                String(), validators=[MinLength(3), MaxLength(5)]
            ),
            "select_your_favorite_interest": String(),
            "enter_your_email": Email(),
        }
    )

    name = Prompt.text("Enter your name", schema=user_schema).ask()
    age = Prompt.number("Enter your age", schema=user_schema).ask()
    interests = Prompt.checkbox(
        "Select your interests",
        choices=["Reading", "Gaming", "Sports", "Cooking", "Travel"],
        schema=user_schema,
    ).ask()
    fav_interest = Prompt.choice(
        "Select your favorite interest",
        choices=["Reading", "Gaming", "Sports", "Cooking", "Travel"],
        schema=user_schema,
    ).ask()
    email = Prompt.text("Enter your email", schema=user_schema).ask()

    print(f"Name: {name}")
    print(f"Age: {age}")
    print(f"Interests: {', '.join(interests)}")
    print(f"Favorite Interest: {fav_interest}")
    print(f"Email: {email}")


if __name__ == "__main__":
    cli.run()
