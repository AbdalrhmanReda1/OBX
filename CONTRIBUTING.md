# Contributing to OBX

Thank you for your interest in contributing to OBX — Autonomous Runtime Intelligence for Python.

## Getting Started

```bash
git clone https://github.com/AbdalrhmanReda1/obx
cd obx
pip install -e ".[dev]"
```

## Code Standards

- Python 3.8+ compatibility required
- Full type hints on all public APIs
- No comments inside source files — code must be self-documenting
- No debug `print()` statements
- All public functions must have docstrings
- Line length: 100 characters maximum

## Testing

```bash
pytest tests/ -v --cov=obx
```

All PRs must maintain or improve test coverage.

## Submitting a Pull Request

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/your-feature`
3. Write tests for your changes
4. Ensure all tests pass: `pytest`
5. Run type checking: `mypy obx/`
6. Submit your PR with a clear description

## Reporting Issues

Use GitHub Issues. Include:
- Python version
- OBX version (`obx --version`)
- Minimal reproducible example
- Full traceback

## Contact

- GitHub: [@AbdalrhmanReda1](https://github.com/AbdalrhmanReda1)
- Telegram: [@o7_4l](https://t.me/o7_4l)
