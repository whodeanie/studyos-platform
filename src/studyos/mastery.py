from __future__ import annotations


class MasteryModel:
    def __init__(self) -> None:
        self._scores: dict[str, float] = {}

    def record(self, topic: str, correct: bool) -> float:
        current = self._scores.get(topic, 0.5)
        delta = 0.12 if correct else -0.16
        score = min(1.0, max(0.0, current + delta))
        self._scores[topic] = round(score, 2)
        return self._scores[topic]

    def score(self, topic: str) -> float:
        return self._scores.get(topic, 0.5)

    def snapshot(self, topics: list[str]) -> dict[str, float]:
        return {topic: self.score(topic) for topic in topics}

    def study_plan(self, topics: list[str]) -> list[str]:
        ordered = sorted(topics, key=self.score)
        return [
            f"{position}. {topic}: mastery {self.score(topic):.0%}"
            for position, topic in enumerate(ordered, 1)
        ]

