from zenif.cli import CLI, req, opt, Prompt as p, install_setup
from zenif.schema import (
    Schema,
    BooleanF,
    StringF,
    IntegerF,
    ListF,
    Length,
    Value,
    Email,
    NotEmpty,
)
import os

cli = CLI(name="cli")

install_setup(cli, os.path.abspath(__file__))


@cli.command
@req("name", help="Name to greet")
@opt("--greeting", default="Hello", help="Greeting to use")
@opt("--shout", is_flag=True, help="Print in uppercase")
def greet(name: str, greeting: str, shout: bool = False):
    """Greet a person."""
    message = f"{greeting}, {name}!"
    if shout:
        message = message.upper()
    return message


@cli.command
def test_prompts():
    """Test all available prompts"""

    class OddOrEven:
        def __init__(self, parity: str = "even"):
            self.parity = 1 if parity == "odd" else 0

        def __call__(self, value):
            if value % 2 != self.parity:
                raise ValueError(
                    f"Must be an {'even' if self.parity ==
                                  0 else 'odd'} number."
                )

    # clear the screen
    os.system("cls" if os.name == "nt" else "clear")

    schema = Schema(
        are_you_sure=BooleanF().name("continue"),
        name=StringF().name("name").has(Length(min=3, max=50)),
        password=StringF().name("password").has(NotEmpty()),
        age=IntegerF()
        .name("age")
        .has(Value(min=18, max=120))
        .has(OddOrEven(parity="odd")),
        interests=ListF()
        .name("interests")
        .item_type(StringF())
        .has(Length(min=3, err="Select a minimum of 3 interests.")),
        fav_interest=StringF().name("fav_interest"),
        email=StringF().name("email").has(Email()),
    ).all_optional()

    for i in range(4):
        print(i + 1)

    if (
        not p.confirm("Are you sure you want to continue?", schema, "are_you_sure")
        .default(True)
        .ask()
    ):
        return
    # name = p.text("Enter your name", schema, "name").ask()
    # email = p.text("Enter your email", schema, "email").ask()
    # password = p.password("Enter your password", schema, "password").peeper().ask()
    # date = p.date("Enter your date of birth").month_first().show_words().ask()
    # age = p.number("Enter your age", schema, "age").ask()
    editor = p.editor("Enter your hacker code").language("py").ask()
    interests = p.checkbox(
        "Select your interests",
        ["Reading", "Gaming", "Sports", "Cooking", "Travel"],
        schema,
        "interests",
    ).ask()
    fav_interest = p.choice(
        "Select your favorite interest",
        interests,
        schema,
        "fav_interest",
    ).ask()

    # print(f"{name=}")
    # print(f"{email=}")
    # print(f"{password=}")
    # print(f"{date=}")
    # print(f"{age=}")
    print(f"{editor=}")
    print(f"{interests=}")
    print(f"{fav_interest=}")


if __name__ == "__main__":
    cli.run()
