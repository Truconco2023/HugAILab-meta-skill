#!/usr/bin/env python3
"""Validate the lightweight HugAILab skill package contract."""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any

_SCRIPT_DIR = Path(__file__).resolve().parent
if str(_SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(_SCRIPT_DIR))

try:
    import yaml  # type: ignore
except Exception:  # pragma: no cover - fallback keeps the script dependency-light.
    yaml = None


REQUIRED_ROOT_FILES = ["SKILL.md", "README.md", "agents/interface.yaml", "manifest.json"]
REQUIRED_FRONTMATTER = ["name", "description"]
REQUIRED_INTERFACE_FIELDS = ["display_name", "short_description", "default_prompt"]
REQUIRED_MANIFEST_FIELDS = ["name", "version", "owner", "updated_at", "status", "maturity_tier"]
META_SKILL_NAMES = {"hugailab-meta-skill", "HugAILab-meta-skill", "qiaomu-meta-skill"}
IGNORED_DISCOVERY_DIRS = {".git", "dist", "node_modules", "__pycache__"}
FORBIDDEN_DISCOVERY_DEPENDENCIES = (
    '.agents/skills/find-skills/SKILL.md',
    'npx skills add https://github.com/vercel-labs/skills --skill find-skills',
)
EVIDENCE_TIERS = {"production", "library", "governed"}
MAX_PRODUCTION_SKILL_BYTES = 14_000
MAX_SKILL_MD_CHARS = 15_000
MAX_REFERENCES_CHARS = 100_000
PATTERN_SCAN_SUFFIXES = {".md", ".json", ".yaml", ".yml", ".py", ".sh", ".js", ".ts", ".toml"}
PATTERN_IGNORED_PARTS = {".git", "__pycache__", ".DS_Store", "node_modules", "dist", "tests", "evals", "reports"}
SCRIPT_SUFFIXES = {".py", ".sh", ".js", ".ts"}
BLOCK_PATTERN_KINDS = {"download_exec", "dynamic_exec", "persistence", "destructive", "prompt_injection"}
DANGEROUS_PATTERNS = (
    ("download_exec", re.compile(r"curl\s+[^\n|;]*\|\s*(?:ba|z)?sh", re.I)),
    ("download_exec", re.compile(r"wget\s+[^\n|;]*\|\s*(?:ba|z)?sh", re.I)),
    ("download_exec", re.compile(r"base64\s*-d[^\n|;]*\|\s*(?:ba|z)?sh", re.I)),
    ("dynamic_exec", re.compile(r"\b(?:eval|exec)\s*\(", re.I)),
    ("dynamic_exec", re.compile(r"os\.system\s*\(", re.I)),
    ("dynamic_exec", re.compile(r"subprocess\.[A-Za-z]+\s*\([^)]*shell\s*=\s*True", re.I)),
    ("credential_access", re.compile(r"(?:id_rsa|id_ed25519|\.aws/credentials|\.ssh/|\.claude\.json|security\s+find-generic-password)", re.I)),
    ("credential_access", re.compile(r"\b(?:OPENAI_API_KEY|ANTHROPIC_API_KEY|GITHUB_TOKEN|GH_TOKEN|OPENROUTER_API_KEY|DEEPSEEK_API_KEY)\b", re.I)),
    ("network_exfil", re.compile(r"https?://[^\s\"']+", re.I)),
    ("destructive", re.compile(r"\brm\s+-rf\b|shutil\.rmtree|os\.remove\s*\(", re.I)),
    ("persistence", re.compile(
        r"(?:launchctl\s+load|crontab\s+[a-z]|write_text\([^)]*\.plist|/Library/Launch(?:Daemons|Agents)/)",
        re.I,
    )),
    ("prompt_injection", re.compile(
        r"ignore\s+(?:all\s+)?(?:previous\s+)?instructions|"
        r"忽略\s+(?:之前|所有).{0,6}(?:指令|约束)|"
        r"绕过\s*(?:安全|审查)|disable\s+(?:safety|guardrails?)", re.I)),
)


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def load_json(path: Path) -> dict[str, Any]:
    try:
        payload = json.loads(read_text(path))
    except json.JSONDecodeError as exc:
        raise ValueError(f"{path}: invalid JSON: {exc}") from exc
    if not isinstance(payload, dict):
        raise ValueError(f"{path}: expected JSON object")
    return payload


def parse_yaml_text(text: str) -> Any:
    """Parse YAML with PyYAML when available, otherwise use the bundled subset parser."""
    if yaml is not None:
        return yaml.safe_load(text)
    from hugai_yaml import safe_load  # type: ignore

    return safe_load(text)


def load_yaml(path: Path) -> dict[str, Any]:
    payload = parse_yaml_text(read_text(path)) or {}
    return payload if isinstance(payload, dict) else {}


def creator_defaults_warnings(manifest: dict[str, Any], root_name: str) -> list[str]:
    warnings: list[str] = []
    creator_defaults = manifest.get("creator_defaults", {})
    if not isinstance(creator_defaults, dict):
        return warnings
    name = str(manifest.get("name", ""))
    max_parts = creator_defaults.get("max_preferred_hyphen_parts")
    if isinstance(max_parts, int) and name:
        parts = len(name.split("-"))
        if parts > max_parts:
            warnings.append(
                f"skill name has {parts} hyphen parts, exceeding "
                f"creator_defaults.max_preferred_hyphen_parts ({max_parts})"
            )
    prefix = str(creator_defaults.get("skill_name_prefix", "")).strip()
    if prefix and name and root_name not in META_SKILL_NAMES and not name.startswith(prefix):
        warnings.append(
            f"skill name does not start with configured creator_defaults.skill_name_prefix: {prefix}"
        )
    return warnings


def parse_frontmatter(text: str) -> dict[str, Any]:
    if not text.startswith("---\n"):
        return {}
    lines = text.splitlines()
    try:
        end = lines[1:].index("---") + 1
    except ValueError:
        return {}
    frontmatter_text = "\n".join(lines[1:end])
    payload = parse_yaml_text(frontmatter_text) or {}
    return payload if isinstance(payload, dict) else {}


def markdown_links(text: str) -> list[str]:
    return re.findall(r"\]\(([^)]+\.md)\)", text)


def scan_dangerous_patterns(root: Path) -> list[dict[str, Any]]:
    """Heuristic dangerous-pattern scan over runtime files (tests/evals/reports excluded)."""
    findings: list[dict[str, Any]] = []
    for path in root.rglob("*"):
        if not path.is_file() or path.suffix.lower() not in PATTERN_SCAN_SUFFIXES:
            continue
        relative = path.relative_to(root)
        if any(part in PATTERN_IGNORED_PARTS for part in relative.parts):
            continue
        try:
            lines = read_text(path).splitlines()
        except (UnicodeDecodeError, OSError):
            continue
        for line_number, line in enumerate(lines, 1):
            for kind, pattern in DANGEROUS_PATTERNS:
                if not pattern.search(line):
                    continue
                if path.suffix.lower() in SCRIPT_SUFFIXES:
                    severity = "high" if kind in BLOCK_PATTERN_KINDS else "medium"
                else:
                    severity = (
                        "medium"
                        if kind in {"download_exec", "dynamic_exec", "credential_access", "persistence"}
                        else "info"
                    )
                if kind == "credential_access" and (
                    "OPENAI_API_KEY" in line or "ANTHROPIC_API_KEY" in line or "GITHUB_TOKEN" in line
                ):
                    if "environ" not in line and "getenv" not in line:
                        severity = "info"
                findings.append(
                    {
                        "file": str(relative),
                        "line": line_number,
                        "kind": kind,
                        "severity": severity,
                        "detail": line.strip()[:160],
                    }
                )
    return findings


def referenced_script_warnings(root: Path) -> list[str]:
    warnings: list[str] = []
    for doc_name in ("SKILL.md", "README.md"):
        path = root / doc_name
        if not path.is_file():
            continue
        for ref in re.findall(r"scripts/[\w./-]+\.(?:py|sh)", read_text(path)):
            if not (root / ref).is_file():
                warnings.append(f"{doc_name} references missing script: {ref}")
    return warnings


def context_budget_warnings(root: Path) -> list[str]:
    warnings: list[str] = []
    skill_md = root / "SKILL.md"
    if skill_md.is_file():
        chars = len(read_text(skill_md))
        if chars > MAX_SKILL_MD_CHARS:
            warnings.append(f"SKILL.md context budget: {chars} chars > {MAX_SKILL_MD_CHARS}")
    references = root / "references"
    if references.is_dir():
        total = sum(len(read_text(p)) for p in references.glob("*.md"))
        if total > MAX_REFERENCES_CHARS:
            warnings.append(f"references context budget: {total} chars > {MAX_REFERENCES_CHARS}")
    return warnings


def discover_skill_entrypoints(root: Path) -> list[Path]:
    """Return exact SKILL.md entrypoints that an installer may expose recursively."""
    entries: list[Path] = []
    for path in root.rglob("SKILL.md"):
        relative = path.relative_to(root)
        if any(part in IGNORED_DISCOVERY_DIRS for part in relative.parts):
            continue
        entries.append(relative)
    return sorted(entries)


def validate_evidence_reports(
    root: Path,
    manifest: dict[str, Any],
    failures: list[str],
    warnings: list[str],
) -> None:
    tier = str(manifest.get("maturity_tier", "")).lower()
    if tier not in EVIDENCE_TIERS:
        return
    required_reports = (
        "reports/skill-ir.json",
        "reports/trigger-eval.json",
        "reports/prior-art-research.md",
        "reports/creation-handoff.md",
    )
    for relative in required_reports:
        if not (root / relative).is_file():
            failures.append(f"{tier} package missing evidence artifact: {relative}")

    ir_path = root / "reports" / "skill-ir.json"
    if ir_path.is_file():
        try:
            package = load_json(ir_path).get("package", {})
        except ValueError as exc:
            failures.append(str(exc))
            package = {}
        if package.get("name") != manifest.get("name"):
            failures.append("reports/skill-ir.json package.name does not match manifest.json")
        if package.get("version") != manifest.get("version"):
            failures.append("reports/skill-ir.json package.version does not match manifest.json")

    trigger_path = root / "reports" / "trigger-eval.json"
    if trigger_path.is_file():
        try:
            trigger = load_json(trigger_path)
        except ValueError as exc:
            failures.append(str(exc))
            trigger = {}
        if trigger.get("ok") is not True:
            failures.append("reports/trigger-eval.json is not passing")
        summary = trigger.get("summary", {})
        total = summary.get("total") if isinstance(summary, dict) else None
        passed = summary.get("passed") if isinstance(summary, dict) else None
        if not isinstance(total, int) or total <= 0 or passed != total:
            failures.append("reports/trigger-eval.json summary is incomplete or failing")

    handoff_path = root / "reports" / "creation-handoff.md"
    if handoff_path.is_file() and str(manifest.get("version")) not in read_text(handoff_path):
        warnings.append("reports/creation-handoff.md may not mention the current manifest version")


def validate(root: Path) -> dict[str, Any]:
    root = root.resolve()
    failures: list[str] = []
    warnings: list[str] = []
    manifest: dict[str, Any] = {}
    skill_bytes = 0

    for rel in REQUIRED_ROOT_FILES:
        if not (root / rel).exists():
            failures.append(f"missing required file: {rel}")

    if root.name in META_SKILL_NAMES:
        for rel in ("SKILL.md", "README.md", "references/prior-art-research.md"):
            path = root / rel
            if not path.exists():
                continue
            normalized = read_text(path).replace("$HOME/", "").replace("~/", "")
            for forbidden in FORBIDDEN_DISCOVERY_DEPENDENCIES:
                if forbidden in normalized:
                    failures.append(f"{rel} contains external discovery-skill dependency: {forbidden}")
        for relative in ("scripts/research_prior_art.py", "scripts/release_check.py", "scripts/publish_skill.py"):
            if not (root / relative).is_file():
                failures.append(f"{root.name} missing built-in factory script: {relative}")

    skill_entrypoints = discover_skill_entrypoints(root)
    nested_entrypoints = [path for path in skill_entrypoints if path != Path("SKILL.md")]
    if nested_entrypoints:
        joined = ", ".join(str(path) for path in nested_entrypoints)
        failures.append(
            "nested discoverable skill entrypoints found: "
            f"{joined}; rename embedded examples to SKILL.example.md and fixtures to SKILL.fixture.md"
        )

    skill_md = root / "SKILL.md"
    if skill_md.exists():
        skill_text = read_text(skill_md)
        skill_bytes = len(skill_text.encode("utf-8"))
        frontmatter = parse_frontmatter(skill_text)
        for field in REQUIRED_FRONTMATTER:
            if not frontmatter.get(field):
                failures.append(f"SKILL.md missing frontmatter field: {field}")
        description = str(frontmatter.get("description", ""))
        if frontmatter.get("name") == "hugailab-meta-skill":
            for token in ("skill", "hugailab", "workflow"):
                if token not in description.lower():
                    warnings.append(f"description may be missing routing token: {token}")
        for rel in markdown_links(skill_text):
            if rel.startswith(("http://", "https://", "#")):
                continue
            if not (root / rel).exists():
                failures.append(f"SKILL.md links to missing reference: {rel}")

    readme = root / "README.md"
    if readme.exists():
        readme_text = read_text(readme)
        readme_checks = {
            "install command": "npx skills add" in readme_text,
            "natural examples": "你可以直接这样说" in readme_text,
            "verification commands": "validate_skill.py" in readme_text,
            "troubleshooting": "Troubleshooting" in readme_text,
        }
        manifest_path = root / "manifest.json"
        if manifest_path.exists():
            try:
                manifest_for_readme = load_json(manifest_path)
            except ValueError:
                manifest_for_readme = {}
            upstream = str(manifest_for_readme.get("upstream_inspiration", "")).strip()
            if upstream:
                readme_checks["declared upstream credit"] = upstream in readme_text
        for label, ok in readme_checks.items():
            if not ok:
                warnings.append(f"README may be missing {label}")

    interface_path = root / "agents" / "interface.yaml"
    if interface_path.exists():
        interface = load_yaml(interface_path)
        meta = interface.get("interface", {}) if isinstance(interface, dict) else {}
        compatibility = interface.get("compatibility", {}) if isinstance(interface, dict) else {}
        for field in REQUIRED_INTERFACE_FIELDS:
            if not meta.get(field):
                failures.append(f"agents/interface.yaml missing interface.{field}")
        targets = compatibility.get("adapter_targets", [])
        if not isinstance(targets, list) or not targets:
            failures.append("agents/interface.yaml missing compatibility.adapter_targets")
        for expected in ("openai", "claude", "generic", "agent-skills-compatible"):
            if isinstance(targets, list) and expected not in targets:
                warnings.append(f"adapter target not declared: {expected}")

    manifest_path = root / "manifest.json"
    if manifest_path.exists():
        try:
            manifest = load_json(manifest_path)
        except ValueError as exc:
            failures.append(str(exc))
            manifest = {}
        for field in REQUIRED_MANIFEST_FIELDS:
            if not manifest.get(field):
                failures.append(f"manifest.json missing field: {field}")
        if manifest.get("version") and not re.match(r"^\d+\.\d+\.\d+$", str(manifest["version"])):
            failures.append("manifest.json version must be semver-like")
        if "release_gates" not in manifest:
            warnings.append("manifest.json missing release_gates")
        if manifest.get("context_budget_tier") == "production" and skill_bytes > MAX_PRODUCTION_SKILL_BYTES:
            warnings.append(
                f"SKILL.md exceeds production context budget: {skill_bytes} > {MAX_PRODUCTION_SKILL_BYTES} bytes"
            )
        warnings.extend(creator_defaults_warnings(manifest, root.name))

    validate_evidence_reports(root, manifest, failures, warnings)

    pattern_findings = scan_dangerous_patterns(root)
    high = sum(1 for item in pattern_findings if item["severity"] == "high")
    medium = sum(1 for item in pattern_findings if item["severity"] == "medium")
    if pattern_findings:
        warnings.append(
            f"pattern scan: {high} high / {medium} medium review signals; "
            "blocking kinds are download_exec/dynamic_exec/persistence/destructive/prompt_injection"
        )
    warnings.extend(referenced_script_warnings(root))
    warnings.extend(context_budget_warnings(root))

    cases_path = root / "evals" / "trigger_cases.json"
    if cases_path.exists():
        try:
            cases = load_json(cases_path)
        except ValueError as exc:
            failures.append(str(exc))
            cases = {}
        for bucket in ("should_trigger", "should_not_trigger", "near_neighbor"):
            if not cases.get(bucket):
                warnings.append(f"evals/trigger_cases.json has no {bucket} cases")
    else:
        warnings.append("evals/trigger_cases.json missing; recommended for production/library packages")

    scripts_dir = root / "scripts"
    if scripts_dir.exists():
        for script in sorted(scripts_dir.glob("*.py")):
            text = read_text(script)
            if "argparse" not in text and 'SCRIPT_INTERFACE = "internal-module"' not in text:
                warnings.append(f"script has no argparse help or internal-module marker: {script.name}")

    return {
        "ok": not failures,
        "root": str(root),
        "failures": failures,
        "warnings": warnings,
        "pattern_findings": pattern_findings,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Validate a HugAILab skill package.")
    parser.add_argument("skill_dir", nargs="?", default=".", help="Skill directory to validate.")
    args = parser.parse_args()

    result = validate(Path(args.skill_dir))
    print(json.dumps(result, ensure_ascii=False, indent=2))
    if not result["ok"]:
        raise SystemExit(2)


if __name__ == "__main__":
    main()
