# Special Prompt Methods

## `default()`

Available for the `text`, `confirm`, and `number` types. If a default is given, the user can submit an empty field and the default value will be used as their submission.

## `peeper()`

Available for the `password` type. When enabled, masked inputs will show the last character if it was just typed. If `Space` or `Backspace` are pressed, the last character of the input will not be visible. After submitting, the "peeper" character will not be visible.

## `commas()`

Available for the `number` type. When enabled, the input shown after the prompt will insert commas (Ex: `12345` -> `12,345`). This will not affect the number returned on submit. Cannot be enabled alongside `allow_decimals()`.

## `allow_decimals()`

Available for the `number` type. When enabled, decimal values are able to be inputted. Until the `.` character is typed, a dim `.` character will trail the inputted number. After a `.` character is typed, the `.` will no longer appear dim and no other `.`s can be added to the input until the existing one is removed from the input. Cannot be enabled alongside `commas()`.

## `allow_negatives()`

Available for the `number` type. When enabled, negative values are able to be inputted. Pressing the `-` key will have no effect until at least one digit is inputted. Upon pressed, the sign in front of the value will be toggled (an implicit positive sign is used). If all numeric digits are removed, the `-` sign will dissappear.

## `month_first()`

Available for the `date` type. When enabled, the date will be inputted in the format month-day-year instead of day-month-year.

## `year_range()`

Available for the `date` type. The `year_range` is the defined minimun and maximum values that the year must be in between, inclusive on both ends. By default, the range is from `1900` to `2100`.

## `separator()`

Available for the `date` type. Used as the separator between the day, month, and year fields. By default, the `"/"` seperator is used.

## `show_words()`

Available for the `date` type. When enabled, the date shown beside the prompt upon submission will be displayed in words. Ex: 1/1/2014 -> January 1, 2014

# Getting Used To Input Controls

For the most part, input types that feature somewhat non-trivial controls will have them listed. However, each prompt type comes with it's own nuances that aren't included in the controls list for conciseness.

## Text Inputs

Press `Escape` to clear the current value.

## Number Inputs

Use `↑` to increase and `↓` to decrease the value.

## Date Inputs

Use `↑` to increase and `↓` to decrease the selected field.
Pressing `Shift` + `Tab` will act like the `Tab` functionality, but highlight fields in the opposite direction.
