#!/usr/bin/env python3
"""Evidence-bound maturity scoring for a HugAILab skill package.

Reads only existing artifacts (never fabricates evidence) and produces a
0-10 maturity score across six weighted dimensions. Missing evidence lowers
the score and is always reported explicitly.

Usage:
  python3 scripts/score_skill.py <skill_dir> [--output reports/scorecard.json] \
      [--report reports/scorecard.md]
"""

from __future__ import annotations

import argparse
import datetime as dt
import json
import sys
from pathlib import Path
from typing import Any

SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))
from validate_skill import validate  # noqa: E402

DIMENSIONS = (
    {"key": "trigger", "label": "触发边界评测", "weight": 0.15},
    {"key": "output", "label": "输出内容质量", "weight": 0.25},
    {"key": "prior_art_ir", "label": "prior-art 与 Skill IR", "weight": 0.15},
    {"key": "reuse_install", "label": "复用/安装验证", "weight": 0.20},
    {"key": "docs_security", "label": "文档/接口/安全", "weight": 0.15},
    {"key": "governance", "label": "发布治理证据", "weight": 0.10},
)


def load_json(path: Path) -> dict[str, Any] | None:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return None
    return payload if isinstance(payload, dict) else None


def score_trigger(root: Path) -> dict[str, Any]:
    report = load_json(root / "reports" / "trigger-eval.json")
    if report is None:
        return {"score": 0.0, "evidence": "missing", "missing_evidence": ["reports/trigger-eval.json 缺失"]}
    summary = report.get("summary") or {}
    total = int(summary.get("total") or 0)
    passed = int(summary.get("passed") or 0)
    weak = int(summary.get("weak") or 0)
    if total <= 0:
        return {"score": 0.0, "evidence": "incomplete", "missing_evidence": ["trigger 评测 summary 不完整"]}
    score = round(10.0 * passed / total, 1)
    if weak:
        score = max(0.0, score - 1.0)
    if report.get("ok") is not True:
        score = min(score, 4.0)
    return {"score": score, "evidence": f"{passed}/{total}, weak={weak}"}


def score_output(root: Path, evidence_path: Path | None) -> dict[str, Any]:
    candidates = [evidence_path] if evidence_path else []
    candidates.append(root / "reports" / "output-evidence.json")
    candidates.append(root / "reports" / "output-eval.json")
    report = None
    for path in candidates:
        if path is None:
            continue
        loaded = load_json(path)
        if loaded is not None:
            report = loaded
            break
    if report is None:
        return {"score": 0.0, "evidence": "missing", "missing_evidence": ["输出评测报告缺失"]}
    kind = str(report.get("evidence_kind") or "recorded_fixture")
    summary = report.get("summary") or {}
    total = int(summary.get("assertions_total") or summary.get("cases_total") or 0)
    executed = int(summary.get("assertions_executed") or summary.get("cases_total") or total)
    passed = int(summary.get("assertions_passed") or summary.get("cases_passed") or 0)
    if total <= 0 or executed <= 0:
        return {"score": 0.0, "evidence": "incomplete", "missing_evidence": ["输出评测 summary 不完整"]}
    rate = summary.get("with_skill_assertion_pass_rate")
    if isinstance(rate, (int, float)) and 0 <= rate <= 1:
        score = round(10.0 * rate, 1)
        evidence_rate = f"rate={rate}"
    else:
        score = round(10.0 * passed / executed, 1)
        evidence_rate = f"{passed}/{executed}"
    missing: list[str] = []
    if kind not in {"provider_backed", "human_blind_review"}:
        score = min(score, 6.5)
        missing.append(f"输出评测仅为 {kind}，未跑 provider/human 证据；该项封顶 6.5")
    if report.get("ok") is not True:
        score = min(score, 4.0)
    return {"score": score, "evidence": f"{kind}, {evidence_rate}", "missing_evidence": missing}


def score_prior_art_ir(root: Path, manifest: dict[str, Any]) -> dict[str, Any]:
    score = 0.0
    missing: list[str] = []
    ir = load_json(root / "reports" / "skill-ir.json")
    if ir is None:
        missing.append("reports/skill-ir.json 缺失")
    else:
        package = ir.get("package") or {}
        if package.get("name") == manifest.get("name") and package.get("version") == manifest.get("version"):
            score += 5.0
        else:
            missing.append("reports/skill-ir.json 与 manifest 不一致")
    prior_path = root / "reports" / "prior-art-research.md"
    if prior_path.is_file():
        text = prior_path.read_text(encoding="utf-8")
        if any(token in text for token in ("Researched at: N/A", "not yet run", "catalog research not yet run")):
            missing.append("prior-art 报告为占位符，未做真实调研")
        else:
            score += 5.0
    else:
        missing.append("reports/prior-art-research.md 缺失")
    return {"score": round(score, 1), "evidence": f"IR+prior-art: {score:.0f}/10", "missing_evidence": missing}


def score_reuse_install(root: Path) -> dict[str, Any]:
    score = 0.0
    missing: list[str] = []
    tests = list((root / "tests").glob("test_*.py")) if (root / "tests").is_dir() else []
    if tests:
        score += 6.0
    else:
        missing.append("tests/ 目录缺失或没有 test_*.py")
    if (root / "examples").is_dir() or (root / "fixtures").is_dir():
        score += 2.0
    else:
        missing.append("examples/ 或 fixtures/ 缺失")
    readme = root / "README.md"
    if readme.is_file() and any(token in readme.read_text(encoding="utf-8") for token in ("validate_skill.py", "check_note.py", "unittest")):
        score += 2.0
    else:
        missing.append("README 未提供验证命令")
    return {"score": round(score, 1), "evidence": f"tests={len(tests)}, examples/fixtures, README", "missing_evidence": missing}


def score_docs_security(root: Path) -> dict[str, Any]:
    result = validate(root)
    if not result["ok"]:
        return {"score": 0.0, "evidence": f"validate failures={len(result['failures'])}", "missing_evidence": result["failures"]}
    warnings = result.get("warnings") or []
    structural = [w for w in warnings if not w.startswith("pattern scan:")]
    score = max(0.0, 10.0 - len(structural))
    return {
        "score": round(score, 1),
        "evidence": f"validate structural warnings={len(structural)}",
        "missing_evidence": structural[:5],
    }


def score_governance(root: Path, manifest: dict[str, Any]) -> dict[str, Any]:
    score = 0.0
    missing: list[str] = []
    gates = manifest.get("release_gates")
    if isinstance(gates, list) and gates:
        score += 3.0
    else:
        missing.append("manifest release_gates 为空（无字段时用评测/调研证据替代部分治理分）")
    if (root / "reports" / "trigger-eval.json").is_file():
        score += 2.0
    evidence = load_json(root / "reports" / "output-evidence.json")
    if evidence is not None and str(evidence.get("evidence_kind")) in {"provider_backed", "human_blind_review"}:
        score += 2.0
    elif (root / "reports" / "output-eval.json").is_file():
        score += 1.0
    handoff = root / "reports" / "creation-handoff.md"
    if handoff.is_file() and str(manifest.get("version")) in handoff.read_text(encoding="utf-8"):
        score += 1.0
    else:
        missing.append("creation-handoff 未提及当前版本")
    prior_path = root / "reports" / "prior-art-research.md"
    if prior_path.is_file() and not any(
        token in prior_path.read_text(encoding="utf-8") for token in ("Researched at: N/A", "not yet run")
    ):
        score += 2.0
    else:
        missing.append("prior-art 调研证据缺失或为占位")
    return {
        "score": round(score, 1),
        "evidence": f"gates={len(gates) if isinstance(gates, list) else 0}, evidence-backed",
        "missing_evidence": missing,
    }


def render_scorecard(payload: dict[str, Any]) -> str:
    lines = [
        f"# Skill 评分卡：{payload['skill_name']} v{payload['version']}",
        "",
        f"- 综合评分：**{payload['score']} / 10**",
        f"- 评分时间：{payload['generated_at']}",
        "- 说明：分数反映证据成熟度，不反映业务价值；缺失证据会降分并明确列出。",
        "",
        "| 维度 | 权重 | 得分 | 加权 | 证据 |",
        "|---|---:|---:|---:|---|",
    ]
    if payload.get("snapshot") == "initial":
        lines.insert(
            4,
            "- ⚠ **初始快照**：脚手架生成时的基线分数，不代表最终状态；"
            "完成 prior-art/测试/provider 评测后请重新运行 score_skill.py 刷新。",
        )
        lines.insert(5, "")
    for item in payload["dimensions"]:
        lines.append(
            f"| {item['label']} | {int(item['weight'] * 100)}% | {item['score']} | "
            f"{round(item['weight'] * item['score'], 2)} | {item['evidence']} |"
        )
    if payload["missing_evidence"]:
        lines += ["", "## Missing evidence", ""]
        lines += [f"- {item}" for item in payload["missing_evidence"]]
    return "\n".join(lines) + "\n"


def score(root: Path, evidence_path: Path | None, label: str = "final") -> dict[str, Any]:
    manifest = load_json(root / "manifest.json") or {}
    manifest_loaded = bool(manifest)
    dimension_results: list[dict[str, Any]] = []
    all_missing: list[str] = []
    for dim in DIMENSIONS:
        key = dim["key"]
        if key == "trigger":
            result = score_trigger(root)
        elif key == "output":
            result = score_output(root, evidence_path)
        elif key == "prior_art_ir":
            result = score_prior_art_ir(root, manifest)
        elif key == "reuse_install":
            result = score_reuse_install(root)
        elif key == "docs_security":
            result = score_docs_security(root)
        else:
            result = score_governance(root, manifest)
        dimension_results.append({**dim, **result})
        all_missing.extend(result.get("missing_evidence") or [])
    if not manifest_loaded:
        all_missing.append("manifest.json 缺失或不可解析")
    total = round(sum(item["weight"] * item["score"] for item in dimension_results), 1)
    return {
        "skill_dir": str(root.resolve()),
        "skill_name": str(manifest.get("name") or root.resolve().name),
        "version": str(manifest.get("version") or "unknown"),
        "snapshot": label,
        "score": total,
        "dimensions": dimension_results,
        "missing_evidence": sorted(set(all_missing)),
        "generated_at": dt.datetime.now().astimezone().isoformat(timespec="seconds"),
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Evidence-bound maturity scoring for a skill package.")
    parser.add_argument("skill_dir", help="Skill directory to score.")
    parser.add_argument("--output", default="", help="JSON output path.")
    parser.add_argument("--report", default="", help="Markdown scorecard output path.")
    parser.add_argument("--evidence", default="", help="Optional provider evidence JSON path (e.g. reports/output-evidence.json).")
    parser.add_argument("--label", choices=("initial", "final"), default="final", help="Snapshot label for the scorecard.")
    args = parser.parse_args()

    root = Path(args.skill_dir).expanduser().resolve()
    if not root.is_dir():
        raise SystemExit(f"skill directory not found: {root}")
    evidence = Path(args.evidence).expanduser().resolve() if args.evidence else None
    payload = score(root, evidence, label=args.label)
    rendered = json.dumps(payload, ensure_ascii=False, indent=2)
    if args.output:
        output_path = Path(args.output).expanduser()
        if not output_path.is_absolute():
            output_path = root / output_path
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(rendered + "\n", encoding="utf-8")
    print(rendered)
    if args.report:
        report_path = Path(args.report).expanduser()
        if not report_path.is_absolute():
            report_path = root / report_path
        report_path.parent.mkdir(parents=True, exist_ok=True)
        report_path.write_text(render_scorecard(payload), encoding="utf-8")
        print(f"scorecard written: {report_path}")


if __name__ == "__main__":
    main()
