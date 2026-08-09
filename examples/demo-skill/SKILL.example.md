---
name: hugai-demo
description: |
  把一段重复的会议纪要做成结构化要点与行动项，并输出可直接粘贴的 Markdown 交付物。仅用于演示 skill 包结构；复制本文件为 SKILL.md 后即可作为独立 skill 使用。
---

# hugai-demo

处理：输入会议记录 → 输出结构化要点 + 行动项 + 负责人/截止日。

## 工作流

1. 读取输入。
2. 抽取决策、待办、负责人与截止日。
3. 输出 Markdown，并标注不确定项。
