#!/usr/bin/env python3
"""Tests for the output-evaluation runner."""

from __future__ import annotations

import importlib.util
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location("output_eval", ROOT / "scripts" / "output_eval.py")
if SPEC is None or SPEC.loader is None:  # pragma: no cover
    raise RuntimeError("unable to load scripts/output_eval.py")
EVAL = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(EVAL)


class OutputEvalTest(unittest.TestCase):
    def test_real_package_passes_recorded_fixture_mode(self) -> None:
        result = EVAL.evaluate(ROOT, ROOT / "evals" / "output_cases.json")
        self.assertFalse(result["ok"])
        self.assertEqual(result["evidence_kind"], "recorded_fixture")
        self.assertTrue(result["missing_evidence"])
        self.assertEqual(result["summary"]["cases_passed"], 2)
        self.assertEqual(result["summary"]["assertions_skipped"], 6)

    def test_deterministic_assertions_on_temp_files(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "SKILL.md").write_text("name: demo\nsecret sk-test\n", encoding="utf-8")
            ok, detail = EVAL.run_assertion(root, {"kind": "contains", "path": "SKILL.md", "needle": "name: demo"})
            self.assertTrue(ok, detail)
            ok, detail = EVAL.run_assertion(
                root, {"kind": "not_contains", "path": "SKILL.md", "needle": "sk-test"}
            )
            self.assertFalse(ok, detail)
            ok, _ = EVAL.run_assertion(root, {"kind": "file_exists", "path": "missing.md"})
            self.assertFalse(ok)

    def test_llm_assert_requires_api_key(self) -> None:
        with patch.dict(EVAL.os.environ, {}, clear=False):
            EVAL.os.environ.pop("OPENAI_API_KEY", None)
            with self.assertRaises(RuntimeError):
                EVAL.llm_judge({"kind": "llm_judge", "prompt": "ok?", "must": "yes"}, "gpt-4o-mini")

    def test_fixture_mode_counts_skipped_llm_judges(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "SKILL.md").write_text("demo\n", encoding="utf-8")
            cases = {
                "cases": [
                    {
                        "id": "a",
                        "prompt": "p",
                        "baseline_output": "b",
                        "with_skill_output": "w",
                        "assertions": [
                            {"kind": "file_exists", "path": "SKILL.md"},
                            {"kind": "llm_judge", "prompt": "q?", "must": "yes"},
                        ],
                    }
                ]
            }
            cases_path = root / "cases.json"
            cases_path.write_text(json.dumps(cases), encoding="utf-8")
            result = EVAL.evaluate(root, cases_path)
            self.assertFalse(result["ok"])
            self.assertEqual(result["summary"]["assertions_total"], 2)
            self.assertEqual(result["summary"]["assertions_executed"], 1)
            self.assertEqual(result["summary"]["assertions_skipped"], 1)
            self.assertEqual(result["summary"]["with_skill_assertion_pass_rate"], 1.0)

    def test_normalize_llm_answer_handles_lists_and_extra_words(self) -> None:
        self.assertEqual(EVAL.normalize_llm_answer("yes"), "yes")
        self.assertEqual(EVAL.normalize_llm_answer("yes, yes, yes"), "yes")
        self.assertEqual(EVAL.normalize_llm_answer("No, because..."), "no")
        self.assertIsNone(EVAL.normalize_llm_answer("maybe"))

    def test_blind_pack_creates_three_artifacts(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            out = root / "pack"
            cases = [
                {"id": "a", "prompt": "p", "baseline_output": "b", "with_skill_output": "w"},
                {"id": "b", "prompt": "p2", "baseline_output": "b2", "with_skill_output": "w2"},
            ]
            files = EVAL.build_blind_pack(root, cases, out)
            self.assertEqual(len(files), 3)
            for name in files:
                self.assertTrue((out / name).is_file(), name)
            key = json.loads((out / "answer-key.json").read_text(encoding="utf-8"))
            self.assertEqual(len(key["mapping"]), 2)
            self.assertIn("DO NOT OPEN", key["_warning"])


if __name__ == "__main__":
    unittest.main()
