# Changelog

## 0.2.0 (2024-08-DD)

*Zenif takes a quantum leap forward with a suite of enhancements designed to supercharge your development experience. This update introduces smart memory management, more informative deprecation warnings, streamlined CLI interactions, and – drum roll, please – a powerful new Schema module for bulletproof data validation. While we've made some breaking changes to keep Zenif sleek and intuitive, the payoff in improved functionality and clarity is well worth it.*

### 🔍 Introducing Schema Module: Data Validation, Zenif Style

Introducing our brand new Schema module, your new best friend for data integrity:

- Define data structures with a fluent, method-chaining approach that prioritizes readability and expressiveness .
- Validate input with pinpoint precision using a rich set of built-in validators.
- Seamlessly integrate with the CLI module for robust, schema-driven command-line interfaces.
- Create custom validators to fit your unique data validation needs.
- Nested schemas? List validation? We've got you covered, because real-world data is complex.

```python
Schema(
    username=StringF()
        .name("username")
        .has(Length(min=3, max=50))
        .has(Regex(r"^[a-zA-Z0-9_]+$")),
    age=IntegerF()
        .name("age")
        .has(Value(min=18, max=120))
        .optional(),
    email=StringF()
        .name("email")
        .has(EmailValidator()),
    interests=ListF()
        .name("interests")
        .item_type(StringF())
        .has(Length(min=3)),
    profile=DictF()
        .name("profile")
        .key_type(StringF())
        .value_type(StringF())
        .optional(),
)
```

Dive deeper into the world of schemas with our [shiny new documentation](/docs/modules/schema.md). It's a page-turner, we promise!

### 🎀 Decorators Module: Smarter and More Informative

- `@cache` now features a `max_size` argument, allowing you to cap the cache size and keep memory usage in check.
- `@deprecated` gets an upgrade with the new `expected_removal` argument, providing clearer timelines for deprecation.
- We've bid farewell to `@retry_exponential_backoff` in favor of the more concise `@retry_expo`.
- Under the hood, `@deprecated` now leverages Zenif's own logger for deprecation messages.
- Our test suite has been expanded to cover these new features comprehensively.

### 💻 CLI Module: Cleaner, More Powerful, and Schema-Aware

- We've renamed `@argument` to `@arg` and `@option` to `@kwarg` for more intuitive use.
- Introducing the `install_setup_command()` method: now you can easily generate a shell script to install your CLI app as a Zsh command alias.
- We've squashed a pesky type hint error in `NumberPrompt`.
- All prompt types now support schema validation, opening the floodgates for a whole new world of prompt types! Bring robust data integrity to your interactive CLIs with ease. And pro-tip by the way, to define a schema, give your prompts IDs that you can use in your your schema. It's like a spell that turns your prompts into schema-ready powerhouses!
- `ChoicePrompt` now comes with built-in type checking, ensuring it plays nice with String schema fields only.
- `CheckboxPrompt` gets a visual upgrade: it now sports a snazzy underline beneath the 'X' if the current position overlaps with a selected item.
- `TextPrompt` and `PasswordPrompt` have learned to ignore arrow keys, because sometimes less is more.
- `TextPrompt`, `NumberPrompt`, and `PasswordPrompt` now come with a magical screen-overflow handling: they'll gracefully truncate the start of long responses, ensuring your CLI stays sleek without losing a single character of input.

### 📝 Log Module: More Flexibility, Less Clutter

- For those who prefer simplicity, we've added new `"simple"` and `"short"` premade formats.
- We've removed the warning log on `Logger` initialization when Stacking > Enabled is set to True, reducing unnecessary output.

### ✨ Polishing Touches

- Our GitHub project link now sports the more fitting label "GitHub" instead of "Homepage".
- The `README` now includes a pronunciation guide for "Zenif" (it's "Zenith", by the way).
- We've given this very changelog a makeover, infusing it with personality and clearer explanations to better showcase Zenif's evolution.
- New documentation for the Schema module has been added, complete with examples and integration guides.

*While these changes bring exciting new capabilities, please note that some are breaking changes. Be sure to review your use of exponential retry decorators and CLI argument decorators when upgrading to this version.*

## 0.1.0 (2024-08-07)

*Behold, the dawn of Zenif! This initial release is not just a toolkit; it's a Swiss Army knife for Python developers. Zenif bursts onto the scene with a triad of powerful modules, each designed to elevate your coding experience to new heights. Whether you're wrestling with logs, yearning for smarter functions, or crafting command-line interfaces, Zenif has got your back.*

### 📝 Log Module: Your Logs, Your Way

Imagine a logging system that bends to your will:

- Flex your creativity with a customizable formatting system that makes your logs a joy to read.
- Juggle multiple output streams like a pro, be it console or file.
- Dive deep into log customization with our advanced templating engine.
- Group your streams for efficient management.
- Take control with rule-based configuration for pinpoint precision in log behavior.
- Add a splash of color with ANSI support and rich formatting options.
- Simplify your testing workflow with the `TestLogger` class.

### 🎀 Decorators Module: Superpowers for Your Functions

Unleash a legion of decorators to transform your functions:

- `@retry`, `@retry_expo`, `@retry_on_exception`: Make your functions resilient in the face of failures.
- `@singleton`: Ensure your class stays unique, just like you.
- `@enforce_types`: Keep your types in check, because discipline is freedom.
- `@background_task`: Let your functions run free in their own threads.
- `@profile`: Gain x-ray vision into your function's performance.
- `@timeout`, `@rate_limiter`: Set boundaries, because even functions need limits.
- `@trace`: Follow your function's journey, breadcrumb by breadcrumb.
- `@suppress_exceptions`, `@deprecated`, `@type_check`: Handle the unexpected with grace.
- `@log_execution_time`, `@cache`: Optimize like a boss.

### 💻 CLI Module: Command Line Interfaces, Reimagined

Craft CLIs that users will actually enjoy using:

- `CLI` class: The foundation of your command-line dreams.
- `@command` decorator: Define commands so intuitively, it feels like cheating.
- `@argument` and `@option` decorators: Handle args and options with finesse.
- `Prompt` class: Interaction is an art, and you're about to become a master.
  - From simple text inputs to multi-select options, create CLIs that talk back.

### 📚 Documentation: Because Great Tools Deserve Great Guides

- Dive into our comprehensive README, complete with examples to get you started.
- Explore detailed documentation for each module in `docs/modules/`.
- Keep track of our journey with this very changelog.

### 🧪 Tests: Because We Believe in Trust, but Verify

- Every module, every feature, rigorously tested.
- Special attention to `TestLogger` and all our beloved decorators.
- CLI module put through its paces with a dedicated test suite.

### 🔧 The Zenif Promise

- Modular architecture: Expand and adapt with ease.
- Consistent coding style: A feast for the eyes of code reviewers.
- Performance optimizations: Because every millisecond counts.

*With Zenif 0.1.0, we're not just releasing a library; we're igniting a revolution in Python development. Welcome to the future of effortless, powerful, and joyful coding!*
