from __future__ import annotations

import re

from .models import SourceChunk


class CourseIndex:
    def __init__(self) -> None:
        self._chunks: list[SourceChunk] = []

    def ingest(self, source_id: str, topic: str, text: str) -> int:
        source_id = source_id.strip()
        topic = topic.strip()
        text = text.strip()
        if not source_id or "#" in source_id:
            raise ValueError("source_id must be non-empty and cannot contain #")
        if not topic:
            raise ValueError("topic must be non-empty")
        if not text:
            raise ValueError("text must be non-empty")

        paragraphs = [
            paragraph.strip()
            for paragraph in re.split(r"\n\s*\n", text)
            if paragraph.strip()
        ]
        self._chunks = [
            chunk
            for chunk in self._chunks
            if chunk.source_id.rsplit("#", 1)[0] != source_id
        ]
        for index, paragraph in enumerate(paragraphs, 1):
            self._chunks.append(
                SourceChunk(
                    source_id=f"{source_id}#{index}",
                    topic=topic,
                    text=paragraph,
                )
            )
        return len(paragraphs)

    def search(self, query: str, limit: int = 3) -> list[SourceChunk]:
        query_terms = terms(query)
        ranked = sorted(
            self._chunks,
            key=lambda chunk: (
                len(query_terms & terms(chunk.text)),
                len(query_terms & terms(chunk.topic)),
            ),
            reverse=True,
        )
        return [
            chunk
            for chunk in ranked
            if query_terms & (terms(chunk.text) | terms(chunk.topic))
        ][:limit]

    def topics(self) -> list[str]:
        return sorted({chunk.topic for chunk in self._chunks})

    def chunks_for_topic(self, topic: str) -> list[SourceChunk]:
        return [chunk for chunk in self._chunks if chunk.topic == topic]

    def source_count(self) -> int:
        return len({chunk.source_id.rsplit("#", 1)[0] for chunk in self._chunks})


def terms(text: str) -> set[str]:
    return {
        token
        for token in re.findall(r"[a-z0-9]+", text.lower())
        if len(token) > 2
    }
