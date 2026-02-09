---
name: python-quality
description: Run Python code quality checks (ruff, black, mypy, pytest). Use before committing Python code.
metadata:
  openclaw:
    emoji: "🐍"
    requires:
      anyBins: ["ruff", "black", "mypy", "pytest"]
---

# Python Quality Checks

Run code quality tools on Python projects.

## Quick Commands

### Format Code (Black)
```bash
black src/ tests/ --quiet
```

### Lint Code (Ruff)
```bash
ruff check src/ tests/ --fix
```

### Type Check (Mypy)
```bash
mypy src/
```

### Run Tests (Pytest)
```bash
pytest tests/ -v
```

### All Checks (before committing)
```bash
# If Makefile exists
make check

# Or manually
black src/ tests/ && ruff check src/ tests/ --fix && mypy src/ && pytest tests/
```

## Usage Pattern

Before considering any Python coding task complete:

1. **Format:** `black src/`
2. **Lint:** `ruff check src/ --fix`
3. **Type check:** `mypy src/`
4. **Test:** `pytest tests/`

If any check fails, fix the issues before committing.

## Tool Configs

Tools should be configured in `pyproject.toml`. Standard config:

```toml
[tool.ruff]
target-version = "py39"
line-length = 100
select = ["E", "W", "F", "I", "B", "C4", "UP", "ARG", "SIM"]

[tool.black]
target-version = ["py39"]
line-length = 100

[tool.mypy]
python_version = "3.9"
disallow_untyped_defs = true
ignore_missing_imports = true

[tool.pytest.ini_options]
testpaths = ["tests"]
addopts = "-v --tb=short"
```

## Fixing Common Issues

### Ruff: Unused import
```python
# ❌ F401: 'os' imported but unused
import os

# ✅ Remove unused imports, or:
import os  # noqa: F401  (if intentionally unused)
```

### Mypy: Missing type annotation
```python
# ❌ error: Function is missing a type annotation
def process(data):
    return data

# ✅ Add type hints
def process(data: dict[str, Any]) -> dict[str, Any]:
    return data
```

### Black: Formatting
```bash
# Auto-fixes formatting
black src/ --quiet
```

## Integration with Coding Agents

When using Codex/Claude Code, add to the prompt:
```
After making changes, run:
1. black src/
2. ruff check src/ --fix
3. mypy src/
4. pytest tests/

Fix any issues before considering the task complete.
```
