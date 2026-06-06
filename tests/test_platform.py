from studyos import StudyOS


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

