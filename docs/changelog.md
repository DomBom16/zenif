# Changelog

## 1.2.0.1 (2024-08-07)

### 🩹 Small Patches

- Changed relative link in `README.md` from `docs/CHANGELOG.md` to `docs/changelog.md`
- Updated main module's docstring
- Renamed `@retry_exponential_backoff` to `@retry_expo`

## 1.2.0 (2024-08-07)

### 🎀 New `decorators` Module

Introduced a powerful set of decorators to enhance function behavior:

- `@retry`: Resilient function execution with customizable retry attempts and delay
- `@retry_exponential_backoff`: Smart retries with exponential backoff
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

### 💻 New `cli` Module

Streamlined command-line interface creation:

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

### 📚 Refactored Documentation

- New documentation inside of `docs/`
  - `modules/`
    - `cli.md`: CLI module documentation
    - `log.md`: Log module documentation
    - `decorators.md`: Decorators module documentation
  - `changelog.md`: Changelog

### 🧪 Tests

- Foundational CLI module test suite
- Extensive unit tests for all decorators

### 🔧 Other

- Updated package dependencies

## 1.1.0 (2024-08-06)

### 🔧 Enhancements to `log` Module

- Introduced `TestLogger` for streamlined testing scenarios
- Fixed ANSI escape sequence handling
- Improved `StreamHandler` configuration
- Refactored `FileHandler` for better performance
- Enhanced support for nested logging groups
- Added multi-stream logging capabilities
- Upgraded `strip_ansi` utility

### 📚 Documentation

- Expanded README with new sections:
  - Changelog
  - Support
  - License
  - Versioning
  - Testing
  - Contributing
- Significantly improved `Logger` documentation
  - Detailed explanations and examples
  - Advanced usage scenarios
  - Best practices guide

### 🧪 Tests

- Enhanced `test1.py` for comprehensive logging tests
- Added `test2.py` to validate `TestLogger` functionality

## 1.0.0 (2024-08-05)

### 🎉 Initial Release

- Launched FluxUtils
- Introduced `log` module with foundational logging capabilities
