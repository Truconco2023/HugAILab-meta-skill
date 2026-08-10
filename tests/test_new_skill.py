#!/usr/bin/env python3
"""Tests for the one-command skill scaffolder."""

from __future__ import annotations

import importlib.util
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location("new_skill", ROOT / "scripts" / "new_skill.py")
if SPEC is None or SPEC.loader is None:  # pragma: no cover
    raise RuntimeError("unable to load scripts/new_skill.py")
NEW_SKILL = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(NEW_SKILL)


class NewSkillTest(unittest.TestCase):
    def test_name_validation(self) -> None:
        self.assertEqual(NEW_SKILL.validate_name(" My-Demo "), "hugailab-my-demo")
        self.assertEqual(NEW_SKILL.validate_name("hugailab-demo"), "hugailab-demo")
        self.assertEqual(NEW_SKILL.validate_name("hugailab-web-clipper"), "hugailab-web-clipper")
        self.assertEqual(
            NEW_SKILL.validate_name("hugailab-a-b-c-d-e"),
            "hugailab-a-b-c-d-e",
        )
        self.assertEqual(NEW_SKILL.validate_name("a-b-c"), "hugailab-a-b-c")
        with self.assertRaises(SystemExit):
            NEW_SKILL.validate_name("Bad Name")
        with self.assertRaises(SystemExit):
            NEW_SKILL.validate_name("skill")
        with self.assertRaises(SystemExit):
            NEW_SKILL.validate_name("hugailab-a-b-c-d-e-f")
        with self.assertRaises(SystemExit):
            NEW_SKILL.validate_name("a-b-c-d-e-f")

    def test_scaffold_mode_creates_valid_package(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            result = subprocess.run(
                [
                    sys.executable,
                    str(ROOT / "scripts" / "new_skill.py"),
                    "my-demo",
                    "--dir",
                    directory,
                    "--description",
                    "把周报整理成要点和待办",
                ],
                capture_output=True,
                text=True,
                check=False,
            )
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            self.assertTrue((Path(directory) / "hugailab-my-demo" / "SKILL.md").is_file())

    def test_production_mode_generates_evidence_reports(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            result = subprocess.run(
                [
                    sys.executable,
                    str(ROOT / "scripts" / "new_skill.py"),
                    "prod-demo",
                    "--dir",
                    directory,
                    "--mode",
                    "production",
                    "--description",
                    "把需求文档整理成验收清单",
                ],
                capture_output=True,
                text=True,
                check=False,
            )
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            reports = Path(directory) / "hugailab-prod-demo" / "reports"
            self.assertTrue((reports / "skill-ir.json").is_file())
            self.assertTrue((reports / "trigger-eval.json").is_file())
            self.assertTrue((reports / "scorecard.json").is_file())
            scorecard = json.loads((reports / "scorecard.json").read_text(encoding="utf-8"))
            self.assertEqual(scorecard["snapshot"], "initial")


if __name__ == "__main__":
    unittest.main()
