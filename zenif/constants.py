class Keys:
    # Arrow keys
    UP = "\x1b[A"
    DOWN = "\x1b[B"
    LEFT = "\x1b[D"
    RIGHT = "\x1b[C"

    ARROWS = (UP, DOWN, LEFT, RIGHT)

    # Special keys
    BACKSPACE = "\x7f"
    ENTER = "\r"
    ESCAPE = "\x1b"
    TAB = "\t"
    STAB = "\x1b[Z"  # Shift+Tab

    # Control keys
    # ****E*G**J*LMN*P******W***

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

    # Formatting
    CTRLB = "\x02"  # Bold
    CTRLI = "\x09"  # Italic
    CTRLU = "\x1d"  # Underline
    CTRLK = "\x0b"  # Strike

    # Version control
    CTRLY = "\x15"  # Redo
    CTRLZ = "\x1a"  # Undo

    # Other
    CTRLH = "\x08"  # Help/About
    CTRLQ = "\x10"  # Quit
    CTRLR = "\x12"  # Redraw
    CTRLT = "\x14"  # Toggle
    CTRLO = "\x0f"  # Open

    # Function keys
    F1 = "\x1bOP"
    F2 = "\x1bOQ"
    F3 = "\x1bOR"
    F4 = "\x1bOS"
    F5 = "\x1b[15~"
    F6 = "\x1b[17~"
    F7 = "\x1b[18~"
    F8 = "\x1b[19~"
    F9 = "\x1b[20~"
    F10 = "\x1b[21~"
    F11 = "\x1b[23~"
    F12 = "\x1b[24~"
