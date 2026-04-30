# Python Specific Guidance

Load this when working in Python — for any framework (Django, FastAPI, Flask) or for scripting/data work.

## The Pythonic mindset

Python has a strong cultural preference for readability and simplicity. The Zen of Python (`import this`) captures it:

- Beautiful is better than ugly
- Explicit is better than implicit
- Simple is better than complex
- Readability counts
- There should be one — and preferably only one — obvious way to do it

When you have two ways to do something, pick the one that reads more naturally. Pythonic code looks like English.

## PEP 8: the style baseline

Follow PEP 8. Don't argue about it. Use `black` (auto-formatter) and `ruff` (linter) and stop thinking about style.

The essentials:
- 4-space indentation, no tabs
- 79–100 character line limit (black defaults to 88)
- `snake_case` for functions and variables
- `PascalCase` for classes
- `SCREAMING_SNAKE_CASE` for constants
- Two blank lines between top-level definitions, one between methods
- Imports grouped: standard lib, third-party, local — separated by blank lines

```python
# Standard library
import os
from datetime import datetime

# Third-party
import requests
from sqlalchemy import select

# Local
from app.config import settings
from app.models import User
```

## Type hints: use them

Modern Python (3.10+) has good type hints. Use them on every function signature.

```python
# Bad — no types, can't tell what this does
def calculate(items, rate, discount=None):
    ...

# Good — types clarify intent
from decimal import Decimal

def calculate(items: list[Item], rate: Decimal, discount: Decimal | None = None) -> Decimal:
    ...
```

Run `mypy --strict` or `pyright` in CI. Type hints without a checker are documentation that lies.

For data classes, use `@dataclass` or Pydantic:

```python
from dataclasses import dataclass

@dataclass(frozen=True)  # frozen=True for immutability
class Money:
    amount: Decimal
    currency: str

# Or for validation + serialization, Pydantic
from pydantic import BaseModel, EmailStr

class User(BaseModel):
    id: int
    email: EmailStr
    name: str
    age: int | None = None
```

## Use the right data structures

| Need | Use | Don't use |
|---|---|---|
| Ordered, mutable sequence | `list` | manual `dict` with int keys |
| Unique items | `set` | `list` with `if x not in lst` checks |
| Fast lookup by key | `dict` | nested lists |
| Immutable record | `tuple` or `@dataclass(frozen=True)` | mutable dict |
| Counting | `collections.Counter` | manual dict |
| Grouping | `collections.defaultdict(list)` | manual `if key not in d` |
| Queue (FIFO) | `collections.deque` | `list` with `pop(0)` |

```python
# Bad — O(n²) because `in` on a list is O(n)
seen = []
for item in big_list:
    if item not in seen:
        seen.append(item)

# Good — O(n)
seen = set()
for item in big_list:
    if item not in seen:
        seen.add(item)

# Better — Pythonic
unique_items = list(set(big_list))  # if order doesn't matter
unique_items = list(dict.fromkeys(big_list))  # preserves order
```

## List/dict/set comprehensions: use them, but readably

Comprehensions are Pythonic when they fit one line. When they're getting long, use a regular loop.

```python
# Good — clear comprehension
squares = [x ** 2 for x in numbers if x > 0]

# Acceptable — slightly more complex
emails = {user.id: user.email for user in users if user.is_active}

# Bad — unreadable nested mess
result = [[x * y for x in range(10) if x % 2 == 0] for y in range(5) if y > 1]

# Good — refactor to loops when complexity grows
result = []
for y in range(5):
    if y <= 1:
        continue
    inner = [x * y for x in range(10) if x % 2 == 0]
    result.append(inner)
```

## Iteration patterns

### `enumerate` instead of manual indexing

```python
# Bad
for i in range(len(items)):
    print(f"{i}: {items[i]}")

# Good
for i, item in enumerate(items):
    print(f"{i}: {item}")
```

### `zip` for parallel iteration

```python
# Bad
for i in range(len(names)):
    print(f"{names[i]} is {ages[i]}")

# Good
for name, age in zip(names, ages, strict=True):
    print(f"{name} is {age}")
```

`strict=True` (Python 3.10+) raises if the iterables have different lengths — usually what you want.

### Iterate over dict items

```python
# Bad
for key in d:
    value = d[key]
    ...

# Good
for key, value in d.items():
    ...
```

## Context managers (`with`)

Always use context managers for resources that need cleanup:

```python
# Bad — leaks file handle on error
f = open('data.txt')
data = f.read()
f.close()

# Good
with open('data.txt') as f:
    data = f.read()
# File automatically closed, even on exception
```

This applies to: files, database connections, locks, network connections, anything with `acquire/release` semantics.

For your own resources, implement `__enter__` and `__exit__`, or use `contextlib.contextmanager`:

```python
from contextlib import contextmanager

@contextmanager
def database_transaction(db):
    db.begin()
    try:
        yield db
        db.commit()
    except Exception:
        db.rollback()
        raise
```

## Errors and exceptions

### Raise specific exceptions

```python
# Bad
raise Exception("user not found")

# Good
class UserNotFoundError(Exception):
    pass

raise UserNotFoundError(f"User {user_id} not found")

# Or use built-in types where they fit
raise ValueError("age must be non-negative")
raise KeyError(user_id)
```

### Catch specific exceptions

```python
# Bad — swallows everything, including bugs and KeyboardInterrupt
try:
    do_thing()
except:
    pass

# Bad — too broad
try:
    do_thing()
except Exception:
    pass

# Good — narrow and intentional
try:
    do_thing()
except (ConnectionError, TimeoutError) as e:
    logger.warning("network failure", exc_info=e)
    return fallback()
```

### Use `raise ... from` to preserve causation

```python
try:
    config = json.loads(raw)
except json.JSONDecodeError as e:
    raise ConfigError(f"invalid config in {path}") from e
```

The `from e` preserves the original exception in the traceback — essential for debugging.

### EAFP vs LBYL

Python culture prefers **EAFP** (Easier to Ask Forgiveness than Permission) over **LBYL** (Look Before You Leap), in many cases:

```python
# LBYL — check first
if 'key' in d and d['key'] is not None:
    process(d['key'])

# EAFP — try and handle
try:
    process(d['key'])
except KeyError:
    pass
```

EAFP is especially good when the "look" itself can be racy (file existence checks, dict access in concurrent code). For simple cases, either is fine.

## Mutable default arguments — the classic footgun

```python
# Bad — the default list is shared across calls
def add_item(item, items=[]):
    items.append(item)
    return items

add_item('a')  # ['a']
add_item('b')  # ['a', 'b']  ← surprise!

# Good
def add_item(item, items=None):
    if items is None:
        items = []
    items.append(item)
    return items
```

Same applies to `{}`, sets, and any mutable object as a default.

## f-strings for formatting

```python
# Old (avoid)
"%s is %d years old" % (name, age)
"{} is {} years old".format(name, age)

# Modern — use f-strings
f"{name} is {age} years old"

# f-strings support expressions and formatting
f"{price:.2f}"           # 2 decimal places
f"{number:,}"            # thousands separators: 1,234,567
f"{percent:.1%}"         # 0.156 → "15.6%"
f"{value=}"              # debugging: "value=42"
```

## Logging

Use `logging`, not `print`. Configure once at the entry point.

```python
import logging
logger = logging.getLogger(__name__)

# Use it everywhere
logger.info("user logged in", extra={"user_id": user.id})
logger.warning("slow query", extra={"duration_ms": 5000})
logger.error("payment failed", exc_info=True, extra={"order_id": order.id})
```

Set up structured logging in production. The `structlog` library is excellent.

## Project structure

For a real Python project (not a one-off script):

```
my_project/
├── pyproject.toml         ← single source of truth for deps + tooling
├── README.md
├── .gitignore
├── src/
│   └── my_project/
│       ├── __init__.py
│       ├── main.py
│       ├── config.py
│       └── features/
│           ├── users/
│           │   ├── __init__.py
│           │   ├── models.py
│           │   ├── service.py
│           │   ├── repository.py
│           │   └── api.py
│           └── orders/
│               └── ...
├── tests/
│   ├── __init__.py
│   ├── unit/
│   └── integration/
└── scripts/
    └── one_off_tools.py
```

The `src/` layout (with code in `src/my_project/` rather than `my_project/` at the root) avoids subtle import problems and is the modern Python recommendation.

## Virtual environments and dependencies

Always use a virtual environment per project. Never `pip install` globally.

Modern recommendation: **`uv`** (fast) or **`poetry`** (mature). `pyproject.toml` is the modern manifest format.

```toml
# pyproject.toml
[project]
name = "my-project"
version = "0.1.0"
dependencies = [
    "fastapi>=0.110",
    "sqlalchemy>=2.0",
    "pydantic>=2.0",
]

[project.optional-dependencies]
dev = [
    "pytest>=8.0",
    "pytest-cov",
    "mypy",
    "ruff",
    "black",
]
```

Pin dependencies. Update them deliberately, not accidentally.

## Testing with pytest

Pytest is the standard. Use fixtures for setup, parametrize for variations.

```python
import pytest

@pytest.fixture
def user_factory(db):
    def make(**kwargs):
        defaults = {"name": "Test", "email": "test@example.com"}
        return User.objects.create(**{**defaults, **kwargs})
    return make

def test_admin_can_delete_users(user_factory):
    admin = user_factory(role="admin")
    user = user_factory(role="user")
    assert can_delete(admin, user) is True

@pytest.mark.parametrize("role,expected", [
    ("admin", True),
    ("user", False),
    ("guest", False),
])
def test_delete_permission_by_role(user_factory, role, expected):
    actor = user_factory(role=role)
    target = user_factory(role="user")
    assert can_delete(actor, target) is expected
```

## Async Python: asyncio

For I/O-bound work (HTTP requests, DB queries), `async`/`await` gives you concurrency without threads.

```python
import asyncio
import httpx

async def fetch_user(client, user_id):
    response = await client.get(f"/users/{user_id}")
    return response.json()

async def fetch_all_users(user_ids):
    async with httpx.AsyncClient() as client:
        tasks = [fetch_user(client, id) for id in user_ids]
        return await asyncio.gather(*tasks)
```

**Don't** mix sync and async carelessly. Calling `time.sleep()` in async code blocks the entire event loop. Use `asyncio.sleep()`.

For CPU-bound work, asyncio doesn't help — use multiprocessing instead.

## Common Python anti-patterns

- **Wildcard imports** (`from module import *`) — pollutes namespace, breaks tooling
- **Modifying a list while iterating** — undefined behavior; iterate over a copy or use a comprehension
- **Using `is` for value comparison** — `is` checks identity, not equality. `if x == 5`, not `if x is 5`. Exception: `is None`/`is not None` is correct.
- **`type(x) == SomeClass`** — use `isinstance(x, SomeClass)` (handles inheritance correctly)
- **String concatenation in a loop** — use `"".join(parts)` instead (much faster for many strings)
- **Catching `Exception` everywhere** — narrow your catches
- **Manual resource management without `with`** — leaks on exception
- **`if len(lst) == 0`** — Pythonic is `if not lst`
- **`if x == True`** — Pythonic is `if x` (assuming x is meant to be boolean)
- **`for i in range(len(seq))`** — use `enumerate(seq)` if you need index, or just iterate

## Tools every Python project should use

- **`black`** — formatter (no debates about style)
- **`ruff`** — fast linter (replaces flake8, isort, and many others)
- **`mypy`** or **`pyright`** — type checker
- **`pytest`** — test framework
- **`pre-commit`** — runs all of the above on every commit
- **`uv`** or **`poetry`** — dependency management

Configure them once in `pyproject.toml`, run them in CI, and you've removed an entire category of code review noise.
