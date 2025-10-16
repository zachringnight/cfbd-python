# Contributing to cfbd-python

Thank you for your interest in contributing to cfbd-python! This document provides guidelines and instructions for contributing.

## Development Setup

1. **Clone the repository**
   ```bash
   git clone https://github.com/CFBD/cfbd-python.git
   cd cfbd-python
   ```

2. **Create a virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   pip install -r test-requirements.txt
   ```

4. **Install the package in development mode**
   ```bash
   pip install -e .
   ```

## Running Tests

Run the full test suite:
```bash
pytest --cov=cfbd
```

Run specific test files:
```bash
pytest test/test_games_api.py
```

Run with verbose output:
```bash
pytest -v
```

## Code Quality

### Linting

This project uses flake8 for linting. Run linting checks with:

```bash
# Check for syntax errors and undefined names
flake8 . --count --select=E9,F63,F7,F82 --show-source --statistics

# Check for style issues (warnings only)
flake8 . --count --exit-zero --max-complexity=10 --max-line-length=127 --statistics
```

### Code Style

- Follow PEP 8 guidelines
- Maximum line length: 127 characters
- Use meaningful variable and function names
- Add docstrings to public functions and classes

## Building the Package

To build the package locally:

```bash
pip install build
python -m build
```

This creates distribution files in the `dist/` directory.

## Submitting Changes

1. **Fork the repository** on GitHub

2. **Create a new branch** for your changes
   ```bash
   git checkout -b feature/your-feature-name
   ```

3. **Make your changes** and commit them
   ```bash
   git add .
   git commit -m "Description of your changes"
   ```

4. **Run tests and linting** to ensure everything works
   ```bash
   pytest --cov=cfbd
   flake8 . --count --select=E9,F63,F7,F82 --show-source --statistics
   ```

5. **Push your changes** to your fork
   ```bash
   git push origin feature/your-feature-name
   ```

6. **Open a Pull Request** on GitHub

## Pull Request Guidelines

- Include a clear description of the changes
- Reference any related issues
- Ensure all tests pass
- Maintain or improve code coverage
- Follow the existing code style

## Getting Help

If you have questions or need help:
- Open an issue on GitHub
- Check the [README](README.md) for basic information
- Review existing issues and pull requests

## Code of Conduct

Please be respectful and constructive in all interactions with the project and community.

## License

By contributing to cfbd-python, you agree that your contributions will be licensed under the MIT License.
