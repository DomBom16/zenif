from zenif.cli import CLI, argument, option, Prompt

cli = CLI()


@cli.command
@argument("name", help="Name to greet")
@option("--greeting", default="Hello", help="Greeting to use")
@option("--shout", is_flag=True, help="Print in uppercase")
def greet(name: str, greeting: str, shout: bool = False):
    """Greet a person."""
    message = f"{greeting}, {name}!"
    if shout:
        message = message.upper()
    return message


@cli.command
def test_prompts():
    """Test all available prompts"""

    _ = Prompt.text("What's your name?").ask()
    _ = (
        Prompt.text("What's your favorite programming language?")
        .default("Python")
        .ask()
    )
    _ = Prompt.password("Enter a password").ask()
    _ = Prompt.confirm("Do you like pizza?").ask()
    _ = Prompt.confirm("Do you want dessert?").default(True).ask()
    _ = Prompt.choice(
        "What's your favorite color?", choices=["Red", "Green", "Blue", "Yellow"]
    ).ask()
    _ = Prompt.checkbox(
        "Select your hobbies",
        choices=["Reading", "Gaming", "Sports", "Cooking", "Traveling"],
    ).ask()
    _ = Prompt.number("How old are you?").ask()
    _ = Prompt.number("Rate your experience").min(1).max(5).ask()

    cli.echo("\nAll prompts completed successfully!")


if __name__ == "__main__":
    cli.run()
