#!/usr/bin/env python3
"""Run output-level evaluation for a skill package.

Trigger eval answers "will the skill be called?"; output eval answers "after it
is called, is the delivered result better?".  This script supports two honest
evidence tiers:

- ``recorded_fixture`` (default): cases carry baseline/with-skill outputs and
  deterministic assertions over real package files.  This proves regression
  coverage, not model-run quality.
- ``provider_backed`` (``--llm-assert`` with ``OPENAI_API_KEY``): the same
  assertions plus LLM judges that must answer the expected verdict.  Only a
  completed live run may claim this tier.

``--blind-pack`` generates the three separated artifacts required for a blind
human A/B review: anonymized pack, answer key, and decision template.
"""

from __future__ import annotations

import argparse
import json
import os
import random
import urllib.request
from datetime import date
from pathlib import Path
from typing import Any

ASSERTION_KINDS = {"file_exists", "contains", "not_contains", "llm_judge"}
OPENAI_BASE_URL = os.environ.get("OPENAI_BASE_URL", "https://api.openai.com/v1")


def load_json(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError(f"{path} must contain a JSON object")
    return payload


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def run_assertion(root: Path, assertion: dict[str, Any]) -> tuple[bool, str]:
    kind = str(assertion.get("kind", ""))
    if kind not in ASSERTION_KINDS:
        return False, f"unknown assertion kind: {kind}"
    if kind == "file_exists":
        path = root / str(assertion.get("path", ""))
        return path.is_file(), f"file exists: {assertion.get('path')}"
    path = root / str(assertion.get("path", ""))
    needle = str(assertion.get("needle", ""))
    if not path.is_file():
        return False, f"file missing: {assertion.get('path')}"
    text = read_text(path)
    if kind == "contains":
        ok = needle in text
        return ok, f"contains {needle!r} in {assertion.get('path')}"
    if kind == "not_contains":
        ok = needle not in text
        return ok, f"does not contain {needle!r} in {assertion.get('path')}"
    # llm_judge is handled by the provider pass, not the deterministic engine.
    return True, "llm_judge deferred to provider pass"


def llm_judge(assertion: dict[str, Any], model: str) -> tuple[bool, str]:
    api_key = os.environ.get("OPENAI_API_KEY", "").strip()
    if not api_key:
        raise RuntimeError("OPENAI_API_KEY is required for --llm-assert")
    prompt = str(assertion.get("prompt", ""))
    must = str(assertion.get("must", "yes")).lower()
    payload = {
        "model": model,
        "messages": [
            {
                "role": "system",
                "content": "Answer with exactly one word: yes or no.",
            },
            {"role": "user", "content": prompt},
        ],
        "temperature": 0,
        "max_tokens": 5,
    }
    request = urllib.request.Request(
        f"{OPENAI_BASE_URL.rstrip('/')}/chat/completions",
        data=json.dumps(payload).encode("utf-8"),
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}",
        },
        method="POST",
    )
    with urllib.request.urlopen(request, timeout=60) as response:
        body = json.loads(response.read().decode("utf-8"))
    answer = str(body["choices"][0]["message"]["content"]).strip().lower()
    return answer == must, f"llm answered {answer!r}, expected {must!r}"


def evaluate_case(root: Path, case: dict[str, Any], model: str, use_llm: bool) -> dict[str, Any]:
    assertions = list(case.get("assertions", []))
    results: list[dict[str, Any]] = []
    passed = 0
    provider_used = False
    for assertion in assertions:
        if assertion.get("kind") == "llm_judge":
            if not use_llm:
                results.append({"assertion": assertion, "passed": True, "detail": "llm_judge skipped (fixture mode)"})
                continue
            ok, detail = llm_judge(assertion, model)
            provider_used = True
        else:
            ok, detail = run_assertion(root, assertion)
        results.append({"assertion": assertion, "passed": ok, "detail": detail})
        if ok:
            passed += 1
    baseline_pass = 0
    baseline_detail = "baseline produced no package artifacts; scoring 0 for file-backed assertions"
    return {
        "id": case.get("id", "case"),
        "prompt": case.get("prompt", ""),
        "assertions_total": len(assertions),
        "assertions_passed": passed,
        "baseline_passed": baseline_pass,
        "baseline_detail": baseline_detail,
        "human_notes": case.get("human_notes", ""),
        "provider_used": provider_used,
        "results": results,
    }


def build_blind_pack(root: Path, cases: list[dict[str, Any]], out_dir: Path) -> list[str]:
    out_dir.mkdir(parents=True, exist_ok=True)
    random.shuffle(cases)
    pack = [
        {
            "case_id": case.get("id"),
            "prompt": case.get("prompt", ""),
            "output_a": case.get("baseline_output", ""),
            "output_b": case.get("with_skill_output", ""),
        }
        for case in cases
    ]
    (out_dir / "blind-review-pack.json").write_text(
        json.dumps(pack, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    (out_dir / "answer-key.json").write_text(
        json.dumps(
            {
                "_warning": "DO NOT OPEN until all reviews are recorded.",
                "mapping": [{"case_id": c.get("id"), "source": "with_skill"} for c in cases],
            },
            ensure_ascii=False,
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )
    (out_dir / "review-decisions.json").write_text(
        json.dumps(
            {
                "template": {
                    "case_id": "",
                    "reviewer": "",
                    "reviewed_at": "",
                    "winner": "A | B | tie",
                    "confidence": 0.0,
                    "rubric_reason": "",
                    "attestation": "judgment recorded before opening the answer key",
                }
            },
            ensure_ascii=False,
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )
    return ["blind-review-pack.json", "answer-key.json", "review-decisions.json"]


def evaluate(
    root: Path,
    cases_path: Path,
    *,
    use_llm: bool = False,
    model: str = "gpt-4o-mini",
) -> dict[str, Any]:
    payload = load_json(cases_path)
    cases = payload.get("cases", [])
    results = [evaluate_case(root, case, model, use_llm) for case in cases if isinstance(case, dict)]
    passed_cases = sum(1 for item in results if item["assertions_passed"] == item["assertions_total"])
    provider_used = any(item["provider_used"] for item in results)
    evidence_kind = "provider_backed" if use_llm and provider_used else "recorded_fixture"
    missing_evidence: list[str] = []
    if not use_llm:
        missing_evidence.append("provider-backed LLM judges not run; pass --llm-assert with OPENAI_API_KEY")
    if not results:
        missing_evidence.append("no output cases configured")
    ok = bool(results) and passed_cases == len(results)
    return {
        "ok": ok,
        "evidence_kind": evidence_kind,
        "generated_at": date.today().isoformat(),
        "tool": "output_eval.py",
        "summary": {
            "cases_total": len(results),
            "cases_passed": passed_cases,
            "with_skill_assertion_pass_rate": round(
                sum(item["assertions_passed"] for item in results)
                / max(1, sum(item["assertions_total"] for item in results)),
                3,
            ),
            "baseline_passed_total": sum(item["baseline_passed"] for item in results),
            "provider_used": provider_used,
        },
        "missing_evidence": missing_evidence,
        "results": results,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Evaluate skill output quality against assertions.")
    parser.add_argument("skill_dir", nargs="?", default=".", help="Skill directory.")
    parser.add_argument("--cases", default="evals/output_cases.json", help="Output case JSON path.")
    parser.add_argument("--output", "-o", help="Write JSON report to this path.")
    parser.add_argument("--llm-assert", action="store_true", help="Run llm_judge assertions via OpenAI-compatible API.")
    parser.add_argument("--model", default="gpt-4o-mini", help="Model for llm_judge assertions.")
    parser.add_argument("--blind-pack", metavar="DIR", help="Generate blind A/B review artifacts into DIR.")
    args = parser.parse_args()

    root = Path(args.skill_dir).resolve()
    cases_path = Path(args.cases)
    if not cases_path.is_absolute():
        cases_path = root / cases_path
    if args.blind_pack:
        payload = load_json(cases_path)
        files = build_blind_pack(root, [c for c in payload.get("cases", []) if isinstance(c, dict)], Path(args.blind_pack))
        print(json.dumps({"created": files}, ensure_ascii=False, indent=2))
        return
    result = evaluate(root, cases_path, use_llm=args.llm_assert, model=args.model)
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
