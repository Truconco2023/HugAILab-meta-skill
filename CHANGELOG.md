# Changelog

## 3.2.0 (2026-08-09)

- 新增 `scripts/output_eval.py`：输出级评测（recorded fixture / provider-backed LLM 断言 / 盲评包生成），配套 `evals/output_cases.json` 与 `reports/output-eval.json`。
- 触发评测新增 `--llm` 语义模式（OpenAI 兼容 API），与关键词 smoke 并存并诚实标注证据层级。
- 工程化：`ruff` + `mypy` 配置与 CI 步骤、`Makefile`（`make check`）、`CHANGELOG.md`。
- 新增 `scripts/new_skill.py` 一键脚手架与 `examples/demo-skill` 成品示例。
- 新增 `.github/workflows/release.yml`：tag 推送后自动运行 published 门禁。
- SKILL.md 指令瘦身；README 增加快速上手与 FAQ。

## 3.1.0 (2026-08-09)

- README 全面 HugAILab 化；发布器/校验器读取 `creator_defaults`；触发评测加固（weak 3 → 0）；彻底移除 `qiaomu-profile` 资产与开关；新增 GitHub Actions CI。

## 3.0.0 (2026-08-09)

- 彻底改名 `hugailab-meta-skill`；`hugai_yaml.py` 模块；触发概念 `brand`。

## 2.9.0 (2026-08-09)

- fork 首轮改造：P0 PyYAML 降级修复、加权触发评测、头像精简、品牌默认值中性化。

## 2.8.1 (2026-08-04)

- 上游 `joeseesun/qiaomu-meta-skill` 基线版本。
