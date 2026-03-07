# generate-pos-flowchart

[English](#english) | [中文](#中文)

---

## 中文

### 简介

一个 **Cursor Agent Skill**，用于通过 Python 代码生成 [ProcessOn](https://www.processon.com/) 的 `.pos` 格式流程图文件。

支持三种图表类型：
- **普通流程图** — 矩形、菱形、胶囊形等标准流程图节点
- **泳道图** — 多角色/多部门的垂直泳道 + 阶段分隔
- **系统架构图** — 彩色模块块 + 标题条 + 子功能项

生成的 `.pos` 文件可直接导入 ProcessOn，无需手动绘图。

### 特性

- 支持 9 种流程图节点类型（process、decision、terminator、start、predefinedProcess、directData、storedData、roundRectangle、text）
- 支持泳道池（verticalPool）、泳道（verticalLane）、水平阶段分隔（horizontalSeparator）
- 连线自动计算正交折线拐角点，避免斜线
- 智能锚点选择规则，确保连线美观
- 支持 RGB 颜色填充和字体样式
- 内置文件验证功能
- 纯 Python 实现，无外部依赖

### 快速开始

```python
from scripts.generate_pos import PosBuilder

B = PosBuilder()

# 添加节点
n1 = B.add_terminator("开始", 300, 50)
n2 = B.add_process("处理步骤", 280, 130, w=200)
d1 = B.add_decision("判断条件", 290, 220)

# 添加连线
B.add_linker(n1, n2)
B.add_linker(n2, d1)

# 构建并保存
data = B.build("我的流程图")
B.save(data, "output.pos")
```

### 命令行使用

```bash
# 生成示例流程图
python scripts/generate_pos.py

# 生成泳道图示例
python scripts/generate_pos.py --demo-swimlane

# 生成架构图示例
python scripts/generate_pos.py --demo-arch

# 验证 .pos 文件
python scripts/generate_pos.py --verify output.pos
```

### 作为 Cursor Skill 使用

将本仓库克隆到 Cursor 的 skills 目录：

```bash
git clone https://github.com/lilyjem/generate-pos-flowchart.git ~/.cursor/skills/generate-pos-flowchart
```

之后在 Cursor 中即可通过 `@generate-pos-flowchart` 引用此 Skill，AI 会自动调用 `PosBuilder` 生成流程图。

### 导入 ProcessOn

1. 打开 [ProcessOn](https://www.processon.com/)
2. 新建流程图
3. 文件 → 导入 → 选择生成的 `.pos` 文件
4. 导入后可自由调整节点位置和样式

### 项目结构

```
generate-pos-flowchart/
├── SKILL.md                    # Cursor Skill 配置文件（AI 读取此文件）
├── pos-format-spec.md          # ProcessOn .pos 文件格式规范
├── scripts/
│   └── generate_pos.py         # PosBuilder 核心脚本
├── README.md
├── LICENSE
└── .gitignore
```

### 文档

- [SKILL.md](SKILL.md) — Skill 使用说明，包含所有节点类型、连线规则、锚点选择规则
- [pos-format-spec.md](pos-format-spec.md) — .pos 文件格式完整规范（基于逆向分析）

---

## English

### Introduction

A **Cursor Agent Skill** for generating [ProcessOn](https://www.processon.com/) `.pos` flowchart files programmatically with Python.

Supports three diagram types:
- **Flowcharts** — standard shapes: process, decision, terminator, etc.
- **Swimlane Diagrams** — vertical pools/lanes with horizontal stage separators
- **Architecture Diagrams** — colored module blocks with title bars

Generated `.pos` files can be directly imported into ProcessOn.

### Features

- 9 node types (process, decision, terminator, start, predefinedProcess, directData, storedData, roundRectangle, text)
- Swimlane support (verticalPool, verticalLane, horizontalSeparator)
- Auto-calculated orthogonal broken-line routing for connectors
- Smart anchor selection rules for clean connector paths
- RGB color fills and font styling
- Built-in file verification
- Pure Python, no external dependencies

### Quick Start

```python
from scripts.generate_pos import PosBuilder

B = PosBuilder()

n1 = B.add_terminator("Start", 300, 50)
n2 = B.add_process("Process Step", 280, 130, w=200)
d1 = B.add_decision("Condition?", 290, 220)

B.add_linker(n1, n2)
B.add_linker(n2, d1)

data = B.build("My Flowchart")
B.save(data, "output.pos")
```

### CLI Usage

```bash
# Generate demo flowchart
python scripts/generate_pos.py

# Generate swimlane demo
python scripts/generate_pos.py --demo-swimlane

# Generate architecture demo
python scripts/generate_pos.py --demo-arch

# Verify a .pos file
python scripts/generate_pos.py --verify output.pos
```

### Use as Cursor Skill

Clone this repo into your Cursor skills directory:

```bash
git clone https://github.com/lilyjem/generate-pos-flowchart.git ~/.cursor/skills/generate-pos-flowchart
```

Then reference it in Cursor with `@generate-pos-flowchart` — the AI will automatically use `PosBuilder` to generate flowcharts.

### License

[MIT](LICENSE)
