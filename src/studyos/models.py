from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone


@dataclass(frozen=True)
class SourceChunk:
    source_id: str
    topic: str
    text: str


@dataclass(frozen=True)
class TutorAnswer:
    answer: str
    citations: list[str]
    route: str


@dataclass(frozen=True)
class QuizQuestion:
    question_id: str
    topic: str
    prompt: str
    answer: str
    explanation: str
    citation: str
    difficulty: int


@dataclass(frozen=True)
class AuditEvent:
    event_type: str
    detail: dict[str, object]
    created_at: str = field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )

