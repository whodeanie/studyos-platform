from __future__ import annotations

import argparse
import json
from dataclasses import asdict

from .platform import StudyOS


COURSE_MATERIALS = [
    (
        "biology-lecture-1",
        "cell biology",
        "Mitochondria generate ATP through cellular respiration. ATP supplies usable energy for cellular work.",
    ),
    (
        "biology-lecture-2",
        "genetics",
        "DNA stores hereditary information. Genes are DNA segments that influence traits through RNA and protein production.",
    ),
    (
        "biology-lecture-3",
        "ecology",
        "An ecosystem includes organisms and their physical environment. Energy flows through food webs while matter cycles.",
    ),
]


def demo() -> dict[str, object]:
    platform = StudyOS()
    for source_id, topic, text in COURSE_MATERIALS:
        platform.ingest(source_id, topic, text)
    answer = platform.ask("How do mitochondria help a cell?")
    quiz = platform.generate_quiz(3)
    if quiz:
        platform.grade(quiz[0], quiz[0].answer)
        for question in quiz[1:]:
            platform.grade(question, "not sure")
    return {
        "tutor_answer": asdict(answer),
        "quiz": [asdict(question) for question in quiz],
        "study_plan": platform.study_plan(),
        "control_plane": platform.control_plane(),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="StudyOS reference platform")
    parser.add_argument("command", choices=["demo"])
    args = parser.parse_args()
    if args.command == "demo":
        print(json.dumps(demo(), indent=2))
    return 0

