# StudyOS Platform

Citation-first tutoring, adaptive quizzes, mastery tracking, study planning, and
AI control-plane events in one dependency-light reference platform.

StudyOS demonstrates the architecture behind a governed AI learning product. It
uses deterministic local implementations so the full workflow is testable
without API keys; model providers, vector stores, and databases can be swapped
behind the existing service boundaries.

## Demo

```bash
PYTHONPATH=src python3 -m studyos demo
```

## Tests

```bash
python3 -m pytest
```

See [docs/PRD.md](docs/PRD.md) for the product and architecture decisions.

