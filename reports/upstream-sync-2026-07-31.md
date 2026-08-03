# Upstream Sync — 2026-07-31

## Snapshot

- Upstream: `https://github.com/yaojingang/yao-meta-skill`
- Reviewed commit: `e15472e1f5dc96f79ea0259bf9fdf67598cea356`
- Upstream commit date: 2026-07-16
- Local target before sync: `qiaomu-meta-skill` 2.2.0
- Local target after sync: `qiaomu-meta-skill` 2.3.0

## Commits inspected

- `d6cf4f8`: avoid activating nested example and fixture skills after Git-based installation.
- `6725a57`: distinguish create/refactor/package actions from audit/evaluate-only and no-skill outcomes.
- `24bea60`: broaden routing coverage for migration, release, packaging, install checks, optimization, and trigger evaluation.
- `01e750d`: add real human blind-review evidence and preserve its limitations.

## Synthesis ledger

### Keep

- One canonical discoverable root `SKILL.md`.
- Action-sensitive output contracts.
- Trigger cases that cover migration, install checks, and audit-only language.
- Separate blind pack, answer key, reviewer decision, and evidence limitations.

### Adapt

- Use `SKILL.example.md` and `SKILL.fixture.md` as a lightweight Qiaomu convention, enforced by the existing validator instead of copying the upstream packaging toolchain.
- Keep blind-review integrity as a method and release gate; do not import upstream's large generated HTML evidence bundle.
- Extend the existing Qiaomu description and trigger suite without replacing its prior-art and generalization gates.
- Export every maintained trigger case into Skill IR instead of silently truncating the positive suite when coverage grows.
- Preserve upstream-sync provenance and the complete output contract in exported Skill IR.

### Reject

- Wholesale mirroring of upstream reports, registry, schemas, dashboards, telemetry hosts, or generated evidence.
- Treating a single-reviewer upstream blind test as portable proof for Qiaomu Meta Skill.
- Copying upstream self-scored benchmark claims.

### Invent

- Record the exact reviewed upstream commit and semantic-adoption policy in `manifest.json` so future updates can distinguish drift from already-reviewed work.
- Combine root-entrypoint isolation with the existing Qiaomu gate ladder and deterministic validator.
- Add local regression tests proving that exact nested `SKILL.md` files are discoverable hazards while `.example` and `.fixture` entrypoints stay inert.
- Make authorization semantics explicit in the same output contract that controls package artifacts.

## Evidence boundary

This report proves source inspection and local semantic adoption. It does not prove that the upstream repository is universally superior, that its blind-review result transfers to this skill, or that Qiaomu Meta Skill 2.3.0 has provider-backed output-eval evidence. Those remain `missing evidence` until separately run and reviewed.

## Forward behavior checks

Two independent, no-write simulations were run against the revised skill instructions:

1. **Migration and install-risk case**: correctly kept the root `SKILL.md`, proposed renaming nested example and fixture entrypoints, required reference updates plus source/archive/install scans, and refused to claim install success without execution evidence.
2. **Audit-only evidence case**: wrote no files, separated trigger coverage from file existence, treated recorded output fixtures as non-provider evidence, and marked a blind-review decision without rubric-based reason as pending / `missing evidence`.

Observed regressions: none in these two new behavior paths. Scope limit: these are instruction-following simulations, not provider-backed comparative output benchmarks.
