# UP TO DATE VERSION CAN BE FOUND IN FLUXUTILS > LOG > UTILS.PY UNDER THE WRAP() FUNCTION
# UP TO DATE VERSION CAN BE FOUND IN FLUXUTILS > LOG > UTILS.PY UNDER THE WRAP() FUNCTION
# UP TO DATE VERSION CAN BE FOUND IN FLUXUTILS > LOG > UTILS.PY UNDER THE WRAP() FUNCTION
# UP TO DATE VERSION CAN BE FOUND IN FLUXUTILS > LOG > UTILS.PY UNDER THE WRAP() FUNCTION
# UP TO DATE VERSION CAN BE FOUND IN FLUXUTILS > LOG > UTILS.PY UNDER THE WRAP() FUNCTION
# UP TO DATE VERSION CAN BE FOUND IN FLUXUTILS > LOG > UTILS.PY UNDER THE WRAP() FUNCTION

import re


def wrap_text(text, width):
    ansi_escape = re.compile(r"\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])")
    result = []

    def visible_length(s):
        return len(ansi_escape.sub("", s))

    lines = text.split("\n")
    print(f"Number of lines: {len(lines)}")  # Debug print

    for line_num, line in enumerate(lines, 1):
        print(f"Processing line {line_num}: {repr(line)}")  # Debug print
        current_line = ""
        current_line_visible_length = 0
        words = re.findall(r"\S+\s*", line)

        for word in words:
            word_visible_length = visible_length(word)

            if current_line_visible_length + word_visible_length > width:
                if current_line:
                    result.append(current_line.rstrip())
                    print(
                        f"Added to result: {repr(current_line.rstrip())}"
                    )  # Debug print
                current_line = ""
                current_line_visible_length = 0

            current_line += word
            current_line_visible_length += word_visible_length

        if current_line:
            result.append(current_line.rstrip())
            print(f"Added to result: {repr(current_line.rstrip())}")  # Debug print

    print(f"Final result: {result}")  # Debug print
    return "\n".join(result)


# Test case 1: ANSI-coded text with multiple lines
text1 = "\x1b[38;5;108m'\x1b[39m\x1b[38;5;108ma\x1b[39m\x1b[38;5;108m'\x1b[39m 3\nThis is \x1b[31mred\x1b[0m and this is \x1b[32mgreen\x1b[0m and this is normal."
print("Test case 1 output:")
wrapped1 = wrap_text(text1, 20)
print(wrapped1)
print("\n")

# Test case 2: Plain text with multiple lines
text2 = "This is a long line of text that should be wrapped.\nAnd this is another line that's also quite long and should be wrapped too."
print("Test case 2 output:")
wrapped2 = wrap_text(text2, 30)
print(wrapped2)
