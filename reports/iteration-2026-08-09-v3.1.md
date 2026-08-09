# Iteration 2026-08-09 — v3.1.0 (HugAILab polish round)

## Changes

1. **README 全面 HugAILab 化**：重写为 HugAILab 自己的项目页；移除上游 28 个案例大表、打赏/公众号区块；仅保留上游链接与必要致谢；同步更新 `test_codex_skill_catalog.py`。
2. **发布器/校验器读取 `creator_defaults`**：`generated_readme` 使用 manifest 的 `copyright`/`x`/`github`；`validate_skill.py` 检查 skill 名 hyphen 数量与 `skill_name_prefix`。
3. **触发评测加固**：`prior_art` 权重 1.0→1.5 并补充 `research`/`synthesize`/`strongest`/`without copying` 等短语；负向模式新增 `不要改成 skill`、`别动结构`；weak 用例 3 → 0。
4. **彻底移除 qiaomu-profile**：删除 `assets/qiaomu-profile/`、`--qiaomu-profile` 开关、profile 注入代码与相关测试；发布器完全品牌中立。
5. **GitHub Actions CI**：新增 `.github/workflows/ci.yml`，Python 3.12 上按「有/无 PyYAML」矩阵运行语法检查、单测、包校验、触发评测与 IR 导出。

## Verification

- Unit tests: 46/46（无 PyYAML 环境）。
- Trigger eval: 34/34, 0 FP, 0 FN, 18/18 families, 0 weak。
- `validate_skill.py .`: 0 failures, 0 warnings。
- 发布器 `--dry-run` / `--prepare-only` 测试通过；`assets/qiaomu-profile` 已删除。

## Missing evidence

- v3.1.0 公开 Release 与干净安装验证（尚未发布）。
- GitHub Actions 首次运行结果（合并后确认）。
- Provider-backed 路由对比评测与人工盲评。
