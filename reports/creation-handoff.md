# Qiaomu Meta Skill Creation Handoff

## Result

- Skill: `qiaomu-meta-skill` 2.7.0
- Job: research, create, evaluate, package, govern, and publish reusable Qiaomu skills through one self-contained workflow
- Status: 2.7.0 pre-publication evidence snapshot; verify current remote state with the executable `pr` and `published` gates rather than inferring it from this static report

## Reference skills studied

### `yaojingang/yao-meta-skill`

- Why shortlisted: direct meta-skill reference with full-lifecycle engineering, evaluation, governance, and portability concepts.
- Learned: Skill IR, evidence boundaries, release gates, output evaluation, review layers, and post-release iteration.
- Applied in: Qiaomu Skill OS layers, gate ladder, Skill IR export, output-eval method, and SkillOps references.

### `wshobson/agents@evaluation-methodology`

- Why shortlisted: complementary evaluation specialist found during prior-art research.
- Learned: separate evaluation dimensions, compare before/after behavior, preserve confidence and evidence limits.
- Applied in: trigger-first evaluation, output assertions, evidence labels, and the distinction between design and validated advantages.

## Absorbed and rejected

- `keep`: platform-neutral intent, trigger/output evaluation, evidence-bound claims, release and iteration gates.
- `adapt`: compress a large Skill OS into a lighter Chinese-first Qiaomu workflow with proportional modes.
- `reject`: copying upstream dashboards and generated report volume; installing or invoking multiple creator/discovery skills; popularity-only ranking; unsupported superiority claims.
- `invent`: resilient dual-catalog research runner, source-separated GitHub-family merging, executable release readiness, single authoring authority, root-entrypoint isolation, generalization gate, and persuasive evidence-labeled creation handoff.

## Advantages and highlights

- `design advantage`: prior-art discovery, synthesis, creation, validation, and handoff remain inside one canonical workflow, avoiding conflicting creator instructions. Evidence: `SKILL.md` Router Rules and Compact Workflow.
- `design advantage`: skills.sh installs and SkillsMP repository stars remain source-separated and cannot be combined into a fake score. Evidence: `references/prior-art-research.md`.
- `design advantage`: every created Production+ skill must expose design lineage and distinguish design advantages, validated advantages, and hypotheses. Evidence: `references/creation-handoff.md`.
- `design advantage`: catalog discovery now degrades explicitly under transient failures instead of losing the whole research run or hiding missing evidence. Evidence: `scripts/search_skillsmp.py` and `scripts/research_prior_art.py`.
- `design advantage`: local, PR, and published completion states are machine-checkable instead of prose-only. Evidence: `scripts/release_check.py`.
- `validated advantage`: package validation passed without failures or warnings; trigger routing passed 19/19; unit tests passed 21/21; and a strict live query completed against both skills.sh and SkillsMP with 9 candidate families and no missing catalog evidence.
- `hypothesis`: the richer handoff should improve user trust and adoption decisions, but a human comprehension or install-conversion study remains `missing evidence`.

## Verification and limits

- Deterministic package validation: passed with 0 failures and 0 warnings.
- Trigger eval: passed 19/19, with 0 false positives and 0 false negatives.
- Unit tests: passed 21/21.
- Live dual-catalog smoke: passed in strict mode for `skill evaluation`; skills.sh and SkillsMP both completed, producing 9 merged candidate families with source metrics kept separate.
- Local release readiness: passed with 6 pass, 3 warn, and 0 block. Warnings accurately record the dirty worktree, unavailable clean-install proof before a remote revision exists, and missing provider/human output evidence.
- PR, merged default-branch, GitHub release, and public clean-install proof: not part of this pre-publication snapshot; they must be recorded by the executable release gates after the corresponding remote state exists.
- Provider-backed head-to-head output evaluation: `missing evidence`.
- Human blind comparison of handoff persuasiveness: `missing evidence`.
