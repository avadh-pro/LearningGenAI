"""Simple dataset evaluation runner for the structured classifier."""

import argparse
import asyncio
import json
from pathlib import Path
from typing import Any

from app.config import get_settings
from app.llm_service import LLMService
from app.validation import validate_and_normalize_message


async def evaluate(dataset_path: Path) -> dict[str, Any]:
    settings = get_settings()
    if not settings.openai_is_configured:
        raise RuntimeError("Set OPENAI_API_KEY before running evaluation")

    records = json.loads(dataset_path.read_text(encoding="utf-8"))
    service = LLMService(
        api_key=settings.openai_api_key.get_secret_value(),  # type: ignore[union-attr]
        model=settings.openai_model,
        timeout_seconds=settings.openai_timeout_seconds,
        max_retries=settings.openai_max_retries,
    )

    results: list[dict[str, Any]] = []
    correct_fields = 0
    total_fields = len(records) * 3
    try:
        for record in records:
            message = validate_and_normalize_message(
                record["message"],
                settings.max_input_chars,
            )
            prediction = await service.generate(message)
            expected = record["expected"]
            predicted = prediction.model_dump(mode="json")
            matches = {
                field: predicted[field] == expected[field]
                for field in ("category", "intent", "priority")
            }
            correct_fields += sum(matches.values())
            results.append(
                {
                    "message": message,
                    "expected": expected,
                    "predicted": predicted,
                    "matches": matches,
                }
            )
    finally:
        await service.close()

    exact_matches = sum(all(item["matches"].values()) for item in results)
    return {
        "model": settings.openai_model,
        "examples": len(records),
        "field_accuracy": round(correct_fields / total_fields, 4) if total_fields else 0,
        "exact_match_accuracy": round(exact_matches / len(records), 4) if records else 0,
        "results": results,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Evaluate the support classifier")
    parser.add_argument(
        "--dataset",
        type=Path,
        default=Path("data/evaluation_dataset.json"),
    )
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()

    report = asyncio.run(evaluate(args.dataset))
    rendered = json.dumps(report, indent=2, ensure_ascii=False)
    if args.output:
        args.output.write_text(rendered + "\n", encoding="utf-8")
    else:
        print(rendered)


if __name__ == "__main__":
    main()
