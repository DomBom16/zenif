# EditorPrompt Known Issues & Roadmap

## Issues

- Lines that exceed the width of the terminal are not handled well
  - Cursor placement at start of trailing lines is not accurate
  - Deleting characters will not clear and redraw the whole line, leaving "ghost" characters
- Cursor positioning is sometimes not accurate

## Unimplemented Features

- Set language is not shown
- Validation is not properly implemented
- Syntax highlighting
- Wordwrapping
- Markdown preview for `.md`
