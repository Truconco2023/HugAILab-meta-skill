#!/usr/bin/env python3
"""Run a weighted trigger-boundary smoke eval for the skill description.

This is a deterministic keyword-overlap smoke gate, not a semantic routing
benchmark.  It is deliberately stricter than a raw ``if phrase in description``
check:

- each concept carries a weight, so incidental words count less than the core
  ``skill`` / ``source_material`` / ``authoring_action`` concepts;
- every should-trigger case can declare the concepts it *requires*, so a case
  cannot pass on two coincidental overlaps;
- negative cases and near neighbors must stay below the threshold (or hit an
  explicit negative pattern);
- family coverage is checked, so silently dropping an entire scenario family
  fails the run.

Limitations stay visible in the report: keyword overlap is not the same as
semantic understanding, and a 100% pass rate here does not prove routing
accuracy against real users.
"""

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
except Exception:  # pragma: no cover
    yaml = None


DEFAULT_CONCEPTS: dict[str, dict[str, Any]] = {
    "skill": {
        "phrases": ["skill", "agent skill", "技能", "agent 能力", "能力包", "skill 包"],
        "weight": 3.0,
        "core": True,
    },
    "source_material": {
        "phrases": [
            "workflow",
            "workflows",
            "prompt",
            "prompts",
            "transcript",
            "transcripts",
            "docs",
            "runbook",
            "runbooks",
            "notes",
            "SOP",
            "流程",
            "工作流",
            "提示词",
            "笔记",
            "对话记录",
            "材料",
            "脚本",
        ],
        "weight": 2.0,
        "core": True,
    },
    "authoring_action": {
        "phrases": [
            "create",
            "turn",
            "convert",
            "refactor",
            "evaluate",
            "package",
            "govern",
            "publish",
            "upgrade",
            "improve",
            "migrate",
            "install",
            "创建",
            "整理",
            "封装",
            "沉淀",
            "优化",
            "升级",
            "迁移",
            "安装",
            "打包",
            "发布",
        ],
        "weight": 2.0,
        "core": True,
    },
    "brand": {
        "phrases": ["hugailab", "hugai", "qiaomu", "乔木", "向阳乔木"],
        "weight": 0.5,
        "core": False,
    },
    "eval_release": {
        "phrases": [
            "eval",
            "trigger eval",
            "output eval",
            "skill ir",
            "release gate",
            "PR",
            "Release",
            "评估",
            "触发评测",
            "输出评测",
            "门禁",
            "治理",
            "发布检查",
            "发布门禁",
        ],
        "weight": 1.0,
        "core": False,
    },
    "prior_art": {
        "phrases": [
            "skills catalog",
            "skill search",
            "skills.sh",
            "popular skill",
            "related skills",
            "existing agent skills",
            "strongest",
            "research",
            "synthesize",
            "without copying",
            "下载量",
            "安装量",
            "好评",
            "口碑",
            "相关 skill",
            "借鉴",
            "取长补短",
        ],
        "weight": 1.5,
        "core": False,
    },
}

DEFAULT_REQUIRED_DESCRIPTION = ["skill", "source_material", "authoring_action"]
POSITIVE_BUCKETS = ("should_trigger", "should_not_trigger", "near_neighbor")


def parse_yaml_text(text: str) -> Any:
    if yaml is not None:
        return yaml.safe_load(text)
    from hugai_yaml import safe_load

    return safe_load(text)


def normalize(text: str) -> str:
    text = text.lower()
    text = re.sub(r"[^\w\u4e00-\u9fff]+", " ", text, flags=re.UNICODE)
    return re.sub(r"\s+", " ", text).strip()


def phrase_present(text: str, phrase: str) -> bool:
    phrase = normalize(phrase)
    if not phrase:
        return False
    if re.search(r"[\u4e00-\u9fff]", phrase):
        return phrase in text
    return f" {phrase} " in f" {text} "


def load_json(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    return payload if isinstance(payload, dict) else {}


def parse_description(skill_md: Path) -> str:
    text = skill_md.read_text(encoding="utf-8")
    if not text.startswith("---\n"):
        return text
    lines = text.splitlines()
    try:
        end = lines[1:].index("---") + 1
    except ValueError:
        return text
    frontmatter_text = "\n".join(lines[1:end])
    payload = parse_yaml_text(frontmatter_text) or {}
    if isinstance(payload, dict):
        return str(payload.get("description", ""))
    return text


def normalize_concepts(concepts: dict[str, Any]) -> dict[str, dict[str, Any]]:
    normalized: dict[str, dict[str, Any]] = {}
    for name, spec in concepts.items():
        if isinstance(spec, dict):
            phrases = list(spec.get("phrases") or [])
            weight = max(0.1, float(spec.get("weight", 1.0)))
            core = bool(spec.get("core", False))
        elif isinstance(spec, list):
            phrases = [str(item) for item in spec]
            weight = 1.0
            core = name in {"skill", "source_material", "authoring_action"}
        else:
            continue
        if phrases:
            normalized[str(name)] = {"phrases": phrases, "weight": weight, "core": core}
    return normalized


def concept_hits(text: str, concepts: dict[str, dict[str, Any]]) -> dict[str, list[str]]:
    normalized = normalize(text)
    hits: dict[str, list[str]] = {}
    for name, spec in concepts.items():
        matched = [phrase for phrase in spec["phrases"] if phrase_present(normalized, phrase)]
        if matched:
            hits[name] = matched
    return hits


def weighted_score(concepts: dict[str, dict[str, Any]], hits: dict[str, list[str]]) -> float:
    total = sum(spec["weight"] for spec in concepts.values())
    if total <= 0:
        return 0.0
    matched = sum(concepts[name]["weight"] for name in hits)
    return round(matched / total, 3)


def negative_hit(text: str, patterns: list[str]) -> str | None:
    normalized = normalize(text)
    for pattern in patterns:
        if phrase_present(normalized, pattern):
            return pattern
    return None


def case_items(cases: dict[str, Any], bucket: str) -> list[dict[str, Any]]:
    output: list[dict[str, Any]] = []
    for raw in cases.get(bucket, []):
        if isinstance(raw, str):
            output.append({"text": raw, "family": "default"})
        elif isinstance(raw, dict):
            item = dict(raw)
            item.setdefault("family", "default")
            output.append(item)
    return output


def evaluate(root: Path, cases_path: Path, lenient: bool = False) -> dict[str, Any]:
    cases = load_json(cases_path)
    concepts = normalize_concepts(cases.get("positive_concepts") or DEFAULT_CONCEPTS)
    threshold = float(cases.get("recommended_threshold", 0.34))
    global_negative = list(cases.get("negative_patterns", []))
    description = parse_description(root / "SKILL.md")
    description_hits = concept_hits(description, concepts)
    required_description = set(
        cases.get("description_required_concepts") or DEFAULT_REQUIRED_DESCRIPTION
    )
    missing_description = sorted(required_description - set(description_hits))

    buckets: dict[str, list[dict[str, Any]]] = {bucket: [] for bucket in POSITIVE_BUCKETS}
    failures: list[dict[str, Any]] = []
    totals = {"total": 0, "passed": 0, "false_positive": 0, "false_negative": 0, "weak": 0}

    for bucket in POSITIVE_BUCKETS:
        expected = bucket == "should_trigger"
        for item in case_items(cases, bucket):
            prompt = str(item.get("text", ""))
            hits = concept_hits(prompt, concepts)
            matched = sorted(hits)
            negatives = global_negative + list(item.get("negative_patterns", []))
            neg = negative_hit(prompt, negatives)
            score = weighted_score(concepts, hits)
            required = [str(name) for name in item.get("required", [])] if not lenient else []
            required_missing = sorted(set(required) - set(matched)) if required else []

            if expected:
                effective_threshold = max(threshold, float(item.get("min_score", 0.0)))
                predicted = neg is None and score >= effective_threshold and not required_missing
                passed = predicted == expected
                if passed and score < 0.5:
                    totals["weak"] += 1
            else:
                effective_threshold = min(threshold, float(item.get("max_score", threshold)))
                predicted = neg is None and score >= effective_threshold
                passed = predicted == expected
                if passed and score >= threshold * 0.8 and neg is None:
                    totals["weak"] += 1

            record = {
                "prompt": prompt,
                "family": item.get("family", "default"),
                "expected_trigger": expected,
                "predicted_trigger": predicted,
                "passed": passed,
                "score": score,
                "threshold": round(effective_threshold, 3),
                "margin": round(score - effective_threshold, 3),
                "matched_concepts": matched,
                "matched_phrases": hits,
                "required_concepts": required,
                "required_missing": required_missing,
                "negative_pattern": neg,
            }
            buckets[bucket].append(record)
            totals["total"] += 1
            if passed:
                totals["passed"] += 1
            else:
                kind = "false_negative" if expected else "false_positive"
                totals[kind] += 1
                failures.append({"bucket": bucket, "kind": kind, **record})

    family_failures: list[dict[str, Any]] = []
    families = {record["family"] for record in buckets["should_trigger"]}
    passed_families = {record["family"] for record in buckets["should_trigger"] if record["passed"]}
    for family in sorted(families - passed_families):
        family_failures.append({"bucket": "family_coverage", "kind": "uncovered_family", "family": family})
        failures.append(family_failures[-1])

    ok = not missing_description and not failures
    return {
        "ok": ok,
        "mode": "strict" if not lenient else "lenient",
        "threshold": threshold,
        "description_concepts": sorted(description_hits),
        "missing_description_concepts": missing_description,
        "summary": {
            **totals,
            "pass_rate": round(totals["passed"] / totals["total"], 3) if totals["total"] else 0,
            "families_covered": len(passed_families),
            "families_total": len(families),
            "uncovered_families": [item["family"] for item in family_failures],
        },
        "failures": failures,
        "results": buckets,
    }


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Evaluate a skill trigger description against weighted smoke cases."
    )
    parser.add_argument("skill_dir", nargs="?", default=".", help="Skill directory.")
    parser.add_argument("--cases", default="evals/trigger_cases.json", help="Trigger case JSON path.")
    parser.add_argument("--output", "-o", help="Write JSON report to this path.")
    parser.add_argument(
        "--lenient",
        action="store_true",
        help="Score-only mode: do not enforce per-case required concepts.",
    )
    args = parser.parse_args()

    root = Path(args.skill_dir).resolve()
    cases_path = Path(args.cases)
    if not cases_path.is_absolute():
        cases_path = root / cases_path
    result = evaluate(root, cases_path, lenient=args.lenient)
    rendered = json.dumps(result, ensure_ascii=False, indent=2)
    if args.output:
        output = Path(args.output)
        if not output.is_absolute():
            output = root / output
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(rendered + "\n", encoding="utf-8")
    print(rendered)
    if not result["ok"]:
        raise SystemExit(2)


if __name__ == "__main__":
    main()
