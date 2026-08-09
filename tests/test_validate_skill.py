#!/usr/bin/env python3
"""Regression tests for the lightweight package validator."""

from __future__ import annotations

import importlib.util
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location("validate_skill", ROOT / "scripts" / "validate_skill.py")
if SPEC is None or SPEC.loader is None:  # pragma: no cover
    raise RuntimeError("unable to load scripts/validate_skill.py")
VALIDATE_SKILL = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(VALIDATE_SKILL)


class DiscoverSkillEntrypointsTest(unittest.TestCase):
    def test_nested_exact_skill_md_is_discoverable(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            (root / "SKILL.md").write_text("root\n", encoding="utf-8")
            nested = root / "examples" / "demo"
            nested.mkdir(parents=True)
            (nested / "SKILL.md").write_text("nested\n", encoding="utf-8")
            (nested / "SKILL.example.md").write_text("safe example\n", encoding="utf-8")

            entries = VALIDATE_SKILL.discover_skill_entrypoints(root)

            self.assertEqual(entries, [Path("SKILL.md"), Path("examples/demo/SKILL.md")])

    def test_noncanonical_example_and_fixture_names_are_safe(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            (root / "SKILL.md").write_text("root\n", encoding="utf-8")
            nested = root / "examples" / "demo"
            nested.mkdir(parents=True)
            (nested / "SKILL.example.md").write_text("example\n", encoding="utf-8")
            (nested / "SKILL.fixture.md").write_text("fixture\n", encoding="utf-8")

            entries = VALIDATE_SKILL.discover_skill_entrypoints(root)

            self.assertEqual(entries, [Path("SKILL.md")])

    def test_evidence_report_version_mismatch_fails(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            (root / "reports").mkdir()
            (root / "reports" / "skill-ir.json").write_text(
                json.dumps({"package": {"name": "qiaomu-test", "version": "1.0.0"}}), encoding="utf-8"
            )
            (root / "reports" / "trigger-eval.json").write_text(
                json.dumps({"ok": True, "summary": {"total": 1, "passed": 1}}), encoding="utf-8"
            )
            (root / "reports" / "prior-art-research.md").write_text("research", encoding="utf-8")
            (root / "reports" / "creation-handoff.md").write_text("qiaomu-test 2.0.0", encoding="utf-8")
            failures: list[str] = []
            warnings: list[str] = []

            VALIDATE_SKILL.validate_evidence_reports(
                root,
                {"name": "qiaomu-test", "version": "2.0.0", "maturity_tier": "governed"},
                failures,
                warnings,
            )

            self.assertTrue(any("package.version" in item for item in failures))

    def test_load_yaml_works_without_pyyaml_via_bundled_parser(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            interface = root / "agents"
            interface.mkdir()
            (interface / "interface.yaml").write_text(
                "interface:\n  display_name: Demo\ncompatibility:\n  adapter_targets: [openai]\n",
                encoding="utf-8",
            )
            with patch.object(VALIDATE_SKILL, "yaml", None):
                payload = VALIDATE_SKILL.load_yaml(interface / "interface.yaml")
            self.assertEqual(payload["interface"]["display_name"], "Demo")
            self.assertEqual(payload["compatibility"]["adapter_targets"], ["openai"])

    def test_parse_frontmatter_works_without_pyyaml(self) -> None:
        text = "---\nname: demo\ndescription: |\n  第一行\n  第二行\n---\n"
        with patch.object(VALIDATE_SKILL, "yaml", None):
            frontmatter = VALIDATE_SKILL.parse_frontmatter(text)
        self.assertEqual(frontmatter["name"], "demo")
        self.assertIn("第一行", frontmatter["description"])

    def test_creator_defaults_warnings_for_name_rules(self) -> None:
        warnings = VALIDATE_SKILL.creator_defaults_warnings(
            {"name": "a-b-c", "creator_defaults": {"max_preferred_hyphen_parts": 2}},
            "some-dir",
        )
        self.assertTrue(any("3 hyphen parts" in item for item in warnings))
        prefix_warnings = VALIDATE_SKILL.creator_defaults_warnings(
            {"name": "demo", "creator_defaults": {"skill_name_prefix": "hugai-"}},
            "some-dir",
        )
        self.assertTrue(any("skill_name_prefix" in item for item in prefix_warnings))
        self.assertEqual(
            VALIDATE_SKILL.creator_defaults_warnings(
                {"name": "demo", "creator_defaults": {"skill_name_prefix": "hugai-"}},
                "hugailab-meta-skill",
            ),
            [],
        )


if __name__ == "__main__":
    unittest.main()
