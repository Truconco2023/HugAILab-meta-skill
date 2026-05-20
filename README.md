# qiaomu-meta-skill

> 把零散的工作流、笔记和想法，整理成可复用、可触发、可发布的乔木技能包。

## 这是什么

`qiaomu-meta-skill` 用来把重复出现的做事方式，改造成一套真正能复用的 skill。

它适合：

- 把 workflow 变成 skill
- 给已有 skill 做重构、收敛和补强
- 补 trigger、边界、评估和治理文件
- 直接把 skill 做完并交给乔木发布器发布到 GitHub
- 打包成适合乔木团队复用的版本

## 安装

```bash
npx skills add joeseesun/qiaomu-meta-skill
```

## 你可以直接这样说

- “把这个流程整理成一个 skill”
- “把这个流程整理成一个 skill 并发布”
- “帮我优化这个 skill 的触发词和边界”
- “给这个 skill 补上评估和治理文件”

## 目录结构

- `SKILL.md`：路由和最小执行骨架
- `agents/interface.yaml`：跨平台适配层
- `references/`：方法论和边界说明
- `reports/`：评估、决策和证据

## 发布提示

这个 skill 设计成可发布的库型包。发布到 GitHub 前，先确认：

- `SKILL.md` 的 frontmatter 完整
- 需要的 `references/` 已补齐
- README 能让陌生用户知道它能做什么

## License

MIT
