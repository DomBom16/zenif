# Changelog

## 0.1.0 (2024-08-07)

### 🎉 Initial Release of Zenif

Zenif emerges as a powerful toolkit for Python developers, combining advanced logging capabilities, a rich set of decorators for enhanced function behaviors, and tools for building intuitive command-line interfaces. This initial release lays a strong foundation for future enhancements and additions to the Zenif ecosystem.

#### 📝 Log Module

- Powerful and flexible logging system with customizable formatting
- Support for multiple output streams (console and file)
- Advanced log line customization with templating engine
- Stream and file handling with grouping capabilities
- Rule-based configuration for fine-grained control over logging behavior
- ANSI color support and rich formatting options
- `TestLogger` class for simplified testing scenarios

#### 🎀 Decorators Module

A suite of powerful decorators to enhance function behavior:

- `@retry`: Resilient function execution with customizable retry attempts and delay
- `@retry_expo`: Smart retries with exponential backoff
- `@retry_on_exception`: Targeted exception handling with flexible retry options
- `@singleton`: Ensures class instantiation uniqueness
- `@enforce_types`: Strict type hint enforcement for robust code
- `@background_task`: Non-blocking execution in separate threads
- `@profile`: In-depth performance profiling with recursive call support
- `@timeout`: Set maximum execution time limits
- `@rate_limiter`: Control function call frequency
- `@trace`: Comprehensive function call logging
- `@suppress_exceptions`: Graceful exception handling
- `@deprecated`: Clear marking of deprecated functions
- `@type_check`: Runtime type verification
- `@log_execution_time`: Performance timing made easy
- `@cache`: Efficient return value caching
- `@requires_permission`: User permission management

#### 💻 CLI Module

Tools for creating intuitive command-line interfaces:

- `CLI` class: Core CLI builder
- `@command` decorator: Intuitive command definition
- `@argument` decorator: Required positional argument handling
- `@option` decorator: Flexible optional argument support
- `Prompt` class: Rich interactive prompts
  - Text input
  - Secure password entry
  - Yes/no confirmations
  - Single and multi-select options
  - Numeric input with optional constraints

### 📚 Documentation

- Comprehensive README with usage examples and best practices
- Detailed module documentation in `docs/modules/`:
  - `cli.md`: CLI module documentation
  - `log.md`: Log module documentation
  - `decorators.md`: Decorators module documentation
- Changelog (`docs/changelog.md`)

### 🧪 Tests

- Extensive test suite covering all modules
- Specific tests for `TestLogger` functionality
- Unit tests for all decorators
- CLI module test suite

### 🔧 Other

- Modular architecture for easy expansion and maintenance
- Consistent coding style across all modules
- Performance optimizations for core functionalities
