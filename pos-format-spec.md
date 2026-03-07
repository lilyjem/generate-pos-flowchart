# ProcessOn .pos 文件格式规范

基于 ProcessOn 导出的 .pos 文件逆向分析，版本 5.0。

## 顶层结构

```json
{
  "diagram": {
    "elements": {
      "editorVersion": "V1",
      "comments": [],
      "plugins": {},
      "elements": { /* 所有图形元素，key=元素ID */ },
      "page": {
        "padding": 20,
        "backgroundColor": "transparent",
        "orientation": "portrait",
        "gridSize": 15,
        "width": 1666,
        "showGrid": true,
        "lineJumps": false,
        "height": 822
      },
      "version": 0,
      "aiContainers": {}
    }
  },
  "meta": {
    "exportTime": "2026-03-07 14:03:40",
    "member": "",
    "diagramInfo": {
      "creator": "",
      "created": "2026-03-07 12:28:36",
      "modified": "2026-03-07 12:28:36",
      "title": "流程图标题",
      "category": "flow"
    },
    "id": "24位十六进制字符串",
    "type": "ProcessOn Schema File",
    "version": "5.0"
  }
}
```

## 元素ID格式

10个随机字母 + 6个随机数字，如 `nyoebYlGuS416557`。

## 形状节点通用结构

```json
{
  "container": "泳道池ID（可选，节点在泳道内时设置）",
  "parent": "父元素ID（泳道元素使用）",
  "link": "",
  "shapeStyle": {"alpha": 1},
  "textBlock": [{
    "position": {"w": "w-20", "x": 10, "h": "h", "y": 0},
    "text": "节点文本"
  }],
  "anchors": [
    {"x": "w/2", "y": "0"},
    {"x": "w/2", "y": "h"},
    {"x": "0", "y": "h/2"},
    {"x": "w", "y": "h/2"}
  ],
  "title": "形状中文名",
  "fontStyle": {"size": 16},
  "dataAttributes": [],
  "props": {
    "zindex": 1,
    "w": 200, "x": 100, "h": 50, "y": 100,
    "angle": 0
  },
  "path": [/* 形状路径定义 */],
  "lineStyle": {"lineWidth": 1.5},
  "children": [],
  "resizeDir": ["tl","tr","br","bl","l","t","r","b"],
  "name": "process",
  "fillStyle": {},
  "theme": {},
  "id": "元素ID",
  "attribute": {
    "container": false,
    "rotatable": true,
    "visible": true,
    "fixedLink": false,
    "collapsable": false,
    "collapsed": false,
    "linkable": true,
    "markerOffset": 5
  },
  "category": "flow",
  "locked": false,
  "group": ""
}
```

## 各形状 path 定义

### process（矩形）
```json
[{"actions": [
  {"x": "0", "action": "move", "y": "0"},
  {"x": "w", "action": "line", "y": "0"},
  {"x": "w", "action": "line", "y": "h"},
  {"x": "0", "action": "line", "y": "h"},
  {"action": "close"}
]}]
```

### decision（菱形）
```json
[{"actions": [
  {"x": "0", "action": "move", "y": "h/2"},
  {"x": "w/2", "action": "line", "y": "0"},
  {"x": "w", "action": "line", "y": "h/2"},
  {"x": "w/2", "action": "line", "y": "h"},
  {"x": "0", "action": "line", "y": "h/2"},
  {"action": "close"}
]}]
```

### terminator / start（圆角胶囊形）
```json
[{"actions": [
  {"x": "Math.min(w,h)/3", "action": "move", "y": "0"},
  {"x": "w-Math.min(w,h)/3", "action": "line", "y": "0"},
  {"y1": "0", "x": "w-Math.min(w,h)/3", "action": "curve",
   "x1": "w+Math.min(w,h)/3/3", "y2": "h", "y": "h", "x2": "w+Math.min(w,h)/3/3"},
  {"x": "Math.min(w,h)/3", "action": "line", "y": "h"},
  {"y1": "h", "x": "Math.min(w,h)/3", "action": "curve",
   "x1": "-Math.min(w,h)/3/3", "y2": "0", "y": "0", "x2": "-Math.min(w,h)/3/3"},
  {"action": "close"}
]}]
```

### predefinedProcess（双边线矩形/子流程）
```json
[{"actions": [
  {"x": "0", "action": "move", "y": "0"},
  {"x": "w", "action": "line", "y": "0"},
  {"x": "w", "action": "line", "y": "h"},
  {"x": "0", "action": "line", "y": "h"},
  {"x": "0", "action": "line", "y": "0"},
  {"action": "close"},
  {"x": "Math.min(w/6,20)", "action": "move", "y": "0"},
  {"x": "Math.min(w/6,20)", "action": "line", "y": "h"},
  {"x": "w- Math.min(w/6,20)", "action": "move", "y": "0"},
  {"x": "w- Math.min(w/6,20)", "action": "line", "y": "h"}
]}]
```
textBlock.position: `{"w": "w-Math.min(w/6,20)*2", "x": "Math.min(w/6,20)", "h": "h", "y": "0"}`

### directData（右侧弧形/策略数据）
```json
[{"actions": [
  {"x": "Math.min(w,h)/6", "action": "move", "y": "0"},
  {"x": "w-Math.min(w,h)/6", "action": "line", "y": "0"},
  {"y1": "0", "x": "w-Math.min(w,h)/6", "action": "curve",
   "x1": "w+Math.min(w,h)/22", "y2": "h", "y": "h", "x2": "w+Math.min(w,h)/22"},
  {"x": "Math.min(w,h)/6", "action": "line", "y": "h"},
  {"y1": "h", "x": "Math.min(w,h)/6", "action": "curve",
   "x1": "-Math.min(w,h)/22", "y2": "0", "y": "0", "x2": "-Math.min(w,h)/22"},
  {"action": "close"}
]}]
```
textBlock.position: `{"w": "w-Math.min(w,h)/6*2", "x": "Math.min(w,h)/6", "h": "h", "y": "0"}`
fontStyle: `{"size": 16, "textAlign": "center", "vAlign": "middle"}`

### storedData（左侧弧形/存储数据）
```json
[{"actions": [
  {"x": "w/6", "action": "move", "y": "0"},
  {"x": "w", "action": "line", "y": "0"},
  {"y1": "0", "x": "w", "action": "curve",
   "x1": "w-w/6", "y2": "h", "y": "h", "x2": "w-w/6"},
  {"x": "w/6", "action": "line", "y": "h"},
  {"y1": "h", "x": "w/7", "action": "curve",
   "x1": "-w/17", "y2": "0", "y": "0", "x2": "-w/17"},
  {"action": "close"}
]}]
```
anchors: `[{"x":"w*0.5","y":"0"},{"x":"w-Math.min(w/8,h/8)","y":"h*0.5"},{"x":"w*0.5","y":"h"},{"x":"0","y":"h*0.5"}]`

### roundRectangle（圆角矩形/功能模块）

用于系统架构图中的模块块，支持颜色填充。使用 `quadraticCurve` 绘制4px圆角。

```json
{
  "name": "roundRectangle",
  "category": "basic",
  "title": "圆角矩形",
  "textBlock": [{"position": {"w": "w-20", "h": "h", "x": 10, "y": 0}, "text": "模块名"}],
  "fontStyle": {"color": "255,255,255", "bold": true},
  "fillStyle": {"color": "41,143,227", "type": "solid"},
  "lineStyle": {"lineWidth": 0},
  "resizeDir": ["tl", "tr", "br", "bl"],
  "attribute": {
    "container": false, "rotatable": true, "visible": true,
    "collapsable": false, "collapsed": false, "linkable": true, "markerOffset": 5
  }
}
```

path:
```json
[{"actions": [
  {"x": "0", "action": "move", "y": "4"},
  {"y1": "0", "x": "4", "action": "quadraticCurve", "y": "0", "x1": "0"},
  {"x": "w-4", "action": "line", "y": "0"},
  {"y1": "0", "x": "w", "action": "quadraticCurve", "y": "4", "x1": "w"},
  {"x": "w", "action": "line", "y": "h-4"},
  {"y1": "h", "x": "w-4", "action": "quadraticCurve", "y": "h", "x1": "w"},
  {"x": "4", "action": "line", "y": "h"},
  {"y1": "h", "x": "0", "action": "quadraticCurve", "y": "h-4", "x1": "0"},
  {"action": "close"}
]}]
```

**关键特征**：
- `lineStyle.lineWidth = 0`（无边框）
- `fillStyle.type = "solid"`，`fillStyle.color = "R,G,B"` 格式
- `fontStyle.color = "255,255,255"` 表示白色文字（用于深色背景）
- 无填充时 `fillStyle = {}`，文字默认黑色
- `attribute` 中无 `fixedLink` 字段

### text（纯文本标签）

用于标题、注释等无边框纯文本。

```json
{
  "name": "text",
  "category": "basic",
  "title": "文本",
  "textBlock": [{"position": {"w": "w", "h": "h", "x": 0, "y": 0}, "text": "标题文字"}],
  "fontStyle": {"size": 35, "bold": true},
  "fillStyle": {},
  "lineStyle": {},
  "resizeDir": ["tl", "tr", "br", "bl"],
  "attribute": {
    "container": false, "rotatable": true, "visible": true,
    "collapsable": false, "collapsed": false, "linkable": true, "markerOffset": 5
  }
}
```

path:
```json
[{"lineStyle": {"lineWidth": 0}, "fillStyle": {"type": "none"},
  "actions": [
    {"x": "0", "action": "move", "y": "0"},
    {"x": "w", "action": "line", "y": "0"},
    {"x": "w", "action": "line", "y": "h"},
    {"x": "0", "action": "line", "y": "h"},
    {"action": "close"}
  ]}]
```

**关键特征**：
- path 内部 `lineWidth: 0` + `fillStyle.type: "none"`（无边框无背景）
- `textBlock.position` 使用 `{"w":"w","h":"h","x":0,"y":0}`（全区域文本）
- 常用于架构图大标题

## 颜色填充（fillStyle）

### 实心填充
```json
{"color": "41,143,227", "type": "solid"}
```

### 无填充（默认）
```json
{}
```

### fontStyle 颜色
```json
{"color": "255,255,255", "bold": true}
```
`fontStyle.color` 使用 `"R,G,B"` 格式字符串，白色文字用于深色背景。

## 泳道元素

### verticalPool（泳道池/顶层容器）

```json
{
  "parent": "",
  "textBlock": [{"position": {"w": "w-20", "x": 10, "h": "height[0]", "y": 0}, "text": "标题"}],
  "anchors": [],
  "title": "泳池(垂直)",
  "fontStyle": {"size": 20},
  "props": {"zindex": -1, "w": 1800, "x": 59, "h": 3395, "y": 50, "angle": 0, "height": [40]},
  "path": [
    {"lineStyle": {"lineStyle": "solid"}, "fillStyle": {"type": "none"},
     "actions": [
       {"x": "0", "action": "move", "y": "0"},
       {"x": "w", "action": "line", "y": "0"},
       {"x": "w", "action": "line", "y": "h"},
       {"x": "0", "action": "line", "y": "h"},
       {"action": "close"}
     ]},
    {"lineStyle": {"lineStyle": "solid"},
     "actions": [
       {"x": 0, "action": "move", "y": 0},
       {"x": "w", "action": "line", "y": 0},
       {"x": "w", "action": "line", "y": "height[0]"},
       {"x": 0, "action": "line", "y": "height[0]"},
       {"action": "close"}
     ]}
  ],
  "lineStyle": {"lineWidth": 1.5},
  "children": ["lane_id_1", "lane_id_2", "separator_bar_id", "h_sep_id_1"],
  "resizeDir": ["l", "b", "r"],
  "name": "verticalPool",
  "attribute": {"container": true, "rotatable": false, "visible": true,
    "fixedLink": false, "collapsable": false, "collapsed": false,
    "linkable": false, "markerOffset": 5},
  "category": "lane"
}
```

**关键**：`props.height[0]` 控制标题栏高度（默认40），`children` 包含所有 lane/separator 的 ID。

### verticalLane（垂直泳道）

```json
{
  "parent": "pool_id",
  "textBlock": [{"position": {"w": "w-20", "x": 10, "h": "height[0]", "y": 0}, "text": "泳道名"}],
  "anchors": [],
  "title": "泳道(垂直)",
  "fontStyle": {"size": 16},
  "props": {"zindex": -1, "w": 250, "x": 92, "h": 3355, "y": 90, "angle": 0, "height": [30]},
  "path": [
    {"lineStyle": {"lineStyle": "solid"}, "fillStyle": {"type": "none"},
     "actions": [
       {"x": "0", "action": "move", "y": "0"},
       {"x": "w", "action": "line", "y": "0"},
       {"x": "w", "action": "line", "y": "h"},
       {"x": "0", "action": "line", "y": "h"},
       {"action": "close"}
     ]},
    {"lineStyle": {"lineStyle": "solid"},
     "actions": [
       {"x": 0, "action": "move", "y": 0},
       {"x": "w", "action": "line", "y": 0},
       {"x": "w", "action": "line", "y": "height[0]"},
       {"x": 0, "action": "line", "y": "height[0]"},
       {"action": "close"}
     ]}
  ],
  "lineStyle": {},
  "children": [],
  "resizeDir": ["l", "b", "r"],
  "name": "verticalLane",
  "attribute": {"container": true, "rotatable": false, "visible": true,
    "fixedLink": false, "collapsable": false, "collapsed": false,
    "linkable": false, "markerOffset": 5},
  "category": "lane"
}
```

**关键**：`parent` 指向 pool ID，`props.height[0]` 控制泳道标题栏高度（默认30），`y` = pool.y + pool.height[0]（标题栏下方开始）。

### verticalSeparatorBar（垂直分隔条）

泳道池最左侧的分隔条，用于显示水平分隔标签区域。

```json
{
  "parent": "pool_id",
  "textBlock": [],
  "title": "水平分隔条",
  "fontStyle": {},
  "props": {"zindex": 29, "w": 33.6, "x": 59, "h": 3355, "y": 90, "angle": 0, "height": [33.6]},
  "resizeDir": [],
  "name": "verticalSeparatorBar",
  "attribute": {"container": false, "rotatable": false, "visible": false,
    "fixedLink": false, "collapsable": false, "collapsed": false,
    "linkable": false, "markerOffset": 5},
  "category": "lane"
}
```

### horizontalSeparator（水平阶段分隔）

```json
{
  "parent": "pool_id",
  "textBlock": [{"position": {"w": "height[0]", "x": 0, "h": "h-10", "y": 5}, "text": "阶段名称"}],
  "title": "分隔符(水平)\u003cbr\u003e需拖动到泳池泳道上",
  "fontStyle": {"orientation": "horizontal", "size": 20, "textAlign": "center", "vAlign": "middle"},
  "props": {"zindex": 31, "w": 1800, "x": 59, "h": 673, "y": 90, "angle": 0, "height": [33.6]},
  "path": [
    {"lineStyle": {"lineStyle": "solid"}, "fillStyle": {"type": "none"},
     "actions": [{"x": 0, "action": "move", "y": "h"}, {"x": "w", "action": "line", "y": "h"}]},
    {"actions": [
       {"x": 0, "action": "move", "y": 0},
       {"x": "height[0]", "action": "line", "y": 0},
       {"x": "height[0]", "action": "line", "y": "h"},
       {"x": 0, "action": "line", "y": "h"},
       {"action": "close"}
     ]}
  ],
  "resizeDir": ["b"],
  "name": "horizontalSeparator",
  "attribute": {"container": false, "rotatable": false, "visible": true,
    "fixedLink": false, "collapsable": false, "collapsed": false,
    "linkable": false, "markerOffset": 5},
  "category": "lane"
}
```

## 连线（linker）

```json
{
  "textBlock": [{"location": 0.5, "text": "标签"}],
  "fontStyle": {"size": 16, "bold": true},
  "points": [{"x": 300, "y": 400}],
  "dataAttributes": [],
  "props": {"zindex": 27},
  "linkerType": "broken",
  "lineStyle": {
    "lineWidth": 1.5,
    "beginArrowStyle": "none",
    "endArrowStyle": "solidArrow"
  },
  "lineType": "solid",
  "name": "linker",
  "from": {"x": 300, "y": 350, "angle": 4.71238898038469, "id": "源节点ID"},
  "to": {"x": 300, "y": 450, "angle": 1.5707963267948966, "id": "目标节点ID"},
  "text": "标签",
  "locked": false,
  "group": ""
}
```

### 锚点角度对照

| 方向 | 角度值 | 说明 |
|------|--------|------|
| 左 | 0 | 0 rad |
| 上 | 1.5707963267948966 | π/2 rad |
| 右 | 3.141592653589793 | π rad |
| 下 | 4.71238898038469 | 3π/2 rad |

### 连线文本

- `textBlock[0].location`：文本在连线上的位置比例（0~1）
- `textPos`：可选，精确文本位置 `{"t": 偏移量, "x": X坐标, "y": Y坐标}`
- `fontStyle`：带文本的连线通常设置 `{"size": 16, "bold": true}`

### 箭头样式

| 值 | 说明 |
|----|------|
| `"none"` | 无箭头 |
| `"solidArrow"` | 实心三角箭头 |

## 布局计算

### 泳道布局

```
pool.x = 起始X
pool.y = 起始Y
pool.height[0] = 标题栏高度（40）

separatorBar.x = pool.x
separatorBar.y = pool.y + pool.height[0]
separatorBar.w = pool.height[0] 的值（约33.6）
separatorBar.h = pool.h - pool.height[0]

lane[i].x = pool.x + separatorBar.w + i * lane_width
lane[i].y = pool.y + pool.height[0]
lane[i].h = pool.h - pool.height[0]
lane[i].height[0] = 泳道标题栏高度（30）
```

### 节点居中于泳道

```
node.x = lane.x + (lane.w - node.w) / 2
```

### 连线坐标计算

```python
# 锚点0=上, 1=下, 2=左, 3=右
def calc_anchor(props, anchor_idx):
    x, y, w, h = props["x"], props["y"], props["w"], props["h"]
    if anchor_idx == 0: return x + w/2, y        # 上
    if anchor_idx == 1: return x + w/2, y + h     # 下
    if anchor_idx == 2: return x, y + h/2          # 左
    if anchor_idx == 3: return x + w, y + h/2      # 右
```
