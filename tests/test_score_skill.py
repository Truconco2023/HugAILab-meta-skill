#!/usr/bin/env python3
"""Tests for the evidence-bound skill scorer."""

from __future__ import annotations

import importlib.util
import json
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location("score_skill", ROOT / "scripts" / "score_skill.py")
if SPEC is None or SPEC.loader is None:  # pragma: no cover
    raise RuntimeError("unable to load scripts/score_skill.py")
SCORE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(SCORE)


MANIFEST = {
    "name": "hugailab-demo",
    "version": "0.1.0",
    "owner": "HugAILab",
    "updated_at": "2026-08-10",
    "status": "active",
    "maturity_tier": "production",
    "lifecycle_stage": "library",
    "creator_defaults": {
        "skill_name_prefix": "hugailab",
        "max_preferred_hyphen_parts": 3,
        "copyright": "Copyright (c) 2026 HugAILab",
        "x": "",
        "github": "",
    },
    "release_gates": ["validate_skill"],
}


def build_full_evidence_package() -> Path:
    root = Path(tempfile.mkdtemp())
    (root / "SKILL.md").write_text(
        "---\nname: hugailab-demo\ndescription: 把重复任务整理成可验证的 skill 包。\n---\n\n# hugailab-demo\n",
        encoding="utf-8",
    )
    (root / "README.md").write_text(
        "# hugailab-demo\n\n```bash\nnpx skills add HugAILab/hugailab-demo\n```\n\n"
        "## 你可以直接这样说\n\n把文档整理成 skill。\n\n"
        "## 验证\n\npython3 scripts/validate_skill.py .\n\n## Troubleshooting\n\n无。\n\n## License\n\nMIT\n",
        encoding="utf-8",
    )
    interface = root / "agents"
    interface.mkdir()
    (interface / "interface.yaml").write_text(
        "interface:\n"
        "  display_name: demo\n"
        "  short_description: demo\n"
        "  default_prompt: demo\n"
        "compatibility:\n"
        '  adapter_targets: ["openai", "claude", "generic", "agent-skills-compatible"]\n',
        encoding="utf-8",
    )
    (root / "manifest.json").write_text(json.dumps(MANIFEST, ensure_ascii=False), encoding="utf-8")
    tests = root / "tests"
    tests.mkdir()
    (tests / "test_demo.py").write_text("def test_x():\n    assert True\n", encoding="utf-8")
    examples = root / "examples"
    examples.mkdir()
    (examples / "demo.md").write_text("demo", encoding="utf-8")
    evals = root / "evals"
    evals.mkdir()
    (evals / "trigger_cases.json").write_text(
        json.dumps(
            {
                "should_trigger": [{"text": "x", "family": "a", "required": ["skill"]}],
                "should_not_trigger": [],
                "near_neighbor": [],
            },
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )
    reports = root / "reports"
    reports.mkdir()
    (reports / "skill-ir.json").write_text(
        json.dumps({"package": {"name": "hugailab-demo", "version": "0.1.0"}}, ensure_ascii=False),
        encoding="utf-8",
    )
    (reports / "trigger-eval.json").write_text(
        json.dumps({"ok": True, "summary": {"total": 4, "passed": 4, "weak": 0}}),
        encoding="utf-8",
    )
    (reports / "output-evidence.json").write_text(
        json.dumps(
            {
                "ok": True,
                "evidence_kind": "provider_backed",
                "summary": {
                    "cases_total": 2,
                    "cases_passed": 2,
                    "assertions_total": 6,
                    "assertions_executed": 6,
                    "assertions_skipped": 0,
                    "assertions_passed": 6,
                },
            },
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )
    (reports / "prior-art-research.md").write_text(
        "# Prior-Art Research\n\n- Researched at: 2026-08-10\n- 双目录调研完成。\n",
        encoding="utf-8",
    )
    (reports / "creation-handoff.md").write_text("v0.1.0", encoding="utf-8")
    return root


class ScoreSkillTest(unittest.TestCase):
    def test_full_evidence_package_scores_high(self) -> None:
        root = build_full_evidence_package()
        payload = SCORE.score(root, None)
        self.assertGreaterEqual(payload["score"], 8.0)
        self.assertEqual(len(payload["dimensions"]), 6)

    def test_empty_directory_scores_low_with_missing_evidence(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            payload = SCORE.score(Path(directory), None)
            self.assertLess(payload["score"], 2.0)
            self.assertTrue(payload["missing_evidence"])

    def test_fixture_only_output_is_capped(self) -> None:
        root = Path(tempfile.mkdtemp())
        reports = root / "reports"
        reports.mkdir()
        (reports / "output-eval.json").write_text(
            json.dumps(
                {
                    "ok": False,
                    "evidence_kind": "recorded_fixture",
                    "summary": {"cases_total": 2, "cases_passed": 2},
                }
            ),
            encoding="utf-8",
        )
        result = SCORE.score_output(root, None)
        self.assertLessEqual(result["score"], 6.5)
        self.assertTrue(any("封顶" in item for item in result["missing_evidence"]))

    def test_provider_rate_field_without_assertions_passed_scores_full(self) -> None:
        root = Path(tempfile.mkdtemp())
        reports = root / "reports"
        reports.mkdir()
        (reports / "output-evidence.json").write_text(
            json.dumps(
                {
                    "ok": True,
                    "evidence_kind": "provider_backed",
                    "summary": {
                        "cases_total": 3,
                        "cases_passed": 3,
                        "assertions_total": 20,
                        "assertions_executed": 20,
                        "assertions_skipped": 0,
                        "with_skill_assertion_pass_rate": 1.0,
                    },
                }
            ),
            encoding="utf-8",
        )
        result = SCORE.score_output(root, None)
        self.assertEqual(result["score"], 10.0)

    def test_placeholder_prior_art_gets_partial_score(self) -> None:
        root = Path(tempfile.mkdtemp())
        reports = root / "reports"
        reports.mkdir()
        (reports / "skill-ir.json").write_text(
            json.dumps({"package": {"name": "x", "version": "1.0.0"}}),
            encoding="utf-8",
        )
        (reports / "prior-art-research.md").write_text(
            "- Researched at: N/A\n- catalog research not yet run\n",
            encoding="utf-8",
        )
        result = SCORE.score_prior_art_ir(root, {"name": "x", "version": "1.0.0"})
        self.assertEqual(result["score"], 5.0)

    def test_scorecard_markdown_contains_table_and_total(self) -> None:
        payload = {
            "skill_name": "hugailab-demo",
            "version": "0.1.0",
            "score": 8.5,
            "generated_at": "2026-08-10T00:00:00+08:00",
            "dimensions": [
                {"label": "触发边界评测", "weight": 0.15, "score": 10.0, "evidence": "4/4"}
            ],
            "missing_evidence": ["缺 provider 评测"],
        }
        text = SCORE.render_scorecard(payload)
        self.assertIn("综合评分", text)
        self.assertIn("8.5", text)
        self.assertIn("Missing evidence", text)
        self.assertIn("缺 provider 评测", text)


if __name__ == "__main__":
    unittest.main()
