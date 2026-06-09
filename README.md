# StudyOS Platform

A small deterministic reference implementation for grounded study workflows:
course-material retrieval, cited tutor responses, quiz generation, mastery
updates, study-plan ordering, routing events, and an in-memory audit log.

StudyOS uses dependency-light local implementations so the complete loop can be
read and tested without API keys. Re-ingesting a source replaces its previous
chunks, only quizzes issued by the current instance can change mastery, and
grading matches answer terms instead of arbitrary substrings.

## What this is not

This is not a deployed tutoring product or an enterprise AI platform. It has no
UI, hosted model, semantic vector search, durable database, authentication,
multi-user state, pedagogical validation, or tamper-resistant audit storage.
The router is a deterministic example based on question length.

## Demo

```bash
PYTHONPATH=src python3 -m studyos demo
```

## Tests

```bash
python3 -m pip install -e ".[dev]"
python3 -m pytest
python3 -m compileall -q src
```

The current suite covers grounded answers, unsupported questions, deterministic
mastery updates, weak-topic planning, route events, idempotent source
replacement, issued-question enforcement, and grading boundaries.

See [docs/PRD.md](docs/PRD.md) for the deliberately narrow architecture.
