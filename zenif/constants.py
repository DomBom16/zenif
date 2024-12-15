class Keys:
    # Arrow keys
    UP = "\033[A"
    DOWN = "\033[B"
    LEFT = "\033[D"
    RIGHT = "\033[C"

    ARROWS = (UP, DOWN, LEFT, RIGHT)

    # Special keys
    BACKSPACE = "\x7f"
    ENTER = "\r"
    ESCAPE = "\033"
    TAB = "\t"
    STAB = "\033[Z"  # Shift+Tab

    # Selection
    CTRLA = "\x01"  # Select all

    # Edit commands
    CTRLC = "\x03"  # Copy
    CTRLV = "\x16"  # Paste
    CTRLX = "\x18"  # Cut

    # File commands
    CTRLD = "\x04"  # Done
    CTRLS = "\x1f"  # Save

    # Search
    CTRLF = "\x06"  # Find
    CTRLH = "\x08"  # Replace

    # Formatting
    CTRLB = "\x02"  # Bold
    CTRLI = "\x09"  # Italic
    CTRLU = "\x1d"  # Underline
    CTRLK = "\x0b"  # Strike

    # Version control
    CTRLY = "\x15"  # Redo
    CTRLZ = "\x1a"  # Undo