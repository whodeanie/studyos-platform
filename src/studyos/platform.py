from __future__ import annotations

import hashlib
import re

from .mastery import MasteryModel
from .models import AuditEvent, QuizQuestion, TutorAnswer
from .retrieval import CourseIndex

QUIZ_STOPWORDS = {
    "about",
    "after",
    "before",
    "generate",
    "includes",
    "influence",
    "stores",
    "through",
    "while",
}


class StudyOS:
    def __init__(self) -> None:
        self.index = CourseIndex()
        self.mastery = MasteryModel()
        self.audit_log: list[AuditEvent] = []

    def ingest(self, source_id: str, topic: str, text: str) -> int:
        count = self.index.ingest(source_id, topic, text)
        self._audit("course.ingested", {"source_id": source_id, "topic": topic, "chunks": count})
        return count

    def ask(self, question: str) -> TutorAnswer:
        chunks = self.index.search(question)
        route = self._route(question)
        if not chunks:
            answer = TutorAnswer(
                answer="I could not find support for that question in the course materials.",
                citations=[],
                route=route,
            )
        else:
            evidence = " ".join(chunk.text for chunk in chunks)
            answer = TutorAnswer(
                answer=f"Based on the course materials: {evidence}",
                citations=[chunk.source_id for chunk in chunks],
                route=route,
            )
        self._audit(
            "tutor.answered",
            {"question": question, "citations": answer.citations, "route": route},
        )
        return answer

    def generate_quiz(self, count: int = 3) -> list[QuizQuestion]:
        topics = sorted(self.index.topics(), key=self.mastery.score)
        questions = []
        for topic in topics:
            chunks = self.index.chunks_for_topic(topic)
            if not chunks:
                continue
            chunk = chunks[0]
            key_terms = [
                word
                for word in re.findall(r"[A-Za-z]{5,}", chunk.text)
                if word.lower() not in QUIZ_STOPWORDS
            ][:3]
            answer = key_terms[0] if key_terms else topic
            question_id = hashlib.sha1(f"{topic}:{chunk.source_id}".encode()).hexdigest()[:8]
            questions.append(
                QuizQuestion(
                    question_id=question_id,
                    topic=topic,
                    prompt=f"Explain the role of {answer} in {topic}.",
                    answer=answer,
                    explanation=chunk.text,
                    citation=chunk.source_id,
                    difficulty=2 if self.mastery.score(topic) < 0.6 else 3,
                )
            )
            if len(questions) == count:
                break
        self._audit("quiz.generated", {"count": len(questions), "topics": [q.topic for q in questions]})
        return questions

    def grade(self, question: QuizQuestion, response: str) -> dict[str, object]:
        correct = question.answer.lower() in response.lower()
        score = self.mastery.record(question.topic, correct)
        result = {
            "question_id": question.question_id,
            "correct": correct,
            "topic": question.topic,
            "mastery": score,
            "citation": question.citation,
        }
        self._audit("quiz.graded", result)
        return result

    def study_plan(self) -> list[str]:
        plan = self.mastery.study_plan(self.index.topics())
        self._audit("plan.generated", {"items": len(plan)})
        return plan

    def control_plane(self) -> dict[str, object]:
        routes: dict[str, int] = {}
        for event in self.audit_log:
            if event.event_type != "router.selected":
                continue
            route = event.detail.get("route")
            if isinstance(route, str):
                routes[route] = routes.get(route, 0) + 1
        return {
            "events": len(self.audit_log),
            "routes": routes,
            "mastery": self.mastery.snapshot(self.index.topics()),
        }

    def _route(self, question: str) -> str:
        route = "grounded-tutor-large" if len(question.split()) > 12 else "grounded-tutor-fast"
        self._audit("router.selected", {"route": route, "reason": "question_length"})
        return route

    def _audit(self, event_type: str, detail: dict[str, object]) -> None:
        self.audit_log.append(AuditEvent(event_type=event_type, detail=detail))
