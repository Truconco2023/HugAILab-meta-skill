#!/usr/bin/env python3
"""Tests for the dependency-light YAML-subset fallback parser."""

from __future__ import annotations

import importlib.util
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location("hugai_yaml", ROOT / "scripts" / "hugai_yaml.py")
if SPEC is None or SPEC.loader is None:  # pragma: no cover
    raise RuntimeError("unable to load scripts/hugai_yaml.py")
YAML = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(YAML)


class YamlSubsetTest(unittest.TestCase):
    def test_nested_mapping_and_flow_list(self) -> None:
        payload = YAML.safe_load(
            """
interface:
  display_name: "Meta Skill"
  enabled: true
compatibility:
  adapter_targets: ["openai", "claude", "generic"]
"""
        )
        self.assertEqual(payload["interface"]["display_name"], "Meta Skill")
        self.assertIs(payload["interface"]["enabled"], True)
        self.assertEqual(payload["compatibility"]["adapter_targets"], ["openai", "claude", "generic"])

    def test_block_list_and_scalars(self) -> None:
        payload = YAML.safe_load(
            """
steps:
  - first
  - second
count: 3
ratio: 0.5
empty: null
"""
        )
        self.assertEqual(payload["steps"], ["first", "second"])
        self.assertEqual(payload["count"], 3)
        self.assertEqual(payload["ratio"], 0.5)
        self.assertIsNone(payload["empty"])

    def test_block_scalar_literal_and_folded(self) -> None:
        literal = YAML.safe_load(
            """
description: |
  line one
  line two
"""
        )
        self.assertEqual(literal["description"], "line one\nline two\n")
        folded = YAML.safe_load(
            """
summary: >-
  first paragraph
  still first
"""
        )
        self.assertEqual(folded["summary"], "first paragraph still first")

    def test_comments_and_quoted_keys(self) -> None:
        payload = YAML.safe_load(
            """
"display name": "hello # world"  # trailing comment
plain: value # comment
"""
        )
        self.assertEqual(payload["display name"], "hello # world")
        self.assertEqual(payload["plain"], "value")

    def test_real_interface_yaml_parses(self) -> None:
        payload = YAML.safe_load((ROOT / "agents" / "interface.yaml").read_text(encoding="utf-8"))
        self.assertEqual(payload["interface"]["display_name"], "HugAILab Meta Skill")
        self.assertIn("openai", payload["compatibility"]["adapter_targets"])
        self.assertIn("scaffold", payload["gates"])

    def test_real_frontmatter_block_scalar_parses(self) -> None:
        text = (ROOT / "SKILL.md").read_text(encoding="utf-8")
        lines = text.splitlines()
        end = lines[1:].index("---") + 1
        payload = YAML.safe_load("\n".join(lines[1:end]))
        self.assertEqual(payload["name"], "hugailab-meta-skill")
        self.assertIn("Research, create", payload["description"])
        self.assertEqual(payload["metadata"]["version"], "3.1.0")


if __name__ == "__main__":
    unittest.main()
