#!/usr/bin/env python3
from zenif.cli import Applet, Prompt as p
from zenif.schema import (
    Schema,
    BooleanF,
    StringF,
    IntegerF,
    DateF,
    ListF,
    Length,
    Value,
    Email,
    NotEmpty,
    Validator,
    ValidationError,
    Regex,
    Truthy,
)
from zenif.constants import Cursor
from zenif.log import Logger

l = Logger()

import os
import time

a = Applet()

a.install(os.path.abspath(__file__))


@a.command(aliases=["f"])
@a.arg("branch", help="The branch to fetch")
@a.opt("depth", default=10, help="The depth to use")
@a.alias("depth", "d")
def fetch(branch, depth):
    """
    Fetch a branch with a specified depth.

    Usage examples:
      fetch main --depth=10
      fetch feature -d=10
    """
    time.sleep(2)
    return f"Fetching branch '{branch}' with depth={depth}"


@a.command
@a.arg("path", help="The folder path")
@a.flag("all", help="Show all")
def ls(path, all):
    """
    List directory contents.

    Usage example: ls /my-path --all
    """
    return f"Listing {path} with all={all}"


@a.command(aliases=["tp"])
def test_prompts():
    """Test all available prompts"""

    class OddOrEven(Validator):
        def __init__(self, parity: str = "even", err: str | None = None):
            super().__init__(err)
            self.parity = 1 if parity == "odd" else 0

        def _validate(self, value):
            if value % 2 != self.parity:
                raise ValidationError(
                    f"Must be an {'even' if self.parity == 0 else 'odd'} number."
                )

    # clear the screen
    os.system("cls" if os.name == "nt" else "clear")

    schema = Schema(
        {
            "are_you_sure": BooleanF().has(Truthy()),
            "name": StringF().has(Length(min=3, max=50)),
            "email": StringF().has(Email()),
            "password": StringF()
            .has(Length(min=8))
            .has(
                Regex(
                    r"^(?=.*[a-z]).+$",
                    err="Password must contain at least one lowercase letter.",
                )
            )
            .has(
                Regex(
                    r"^(?=.*[A-Z]).+$",
                    err="Password must contain at least one uppercase letter.",
                )
            )
            .has(
                Regex(r"^(?=.*\d).+$", err="Password must contain at least one digit.")
            )
            .has(
                Regex(
                    r"^(?=.*[@$!%*#?&]).+$",
                    err="Password must contain at least one special character.",
                )
            ),
            "date": DateF().has(NotEmpty()),
            "salary": IntegerF().has(Value(min=0, max=1000000)),
            "age": IntegerF().has(Value(min=18, max=120)).has(OddOrEven(parity="odd")),
            "editor": StringF().has(NotEmpty()),
            "interests": ListF()
            .items(StringF())
            .has(Length(min=3, err="Select a minimum of 3 interests.")),
            "fav_interest": StringF(),
        }
    )

    for i in range(4):
        print(i + 1)

    print(Cursor.get())

    p.keypress("Press a, b, or c").keys("a", "b", "c").ask()

    l.info(
        schema.validate(
            {
                "are_you_sure": False,
                "name": "Al",
                "email": "invalid-email",
                "password": "",
                "date": "not-a-date",
                "salary": -500,
                "age": 15,
                "editor": "",
                "interests": ["Re"],
                "fav_interest": "This can always be valid",
            }
        )
    )

    if (
        not p.confirm(
            "Are you sure you want to continue?", schema=schema, id="are_you_sure"
        )
        .default(True)
        .ask()
    ):
        return
    name = p.text("Enter your name", schema=schema, id="name").ask()
    email = p.text("Enter your email", schema=schema, id="email").ask()
    password = (
        p.password("Enter your password", schema=schema, id="password").peeper().ask()
    )
    date = (
        p.date("Enter your date of birth", schema=schema, id="date")
        .month_first()
        .show_words()
        .ask()
    )
    salary = p.number("Enter your salary", schema=schema, id="salary").commas().ask()
    age = p.number("Enter your age", schema=schema, id="age").ask()
    editor = (
        p.editor("Enter your hacker code", schema=schema, id="editor")
        .language("py")
        .ask()
    )
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

    print(f"{name=}")
    print(f"{email=}")
    print(f"{password=}")
    print(f"{date=}")
    print(f"{salary=}")
    print(f"{age=}")
    print(f"{editor=}")
    print(f"{interests=}")
    print(f"{fav_interest=}")


@a.root
def root():
    a.execute("test_prompts")


@a.help
def help():
    # return "This is the help command"
    pass


@a.before
def before(command: str, args: list[str]):
    # return f"Command: {command}, Args: {args}"
    pass


if __name__ == "__main__":
    a.run()
