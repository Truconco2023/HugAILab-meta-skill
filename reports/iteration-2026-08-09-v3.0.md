# Iteration 2026-08-09 — v3.0.0 (HugAILab rename)

## Changes

1. **彻底改名**：内部 skill 名 `qiaomu-meta-skill` → `hugailab-meta-skill`，同步更新 SKILL.md、manifest、interface.yaml、README、安装命令、校验器、发布器与测试。
2. **模块更名**：`scripts/qiaomu_yaml.py` → `scripts/hugai_yaml.py`；`tests/test_qiaomu_yaml.py` → `tests/test_hugai_yaml.py`。
3. **触发评测品牌概念**：`qiaomu` → `brand`（phrases 覆盖 `hugailab`/`hugai`/`qiaomu`/`乔木`），相关用例文本更新为 HugAILab 说法。
4. **版本**：2.9.0 → 3.0.0（major bump）；SkillsMP User-Agent 同步为 `hugailab-meta-skill/3.0`。

## Preserved attribution

- 上游仓库链接 `joeseesun/qiaomu-meta-skill` 与 `qiaomu-skill-publisher`。
- `assets/qiaomu-profile` 资产与 `--qiaomu-profile` 显式开关。
- README 上游案例表（28 个 Qiaomu skills）与 LICENSE 原作者版权。

## Verification

- Unit tests: 48/48（无 PyYAML 环境）。
- Trigger eval: 34/34, 0 FP, 0 FN, 18/18 families。
- `validate_skill.py .`: 0 failures, 0 warnings。
- Skill IR / trigger report 重新生成，package.name = `hugailab-meta-skill`, version = 3.0.0。
