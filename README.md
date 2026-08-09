# hugailab-meta-skill

> 把一句「把这个流程做成 Skill」，变成一个真正能被发现、能稳定触发、能通过验证、还能一键开源的 Skill。

[![GitHub Release](https://img.shields.io/github/v/release/Truconco2023/HugAILab-meta-skill?display_name=tag&sort=semver)](https://github.com/Truconco2023/HugAILab-meta-skill/releases)
[![Stars](https://img.shields.io/github/stars/Truconco2023/HugAILab-meta-skill?style=flat)](https://github.com/Truconco2023/HugAILab-meta-skill/stargazers)
[![Last commit](https://img.shields.io/github/last-commit/Truconco2023/HugAILab-meta-skill)](https://github.com/Truconco2023/HugAILab-meta-skill/commits/main)
[![License](https://img.shields.io/github/license/Truconco2023/HugAILab-meta-skill)](LICENSE)

```bash
npx skills add Truconco2023/HugAILab-meta-skill
```

安装以后，你只需要把提示词、SOP、聊天记录、旧 Skill、脚本或一个模糊想法交给 Agent：

```text
用 HugAILab Meta Skill，把这套工作流做成一个可复用的 Skill；
先研究同类热门 Skill，完成触发评测和安全检查，然后发布到 GitHub。
```

它会自己完成：**需求收敛 → 同类检索 → 取长避短 → Skill 设计 → 触发评测 → 格式校验 → README → API 泄露检查 → PR → Release → npx 安装验证**。

**v3.1.0 本地候选已验证：** 46/46 单元测试、34/34 触发评测（18/18 场景族、0 个弱用例）、0 个包校验问题（无 PyYAML 环境同样通过）。公开发布证据以 [Releases](https://github.com/Truconco2023/HugAILab-meta-skill/releases) 为准。

## 这是做什么的

`hugailab-meta-skill` 是 [HugAILab](https://github.com/Truconco2023) 维护的元技能，fork 自 [`joeseesun/qiaomu-meta-skill`](https://github.com/joeseesun/qiaomu-meta-skill)。它把提示词、SOP、脚本、聊天记录或一个模糊想法，变成可复用、可评测、可安全发布的 Agent Skill 包——而不是一份越写越长的 Prompt。

与上游相比，本 fork 的主要改进：

- **无 PyYAML 也能自校验**：内置纯标准库 YAML 解析器，干净环境开箱即用。
- **触发评测更严格**：加权概念 + 每用例必选概念 + 场景族覆盖，默认 strict 模式，杜绝"两个词碰巧重叠就通过"。
- **资产体积精简**：头像由 5.9MB 压缩到 68.6KB。
- **品牌中立**：默认不注入任何作者个人品牌、二维码或打赏入口；发布产物只带持有者自己的版权信息。
- **彻底改名**：内部 skill 名为 `hugailab-meta-skill`（v3.x），上游署名按来源保留。

## 安装与验证

```bash
npx skills add Truconco2023/HugAILab-meta-skill
```

只安装这个 Skill：

```bash
npx skills add Truconco2023/HugAILab-meta-skill --skill hugailab-meta-skill
```

验证：

```bash
test -f ~/.agents/skills/hugailab-meta-skill/SKILL.md
python3 ~/.agents/skills/hugailab-meta-skill/scripts/validate_skill.py \
  ~/.agents/skills/hugailab-meta-skill
```

## 你可以直接这样说

- “把这个流程整理成一个可复用的 skill”
- “先搜索同类热门 Skill，分析优缺点，再做一个不抄袭的版本”
- “优化这个已有 Skill 的触发率、准确性和指令遵循”
- “审计这个 Skill，只给问题和建议，先不要修改文件”
- “把这个 Skill 发布到 GitHub，生成 npx 安装命令并验证别人能装”

## 它比普通 Skill 创建器多做什么

| 能力 | 普通“生成 SKILL.md” | hugailab-meta-skill |
|---|---:|---:|
| 从 Prompt / SOP / 对话 / 旧 Skill 提炼工作流 | ✓ | ✓ |
| 先搜索 skills.sh 与 SkillsMP 的相关 Skill |  | ✓ |
| 回到 GitHub 核对来源、维护、安全与许可证 |  | ✓ |
| 记录 `keep / adapt / reject / invent`，避免拼贴抄袭 |  | ✓ |
| 测试该触发与不该触发的真实说法 | 视实现而定 | ✓ |
| 区分设计优势、已验证优势和待验证假设 |  | ✓ |
| 校验目录、版本、上下文预算与递归发现 |  | ✓ |
| Secret / API 泄露扫描 |  | ✓ |
| 功能分支、PR、检查、Release |  | ✓ |
| `npx skills add` 公开发现与隔离安装验证 |  | ✓ |

它不是让 Skill 变得更重，而是让复杂度与风险匹配：个人试验走轻量 `Scaffold`，公开发布才启用完整 `Governed` 门禁。

## 它会产出什么

根据场景复杂度，元 Skill 会创建必要而非礼仪性的文件：

```text
your-skill/
├── SKILL.md                    # Agent 路由与最小执行骨架
├── README.md                   # 给人看的产品页
├── LICENSE                     # 默认 MIT
├── manifest.json               # 版本、作者、平台与门禁
├── agents/interface.yaml       # 跨 Agent 接口
├── references/                 # 长方法、判断与安全边界
├── scripts/                    # 可重复验证与确定性工具
├── evals/trigger_cases.json    # 应触发、不应触发、近邻场景
└── reports/                    # Skill IR、研究、评测与发布证据
```

## 一套完整工作流

1. **Intent**：确认重复任务、目标用户、输入、输出、边界与成功标准。
2. **Search**：用 2–4 组意图关键词查询 skills.sh 与 SkillsMP，再回到 GitHub 验源。
3. **Synthesis**：记录每个候选的 `keep / adapt / reject / invent`，明确原创贡献。
4. **Package**：写精简 `SKILL.md`，把长判断放进 references，把确定性动作放进 scripts。
5. **Eval**：先测触发边界；风险需要时再补输出、运行时或人工评测。
6. **Release**：检查版本、README、许可证、秘密信息与安装入口，经功能分支和 PR 发布。
7. **Verify**：创建 Release，确认远端默认分支，并在隔离环境完成公开安装。

## 内置搜索

```bash
python3 scripts/research_prior_art.py \
  "<query 1>" "<query 2>" \
  --strict --summary \
  --output reports/prior-art-candidates.json
```

底层数据源：

```bash
npx --yes skills find "<query>"
python3 scripts/search_skillsmp.py "<query>" --limit 20 --sort stars
```

详细方法见 [`references/prior-art-research.md`](references/prior-art-research.md)。

## 自包含发布

只检查，不改文件、不写 GitHub：

```bash
python3 scripts/publish_skill.py /path/to/skill --dry-run
```

正式发布：

```bash
python3 scripts/publish_skill.py /path/to/skill
```

发布器会依次执行包验证、版本一致性、secret scan、功能分支、PR 检查、合并、GitHub Release、`npx skills add --list`、隔离安装和本地安全同步。

- 不直接推送 `main/master`
- 不覆盖已经发布的同版本 Release
- 不吞掉 push 或检查失败
- PR 冲突、未完成/失败检查或 requested changes 会阻断自动合并

## 本地质量检查

```bash
python3 scripts/validate_skill.py .
python3 scripts/export_skill_ir.py . --output reports/skill-ir.json
python3 scripts/trigger_eval.py . --cases evals/trigger_cases.json --output reports/trigger-eval.json
python3 scripts/release_check.py . --phase local --run-tests
python3 -m unittest discover -s tests -p 'test_*.py'
```

## 前置条件

- [ ] Node.js 18+：`node --version`
- [ ] npx 可用：`npx --version`
- [ ] Python 3.9+：`python3 --version`（不需要 PyYAML，脚本内置降级解析器）
- [ ] 发布到 GitHub 时安装并登录 GitHub CLI：`gh auth status`
- [ ] 搜索或发布时允许访问 skills.sh、SkillsMP 与 GitHub

## Troubleshooting

| 问题 | 常见原因 | 处理方式 |
|---|---|---|
| `No valid skills found` | `SKILL.md` frontmatter 不完整或嵌套入口错误 | 运行 `scripts/validate_skill.py`，修正 `name`、`description` 与根入口 |
| Skill 到处误触发 | description 太泛 | 补 should-not-trigger 与 near-neighbor 用例，收窄描述 |
| Skill 永远不触发 | 用户自然说法没有进入 description | 从真实对话补触发词，再跑 trigger eval |
| README 像内部说明书 | 把 `SKILL.md` 直接复制成 README | 重写成价值、安装、说法、输出、风险与排错 |
| 发布后别人装不上 | 只验证本地目录，没有公开发现和隔离安装 | 完整运行发布器，不把 push 成功当作发布完成 |
| 发布器拒绝版本 | `vX.Y.Z` 已存在 | 提升版本；已发布版本不可覆盖 |

## 研究与致谢

- 上游：[`joeseesun/qiaomu-meta-skill`](https://github.com/joeseesun/qiaomu-meta-skill)（MIT）
- 初始方法：[`yaojingang/yao-meta-skill`](https://github.com/yaojingang/yao-meta-skill)
- 发布器前身：[`joeseesun/qiaomu-skill-publisher`](https://github.com/joeseesun/qiaomu-skill-publisher)
- 官方参考：[`anthropics/skills`](https://github.com/anthropics/skills)、[`openai/skills`](https://github.com/openai/skills)
- 完整 prior-art 研究：`reports/prior-art-research.md`
- 上游历史实践案例：`reports/codex-skill-catalog.md`

Upstream inspiration: https://github.com/yaojingang/yao-meta-skill; https://github.com/joeseesun/qiaomu-skill-publisher

上游思想以语义方式吸收并保留归因，不整库镜像，不复制许可证不明的正文，也不把搜索热度冒充质量。

## 安全与证据边界

- 公开候选只读取元数据与源码，不会为了学习而执行未经审查的第三方脚本。
- API key、Cookie、Token、私有附件、绝对路径和原始对话不得进入公开仓库。
- 目录安装量、仓库 stars、安全审计和许可证分别记录，不合并为“最佳 Skill 分数”。
- 没有 provider 实跑、人工盲评或用户结果时，必须明确标记 `missing evidence`。
- 发布是外部写操作，只有明确要求时才执行，并通过功能分支、PR、Release 与公开安装验证。

---

<a name="english"></a>
## English

`hugailab-meta-skill` turns prompts, SOPs, transcripts, scripts, and existing skills into researched, evaluated, installable agent-skill packages.

Unlike a one-shot `SKILL.md` generator, it includes dual-catalog prior-art research, GitHub source verification, weighted trigger evaluation, evidence-aware release gates, secret scanning, pull-request publication, versioned Releases, and clean `npx` installation verification. It works without PyYAML and ships brand-neutral packages by default.

```bash
npx skills add Truconco2023/HugAILab-meta-skill
```

Try saying:

- “Turn this repeated workflow into a reusable skill.”
- “Research the strongest related skills, then synthesize an original version.”
- “Publish this skill to GitHub and prove that a clean machine can discover and install it.”

The project is intentionally fork-friendly: install it, run a real workflow, then replace the defaults with your own judgment, tools, style, and evaluation boundary.

## License

MIT。原作者版权见 [LICENSE](LICENSE)，fork 保留上游署名。
