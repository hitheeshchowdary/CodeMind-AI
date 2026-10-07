import sys
import json
import time
from pathlib import Path

sys.path.insert(
    0,
    str(
        Path(__file__).resolve().parent.parent
    )
)

from app.agents.graph import agent_graph


BASE_DIR = Path(__file__).resolve().parent

QUESTIONS_FILE = (
    BASE_DIR / "evaluation_questions.json"
)

RESULTS_FILE = (
    BASE_DIR / "evaluation_results.json"
)

REPOSITORY_NAME = "RepoMind-AI"


def load_questions():
    with open(
        QUESTIONS_FILE,
        "r",
        encoding="utf-8",
    ) as file:
        return json.load(file)


def run_question(question_data):
    question = question_data["question"]

    print("\n" + "=" * 70)
    print(
        f"Question {question_data['id']}: "
        f"{question}"
    )
    print(
        f"Category: "
        f"{question_data['category']}"
    )
    print("=" * 70)

    start_time = time.perf_counter()

    result = agent_graph.invoke(
        {
            "repository_name": REPOSITORY_NAME,
            "question": question,
            "top_k": 3,
        }
    )

    total_time = (
        time.perf_counter()
        - start_time
    )

    sources = result.get(
        "sources",
        [],
    )

    evaluation_result = {
        "id": question_data["id"],
        "category": question_data["category"],
        "question": question,
        "route": result.get(
            "route",
            "unknown",
        ),
        "retry_count": result.get(
            "retry_count",
            0,
        ),
        "verification_status": result.get(
            "verification_status",
            "not_applicable",
        ),
        "evidence_summary": result.get(
            "evidence_summary",
            "",
        ),
        "answer": result.get(
            "answer",
            "",
        ),
        "sources": sources,
        "source_count": len(sources),
        "latency_seconds": round(
            total_time,
            3,
        ),
    }

    print(
        f"Route: "
        f"{evaluation_result['route']}"
    )

    print(
        f"Retry count: "
        f"{evaluation_result['retry_count']}"
    )

    print(
        f"Sources: "
        f"{evaluation_result['source_count']}"
    )

    print(
        f"Latency: "
        f"{evaluation_result['latency_seconds']} "
        f"seconds"
    )

    return evaluation_result


def main():
    questions = load_questions()

    print(
        f"\nLoaded {len(questions)} "
        f"evaluation questions."
    )

    results = []

    for question_data in questions:
        try:
            result = run_question(
                question_data
            )

            results.append(result)

        except Exception as error:
            print(
                f"ERROR on question "
                f"{question_data['id']}: "
                f"{error}"
            )

            results.append(
                {
                    "id": question_data["id"],
                    "category": question_data[
                        "category"
                    ],
                    "question": question_data[
                        "question"
                    ],
                    "error": str(error),
                }
            )

    with open(
        RESULTS_FILE,
        "w",
        encoding="utf-8",
    ) as file:
        json.dump(
            results,
            file,
            indent=2,
            ensure_ascii=False,
        )

    print("\n" + "=" * 70)
    print("EVALUATION COMPLETE")
    print("=" * 70)

    print(
        f"Results saved to: "
        f"{RESULTS_FILE}"
    )


if __name__ == "__main__":
    main()