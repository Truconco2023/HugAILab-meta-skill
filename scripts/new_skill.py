#!/usr/bin/env python3
"""Scaffold a new HugAILab skill package in one command.

Generates a lean, validator-clean package (SKILL.md, README, manifest,
interface, trigger cases) and, in production mode, runs the bundled trigger
eval and Skill IR export so the generated evidence reports are real, not
placeholders.
"""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from datetime import date
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
BRAND_PREFIX = "hugailab"


def validate_name(name: str) -> str:
    raw = name.strip().lower()
    if raw in {"skill", "skills", "meta"}:
        raise SystemExit(f"reserved skill name: {raw!r}")
    core = raw[len(BRAND_PREFIX) + 1 :] if raw.startswith(f"{BRAND_PREFIX}-") else raw
    if not re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)?", core):
        raise SystemExit(
            f"invalid skill name: {name!r} "
            f"(HugAILab default is {BRAND_PREFIX}-<word> or {BRAND_PREFIX}-<word>-<word>; "
            "lowercase letters, digits and 1-2 segments after the prefix)"
        )
    return raw if raw.startswith(f"{BRAND_PREFIX}-") else f"{BRAND_PREFIX}-{core}"


def frontmatter(name: str, description: str) -> str:
    return (
        "---\n"
        f"name: {name}\n"
        "description: |\n"
        f"  {description}\n"
        "---\n"
    )


def write_files(root: Path, name: str, description: str, owner: str, production: bool) -> list[Path]:
    version = "0.1.0"
    tail = "" if ("skill" in description.lower() or "技能" in description) else "；作为可复用的 agent skill 交付"
    skill_description = description + tail
    root.mkdir(parents=True, exist_ok=True)
    (root / "SKILL.md").write_text(
        frontmatter(name, skill_description)
        + f"\n# {name}\n\n把「{description}」变成稳定、可验证、可复用的交付物。\n",
        encoding="utf-8",
    )
    (root / "README.md").write_text(
        f"# {name}\n\n> {description}\n\n```bash\nnpx skills add <owner>/{name}\n```\n\n## License\n\nMIT\n",
        encoding="utf-8",
    )
    (root / "manifest.json").write_text(
        json.dumps(
            {
                "name": name,
                "version": version,
                "owner": owner,
                "updated_at": date.today().isoformat(),
                "status": "active",
                "maturity_tier": "production" if production else "scaffold",
                "lifecycle_stage": "library" if production else "scaffold",
                "creator_defaults": {
                    "skill_name_prefix": "",
                    "max_preferred_hyphen_parts": 3,
                    "copyright": f"Copyright (c) {date.today().year} {owner}",
                    "x": "",
                    "github": "",
                },
                "release_gates": [],
            },
            ensure_ascii=False,
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )
    (root / "agents").mkdir(exist_ok=True)
    (root / "agents" / "interface.yaml").write_text(
        "interface:\n"
        f"  display_name: \"{name}\"\n"
        f"  short_description: \"{skill_description}\"\n"
        f"  default_prompt: \"Use ${name} for: {description}. Verify output before delivery.\"\n"
        "compatibility:\n"
        "  canonical_format: agent-skills\n"
        '  adapter_targets: ["openai", "claude", "generic", "agent-skills-compatible"]\n',
        encoding="utf-8",
    )
    (root / "evals").mkdir(exist_ok=True)
    (root / "evals" / "trigger_cases.json").write_text(
        json.dumps(
            {
                "recommended_threshold": 0.34,
                "description_required_concepts": ["skill"],
                "positive_concepts": {
                    "skill": {"phrases": ["skill", "技能"], "weight": 3.0, "core": True}
                },
                "negative_patterns": [],
                "should_trigger": [
                    {
                        "text": f"用 {name} 处理这个任务，输出可复用的 skill 交付物",
                        "family": "main",
                        "required": ["skill"],
                    }
                ],
                "should_not_trigger": [],
                "near_neighbor": [],
            },
            ensure_ascii=False,
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )
    if production:
        (root / "reports").mkdir(exist_ok=True)
    return sorted(root.rglob("*"))


def run_bundled_scripts(root: Path, production: bool) -> None:
    if not production:
        return
    subprocess.run(
        [sys.executable, str(SCRIPT_DIR / "trigger_eval.py"), str(root), "--output", "reports/trigger-eval.json"],
        check=True,
    )
    subprocess.run(
        [sys.executable, str(SCRIPT_DIR / "export_skill_ir.py"), str(root), "--output", "reports/skill-ir.json"],
        check=True,
    )
    (root / "reports" / "prior-art-research.md").write_text(
        "# Prior-Art Research\n\n- Researched at: N/A\n- Missing evidence: catalog research not yet run for this generated package.\n",
        encoding="utf-8",
    )
    (root / "reports" / "creation-handoff.md").write_text(
        "# Creation Handoff\n\n- Reference skills studied: N/A\n- Missing evidence: real task history not yet recorded.\n",
        encoding="utf-8",
    )


def main() -> None:
    parser = argparse.ArgumentParser(description="Scaffold a new HugAILab skill package.")
    parser.add_argument("name", help="Skill name (lowercase letters, digits, hyphens).")
    parser.add_argument("--dir", default=".", help="Parent directory for the new skill.")
    parser.add_argument("--description", default="处理一类重复任务并交付可验证结果", help="One-line job description.")
    parser.add_argument("--owner", default="HugAILab", help="Package owner for manifest.")
    parser.add_argument("--mode", choices=("scaffold", "production"), default="scaffold")
    args = parser.parse_args()

    name = validate_name(args.name)
    target = Path(args.dir).resolve() / name
    if target.exists():
        raise SystemExit(f"target already exists: {target}")
    files = write_files(target, name, args.description, args.owner, args.mode == "production")
    run_bundled_scripts(target, args.mode == "production")
    validation = subprocess.run(
        [sys.executable, str(SCRIPT_DIR / "validate_skill.py"), str(target)],
        capture_output=True,
        text=True,
        check=False,
    )
    print(
        json.dumps(
            {
                "name": name,
                "created": str(target),
                "files": len(files),
                "mode": args.mode,
                "validation_ok": validation.returncode == 0,
            },
            indent=2,
        )
    )
    if validation.returncode != 0:
        print(validation.stdout, file=sys.stderr)
        raise SystemExit(2)


if __name__ == "__main__":
    main()
