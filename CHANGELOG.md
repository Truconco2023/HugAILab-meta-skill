# Changelog

## 3.3.0 (2026-08-10)

- `output_eval.py`：`llm_judge` 网络调用支持重试（`--retries` / `--retry-backoff`），单次 connection reset 不再中断整轮评测；fixture 模式明确统计 `assertions_skipped`，pass rate 只按已执行断言计算，CLI 仅对已执行断言失败退出非零（`make check` 兼容 fixture 跳过）。
- `new_skill.py`：去掉 description 模板尾巴「；作为可复用的 skill 交付可验证结果」，用户描述原样进入 SKILL.md / interface / README，避免重复与标点噪音。
- `research_prior_art.py`：`--summary` 输出扁平化候选清单（family / catalogs / installs / stars / url），降低消费成本。
- `references/output-eval-method.md`：新增 llm_judge 断言写法实战指引（自包含提示词、避免逐字比对、摘要忠实度问法、输出协议、重试建议）。
- `references/publishing.md`：补充受限网络下 `gh auth status` 误报说明与发布前联网核验建议。

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
