from __future__ import annotations

import re

from .models import SourceChunk


class CourseIndex:
    def __init__(self) -> None:
        self._chunks: list[SourceChunk] = []

    def ingest(self, source_id: str, topic: str, text: str) -> int:
        paragraphs = [
            paragraph.strip()
            for paragraph in re.split(r"\n\s*\n", text)
            if paragraph.strip()
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


def terms(text: str) -> set[str]:
    return {
        token
        for token in re.findall(r"[a-z0-9]+", text.lower())
        if len(token) > 2
    }

