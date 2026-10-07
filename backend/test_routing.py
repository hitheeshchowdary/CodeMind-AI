import json
from pathlib import Path

from app.services.question_service import QuestionService


question_service = QuestionService()

evaluation_file = Path("evaluation/evaluation_questions.json")

questions = json.loads(
    evaluation_file.read_text(
        encoding="utf-8"
    )
)

for item in questions:
    question = item["question"]

    question_type = question_service.classify_question(
        question
    )

    print(
        f"Q{item['id']}: "
        f"{question_type} | "
        f"{question}"
    )