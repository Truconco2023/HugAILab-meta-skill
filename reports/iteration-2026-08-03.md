# Iteration — 2026-08-03

## Failure

Creating a Qiaomu skill invoked both `qiaomu-meta-skill` and a generic `skill-creator`. This produced two competing authoring workflows and unnecessary instruction loading.

## Domain-neutral cause

The router had no canonical-authority rule for overlapping meta skills. It distinguished domain prior-art discovery from authoring only implicitly, so a general creator could be selected alongside the Qiaomu creator.

## Durable correction

- Make `qiaomu-meta-skill` the single authoring authority once triggered.
- Keep domain prior-art discovery inside `qiaomu-meta-skill`; do not install a separate discovery skill.
- Forbid automatic chaining to generic `skill-creator` or other meta skills.
- Permit a second creator only when the user explicitly requests comparison or the canonical creator is unavailable/blocked.

## Regression expectation

For “生成一个 SEO skill”, the selected workflow should be `qiaomu-meta-skill` using its own catalog-discovery method; neither a separate creator nor a separate discovery skill should appear in the execution chain.

## Built-in discovery correction

The earlier correction still left prior-art discovery as an external skill dependency. Version 2.4.0 internalizes the full search, evidence, shortlist, source-inspection, and synthesis method. It calls `npx --yes skills find` as a catalog query only and never installs a discovery skill.

## SkillsMP expansion

Version 2.5.0 adds SkillsMP as a second built-in discovery source. skills.sh remains the adoption/install signal; SkillsMP expands GitHub, language, creator, category, and occupation coverage. Candidates are deduplicated by GitHub source family, and cross-catalog metrics remain separate. SkillsMP repository stars must never be presented as skill ratings or added to skills.sh installs.

## Persuasive creation handoff

Version 2.6.0 promotes research lineage from a hidden report into the user-facing output contract. Every materially researched creation now names the reference skills, explains the mechanism learned from each, records deliberate rejections, and presents Qiaomu's original highlights. Advantage claims are labeled as design-visible, validated, or hypothetical so persuasive communication does not become unsupported superiority marketing.

## Adjacent factory fix

The package validator also assumed every generated Qiaomu skill must contain the meta skill's own routing tokens and Yao upstream credit. Validation is now package-aware: meta-only routing checks apply only to `qiaomu-meta-skill`, and README upstream credit is required only when `manifest.json` declares `upstream_inspiration`.
