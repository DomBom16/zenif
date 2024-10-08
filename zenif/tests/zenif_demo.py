from zenif.cli import CLI, arg, kwarg, Prompt, install_setup_command
from zenif.log import Logger
from zenif.decorators import retry, cache
import os
import random

cli = CLI(name="zenif-demo")
logger = Logger(ruleset={"log_line": {"format": "simple"}})

# Add the install command to your CLI
install_setup_command(cli, os.path.abspath(__file__))


@cli.command
@arg("name", help="Your name")
@kwarg("--greeting", default="Hello", help="Greeting to use")
def greet(name: str, greeting: str):
    """Greet the user"""
    logger.info(f"{greeting}, {name}!")


@cli.command
@retry(max_retries=8, delay=1.0)
def flaky_operation():
    """Demonstrate a flaky operation with retry on exception"""
    logger.info("Attempting a flaky operation...")
    if random.random() < 0.7:  # 70% chance of failure
        logger.error("Randon failure occurred! Retrying...")
        raise Exception("Random failure occurred!")
    logger.success("Flaky operation succeeded!")


@cli.command
@arg("n", help="Calculate the nth Fibonacci number")
@cache
def fibonacci(n: int):
    """Calculate the nth Fibonacci number"""
    n = int(n)
    if n > 488:
        logger.error("n must less than or equal to 488.")
        return
    if n <= 1:
        return n
    else:
        return fibonacci(n - 1) + fibonacci(n - 2)


@cli.command
def interactive_prompt():
    """Demonstrate interactive prompts"""
    name = Prompt.text("What's your name?").ask()
    age = Prompt.number("How old are you?").min(0).max(120).ask()
    likes_python = Prompt.confirm("Do you like Python?").ask()
    favorite_color = Prompt.choice(
        "What's your favorite color?", choices=["Red", "Green", "Blue", "Yellow"]
    ).ask()

    logger.info(f"Name: {name}")
    logger.info(f"Age: {age}")
    logger.info(f"Likes Python: {likes_python}")
    logger.info(f"Favorite color: {favorite_color}")


@cli.command
@kwarg("--verbose", is_flag=True, help="Enable verbose logging")
def log_demo(verbose: bool):
    """Demonstrate different log levels"""
    if verbose:
        logger.debug("This is a debug message")
    logger.info("This is an info message")
    logger.success("This is a success message")
    logger.warning("This is a warning message")
    logger.error("This is an error message")


if __name__ == "__main__":
    cli.run()
