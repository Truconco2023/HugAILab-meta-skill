# HugAILab Meta Skill Creation Handoff

## Result

- Skill: `hugailab-meta-skill` 3.6.1（fork：`Truconco2023/HugAILab-meta-skill`）
- Job: research, create, evaluate, package, govern, and safely publish reusable agent skills through one self-contained workflow
- Status: v3.1.0 已发布并通过 published 门禁；v3.2.0 为新一轮质量/易用性升级，本地验证通过后待推送合并与发布。

## v3.6.1 修复内容（2026-08-10）

- 评分生命周期缺陷修复：脚手架评分顺序（占位文件先就位）、初始快照标识（`--label initial`）、scorecard 新鲜度门禁、docs/governance 评分公平性。

## v3.6.0 升级内容（2026-08-10）

- 新增 `score_skill.py` 证据绑定自动评分器（六维加权、只读证据、missing evidence 降分）。
- `new_skill.py --mode production` 自动生成评分卡；meta-skill 自身评分卡由评分器自举产出。

## v3.5.0 升级内容（2026-08-10）

基于 obsidian-clip / macos-security-audit / meta-skill 自身三个真实实例的第三轮自举提升：

- 发布器自动等待 PR CI（消除两次发布中“pending → 人工重跑”的重复劳动）。
- 内置危险模式扫描并接入发布门禁（把 macos-security-audit 的静态扫描能力收编为工厂自身能力）。
- validate 增加“SKILL.md/README 引用脚本存在性”检查（obsidian-clip 扫描发现的 4 条 medium 正是此类）。
- references 上下文预算告警，防止工厂自身膨胀。
- 评分卡落盘 `reports/scorecard.md`，综合 9.6。

## v3.4.0 升级内容（2026-08-10）

- 新增默认命名规则：新 skill 一律 `hugailab-` 前缀（`hugailab-xxxxx` 或 `hugailab-xxx-xxxx`，前缀后最多 5 段）；`new_skill.py` 自动补前缀，`creator_defaults.skill_name_prefix` 默认 `hugailab`。
- 目的：提升 Hug AI Lab 品牌辨识度与影响力；用户显式要求其他前缀时遵循用户。

## v3.3.0 升级内容（2026-08-10）

基于 obsidian-clip v0.3.0 与 macos-security-audit v0.1.0 两个真实陪跑实例的实战反馈：

- `output_eval.py`：llm_judge 网络调用重试（`--retries` / `--retry-backoff`）；fixture 模式新增 `assertions_skipped` 计数，pass rate 只按已执行断言计算。
- `new_skill.py`：description 模板尾巴改为条件追加（仅当描述未含 skill/技能 时补最小尾巴），消除重复与标点噪音，同时保住 production 模式触发评测。
- `research_prior_art.py`：`--summary` 输出扁平化候选清单（family/catalogs/installs/url），消费成本降低。
- `references/output-eval-method.md`：新增 llm_judge 断言写法实战指引（自包含提示词、避免逐字比对、摘要忠实度问法、输出协议、重试建议）。
- `references/publishing.md`：补充受限网络下 `gh auth status` 误报说明与发布前联网核验建议。
- 回归：58/58 单元测试（新增 fixture skipped 语义测试、summary 扁平化测试）。

## v3.2.0 升级内容

1. **P0 输出评测**：`scripts/output_eval.py`（确定性断言 + 可选 provider LLM 判定 + 盲评包生成），`evals/output_cases.json` 2 场景，fixture 模式通过；provider 运行诚实标记 `missing evidence`。
2. **P0 语义触发评测**：`trigger_eval.py --llm` 模式（OpenAI 兼容 API），与关键词 smoke 并存。
3. **P1 工程化**：ruff/mypy/Makefile/CHANGELOG；修复 Python <3.11 的 `datetime.UTC` 兼容问题；修复 `hugai_yaml` 块标量 chomping 与空行保留。
4. **P1 脚手架**：`scripts/new_skill.py`（scaffold/production）与 `examples/demo-skill` 示例。
5. **P2 发布自动化**：`.github/workflows/release.yml` tag 门禁；SKILL.md 瘦身 + README 快速上手/FAQ。

## v3.1.0 迭代升级

1. **README 全面 HugAILab 化**：重写为 HugAILab 自己的项目页，移除上游 28 个案例大表与打赏/公众号区块，仅保留上游链接与必要致谢；`test_codex_skill_catalog.py` 同步改为校验 README 包含上游仓库链接。
2. **发布器/校验器真正读取 `creator_defaults`**：`generated_readme` 使用 manifest 中的 `copyright`/`x`/`github` 生成版权与链接；`validate_skill.py` 对 skill 名超长（超过 `max_preferred_hyphen_parts`）或未按 `skill_name_prefix` 开头给出警告。
3. **触发评测加固**：`prior_art` 概念补充 `research`/`synthesize`/`strongest`/`without copying` 等短语并把权重提到 1.5；负向模式新增 `不要改成 skill`、`别动结构`。结果 34/34 通过、0 误报 0 漏报、**0 个 weak 用例**。
4. **彻底移除 `qiaomu-profile` 资产**：删除 `assets/qiaomu-profile/` 与 `--qiaomu-profile` 开关、profile 注入代码；发布器完全品牌中立（无作者 Profile、二维码、打赏入口）。LICENSE 与上游链接保留。
5. **GitHub Actions CI**：新增 `.github/workflows/ci.yml`，在 Python 3.12 上分别以「有 PyYAML / 无 PyYAML」运行语法检查、46 个单元测试、包校验、触发评测与 Skill IR 导出。

## v3.0.0 彻底改名

- 内部 skill 名由 `qiaomu-meta-skill` 改为 `hugailab-meta-skill`：SKILL.md frontmatter、manifest、interface.yaml、README、安装命令、`~/.agents/skills` 路径、校验器 `META_SKILL_NAMES`、发布器错误信息全部同步。
- 内置 YAML 模块由 `qiaomu_yaml.py` 更名为 `hugai_yaml.py`；触发评测品牌概念由 `qiaomu` 改为 `brand`（phrases 保留 `hugailab`/`hugai`，同时兼容 `qiaomu`/`乔木` 旧说法）。
- 方法文档中的品牌称谓更新为 HugAILab；上游 `joeseesun/qiaomu-meta-skill`、`qiaomu-skill-publisher` 与 `向阳乔木` 署名按来源保留（`qiaomu-profile` 资产与 `--qiaomu-profile` 标志在 v3.1 已彻底移除）。
- 版本升至 3.0.0（major bump，因为对外身份变更）；`search_skillsmp.py` User-Agent 同步为 `hugailab-meta-skill/3.0`。

## v2.9.0 升级内容

### P0：PyYAML 可选依赖缺陷（已修复）

- 新增 `scripts/qiaomu_yaml.py`：纯标准库的 YAML 子集解析器，支持嵌套映射、流式/块式列表、引号标量、布尔/空值、注释、`|`/`>` 块标量。
- `validate_skill.py`、`trigger_eval.py`、`export_skill_ir.py` 在 PyYAML 缺失时自动降级到该解析器，不再静默返回空对象。
- 已在无 PyYAML 的 Python 3.12 环境实测：包校验 0 失败 0 警告，Skill IR 正常导出，48/48 测试通过。

### 触发评测更可靠

- 概念改为加权评分（`skill` 3.0、`source_material`/`authoring_action` 2.0、辅助概念 0.5–1.0），单核心词无法再靠巧合通过。
- 每个 should-trigger 用例可声明 `required` 必选概念；缺任何一个即失败，杜绝"两个词碰巧重叠就通过"。
- 新增 family coverage：某个场景族整族失败会直接阻断运行，而不是悄悄漏检。
- 报告新增 margin、matched_phrases、required_missing、weak 用例计数，便于人工判断边界脆弱性。
- 默认 strict 模式；`--lenient` 可临时降级为纯分数模式。
- 用例从 23 个扩展到 34 个（新增 4 个 should-trigger、4 个 should-not、3 个 near-neighbor），场景族从 14 个增至 18 个，当前 34/34 通过、0 误报 0 漏报。

### 精简头像体积

- `assets/qiaomu-profile/qiaomu_avatar.jpeg`：4096×4096 / 5.9MB → 512×512 / 68.6KB（减少约 98.8%）。

### 默认不注入乔木品牌

- 发布器默认不再向新 skill 注入乔木 Profile、二维码、打赏入口或"向阳乔木"版权行；`--qiaomu-profile` 改为显式选择（opt-in）。
- 生成的 README 使用 `Copyright (c) <year> <owner>`，不再硬编码乔木身份。
- `manifest.json` 的 `qiaomu_defaults` 改为中性的 `creator_defaults`；SKILL.md Router Rules 与 Creator Defaults 同步改为"品牌注入必须显式请求"。
- fork 的 README 移除乔木打赏/公众号区块，替换为「关于本 Fork」说明。

## Reference skills studied

### `yaojingang/yao-meta-skill`

- Why shortlisted: direct meta-skill reference with full-lifecycle engineering, evaluation, governance, and portability concepts.
- Learned: Skill IR, evidence boundaries, release gates, output evaluation, review layers, and post-release iteration.
- Applied in: HugAILab Skill OS layers, gate ladder, Skill IR export, output-eval method, and SkillOps references.

### `wshobson/agents@evaluation-methodology`

- Why shortlisted: complementary evaluation specialist found during prior-art research.
- Learned: separate evaluation dimensions, compare before/after behavior, preserve confidence and evidence limits.
- Applied in: trigger-first evaluation, output assertions, evidence labels, and the distinction between design and validated advantages.

### `joeseesun/qiaomu-skill-publisher`

- Why shortlisted: the user's explicit reference and the upstream Qiaomu implementation of LICENSE, README, Profile, repository naming and `npx` installation.
- Learned: strict YAML handling, repository/skill-name separation, brand-neutral public README scaffolding, discovery and temporary installation.
- Applied in: bundled `scripts/publish_skill.py`, `references/publishing.md`, trigger cases and publisher regression tests.

## Absorbed and rejected

- `keep`: platform-neutral intent, trigger/output evaluation, evidence-bound claims, release gates, publisher README/License preparation and install verification.
- `adapt`: profile injection is removed entirely; YAML parsing degrades to a bundled subset parser; trigger eval uses weighted and per-case required concepts; manifest defaults are neutral.
- `reject`: PyYAML as a silently-optional dependency; empty-dict fallback on parse failure; equal-weight keyword scoring; default third-party branding in generated packages.
- `invent`: `scripts/hugai_yaml.py`; strict weighted trigger eval with required concepts and family coverage; brand-neutral publisher; neutral creator defaults.

## Advantages and highlights

- `validated advantage`: package validation passes with 0 failures and 0 warnings on a Python 3.12 environment without PyYAML (46/46 unit tests, 34/34 trigger cases, 18/18 families, 0 weak cases).
- `design advantage`: trigger cases can no longer pass on two coincidental keyword overlaps; a missing required concept or an uncovered family fails the run.
- `design advantage`: published skill packages are brand-neutral by default; no third-party profile, QR, or donation injection exists in the publisher.
- `design advantage`: prior-art discovery, synthesis, creation, validation, and handoff remain inside one canonical workflow.
- `design advantage`: skills.sh installs and SkillsMP repository stars remain source-separated and cannot be combined into a fake score.
- `validated advantage`: publisher unit tests cover URL parsing, creator_defaults handling, generated README quality, default-branch rejection, pending-check blocking, read-only dry-run and brand-neutral output.
- `hypothesis`: stricter trigger gates should reduce real-world false positives, but a provider-backed routing benchmark remains `missing evidence`.

## Verification and limits

- Deterministic package validation: 0 failures, 0 warnings（系统 Python 3.12 无 PyYAML 环境实测）。
- Trigger eval: 34/34 通过，0 false positive，0 false negative，18/18 family 覆盖，0 个 weak 用例。
- Unit tests: 57/57 通过，覆盖 YAML 降级、触发评测严格性/覆盖度、输出评测、LLM 模式、creator_defaults、脚手架与发布器品牌中立行为。
- Lint/type: ruff 与 mypy 全绿（10 个脚本）。
- Output eval: recorded fixture 2/2 通过；provider-backed LLM 判定与人工盲评保持 `missing evidence`。
- Python 兼容性：修复 `datetime.UTC` 在 Python <3.11 的导入问题；YAML 块标量 chomping 与空行保留已修复并有测试。
- Avatar: 4096²/5.9MB → 512²/68.6KB。
- 发布器 `--dry-run`、`--prepare-only` 行为由更新后的测试覆盖；发布器不含任何 Profile/QR 注入代码。
- GitHub Actions CI: 已新增（Python 3.12，有/无 PyYAML 双路径），首次运行时需要在合并后确认绿。
- Public release / clean-install proof for 3.2.0: `missing evidence` until the release workflow completes.
- Provider-backed head-to-head output evaluation: `missing evidence`.
- Human blind comparison of trigger reliability: `missing evidence`.
