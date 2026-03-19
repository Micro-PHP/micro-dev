# micro-dev
Development Framework

The repository initialization process now fetches remote history and ensures
the package repository is in sync with the monorepo. Any local changes after
initialization are logged as warnings.
The release scripts require the `gh` GitHub CLI to be installed and accessible
in the `PATH`. Version numbers are automatically derived from existing git
tags and release notes are collected from merge commit messages.

## Running Python tests

Install dependencies:

```
pip install -r requirements.txt
```

Execute the test suite using:

```
pytest tests/python
```

No additional environment variables are required.
