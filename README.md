# Antipodal Calculator

A small Python utility that computes the **antipode** (the point on Earth's
surface diametrically opposite a given coordinate), the great-circle distance
to it, and some related helpers.

> ⚠️ **This project is a SonarQube demo fixture.** It intentionally contains
> security vulnerabilities, reliability bugs, and maintainability smells so they
> can be surfaced by a SonarQube Server / SonarQube Cloud scan. **Do not use any
> of this code in production.**

## Layout

```
antipodal-calculator/
  main.py                 CLI entry point
  requirements.txt        pinned (deliberately outdated) dependency
  sonar-project.properties
  antipodal/
    __init__.py
    config.py             hardcoded secrets, insecure defaults
    calculator.py         core antipodal math
    database.py           SQL injection, weak hashing, resource leaks
    api.py                insecure HTTP, eval, pickle, command injection
    utils.py              duplication, dead code, complexity
```

## Run

```bash
python main.py 40.7128 -74.0060 "New York"
```

## Analyze with SonarQube

```bash
sonar-scanner
```

## Categories of planted issues

- **Security (Blocker/Critical):** hardcoded DB password & API keys that must be
  rotated, SQL injection, `eval()`, insecure deserialization (`pickle`),
  command injection (`shell=True`), disabled TLS verification (`verify=False`),
  weak hashing (MD5), insecure randomness for tokens.
- **Reliability (Bugs):** bare `except`, mutable default argument, potential
  division by zero, unclosed resources, unreachable code, unchecked `argv`.
- **Maintainability (Code Smells):** duplicated functions, high cognitive
  complexity, magic numbers, commented-out code, unused imports, TODOs.
- **Dependency risk (SCA):** outdated `requests` pin in `requirements.txt`.
