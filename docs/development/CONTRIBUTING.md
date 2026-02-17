# Contributing to OracleDBA

First off, thank you for considering contributing to OracleDBA! 🎉

## How Can I Contribute?

### Reporting Bugs

Before creating bug reports, please check the existing issues to avoid duplicates. When you create a bug report, include as many details as possible:

- **Use a clear and descriptive title**
- **Describe the exact steps to reproduce the problem**
- **Provide specific examples**
- **Describe the behavior you observed and what you expected**
- **Include screenshots if relevant**
- **Specify your environment**: OS, Oracle version, Python version

### Suggesting Enhancements

Enhancement suggestions are tracked as GitHub issues. When creating an enhancement suggestion:

- **Use a clear and descriptive title**
- **Provide a detailed description of the suggested enhancement**
- **Explain why this enhancement would be useful**
- **List any similar features in other tools**

### Pull Requests

1. Fork the repository
2. Create a new branch (`git checkout -b feature/amazing-feature`)
3. Make your changes
4. Run tests if available
5. Commit your changes (`git commit -m 'Add amazing feature'`)
6. Push to the branch (`git push origin feature/amazing-feature`)
7. Open a Pull Request

#### Pull Request Guidelines

- Follow the existing code style
- Add docstrings to new functions and classes
- Update documentation if needed
- Keep changes focused - one feature/fix per PR
- Write clear commit messages
- Test your changes thoroughly

## Development Setup

```bash
# Clone your fork
git clone https://github.com/ELMRABET-Abdelali/oracledba.git
cd oracledba

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install in development mode
pip install -e .

# Install development dependencies
pip install -e .[dev]
```

## Code Style

- Follow PEP 8 guidelines
- Use meaningful variable and function names
- Add comments for complex logic
- Keep functions focused and modular
- Use type hints where appropriate

```python
def backup_database(backup_type: str, tag: Optional[str] = None) -> bool:
    """
    Perform database backup.
    
    Args:
        backup_type: Type of backup (full, incremental, archive)
        tag: Optional backup tag
        
    Returns:
        bool: True if backup succeeded, False otherwise
    """
    # Implementation
    pass
```

## Testing

```bash
# Run tests
pytest

# With coverage
pytest --cov=oracledba

# Specific test file
pytest tests/test_rman.py
```

## Documentation

- Update README.md for user-facing changes
- Add docstrings to all public functions and classes
- Update CHANGELOG.md with your changes
- Create/update guides in the docs/ folder if needed

## Commit Messages

- Use present tense ("Add feature" not "Added feature")
- Use imperative mood ("Move cursor to..." not "Moves cursor to...")
- Limit first line to 72 characters
- Reference issues and pull requests when relevant

Examples:
```
Add RMAN incremental backup support

Implement incremental level 0 and 1 backups with proper
retention policy management.

Fixes #123
```

## Community

- Be respectful and inclusive
- Help others in discussions and issues
- Share knowledge and best practices
- Follow the Code of Conduct

## Questions?

Feel free to open an issue with the "question" label or reach out to the maintainers.

Thank you for contributing! 🙏
