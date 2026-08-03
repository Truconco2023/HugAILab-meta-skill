# Iteration — 2026-08-03 — 2.7.0

## Observed failures and gaps

1. SkillsMP returned truncated chunked responses during several unrelated SEO research queries. `json.load(response)` raised `http.client.IncompleteRead`, which the client did not catch.
2. skills.sh and SkillsMP were queried by separate commands; cross-catalog normalization, failure recording, and family merging were largely manual.
3. Release requirements existed in prose, but no command could distinguish local readiness, PR readiness, and verified publication.
4. `qiaomu-meta-skill` required generated `SKILL.md` files to stay lean while its own entrypoint had grown beyond 16 KB.
5. Package validation did not block a stale Skill IR or failing trigger report after a Manifest version bump.

## Domain-neutral causes

- External metadata services are transient and must have bounded retry plus explicit degradation.
- Repeated multi-source research needs one reproducible orchestration contract.
- A written release checklist is not release evidence.
- Resource-boundary rules need deterministic enforcement against the factory itself.
- Generated reports are evidence only when their identity/version/status matches the package.

## Durable corrections

- Retry incomplete reads, connection failures, timeouts, HTTP 408/425/429, and 5xx responses with capped exponential backoff; do not retry ordinary 4xx errors.
- Add `research_prior_art.py` to run both catalogs, preserve query-level failures, merge matching candidate families, and keep installs/stars separate.
- Add `release_check.py` with `local`, `pr`, and `published` phases, secret scan, version/report checks, Git/PR/Release state, and isolated-HOME install proof.
- Add evidence-report consistency and production context-budget checks to `validate_skill.py`.
- Reduce root `SKILL.md` from roughly 16 KB/207 lines to roughly 10 KB/153 lines while preserving the full methods in references.

## Evidence added

- Retry and non-retryable HTTP tests.
- ANSI skills.sh parsing, cross-catalog merge, partial-degradation, and strict-mode tests.
- Secret-scan and stale Skill IR tests.
- Final trigger, unit, live catalog, package, and release-readiness results are recorded in the creation handoff after execution.

## Boundaries

- The dual-catalog runner produces a review queue, not an automatic “best skill” verdict.
- Cross-catalog family keys still require canonical GitHub source inspection because repository renames and forks can defeat catalog identifiers.
- Publication, PR, Release, and public clean-install evidence remain absent until the user explicitly requests publishing.
