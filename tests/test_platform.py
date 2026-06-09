import pytest

from studyos import StudyOS
from studyos.models import QuizQuestion


def make_platform() -> StudyOS:
    platform = StudyOS()
    platform.ingest("lecture-1", "cell biology", "Mitochondria generate ATP for cellular work.")
    platform.ingest("lecture-2", "genetics", "DNA stores hereditary information in genes.")
    return platform


def test_tutor_answer_is_grounded_and_cited() -> None:
    platform = make_platform()

    answer = platform.ask("What do mitochondria generate?")

    assert "ATP" in answer.answer
    assert answer.citations == ["lecture-1#1"]
    assert answer.route.startswith("grounded-tutor")


def test_unknown_question_does_not_invent_answer() -> None:
    platform = make_platform()

    answer = platform.ask("Explain medieval architecture.")

    assert answer.citations == []
    assert "could not find support" in answer.answer


def test_quiz_grading_updates_mastery() -> None:
    platform = make_platform()
    question = platform.generate_quiz(1)[0]
    before = platform.mastery.score(question.topic)

    result = platform.grade(question, question.answer)

    assert result["correct"] is True
    assert platform.mastery.score(question.topic) > before


def test_study_plan_prioritizes_weak_topic() -> None:
    platform = make_platform()
    question = next(q for q in platform.generate_quiz(2) if q.topic == "genetics")
    platform.grade(question, "wrong")

    plan = platform.study_plan()

    assert "genetics" in plan[0]


def test_control_plane_records_routes_and_events() -> None:
    platform = make_platform()
    platform.ask("What do genes store?")

    control = platform.control_plane()

    assert control["events"] >= 4
    assert control["routes"]["grounded-tutor-fast"] == 1


def test_reingesting_a_source_replaces_old_evidence() -> None:
    platform = StudyOS()
    platform.ingest("lecture-1", "cell biology", "Mitochondria generate ATP.")
    platform.ingest("lecture-1", "cell biology", "Mitochondria support cellular respiration.")

    answer = platform.ask("What do mitochondria support?")

    assert answer.citations == ["lecture-1#1"]
    assert "generate ATP" not in answer.answer
    assert platform.control_plane()["sources"] == 1


def test_grading_requires_an_issued_question() -> None:
    platform = make_platform()
    fabricated = QuizQuestion(
        question_id="fabricated",
        topic="genetics",
        prompt="What is DNA?",
        answer="DNA",
        explanation="DNA stores hereditary information.",
        citation="lecture-2#1",
        difficulty=2,
    )

    with pytest.raises(ValueError, match="not issued"):
        platform.grade(fabricated, "DNA")


def test_grading_matches_terms_instead_of_substrings() -> None:
    platform = make_platform()
    question = platform.generate_quiz(1)[0]
    before = platform.mastery.score(question.topic)

    result = platform.grade(question, f"{question.answer}ase")

    assert result["correct"] is False
    assert platform.mastery.score(question.topic) < before


def test_blank_questions_are_rejected_without_an_audit_event() -> None:
    platform = make_platform()
    before = len(platform.audit_log)

    with pytest.raises(ValueError, match="question"):
        platform.ask("   ")

    assert len(platform.audit_log) == before
