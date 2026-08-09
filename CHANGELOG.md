# Changelog

## 3.6.0 (2026-08-10)

- 新增 `scripts/score_skill.py`：证据绑定自动评分器。六维加权（触发 15% / 输出 25% / prior-art+IR 15% / 复用安装 20% / 文档安全 15% / 治理 10%），只读 reports、不制造证据；缺失证据明确列出并降分（fixture-only 输出封顶 6.5）。
- `new_skill.py --mode production` 生成后自动输出 `reports/scorecard.json` 与 `reports/scorecard.md`（初始分 + missing evidence）。
- meta-skill 自举：用评分器给自身打分并落盘评分卡。

## 3.5.0 (2026-08-10)

- `publish_skill.py`：PR 创建后自动等待 GitHub 状态检查（`--wait-checks-timeout`，默认 600s），CI pending 不再要求人工重跑发布器。
- `validate_skill.py`：内置危险模式静态扫描 `scan_dangerous_patterns`（下载执行/动态执行/凭据读取/外传/持久化/提示词注入，文档降级 + os.environ 上下文判定）；新增 SKILL.md/README 引用脚本存在性检查与 references 上下文预算告警。
- `release_check.py`：新增 `skill_pattern_scan` 门禁（block 仅限脚本内高危 kind：download_exec/dynamic_exec/persistence/destructive/prompt_injection；其余为人工审查 warn 信号）。
- `output_eval.py`：llm_judge 裁判输出容错（`normalize_llm_answer` 取首个 yes/no，兼容 “yes, yes, yes” 等列表式回答）。
- 自证扩展：output cases 覆盖 CI 等待、危险模式扫描、引用检查；65/65 单元测试。

## 3.4.0 (2026-08-10)

- 新 skill 默认命名规则：`hugailab-` 前缀（`hugailab-xxxxx` 或 `hugailab-xxx-xxxx`，前缀后最多 5 段）。`new_skill.py` 自动为名称补前缀（已带前缀不重复添加）；`manifest.json` 的 `creator_defaults.skill_name_prefix` 默认改为 `hugailab`。
- README 快速上手与 SKILL.md Creator Defaults 同步命名规则；CLI 输出新增 `name` 字段。

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
