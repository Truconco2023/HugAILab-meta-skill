# HugAILab Meta Skill Creation Handoff

## Result

- Skill: `hugailab-meta-skill` 3.0.0（fork：`Truconco2023/HugAILab-meta-skill`）
- Job: research, create, evaluate, package, govern, and safely publish reusable agent skills through one self-contained workflow
- Status: 本地候选已完整验证（无 PyYAML 环境 48/48 测试、34/34 触发评测、0 个包校验失败）；公开发布与干净安装证明在 v3.0.0 发布流程完成前保持 `missing evidence`

## v3.0.0 彻底改名

- 内部 skill 名由 `qiaomu-meta-skill` 改为 `hugailab-meta-skill`：SKILL.md frontmatter、manifest、interface.yaml、README、安装命令、`~/.agents/skills` 路径、校验器 `META_SKILL_NAMES`、发布器错误信息全部同步。
- 内置 YAML 模块由 `qiaomu_yaml.py` 更名为 `hugai_yaml.py`；触发评测品牌概念由 `qiaomu` 改为 `brand`（phrases 保留 `hugailab`/`hugai`，同时兼容 `qiaomu`/`乔木` 旧说法）。
- 方法文档中的品牌称谓更新为 HugAILab；上游 `joeseesun/qiaomu-meta-skill`、`qiaomu-skill-publisher`、`qiaomu-profile` 资产、`--qiaomu-profile` 标志、README 上游案例表与 `向阳乔木` 署名按来源保留。
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
- Learned: idempotent profile markers, strict YAML handling, repository/skill-name separation, public README scaffolding, discovery and temporary installation.
- Applied in: bundled `scripts/publish_skill.py`, `references/publishing.md`, profile assets, trigger cases and publisher regression tests.

## Absorbed and rejected

- `keep`: platform-neutral intent, trigger/output evaluation, evidence-bound claims, release gates, publisher README/Profile/License preparation and install verification.
- `adapt`: profile injection is now opt-in; YAML parsing degrades to a bundled subset parser; trigger eval uses weighted and per-case required concepts; manifest defaults are neutral.
- `reject`: PyYAML as a silently-optional dependency; empty-dict fallback on parse failure; equal-weight keyword scoring; default third-party branding in generated packages.
- `invent`: `scripts/qiaomu_yaml.py`; strict weighted trigger eval with required concepts and family coverage; `--qiaomu-profile` opt-in publisher behavior; neutral creator defaults.

## Advantages and highlights

- `validated advantage`: package validation passes with 0 failures and 0 warnings on a Python 3.12 environment without PyYAML (48/48 unit tests, 34/34 trigger cases, 18/18 families).
- `design advantage`: trigger cases can no longer pass on two coincidental keyword overlaps; a missing required concept or an uncovered family fails the run.
- `design advantage`: published skill packages are brand-neutral by default; Qiaomu profile/QR injection requires an explicit flag.
- `design advantage`: prior-art discovery, synthesis, creation, validation, and handoff remain inside one canonical workflow.
- `design advantage`: skills.sh installs and SkillsMP repository stars remain source-separated and cannot be combined into a fake score.
- `validated advantage`: publisher unit tests cover URL parsing, profile idempotence, generated README quality, default-branch rejection, pending-check blocking, read-only dry-run, opt-in profile behavior and bundled assets.
- `hypothesis`: stricter trigger gates should reduce real-world false positives, but a provider-backed routing benchmark remains `missing evidence`.

## Verification and limits

- Deterministic package validation: 0 failures, 0 warnings（系统 Python 3.12 无 PyYAML 环境实测）。
- Trigger eval: 34/34 通过，0 false positive，0 false negative，18/18 family 覆盖；3 个 weak 用例（2 个依赖负向模式的近邻、1 个 margin 仅 0.028 的英文 prior-art 用例）。
- Unit tests: 48/48 通过，新增 YAML 降级、触发评测严格性/覆盖度、发布器品牌默认值测试。
- Avatar: 4096²/5.9MB → 512²/68.6KB。
- 发布器 `--dry-run`、`--prepare-only` 行为由更新后的测试覆盖；默认不再写入 Profile。
- Public release / clean-install proof for 3.0.0: `missing evidence` until the release workflow completes.
- Provider-backed head-to-head output evaluation: `missing evidence`.
- Human blind comparison of trigger reliability: `missing evidence`.
