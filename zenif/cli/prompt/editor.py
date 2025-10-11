import sys
from dataclasses import dataclass
from shutil import get_terminal_size

from colorama import Fore, Style
from pygments.lexer import Lexer
from pygments.lexers import get_lexer_for_filename

# from pygments import highlight
from pygments.util import ClassNotFound

from ...constants import Cursor, Keys
from ...schema import Schema, StringF
from .base import BasePrompt


@dataclass
class VisualLine:
    buffer_index: int
    segment_index: int
    start: int
    text: str

    @property
    def length(self) -> int:
        return len(self.text)


@dataclass
class RenderState:
    controls_line: str
    display_lines: list[str]
    visual_lines: list[VisualLine]
    cursor_row: int
    cursor_col: int
    cursor_visual_index: int
    render_height: int
    indent: int


class EditorPrompt(BasePrompt):
    def __init__(
        self,
        message: str,
        schema: Schema | None = None,
        id: str | None = None,
    ):
        super().__init__(message, schema, id)
        self._language: str = "txt"

        # Check if the field is a StringF
        if schema and not isinstance(self.field, StringF):
            field_type = type(self.field).__name__
            error_message = (
                f"EditorPrompt requires a StringF field, but got {field_type}"
            )
            raise TypeError(error_message)

    def language(self, language: str) -> "EditorPrompt":
        """Set the file language for the prompt."""
        self._language = language
        return self

    def _get_lexer(self, ext: str) -> Lexer | None:
        try:
            return get_lexer_for_filename(
                f"editor.{ext}"
            )  # Filename doesn't matter, just the extension
        except ClassNotFound:
            return None

    @staticmethod
    def _split_line(line: str, width: int) -> list[str]:
        if width <= 0:
            return [line]
        if not line:
            return [""]
        segments: list[str] = []
        start = 0
        while start < len(line):
            end = start + width
            segments.append(line[start:end])
            start = end
        return segments or [""]

    def _build_render_state(
        self,
        buffer: list[str],
        cx: int,
        cy: int,
        columns: int,
        indent: int,
        controls: str,
    ) -> RenderState:
        usable_indent = min(indent, max(columns - 1, 0))
        visible_width = max(columns - usable_indent, 1)

        display_lines: list[str] = []
        visual_lines: list[VisualLine] = []

        cursor_visual_index = 0
        cursor_segment_index = 0
        cursor_offset_in_segment = 0

        for line_index, line in enumerate(buffer):
            segments = self._split_line(line, visible_width)
            segment_start = 0

            # Determine which segment the cursor falls into for this line
            if line_index == cy:
                cursor_segment_index = len(segments) - 1
                cursor_offset_in_segment = len(segments[-1])

                for idx, segment in enumerate(segments):
                    segment_end = segment_start + len(segment)
                    if cx < segment_end:
                        cursor_segment_index = idx
                        cursor_offset_in_segment = cx - segment_start
                        break
                    if cx == segment_end and idx < len(segments) - 1:
                        cursor_segment_index = idx + 1
                        cursor_offset_in_segment = 0
                        break
                    segment_start = segment_end

                # Reset for iteration since we mutated segment_start
                segment_start = 0

            for segment_idx, segment in enumerate(segments):
                visual_line = VisualLine(
                    buffer_index=line_index,
                    segment_index=segment_idx,
                    start=segment_start,
                    text=segment,
                )
                visual_lines.append(visual_line)
                display_lines.append(
                    f"{Cursor.lclear()}{' ' * usable_indent}"
                    f"{Fore.YELLOW}{segment}{Style.RESET_ALL}"
                )

                if line_index == cy and segment_idx == cursor_segment_index:
                    cursor_visual_index = len(visual_lines) - 1

                segment_start += len(segment)

        controls_line = (
            f"{Cursor.lclear()}{' ' * usable_indent}"
            f"{Fore.RESET}{Style.DIM}{controls}{Style.RESET_ALL}"
        )

        cursor_row = 1 + cursor_visual_index  # account for controls line
        cursor_col = usable_indent + cursor_offset_in_segment
        render_height = 1 + len(display_lines)  # controls + buffer view

        return RenderState(
            controls_line=controls_line,
            display_lines=display_lines,
            visual_lines=visual_lines,
            cursor_row=cursor_row,
            cursor_col=cursor_col,
            cursor_visual_index=cursor_visual_index,
            render_height=render_height,
            indent=usable_indent,
        )

    def _render(
        self,
        state: RenderState,
        error: str | None,
        previous_state: RenderState | None,
    ) -> None:
        stdout = sys.stdout

        self._reset_view(previous_state)

        self._print_prompt(self.message, error=error)

        stdout.write("\n")
        stdout.write(state.controls_line)
        for line in state.display_lines:
            stdout.write("\n")
            stdout.write(line)

        # Position cursor
        stdout.write("\r")
        rows_up = state.render_height - 1 - state.cursor_row
        if rows_up > 0:
            stdout.write(Cursor.up(rows_up))
        elif rows_up < 0:
            stdout.write(Cursor.down(-rows_up))

        if state.cursor_col > 0:
            stdout.write(Cursor.right(state.cursor_col))

        stdout.flush()

    def _reset_view(self, previous_state: RenderState | None) -> None:
        if not previous_state:
            return

        stdout = sys.stdout
        if previous_state.cursor_col > 0:
            stdout.write(Cursor.left(previous_state.cursor_col))

        rows_up = previous_state.cursor_row + 1  # include prompt line
        if rows_up > 0:
            stdout.write(Cursor.up(rows_up))

        stdout.write("\r")
        stdout.write(Cursor.lclear())

        for _ in range(previous_state.render_height):
            stdout.write(Cursor.down(1))
            stdout.write(Cursor.lclear())

        if previous_state.render_height:
            stdout.write(Cursor.up(previous_state.render_height))

        stdout.flush()

    def _move_vertical(
        self,
        cx: int,
        cy: int,
        direction: int,
        state: RenderState,
        target_visual_col: int | None,
    ) -> tuple[int, int, int]:
        if not state.visual_lines:
            return cx, cy, 0 if target_visual_col is None else target_visual_col

        current_index = state.cursor_visual_index
        next_index = current_index + direction
        if next_index < 0 or next_index >= len(state.visual_lines):
            return (
                cx,
                cy,
                state.cursor_col if target_visual_col is None else target_visual_col,
            )

        desired_col = (
            state.cursor_col if target_visual_col is None else target_visual_col
        )
        visual_line = state.visual_lines[next_index]
        relative_col = max(desired_col - state.indent, 0)
        relative_col = min(relative_col, visual_line.length)

        new_cx = visual_line.start + relative_col
        new_cy = visual_line.buffer_index
        return new_cx, new_cy, desired_col

    @staticmethod
    def _clamp_cursor(buffer: list[str], cx: int, cy: int) -> tuple[int, int]:
        cy = max(0, min(cy, len(buffer) - 1))
        cx = max(0, min(cx, len(buffer[cy])))
        return cx, cy

    def ask(self) -> str:
        """Prompt the user for input."""

        # Prompt and error on first line
        # Controls on second line
        # Editor on third line and extends downward
        # After editor, language and other metrics (words, lines, etc.)

        buffer: list[str] = [""]
        cx: int = 0
        cy: int = 0
        indent: int = 2

        # lexer = self._get_lexer(self._language)

        controls: str = "Enter for newline, Ctrl+D to confirm"
        previous_state: RenderState | None = None
        target_visual_col: int | None = None

        while True:
            error: str | None = self.validate("\n".join(buffer) or "")

            try:
                columns = max(get_terminal_size().columns, 20)
            except OSError:
                columns = 80
            state = self._build_render_state(buffer, cx, cy, columns, indent, controls)
            self._render(state, error, previous_state)
            previous_state = state

            char = self._get_key()

            if char == Keys.CTRLD:
                if not error and buffer:
                    summary = buffer[0].strip()
                    if len(buffer) > 1:
                        summary = f"{summary} …"
                    self._reset_view(state)
                    self._print_prompt(self.message, summary)
                    return "\n".join(buffer)
                continue

            if char == Keys.BACKSPACE:
                target_visual_col = None
                if cx > 0:
                    buffer[cy] = buffer[cy][: cx - 1] + buffer[cy][cx:]
                    cx -= 1
                elif cy > 0:
                    prev_line = buffer.pop(cy)
                    cy -= 1
                    cx = len(buffer[cy])
                    buffer[cy] += prev_line
                cx, cy = self._clamp_cursor(buffer, cx, cy)
                continue

            if char == Keys.ENTER:
                target_visual_col = None
                current_line = buffer[cy]
                before_cursor, after_cursor = current_line[:cx], current_line[cx:]
                buffer[cy] = before_cursor
                buffer.insert(cy + 1, after_cursor)
                cy += 1
                cx = 0
                cx, cy = self._clamp_cursor(buffer, cx, cy)
                continue

            if char in Keys.ARROWS:
                if char == Keys.UP:
                    cx, cy, target_visual_col = self._move_vertical(
                        cx, cy, -1, state, target_visual_col
                    )
                elif char == Keys.DOWN:
                    cx, cy, target_visual_col = self._move_vertical(
                        cx, cy, 1, state, target_visual_col
                    )
                elif char == Keys.LEFT:
                    target_visual_col = None
                    if cx > 0:
                        cx -= 1
                    elif cy > 0:
                        cy -= 1
                        cx = len(buffer[cy])
                elif char == Keys.RIGHT:
                    target_visual_col = None
                    if cx < len(buffer[cy]):
                        cx += 1
                    elif cy < len(buffer) - 1:
                        cy += 1
                        cx = 0
                cx, cy = self._clamp_cursor(buffer, cx, cy)
                continue

            target_visual_col = None
            if len(char) == 1 and (char.isprintable() or char == "\t"):
                buffer[cy] = buffer[cy][:cx] + char + buffer[cy][cx:]
                cx += 1
                cx, cy = self._clamp_cursor(buffer, cx, cy)
                continue

            if char.startswith(Keys.ESCAPE):
                continue

            if char in Keys.CTRLKEYS:
                continue
