import black
import pprint
from pygments import highlight
from pygments.lexers import PythonLexer
from pygments.formatters import Terminal256Formatter
from pygments.styles import get_style_by_name, STYLE_MAP

print(STYLE_MAP)


def format_variable(variable) -> str:
    # Pretty print the variable
    pretty_printer = pprint.PrettyPrinter()
    pretty_str = pretty_printer.pformat(variable)

    # Format the pretty-printed string using black
    formatted_str = black.format_str(pretty_str, mode=black.FileMode())

    # Highlight the formatted string
    style = get_style_by_name("one-dark")

    highlighted_str = highlight(
        formatted_str, PythonLexer(), Terminal256Formatter(style=style)
    )

    return highlighted_str


# Example usage
example_dict = {
    "name": "John",
    "age": 30,
    "children": [{"name": "Jane", "age": 10}, {"name": "Doe", "age": 8}],
}

print(len(format_variable("example_dict")), len("example_dict"))
