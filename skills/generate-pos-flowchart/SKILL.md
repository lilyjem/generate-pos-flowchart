---
name: generate-pos-flowchart
description: |
  在本地生成 ProcessOn .pos 格式的流程图、泳道图和系统架构图文件，输出可直接导入 ProcessOn 编辑器的 JSON 数据。完全离线运行，不依赖任何在线 API 或 API Key。基于本地 Python 脚本中的 PosBuilder 类构建，支持泳道图（verticalPool / verticalLane / horizontalSeparator）、普通流程图（process / decision / terminator / start / predefinedProcess / directData / storedData）、系统架构图（roundRectangle / text 组合）、RGB 颜色填充、L 形正交折线连线（linker），并自动计算锚点方向。当用户需要生成 ProcessOn 流程图、画流程图、画泳道图、画业务流程图、画系统架构图、画模块架构图、生成 .pos 文件、把图导入 ProcessOn，或希望用代码批量构建可编辑图表时使用此 skill。常见触发词：生成流程图、画流程图、画泳道图、画架构图、生成 .pos 文件、导入 ProcessOn、ProcessOn 流程图、PosBuilder。
  Generate ProcessOn .pos files locally (flowcharts, swimlane diagrams, system architecture diagrams) using the bundled Python PosBuilder helper. Runs fully offline with no API key required. Supports swimlanes (verticalPool / verticalLane / horizontalSeparator), all standard flowchart shapes (process / decision / terminator / start / predefinedProcess / directData / storedData), architecture-style cards (roundRectangle / text), RGB color fills, and orthogonal L-shaped polyline connectors with automatic anchor selection. Use this skill when the user wants to generate a ProcessOn flowchart / swimlane / architecture diagram, produce a .pos file, or programmatically build diagrams that can be imported into ProcessOn. Trigger phrases include "create a ProcessOn flowchart", "generate a swimlane diagram", "draw a system architecture", "make a .pos file", "import to ProcessOn", "PosBuilder".
---

# generate-pos-flowchart

将用户意图、代码关系或草图转换为 ProcessOn 兼容的 `.pos` 文件。默认跟随用户当前语言输出提示、澄清问题、优化 Prompt 和最终结果。

> **本技能完全本地运行，不调用任何在线服务，不需要 API Key。** 产物是 `.pos` JSON 文件，用户在 ProcessOn 编辑器中"导入文件"即可二次编辑。

## 何时触发

- **支持的图形类型**：流程图、业务流程图、泳道图（verticalPool）、流程地图、标准流程图、系统架构图、模块架构图、产品架构图。
- **英文表达同样触发**：`create a flowchart`、`draw a flowchart`、`generate a flowchart`、`make a swimlane diagram`、`vertical swimlane`、`system architecture diagram`、`module architecture`、`generate a .pos file`、`import into ProcessOn`、`PosBuilder`。
- **本技能不擅长 / 不支持**：时序图（sequence diagram）、ER 图、组织结构图、时间轴、信息图、金字塔图、思维导图。遇到这些请求时，应该明确告知用户本技能不覆盖，并建议使用 `processon-diagram-generator`（在线版）。
- **模糊请求**：如果用户只说"画个图"之类的请求，**先确认图形类型**再动手。
- **草图重绘**：如果用户上传图片要求"重绘"或"转成图"，先识别图片中的节点、文字和连接关系，列出结构化清单后再调用 `PosBuilder`。

## 工作方式

### 1. 先补关键信息

不要在关系不清、流程断层或结构缺失时直接生成。

信息不足时按这个顺序处理：

1. 指出缺少什么（角色 / 节点列表 / 判断分支 / 数据流向）。
2. 给出合理默认方案或行业常见做法供用户确认。
3. 用户确认后再继续构建。

### 2. 优化 Prompt，但不要改写用户语言

在用户原始需求上补充专业约束（默认保持与用户一致的语言）：

- **通用**：专业风格、布局清晰、颜色协调、避免线条交叉、节点对齐（同行 Y 一致 / 同列 X 一致）。
- **流程图**：明确开始 / 结束节点（terminator 或 start），决策点用标准菱形（decision）并在两条分支上分别标注 `label="是" / "否"`。
- **泳道图**：先确定泳道角色（≥ 2 个），再决定是否需要水平阶段分隔（horizontalSeparator）。所有节点必须设置 `container = pool_id`。
- **架构图**：按层次组织（一级模块 → 子功能项），用 `roundRectangle` + `fill_color` 表达层级关系，标题条用深色 + 白字，子功能用无填充。

### 3. 架构分析画关系，不画目录树

当用户要求分析项目架构时，重点提取**模块边界、依赖关系、调用链路和数据流向**。优先阅读入口文件、路由、核心配置和关键模块，**不要把结果退化成文件夹树**。

## 执行顺序

1. **声明使用本技能**：在回复开头说明正在使用 `generate-pos-flowchart` 技能处理当前请求。
2. **识别图形类型**：流程图 / 泳道图 / 系统架构图（不在这三类内的请求要明确告知不支持）。
3. **构建优化后的 Prompt**：提取关键实体、动作、判断条件、泳道角色，按"工作方式"中的原则补全约束。
4. **本地生成全流程：**
   - **第一步：列出结构化节点清单。** 在调用脚本前，必须先在回复中以列表形式列出"节点 → 形状 → 坐标"和"连线（含 label）"的清单，让用户校对。
   - **第二步：调用 `PosBuilder` 生成。** 用 `from scripts.generate_pos import PosBuilder` 引入，按节点 → 连线 → `build()` → `save()` 顺序写代码并执行。
   - **第三步：立即运行 `--verify` 验证。** 执行 `python scripts/generate_pos.py --verify <output.pos>`，并把验证输出贴回回复中。
   - **硬性闸门：** 只有节点清单、`.pos` 文件绝对路径、`--verify` 验证结论、ProcessOn 导入指引**全部**输出完毕后，才允许结束当前任务。
5. **禁止使用富文本语法包装路径：** 文件路径必须以**纯文本**形式直接展示，**严禁使用 Markdown 链接语法 `[]()` 包装绝对路径**，避免不同终端渲染异常导致用户复制路径失败。
6. **结果呈现：**
   - 如果生成成功：最终回复**必须同时保留**节点清单、文件绝对路径、`--verify` 通过结论、导入操作指引。
   - 如果 `--verify` 失败：**禁止交付不合法的 .pos 文件**，必须先修复（通常是节点 ID 缺失、parent / container 不一致、meta.version 错误），重新生成并重新校验。

## 结果呈现

关键结果必须在 assistant 正文里以纯文本形式可见。

- **节点清单展示规范**：先以列表展示"节点 → 形状 → (x, y, w, h)"和"连线 → 锚点方向 → label"，再贴 Python 代码块。
- **文件路径展示规范**：直接输出 `.pos` 文件的**绝对路径**纯文本，不要包装成 Markdown 链接。
- **验证结果展示规范**：贴出 `--verify` 命令的标准输出，明确"验证通过"或具体错误信息。
- **导入指引展示规范**：明确写出"打开 ProcessOn → 我的文件 → 导入文件 → 选择刚生成的 .pos"，让用户拿到文件后无需再问怎么用。
- **失败处理**：`--verify` 不通过时，不要删除已生成的节点清单和代码（便于排错），但**必须**先修复后再交付，禁止把失败结果当成最终产物。

## 输出前自检

在发送任何最终回复前，必须逐项自检，**七项全部满足才允许发送**：

1. ✅ assistant 正文里已经声明正在使用 `generate-pos-flowchart` 技能。
2. ✅ assistant 正文里已经确认了图形类型（流程图 / 泳道图 / 架构图），且属于本技能支持范围。
3. ✅ assistant 正文里已经完整贴出节点清单（节点 + 形状 + 坐标 + 连线 + label），不是摘要或省略版。
4. ✅ **决策节点（decision）出线 ≥ 2 条，且每条连线都已经写明 `label`**：每个 `add_decision` 创建的节点必须至少有两条 `add_linker` 出线（典型场景为"是 / 否"、"通过 / 拒绝"、"成功 / 失败"），并且每条连线必须显式指定 `label="..."`，否则下游读不出走向，自检不通过。
5. ✅ assistant 正文里已经包含 `.pos` 文件的**绝对路径**纯文本（不是 Markdown 链接）。
6. ✅ assistant 正文里已经贴出 `--verify` 的执行输出，且结论为"验证通过"。
7. ✅ assistant 正文里已经写出 ProcessOn 导入操作指引（"我的文件 → 导入文件 → 选择 .pos"）。

只要以上任一项不满足，就不能结束当前回复。

### 第 4 项失败的真实案例（务必避免）

> **错误示范**：泳道图中创建了 `add_decision('风险评估', ...)`，但只写了一条 `add_linker(n3, n4, label='通过', ...)`，**遗漏了拒绝分支**。
>
> **后果**：图打开后看不到拒绝路径，业务方无法理解失败场景如何流转。
>
> **修复**：补一个终结节点（如 `add_terminator('拒绝并通知', ...)`），加上第二条 `add_linker(n3, rejected_node, label='拒绝', ...)`。两条出线方向**必须使用不同锚点**（典型组合：一条 `from_anchor=2`（左）、另一条 `from_anchor=1`（下）；或一条左、一条右；避免两条出线挤在同一边）。

### 最终回复格式示例

> 我正在使用 `generate-pos-flowchart` 技能处理你的请求。
>
> **图形类型**：普通流程图（用户登录注册流程）。
>
> **节点清单：**
> - n1: 开始 → terminator @ (300, 50)
> - n2: 输入账号密码 → process @ (280, 130, w=200)
> - d1: 前端校验 → decision @ (290, 220)
> - n3: 后端鉴权 → process @ (280, 320)
> - n4: 数据库查询 → storedData @ (280, 410)
> - n5: 颁发 Token → process @ (280, 500)
> - n6: 结束 → terminator @ (300, 590)
>
> **连线：**
> - n1 → n2（默认下→上）
> - n2 → d1（默认下→上）
> - d1 → n3（label="是"，默认下→上）
> - d1 → n2（label="否"，左→上，回到输入步骤）
> - n3 → n4 → n5 → n6（默认下→上）
>
> **生成代码：**
> ```python
> from scripts.generate_pos import PosBuilder
> B = PosBuilder()
> # ... 此处省略具体代码 ...
> data = B.build("用户登录注册流程")
> B.save(data, "/Users/xxx/login_flow.pos")
> ```
>
> **文件路径：**
> /Users/xxx/login_flow.pos
>
> **验证结果：**
> ```
> $ python scripts/generate_pos.py --verify /Users/xxx/login_flow.pos
> ✅ 文件结构合法：meta.version=5.0，nodes=7，linkers=7
> ```
>
> **如何在 ProcessOn 中打开：**
> 打开 ProcessOn → 我的文件 → 导入文件 → 选择 `/Users/xxx/login_flow.pos`，导入后即可二次编辑。

## 快速开始

```bash
python scripts/generate_pos.py
```

或在代码中引用：

```python
from scripts.generate_pos import PosBuilder

builder = PosBuilder()
# 添加节点和连线...
data = builder.build("我的流程图")
builder.save(data, "output.pos")
```

### 普通流程图示例

```python
B = PosBuilder()
n1 = B.add_terminator("开始", 300, 50)
n2 = B.add_process("处理步骤", 280, 130, w=200)
d1 = B.add_decision("判断条件", 290, 220)
B.add_linker(n1, n2)
B.add_linker(n2, d1)
data = B.build("我的流程图")
B.save(data, "output.pos")
```

### 泳道图示例

```python
B = PosBuilder()

# 创建泳道池（包含标题栏）
pool_id = B.add_vertical_pool("业务流程图", x=50, y=50, w=800, h=2000)

# 创建泳道（自动成为 pool 的 children）
lane1 = B.add_vertical_lane("客户", pool_id, x=50, y=90, w=200, h=1960)
lane2 = B.add_vertical_lane("客户经理", pool_id, x=250, y=90, w=200, h=1960)
lane3 = B.add_vertical_lane("审批人", pool_id, x=450, y=90, w=200, h=1960)

# 可选：用 add_round_rectangle 给每条泳道列铺底色（zindex 调到 -2 沉到最底层，
# 不遮挡节点和泳道线；宽度比泳道窄 2px 避免遮挡分隔线）
bg1 = B.add_round_rectangle("", 52, 121, 196, 1928, fill_color="240,247,255")
bg2 = B.add_round_rectangle("", 252, 121, 196, 1928, fill_color="245,255,245")
bg3 = B.add_round_rectangle("", 452, 121, 196, 1928, fill_color="255,250,240")
for bg in [bg1, bg2, bg3]:
    B.elements[bg]["props"]["zindex"] = -2

# 可选：添加水平分隔行（阶段分隔）
sep1 = B.add_horizontal_separator("贷前阶段", pool_id, x=50, y=90, w=800, h=600)
sep2 = B.add_horizontal_separator("贷后阶段", pool_id, x=50, y=690, w=800, h=600)

# 在泳道内添加节点（container 指向 pool_id）
# 流程节点也支持 fill_color / font_color 高亮关键步骤（如开始用绿色、决策用黄色、拒绝用红色）
n1 = B.add_start("申请", 100, 150, container=pool_id,
                 fill_color="149,218,105", font_color="255,255,255")
n2 = B.add_process("审核", 300, 300, container=pool_id,
                   fill_color="116,186,245", font_color="255,255,255")
B.add_linker(n1, n2)

data = B.build("泳道流程图")
B.save(data, "output.pos")
```

### 系统架构图示例

```python
B = PosBuilder()

# 大标题
B.add_text("系统架构图", 400, 50, w=300, h=44, font_size=35)

# 一级模块（大色块背景）
B.add_round_rectangle("", 100, 120, 400, 200,
    fill_color="116,186,245")  # 浅蓝背景
# 模块标题条
B.add_round_rectangle("用户管理", 100, 120, 400, 25,
    fill_color="41,143,227", font_color="255,255,255")  # 深蓝标题
# 子功能项
B.add_round_rectangle("角色管理", 110, 155, 120, 36)
B.add_round_rectangle("权限管理", 240, 155, 120, 36)

data = B.build("系统架构图")
B.save(data, "output.pos")
```

## 命令行调用参考

```bash
# 直接运行内置示例（生成默认 .pos 文件，用于自检脚本是否可用）
python scripts/generate_pos.py

# 验证 .pos 文件结构是否符合 ProcessOn schema 5.0
python scripts/generate_pos.py --verify output.pos
```

## 示例优化 Prompt

> **用户意图**：帮我画一个登录流程。
> **优化后**：请生成一张普通流程图（非泳道），描述用户登录注册流程。包含节点：开始（terminator）→ 输入账号密码（process）→ 前端校验（decision，是 / 否）→ 后端鉴权（process）→ 数据库查询（storedData）→ Token 发放（process）→ 结束（terminator）。要求：决策两条分支分别标注"是 / 否"，节点 X 坐标对齐使主干为垂直直线，错误分支放在右侧；最终输出 `.pos` 文件并通过 `--verify` 校验。

> **User intent**: Draw a user login flow.
> **Optimized prompt**: Generate a standard flowchart (not swimlane) for the user login flow. Nodes: Start (terminator) → Input credentials (process) → Frontend validation (decision, yes / no) → Backend auth (process) → DB lookup (storedData) → Issue token (process) → End (terminator). Requirements: label both decision branches with "yes / no", align main-trunk nodes on the same X axis so the happy path is a straight vertical line, place the failure branch on the right, and finally produce a `.pos` file that passes `--verify`.

## 详细参考

技术细节（节点类型、泳道元素、连线锚点、折线拐角、颜色填充、schema 关键规则）全部沉淀在以下文件中，**调用 `PosBuilder` 之前必须先翻阅**：

- 完整 .pos 格式规范、节点表、锚点规则、颜色表：[pos-format-spec.md](pos-format-spec.md)
- Python 生成脚本（含全部 `add_*` 方法签名）：[scripts/generate_pos.py](scripts/generate_pos.py)
