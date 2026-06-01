# Contributing to the QuantaSeal Python SDK

Thank you for your interest in contributing!

## What this repo is

This is the **Python SDK** for [QuantaSeal](https://quantaseal.io) - a
quantum-safe security middleware platform. The SDK is a thin typed client over
the QuantaSeal REST API. It does not contain the PQC cryptographic engine
(that runs server-side).

## How to contribute

1. **Bug reports** - open a GitHub issue with reproduction steps
2. **Feature requests** - open an issue describing the use case
3. **Pull requests** - welcome for bug fixes, docs, and new resource methods

## Development setup

```bash
git clone https://github.com/quantaseal/sdk-python.git
cd sdk-python
python -m venv .venv && source .venv/bin/activate
pip install -e ".[dev]"

# Run tests (requires QUANTASEAL_API_KEY env var for integration tests)
pytest tests/ -v

# Lint + format
ruff check src/ tests/
ruff format src/ tests/

# Type check
mypy src/
```

## Pull request guidelines

- Target the `main` branch
- Include tests for any new functionality
- `ruff` and `mypy` must pass with zero errors
- Follow the existing code style (async-first, typed, no bare `except`)

## Licence

Apache 2.0. By submitting a PR you agree your contribution will be licensed under the same terms.
