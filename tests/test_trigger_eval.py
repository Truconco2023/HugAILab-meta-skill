#!/usr/bin/env python3
"""Tests for the weighted trigger-boundary smoke eval."""

from __future__ import annotations

import importlib.util
import json
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location("trigger_eval", ROOT / "scripts" / "trigger_eval.py")
if SPEC is None or SPEC.loader is None:  # pragma: no cover
    raise RuntimeError("unable to load scripts/trigger_eval.py")
EVAL = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(EVAL)


def temp_skill(description: str) -> str:
    directory = tempfile.mkdtemp()
    Path(directory, "SKILL.md").write_text(
        f"---\nname: demo\ndescription: |\n  {description}\n---\n",
        encoding="utf-8",
    )
    return directory


def write_cases(root: str, payload: dict) -> Path:
    path = Path(root) / "cases.json"
    path.write_text(json.dumps(payload, ensure_ascii=False), encoding="utf-8")
    return path


class TriggerEvalTest(unittest.TestCase):
    def test_real_package_passes_strict_mode(self) -> None:
        result = EVAL.evaluate(ROOT, ROOT / "evals" / "trigger_cases.json")
        self.assertTrue(result["ok"], result["failures"])
        self.assertEqual(result["summary"]["pass_rate"], 1.0)
        self.assertEqual(
            result["summary"]["families_covered"],
            result["summary"]["families_total"],
        )
        self.assertEqual(result["mode"], "strict")

    def test_missing_required_concept_fails_strict_but_passes_lenient(self) -> None:
        root = temp_skill("create reusable skill packages from workflows and prompts.")
        cases = write_cases(
            root,
            {
                "description_required_concepts": ["skill", "source_material", "authoring_action"],
                "positive_concepts": EVAL.DEFAULT_CONCEPTS,
                "recommended_threshold": 0.34,
                "negative_patterns": [],
                "should_trigger": [
                    {
                        "text": "把这个流程整理成一个 skill",
                        "family": "workflow",
                        "required": ["skill", "brand"],
                    }
                ],
                "should_not_trigger": [],
                "near_neighbor": [],
            },
        )
        strict = EVAL.evaluate(Path(root), cases)
        self.assertFalse(strict["ok"])
        self.assertTrue(any("brand" in item["required_missing"] for item in strict["failures"]))
        lenient = EVAL.evaluate(Path(root), cases, lenient=True)
        self.assertTrue(lenient["ok"], lenient["failures"])

    def test_uncovered_family_fails_run(self) -> None:
        root = temp_skill("create reusable skill packages from workflows and prompts.")
        cases = write_cases(
            root,
            {
                "description_required_concepts": ["skill"],
                "positive_concepts": EVAL.DEFAULT_CONCEPTS,
                "recommended_threshold": 0.34,
                "negative_patterns": [],
                "should_trigger": [
                    {
                        "text": "把这个流程整理成一个 skill",
                        "family": "workflow",
                        "required": ["skill", "source_material"],
                    },
                    {
                        "text": "发布这个 skill",
                        "family": "publish",
                        "required": ["skill", "brand", "eval_release"],
                    },
                ],
                "should_not_trigger": [],
                "near_neighbor": [],
            },
        )
        result = EVAL.evaluate(Path(root), cases)
        self.assertFalse(result["ok"])
        self.assertIn("publish", result["summary"]["uncovered_families"])
        self.assertTrue(any(item["bucket"] == "family_coverage" for item in result["failures"]))

    def test_near_neighbor_stays_below_threshold(self) -> None:
        root = temp_skill("create reusable skill packages from workflows and prompts.")
        cases = write_cases(
            root,
            {
                "description_required_concepts": ["skill", "source_material", "authoring_action"],
                "positive_concepts": EVAL.DEFAULT_CONCEPTS,
                "recommended_threshold": 0.34,
                "negative_patterns": [],
                "should_trigger": [],
                "should_not_trigger": [],
                "near_neighbor": [
                    {
                        "text": "给这个脚本加一个 argparse 参数",
                        "family": "script_edit",
                    }
                ],
            },
        )
        result = EVAL.evaluate(Path(root), cases)
        self.assertTrue(result["ok"], result["failures"])
        record = result["results"]["near_neighbor"][0]
        self.assertFalse(record["predicted_trigger"])
        self.assertLess(record["score"], 0.34)


if __name__ == "__main__":
    unittest.main()
