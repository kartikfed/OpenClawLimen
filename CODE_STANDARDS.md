# CODE_STANDARDS.md - Coding Practices

When writing code, follow these standards. No exceptions.

## Before Writing Code

1. **Plan first** — Outline approach and file changes before coding
2. **Ask if ambiguous** — Clarify requirements rather than assuming

## While Writing Code

- **Type hints required** — All function signatures must have annotations
- **Docstrings required** — All public functions and classes
- **Meaningful names** — No abbreviations unless universally understood
- **No hardcoded values** — Use constants, configs, or env vars
- **Explicit error handling** — Specific exceptions, never bare `except:`
- **Logging over print** — Use `logging` module
- **Small functions** — Under ~30 lines, single-purpose

## Before Considering Task Complete

1. **Format:** `black src/`
2. **Lint:** `ruff check src/ --fix`
3. **Type check:** `mypy src/`
4. **Test:** `pytest tests/`
5. **Review diff** — Check for unused imports, dead code

## Git Commits

- **Atomic commits** — One logical change per commit
- **Conventional messages** — `feat:`, `fix:`, `refactor:`, `docs:`, `test:`
- **No debris** — No commented-out code, no TODOs without context

## Refactoring Rules

- Preserve existing test coverage
- Don't change behavior unless explicitly asked
- Follow existing patterns in the codebase

---

## Python Example

```python
"""Module docstring explaining purpose."""

import logging
from typing import Optional

logger = logging.getLogger(__name__)

# Constants at top
DEFAULT_TIMEOUT = 30
MAX_RETRIES = 3


def fetch_data(url: str, timeout: Optional[int] = None) -> dict:
    """Fetch data from URL with retry logic.
    
    Args:
        url: The endpoint to fetch from
        timeout: Request timeout in seconds (default: DEFAULT_TIMEOUT)
    
    Returns:
        Parsed JSON response as dict
    
    Raises:
        ConnectionError: If all retries fail
    """
    timeout = timeout or DEFAULT_TIMEOUT
    
    for attempt in range(MAX_RETRIES):
        try:
            response = requests.get(url, timeout=timeout)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            logger.warning(f"Attempt {attempt + 1} failed: {e}")
            if attempt == MAX_RETRIES - 1:
                raise ConnectionError(f"Failed after {MAX_RETRIES} attempts") from e
```

## TypeScript Example

```typescript
/**
 * Fetches user data with proper error handling
 */
async function fetchUser(userId: string): Promise<User> {
  const response = await fetch(`/api/users/${userId}`);
  
  if (!response.ok) {
    throw new Error(`Failed to fetch user: ${response.status}`);
  }
  
  return response.json();
}
```
