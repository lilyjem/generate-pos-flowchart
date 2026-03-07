---
name: generate-pos-flowchart
description: 生成ProcessOn .pos格式的流程图和架构图文件，支持泳道图（verticalPool/verticalLane）、普通流程图、系统架构图、各类节点（process/decision/terminator/start/predefinedProcess/directData/storedData/roundRectangle/text）、颜色填充和连线（linker）。当用户需要生成ProcessOn流程图、泳道图、架构图、.pos文件、导入ProcessOn时使用此skill。
---

# 生成 ProcessOn .pos 流程图

## 快速开始

使用 `scripts/generate_pos.py` 中的 `PosBuilder` 类生成 `.pos` 文件。

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

## 工作流程

```
Task Progress:
- [ ] 1. 确认流程图类型（普通流程图 / 泳道图）
- [ ] 2. 确认节点列表和连接关系
- [ ] 3. 使用 PosBuilder 构建图表
- [ ] 4. 生成 .pos 文件
- [ ] 5. 验证文件结构
```

### 步骤1：确认图表类型

**普通流程图？** → 直接添加节点和连线
**泳道图？** → 先创建 verticalPool + verticalLane，再添加节点
**系统架构图？** → 使用 roundRectangle + text 组合，通过颜色和层级表达结构

### 步骤2：构建图表

**普通流程图示例：**

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

**泳道图示例：**

```python
B = PosBuilder()

# 创建泳道池（包含标题栏）
pool_id = B.add_vertical_pool("业务流程图", x=50, y=50, w=800, h=2000)

# 创建泳道（自动成为pool的children）
lane1 = B.add_vertical_lane("客户", pool_id, x=50, y=90, w=200, h=1960)
lane2 = B.add_vertical_lane("客户经理", pool_id, x=250, y=90, w=200, h=1960)
lane3 = B.add_vertical_lane("审批人", pool_id, x=450, y=90, w=200, h=1960)

# 可选：添加水平分隔行（阶段分隔）
sep1 = B.add_horizontal_separator("贷前阶段", pool_id, x=50, y=90, w=800, h=600)
sep2 = B.add_horizontal_separator("贷后阶段", pool_id, x=50, y=690, w=800, h=600)

# 在泳道内添加节点（container 指向 pool_id）
n1 = B.add_start("申请", 100, 150, container=pool_id)
n2 = B.add_process("审核", 300, 300, container=pool_id)
B.add_linker(n1, n2)

data = B.build("泳道流程图")
B.save(data, "output.pos")
```

**系统架构图示例：**

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

### 步骤3：验证

```bash
python scripts/generate_pos.py --verify output.pos
```

## 可用节点类型

### 流程图节点

| 方法 | 形状 | name值 | 用途 |
|------|------|--------|------|
| `add_process()` | 矩形 | process | 普通处理步骤 |
| `add_decision()` | 菱形 | decision | 判断/分支 |
| `add_terminator()` | 圆角矩形 | terminator | 开始/结束（胶囊形） |
| `add_start()` | 圆角矩形 | start | 开始/结束（同terminator） |
| `add_predefined_process()` | 双边线矩形 | predefinedProcess | 子流程/预定义流程 |
| `add_direct_data()` | 右侧弧形 | directData | 策略/数据源 |
| `add_stored_data()` | 左侧弧形 | storedData | 存储数据 |

### 通用节点（架构图/自由布局）

| 方法 | 形状 | name值 | 用途 |
|------|------|--------|------|
| `add_round_rectangle()` | 圆角矩形 | roundRectangle | 模块/功能块（支持颜色填充） |
| `add_text()` | 纯文本 | text | 标题/标签（无边框无填充） |

## 可用泳道元素

| 方法 | name值 | 用途 |
|------|--------|------|
| `add_vertical_pool()` | verticalPool | 泳道池（顶层容器） |
| `add_vertical_lane()` | verticalLane | 垂直泳道 |
| `add_horizontal_separator()` | horizontalSeparator | 水平阶段分隔 |

## 连线

```python
# 基本连线（从下锚点到上锚点，适用于正下方的目标）
B.add_linker(from_id, to_id)

# 带文本标签
B.add_linker(from_id, to_id, label="是")

# 指定锚点方向：0=上, 1=下, 2=左, 3=右
B.add_linker(from_id, to_id, label="否", from_anchor=3, to_anchor=2)

# 双向箭头
B.add_linker(from_id, to_id, begin_arrow="solidArrow")

# 无箭头连线
B.add_linker(from_id, to_id, end_arrow="none")
```

### 锚点选择规则（重要）

根据**目标节点相对于源节点的实际位置**选择锚点，确保连线为美观的正交折线：

**源锚点**：朝目标方向出发
**目标锚点**：连线从哪个方向"进入"目标

| 目标相对位置 | 源锚点 | 目标锚点 | 折线形状 |
|-------------|--------|----------|----------|
| 正下方 | 下(1) | 上(0) | 垂直直线 |
| 正右方（同行） | 右(3) | 左(2) | 水平直线 |
| 正左方（同行） | 左(2) | 右(3) | 水平直线 |
| 正上方 | 上(0) | 下(1) | 垂直直线 |
| **右下方** | 右(3) | **上(0)** | 先水平再垂直下（L形折线） |
| **左下方** | 左(2) | **上(0)** | 先水平再垂直下（L形折线） |
| **右上方** | 右(3) | **下(1)** | 先水平再垂直上（L形折线） |
| **左上方** | 左(2) | **下(1)** | 先水平再垂直上（L形折线） |

**关键原则**：
- 目标不在源的正水平方向时，目标锚点用**垂直方向**（上/下），不要用左/右，否则会产生斜线
- 同行节点（Y坐标相同或接近）使用水平连线：右(3)→左(2) 或 左(2)→右(3)
- 同列节点（X坐标相同或接近）使用垂直连线：下(1)→上(0) 或 上(0)→下(1)
- 节点尽量对齐（X或Y坐标一致），减少不必要的折线

### 折线拐角点（自动计算）

`add_linker` 会根据源/目标锚点的方向组合，自动计算正交折线的拐角点（points）：

| 锚点组合 | 折线路径 | 拐角点 |
|----------|----------|--------|
| 水平→垂直（如右→上） | 先水平走，再垂直 | `(tx, fy)` — 1个拐角 |
| 垂直→水平（如下→左） | 先垂直走，再水平 | `(fx, ty)` — 1个拐角 |
| 水平→水平（如右→左） | 水平→垂直→水平 | 2个拐角，中间垂直段 |
| 垂直→垂直（如下→上） | 垂直→水平→垂直 | 2个拐角，中间水平段 |

## 颜色填充

```python
# roundRectangle 支持颜色填充
B.add_round_rectangle("模块名", x, y, w, h,
    fill_color="41,143,227",      # RGB字符串，如 "R,G,B"
    font_color="255,255,255")     # 白色文字

# 无填充（默认）
B.add_round_rectangle("子项", x, y, w, h)  # 无色背景，黑色文字
```

常用颜色参考：

| 颜色 | RGB值 | 用途 |
|------|-------|------|
| 深蓝 | `41,143,227` | 标题条 |
| 浅蓝 | `116,186,245` | 模块背景 |
| 藏蓝 | `33,113,180` | 侧边栏标签 |
| 绿色 | `149,218,105` | 客户管理类 |
| 橙色 | `241,152,34` | 角色管理类 |
| 青色 | `44,198,222` | 消息/日志类 |
| 深青 | `35,172,193` | 审计/模板类 |
| 红色 | `236,114,112` | 线索管理类 |
| 粉色 | `232,85,164` | 首页/贷款类 |
| 黄色 | `224,196,49` | 授权类 |
| 深绿 | `17,130,107` | 系统设置类 |
| 紫色 | `100,84,133` | 主系统 |

## 关键规则

1. **文件格式**：单行JSON，`separators=(',', ':')`，`ensure_ascii=False`
2. **meta.type** 必须为 `"ProcessOn Schema File"`，**meta.version** 必须为 `"5.0"`
3. **泳道层级**：verticalPool → children 包含 verticalLane ID 列表；verticalLane.parent = pool.id
4. **节点放置在泳道内**：设置 `container = pool_id`（指向 verticalPool 的 ID）
5. **fontStyle.size**：节点默认 `16`，泳道池标题 `20`，水平分隔 `20`，架构图大标题 `35`
6. **zindex**：泳道元素用 `-1`，节点从 `1` 递增
7. **锚点角度**：上=`1.5708`(π/2)，下=`4.7124`(3π/2)，左=`0`，右=`3.1416`(π)
8. **roundRectangle**：`lineStyle.lineWidth=0`（无边框），`resizeDir=["tl","tr","br","bl"]`（仅四角）
9. **text**：路径中 `lineWidth=0` + `fillStyle.type="none"`，`textBlock.position` 用 `{"w":"w","h":"h","x":0,"y":0}`
10. **连线锚点**：根据目标相对位置选择锚点方向，正方向用对应锚点，斜方向时目标锚点用垂直方向（上/下），避免产生斜线
11. **折线拐角**：`add_linker` 自动根据锚点组合计算正交折线拐角点（points），水平→垂直组合产生1个拐角，同方向组合产生2个拐角
12. **节点对齐**：同行水平连线的节点Y坐标应一致，同列垂直连线的节点X坐标应一致（如开始节点与后续节点居中对齐），减少不必要折线

## 详细参考

- 完整 .pos 格式规范：[pos-format-spec.md](pos-format-spec.md)
- Python 生成脚本：[scripts/generate_pos.py](scripts/generate_pos.py)
