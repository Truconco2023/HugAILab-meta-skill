# Iteration 2026-08-09 — v2.9.0 (HugAILab fork upgrade)

## Changes

1. **P0 — PyYAML 可选依赖缺陷**：新增 `scripts/qiaomu_yaml.py` 纯标准库 YAML 子集解析器，`validate_skill.py`、`trigger_eval.py`、`export_skill_ir.py` 在无 PyYAML 时自动降级；本机（Python 3.12 无 PyYAML）自校验从失败变为 0 失败 0 警告。
2. **触发评测可靠性**：加权概念 + 每用例必选概念 + family coverage + margin/weak 报告 + 默认 strict（`--lenient` 可降级）。用例 23 → 34，family 14 → 18，34/34 通过。
3. **头像精简**：`qiaomu_avatar.jpeg` 4096²/5.9MB → 512²/68.6KB（-98.8%）。
4. **默认不注入乔木品牌**：发布器 `--qiaomu-profile` 改为 opt-in；生成的 README 使用 owner 版权；`manifest.json` 改为中性 `creator_defaults`；fork README 移除乔木打赏/公众号区块。

## Verification

- Unit tests: 48/48（无 PyYAML 环境）。
- Trigger eval: 34/34, 0 FP, 0 FN, 18/18 families。
- `validate_skill.py .`: 0 failures, 0 warnings。
- `export_skill_ir.py`: 无 PyYAML 下正常导出，portability 字段完整。
- Avatar 体积: 68,595 bytes。

## Missing evidence

- v2.9.0 公开 Release 与干净安装验证（尚未发布）。
- Provider-backed 路由对比评测。
- 人工盲评。
