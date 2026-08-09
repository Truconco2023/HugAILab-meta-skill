# Iteration 2026-08-09 — v3.2.0 (quality and usability round)

## Changes

### P0 — Output evaluation

- 新增 `scripts/output_eval.py`：确定性断言（file_exists / contains / not_contains）+ 可选 `--llm-assert` provider 判定 + `--blind-pack` 盲评包/答案钥/评审模板三件套。
- 新增 `evals/output_cases.json`（2 个真实场景）与 `reports/output-eval.json`；fixture 模式通过，provider 运行诚实标记 `missing evidence`。

### P0 — Semantic trigger eval

- `trigger_eval.py` 新增 `--llm` / `--llm-model` / `--llm-limit`：OpenAI 兼容 API 逐用例判断是否触发，输出 `evidence_kind: provider_backed`；无 key 时明确报错。

### P1 — Engineering hardening

- `ruff` + `mypy` 配置与 CI 步骤；`Makefile`（`make check`）；`CHANGELOG.md`。
- 修复真实兼容问题：`datetime.UTC` 在 Python <3.11 不可用（search_skillsmp.py 增加降级）。
- 修复 `hugai_yaml` 块标量 chomping（`|+`/`|-`）与空行保留；补 creator_defaults 命名规则测试。

### P1 — Scaffold + example

- 新增 `scripts/new_skill.py`（scaffold / production 两档，production 自动生成 trigger/IR 证据报告）。
- 新增 `examples/demo-skill` 完整示例（按规范使用 `SKILL.example.md`）。

### P2 — Release automation & docs

- 新增 `.github/workflows/release.yml`：tag 推送后自动跑单测、lint/type、校验、评测与 published 门禁。
- SKILL.md 指令瘦身（11.2KB → 约 9KB）；README 增加 5 分钟快速上手与 FAQ。

## Verification

- Unit tests: 57/57（无 PyYAML 环境；有 PyYAML 对照也 57/57）。
- ruff / mypy: 全绿（10 个脚本）。
- `validate_skill.py .`: 0 failures, 0 warnings。
- Trigger eval: 34/34, 0 FP, 0 FN, 18/18 families, 0 weak。
- Output eval: recorded fixture 2/2；provider 运行保持 `missing evidence`。
- SKILL.md: 11.2KB → 10.1KB；README 新增快速上手与 FAQ。

## Missing evidence

- Provider-backed LLM 触发评测与输出断言（需要 OPENAI_API_KEY 实跑）。
- 人工盲评（`--blind-pack` 产物已就绪，等待评审人）。
- v3.2.0 公开 Release 与合并后的 CI 运行。
