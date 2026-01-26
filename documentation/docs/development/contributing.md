# Contributing

Thank you for your interest in contributing to Compere!

## Development Setup

1. Fork the repository on GitHub
2. Clone your fork:

```bash
git clone https://github.com/YOUR_USERNAME/compere.git
cd compere
```

3. Install dependencies:

```bash
uv sync --all-extras
```

4. Create a branch:

```bash
git checkout -b feature/your-feature-name
```

## Code Style

We use [ruff](https://github.com/astral-sh/ruff) for linting and formatting.

### Check Code

```bash
uvx ruff check .
```

### Format Code

```bash
uvx ruff format .
```

### Configuration

Ruff is configured in `pyproject.toml`:

- Line length: 120
- Target: Python 3.11
- Rules: E, W, F, I, B, C4, UP

## Testing

### Run Tests

```bash
# All tests
uv run pytest

# With coverage
uv run pytest --cov=compere --cov-report=html

# Specific file
uv run pytest tests/test_api.py

# Verbose output
uv run pytest -v
```

### Write Tests

- Place tests in the `tests/` directory
- Name test files `test_*.py`
- Name test functions `test_*`
- Use pytest fixtures for setup

## Pull Request Process

1. **Update documentation** for any new features
2. **Add tests** for new functionality
3. **Run the test suite** and ensure all tests pass
4. **Run linting** and fix any issues
5. **Write a clear PR description**

### PR Title Format

Use conventional commits:

- `feat:` New features
- `fix:` Bug fixes
- `docs:` Documentation
- `test:` Tests
- `refactor:` Code refactoring
- `chore:` Maintenance tasks

### PR Description Template

```markdown
## Summary
Brief description of changes

## Changes
- Change 1
- Change 2

## Testing
How to test these changes

## Checklist
- [ ] Tests added/updated
- [ ] Documentation updated
- [ ] Linting passes
```

## Commit Messages

Write clear, concise commit messages:

```
feat: add entity search functionality

- Add search parameter to list_entities endpoint
- Update tests for search functionality
- Add documentation for search feature
```

## Code Review

All PRs require review before merging. Reviewers will check:

- Code quality and style
- Test coverage
- Documentation
- Backwards compatibility

## Reporting Issues

### Bug Reports

Include:

- Compere version
- Python version
- Operating system
- Steps to reproduce
- Expected vs actual behavior
- Full error message/stack trace

### Feature Requests

Include:

- Use case description
- Proposed solution
- Alternatives considered

## Questions?

- Open a GitHub Discussion
- Check existing issues first

## License

By contributing, you agree that your contributions will be licensed under the MIT License.
