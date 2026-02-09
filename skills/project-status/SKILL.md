---
name: project-status
description: Get status of a project - files changed, test coverage, code stats, recent commits. Useful for Kartik to see what Limen has built.
metadata:
  openclaw:
    emoji: "📊"
---

# Project Status

Quick commands to understand a project's current state.

## For Kartik: "What did Limen build?"

### See Recent Changes
```bash
# Last 10 commits with files changed
git log --oneline --stat -10

# What changed today
git log --oneline --since="midnight"

# Diff of uncommitted changes
git diff --stat
```

### Code Statistics
```bash
# Lines of code by file type
find src -name "*.py" | xargs wc -l | tail -1

# Number of Python files
find src -name "*.py" | wc -l

# Functions defined
grep -r "^def \|^async def " src/ | wc -l

# Classes defined
grep -r "^class " src/ | wc -l
```

### Test Coverage
```bash
# Run tests with coverage
pytest tests/ --cov=src --cov-report=term-missing

# Quick test count
find tests -name "test_*.py" -exec grep -l "def test_" {} \; | wc -l
```

### Project Structure
```bash
# Show directory tree (excluding caches)
tree -I '__pycache__|*.egg-info|.git|.mypy_cache|.pytest_cache|.ruff_cache' -L 3

# Or without tree installed
find . -type f -name "*.py" | grep -v __pycache__ | sort
```

## For Limen: Before Reporting to Kartik

When Kartik asks "what did you build?" or "show me progress":

1. **Run git log** to see commits
2. **Run tree** to show structure
3. **Run tests** to confirm everything works
4. **Summarize** key files and their purpose

### Quick Status Script

```bash
#!/bin/bash
echo "=== Project Status ==="
echo ""
echo "📁 Structure:"
tree -I '__pycache__|*.egg-info|.git' -L 2
echo ""
echo "📝 Recent commits:"
git log --oneline -5
echo ""
echo "📊 Code stats:"
echo "  Python files: $(find src -name '*.py' 2>/dev/null | wc -l)"
echo "  Test files: $(find tests -name 'test_*.py' 2>/dev/null | wc -l)"
echo "  Lines of code: $(find src -name '*.py' -exec cat {} \; 2>/dev/null | wc -l)"
echo ""
echo "✅ Quality check:"
make check 2>/dev/null || echo "  (run 'make check' manually)"
```

## Understanding the Codebase

### Find where something is defined
```bash
# Find a function
grep -rn "def function_name" src/

# Find a class
grep -rn "class ClassName" src/

# Find all imports of a module
grep -rn "from module import\|import module" src/
```

### Understand dependencies
```bash
# What does this file import?
head -30 src/main.py | grep "^import\|^from"

# What imports this file?
grep -rn "from src.module import\|import src.module" src/
```

## Generating Reports

### Markdown Summary
```bash
echo "# Project Status - $(date +%Y-%m-%d)"
echo ""
echo "## Recent Changes"
git log --oneline -10
echo ""
echo "## File Structure"
echo '```'
tree -I '__pycache__|.git' -L 2
echo '```'
echo ""
echo "## Test Results"
pytest tests/ -v --tb=no 2>&1 | tail -20
```
