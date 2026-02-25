# Contributing to DRIXL

Thank you for your interest in contributing to DRIXL!

## Ways to Contribute

- **Propose new verbs** - Open an issue with the verb code, full meaning, and example
- **Improve the parser** - Edge cases, performance, error handling
- **Add backends** - New context store backends (DynamoDB, MongoDB, etc.)
- **Write examples** - Real-world agent pipeline examples
- **Fix bugs** - Check open issues labeled `bug`
- **Improve docs** - Clarity, typos, missing sections

## Setup

```bash
git clone https://github.com/SamoTech/DRIXL.git
cd DRIXL
pip install -e ".[all]"
pip install pytest
```

## Running Tests

```bash
pytest tests/
```

## Verb Proposal Format

When proposing a new verb, open an issue with this format:

```
Verb: NEWVB
Full Meaning: [What it does]
Example: NEWVB [param1] [param2]
Rationale: [Why it's needed - what existing verbs don't cover]
```

## Pull Request Guidelines

1. Fork the repo and create a branch: `git checkout -b feature/my-feature`
2. Write tests for any new functionality
3. Ensure all tests pass: `pytest tests/`
4. Submit a PR with a clear description
