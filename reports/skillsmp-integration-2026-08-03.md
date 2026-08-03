# SkillsMP Integration — 2026-08-03

## Source contract

- Catalog: https://skillsmp.com/
- API documentation: https://skillsmp.com/docs/api
- Endpoint: `GET /api/v1/skills/search`
- Authentication used for smoke test: anonymous
- Search fields used: query, limit, sort
- Mutable catalog metrics are dated and must be rechecked.

## Semantics preserved

- SkillsMP `stars` is stored as `repo_stars`; it is not a rating, install count, or skill-specific quality score.
- `updatedAt` is the catalog's indexed timestamp; GitHub remains the source of truth.
- `pagination.totalIsExact` may be false and must remain visible when present.
- Anonymous and authenticated quotas are external service limits, not Qiaomu guarantees.

## Live smoke evidence

- Date: 2026-08-03
- Query: `seo`
- Command: `python3 scripts/search_skillsmp.py 'seo' --limit 5 --sort stars`
- HTTP result: success
- Raw candidates: 5
- Deduplicated families: 3
- One SEO family collapsed four language/source variants and preserved three aliases.
- Anonymous daily remaining reported by the response: 49 of 50 at test time.

## Boundary

This proves the API contract, normalization, rate-header capture, and within-SkillsMP family deduplication at the recorded time. Cross-catalog semantic matching with skills.sh remains a review step because its CLI output is not treated as a stable machine-readable API. GitHub source, license, activity, permissions, and actual skill content still require verification before adoption.
