# Contributing to MnMCP

Thank you for your interest in contributing to MnMCP.

## Getting Started

1. Fork the repository
2. Clone your fork
3. Create a branch for your changes
4. Make your changes
5. Run tests
6. Submit a pull request

## Development Setup

```bash
# Clone repository
git clone https://github.com/StarsailsClover/MnMCP.git
cd MnMCP

# Install dependencies
cd mnmcp-v3-integrated
pip install -r requirements.txt

# Run tests
python -m pytest tests/ -v
```

## Code Style

- Follow PEP 8
- Use type annotations
- Write docstrings for all public functions
- Keep functions focused and small

## Testing

All contributions must include tests:

```bash
# Run tests
python -m pytest tests/ -v

# Check coverage
python -m pytest --cov=src --cov-report=html
```

## Commit Messages

Use clear, descriptive commit messages:

```
feat: add new feature
fix: fix bug
docs: update documentation
test: add tests
refactor: refactor code
```

## Pull Request Process

1. Update documentation if needed
2. Add tests for new features
3. Ensure all tests pass
4. Update CHANGELOG.md
5. Request review

## Code of Conduct

- Be respectful
- Welcome newcomers
- Focus on constructive feedback
