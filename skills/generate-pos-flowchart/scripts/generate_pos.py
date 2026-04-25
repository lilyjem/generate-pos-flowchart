# -*- coding: utf-8 -*-
"""
ProcessOn .pos 文件生成器
支持泳道图、普通流程图和系统架构图

使用方法:
  生成示例: python generate_pos.py
  验证文件: python generate_pos.py --verify <文件路径>
"""

import json
import uuid
import random
import sys
import os
from datetime import datetime


def gen_id():
    """生成ProcessOn风格的随机ID：10个字母 + 6个数字"""
    chars = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ'
    nums = '0123456789'
    return ''.join(random.choice(chars) for _ in range(10)) + ''.join(random.choice(nums) for _ in range(6))


# ==================== 锚点角度常量 ====================
ANCHOR_ANGLES = {
    0: 1.5707963267948966,   # 上 (π/2)
    1: 4.71238898038469,     # 下 (3π/2)
    2: 0,                    # 左 (0)
    3: 3.141592653589793     # 右 (π)
}

# ==================== 形状路径模板 ====================
PATH_PROCESS = [{"actions": [
    {"x": "0", "action": "move", "y": "0"},
    {"x": "w", "action": "line", "y": "0"},
    {"x": "w", "action": "line", "y": "h"},
    {"x": "0", "action": "line", "y": "h"},
    {"action": "close"}
]}]

PATH_DECISION = [{"actions": [
    {"x": "0", "action": "move", "y": "h/2"},
    {"x": "w/2", "action": "line", "y": "0"},
    {"x": "w", "action": "line", "y": "h/2"},
    {"x": "w/2", "action": "line", "y": "h"},
    {"x": "0", "action": "line", "y": "h/2"},
    {"action": "close"}
]}]

PATH_TERMINATOR = [{"actions": [
    {"x": "Math.min(w,h)/3", "action": "move", "y": "0"},
    {"x": "w-Math.min(w,h)/3", "action": "line", "y": "0"},
    {"y1": "0", "x": "w-Math.min(w,h)/3", "action": "curve",
     "x1": "w+Math.min(w,h)/3/3", "y2": "h", "y": "h", "x2": "w+Math.min(w,h)/3/3"},
    {"x": "Math.min(w,h)/3", "action": "line", "y": "h"},
    {"y1": "h", "x": "Math.min(w,h)/3", "action": "curve",
     "x1": "-Math.min(w,h)/3/3", "y2": "0", "y": "0", "x2": "-Math.min(w,h)/3/3"},
    {"action": "close"}
]}]

PATH_PREDEFINED_PROCESS = [{"actions": [
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

PATH_DIRECT_DATA = [{"actions": [
    {"x": "Math.min(w,h)/6", "action": "move", "y": "0"},
    {"x": "w-Math.min(w,h)/6", "action": "line", "y": "0"},
    {"y1": "0", "x": "w-Math.min(w,h)/6", "action": "curve",
     "x1": "w+Math.min(w,h)/22", "y2": "h", "y": "h", "x2": "w+Math.min(w,h)/22"},
    {"x": "Math.min(w,h)/6", "action": "line", "y": "h"},
    {"y1": "h", "x": "Math.min(w,h)/6", "action": "curve",
     "x1": "-Math.min(w,h)/22", "y2": "0", "y": "0", "x2": "-Math.min(w,h)/22"},
    {"action": "close"}
]}]

PATH_STORED_DATA = [{"actions": [
    {"x": "w/6", "action": "move", "y": "0"},
    {"x": "w", "action": "line", "y": "0"},
    {"y1": "0", "x": "w", "action": "curve",
     "x1": "w-w/6", "y2": "h", "y": "h", "x2": "w-w/6"},
    {"x": "w/6", "action": "line", "y": "h"},
    {"y1": "h", "x": "w/7", "action": "curve",
     "x1": "-w/17", "y2": "0", "y": "0", "x2": "-w/17"},
    {"action": "close"}
]}]

# 圆角矩形路径（4px圆角，使用quadraticCurve）
PATH_ROUND_RECTANGLE = [{"actions": [
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

# 纯文本路径（无边框无背景）
PATH_TEXT = [{"lineStyle": {"lineWidth": 0}, "fillStyle": {"type": "none"},
    "actions": [
        {"x": "0", "action": "move", "y": "0"},
        {"x": "w", "action": "line", "y": "0"},
        {"x": "w", "action": "line", "y": "h"},
        {"x": "0", "action": "line", "y": "h"},
        {"action": "close"}
    ]}]

# 泳道池路径（外框 + 标题栏）
PATH_VERTICAL_POOL = [
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
]

# 泳道路径（外框 + 标题栏）
PATH_VERTICAL_LANE = [
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
]

# 垂直分隔条路径
PATH_SEPARATOR_BAR = [
    {"lineStyle": {"lineStyle": "solid"},
     "actions": [
         {"x": "0", "action": "move", "y": "0"},
         {"x": "w", "action": "line", "y": "0"},
         {"x": "w", "action": "line", "y": "h"},
         {"x": "0", "action": "line", "y": "h"},
         {"action": "close"}
     ]}
]

# 水平分隔路径
PATH_HORIZONTAL_SEPARATOR = [
    {"lineStyle": {"lineStyle": "solid"}, "fillStyle": {"type": "none"},
     "actions": [
         {"x": 0, "action": "move", "y": "h"},
         {"x": "w", "action": "line", "y": "h"}
     ]},
    {"actions": [
         {"x": 0, "action": "move", "y": 0},
         {"x": "height[0]", "action": "line", "y": 0},
         {"x": "height[0]", "action": "line", "y": "h"},
         {"x": 0, "action": "line", "y": "h"},
         {"action": "close"}
     ]}
]

# 标准四方向锚点
ANCHORS_4DIR = [
    {"x": "w/2", "y": "0"},
    {"x": "w/2", "y": "h"},
    {"x": "0", "y": "h/2"},
    {"x": "w", "y": "h/2"}
]

# storedData 特殊锚点
ANCHORS_STORED_DATA = [
    {"x": "w*0.5", "y": "0"},
    {"x": "w-Math.min(w/8,h/8)", "y": "h*0.5"},
    {"x": "w*0.5", "y": "h"},
    {"x": "0", "y": "h*0.5"}
]

# 可连接节点的通用属性（流程图节点）
ATTR_LINKABLE = {
    "container": False, "rotatable": True, "visible": True,
    "fixedLink": False, "collapsable": False, "collapsed": False,
    "linkable": True, "markerOffset": 5
}

# 基础图形属性（roundRectangle/text，无fixedLink字段）
ATTR_BASIC = {
    "container": False, "rotatable": True, "visible": True,
    "collapsable": False, "collapsed": False,
    "linkable": True, "markerOffset": 5
}

# 泳道容器属性
ATTR_CONTAINER = {
    "container": True, "rotatable": False, "visible": True,
    "fixedLink": False, "collapsable": False, "collapsed": False,
    "linkable": False, "markerOffset": 5
}

# 不可连接/不可见元素属性
ATTR_INVISIBLE = {
    "container": False, "rotatable": False, "visible": False,
    "fixedLink": False, "collapsable": False, "collapsed": False,
    "linkable": False, "markerOffset": 5
}

# 水平分隔属性
ATTR_SEPARATOR = {
    "container": False, "rotatable": False, "visible": True,
    "fixedLink": False, "collapsable": False, "collapsed": False,
    "linkable": False, "markerOffset": 5
}

RESIZE_ALL = ["tl", "tr", "br", "bl", "l", "t", "r", "b"]
RESIZE_LANE = ["l", "b", "r"]


class PosBuilder:
    """ProcessOn .pos 文件构建器"""

    def __init__(self):
        self.elements = {}
        self._zindex = 0

    def _next_z(self):
        self._zindex += 1
        return self._zindex

    # ==================== 基础形状节点 ====================

    def _add_shape(self, name, text, x, y, w, h, path, anchors, attribute,
                   category="flow", title="", font_style=None, text_position=None,
                   resize_dir=None, container=None, parent=None,
                   fill_color=None, font_color=None):
        """通用形状节点创建方法

        新增参数：
        fill_color: RGB 字符串如 "41,143,227"，None 表示无填充（保持默认透明）
        font_color: RGB 字符串如 "255,255,255"，None 表示默认黑色字体
        """
        nid = gen_id()
        if font_style is None:
            font_style = {"size": 16}
        else:
            font_style = dict(font_style)
        if text_position is None:
            text_position = {"w": "w-20", "x": 10, "h": "h", "y": 0}
        if resize_dir is None:
            resize_dir = RESIZE_ALL

        if font_color:
            font_style["color"] = font_color

        fill_style = {}
        if fill_color:
            fill_style = {"color": fill_color, "type": "solid"}

        el = {
            "link": "",
            "shapeStyle": {"alpha": 1},
            "textBlock": [{"position": text_position, "text": text}],
            "anchors": anchors,
            "title": title,
            "fontStyle": font_style,
            "dataAttributes": [],
            "props": {"zindex": self._next_z(), "w": w, "x": x, "h": h, "y": y, "angle": 0},
            "path": path,
            "lineStyle": {"lineWidth": 1.5},
            "children": [],
            "resizeDir": resize_dir,
            "name": name,
            "fillStyle": fill_style,
            "theme": {},
            "id": nid,
            "attribute": attribute,
            "category": category,
            "locked": False,
            "group": ""
        }

        # 泳道内节点需要 container 字段
        if container:
            el["container"] = container
            el["parent"] = ""
        if parent:
            el["parent"] = parent

        self.elements[nid] = el
        return nid

    def add_process(self, text, x, y, w=200, h=70, container=None,
                    fill_color=None, font_color=None):
        """矩形处理节点。fill_color/font_color 为 RGB 字符串，如 "41,143,227"。"""
        return self._add_shape("process", text, x, y, w, h,
                               PATH_PROCESS, ANCHORS_4DIR, ATTR_LINKABLE,
                               title="流程", container=container,
                               fill_color=fill_color, font_color=font_color)

    def add_decision(self, text, x, y, w=120, h=70, container=None,
                     fill_color=None, font_color=None):
        """菱形判断节点。fill_color/font_color 为 RGB 字符串。"""
        return self._add_shape("decision", text, x, y, w, h,
                               PATH_DECISION, ANCHORS_4DIR, ATTR_LINKABLE,
                               title="判断", container=container,
                               fill_color=fill_color, font_color=font_color)

    def add_terminator(self, text, x, y, w=120, h=50, container=None,
                       fill_color=None, font_color=None):
        """圆角胶囊形（开始/结束）。fill_color/font_color 为 RGB 字符串。"""
        return self._add_shape("terminator", text, x, y, w, h,
                               PATH_TERMINATOR, ANCHORS_4DIR, ATTR_LINKABLE,
                               title="开始/结束", container=container,
                               fill_color=fill_color, font_color=font_color)

    def add_start(self, text, x, y, w=120, h=50, container=None,
                  fill_color=None, font_color=None):
        """开始/结束节点（与terminator形状相同，name不同）。"""
        return self._add_shape("start", text, x, y, w, h,
                               PATH_TERMINATOR, ANCHORS_4DIR, ATTR_LINKABLE,
                               category="basic", title="开始/结束", container=container,
                               fill_color=fill_color, font_color=font_color)

    def add_predefined_process(self, text, x, y, w=160, h=70, container=None,
                               fill_color=None, font_color=None):
        """双边线矩形（子流程/预定义流程）。"""
        return self._add_shape("predefinedProcess", text, x, y, w, h,
                               PATH_PREDEFINED_PROCESS, ANCHORS_4DIR, ATTR_LINKABLE,
                               title="子流程",
                               text_position={"w": "w-Math.min(w/6,20)*2", "x": "Math.min(w/6,20)", "h": "h", "y": "0"},
                               container=container,
                               fill_color=fill_color, font_color=font_color)

    def add_direct_data(self, text, x, y, w=150, h=50, container=None,
                        fill_color=None, font_color=None):
        """右侧弧形（策略/直接数据）。"""
        return self._add_shape("directData", text, x, y, w, h,
                               PATH_DIRECT_DATA, ANCHORS_4DIR, ATTR_LINKABLE,
                               title="直接数据",
                               font_style={"size": 16, "textAlign": "center", "vAlign": "middle"},
                               text_position={"w": "w-Math.min(w,h)/6*2", "x": "Math.min(w,h)/6", "h": "h", "y": "0"},
                               container=container,
                               fill_color=fill_color, font_color=font_color)

    def add_stored_data(self, text, x, y, w=140, h=70, container=None,
                        fill_color=None, font_color=None):
        """左侧弧形（存储数据）。"""
        return self._add_shape("storedData", text, x, y, w, h,
                               PATH_STORED_DATA, ANCHORS_STORED_DATA, ATTR_LINKABLE,
                               title="存储数据", container=container,
                               fill_color=fill_color, font_color=font_color)

    # ==================== 通用图形节点（架构图） ====================

    def add_round_rectangle(self, text, x, y, w=200, h=50,
                            fill_color=None, font_color=None, font_size=None, bold=True):
        """
        圆角矩形（架构图模块/功能块）
        fill_color: RGB字符串如 "41,143,227"，None表示无填充
        font_color: RGB字符串如 "255,255,255"，None表示默认黑色
        """
        nid = gen_id()

        fill_style = {}
        if fill_color:
            fill_style = {"color": fill_color, "type": "solid"}

        font_style = {}
        if font_color:
            font_style["color"] = font_color
        if font_size:
            font_style["size"] = font_size
        if bold:
            font_style["bold"] = True

        self.elements[nid] = {
            "parent": "",
            "link": "",
            "shapeStyle": {"alpha": 1},
            "textBlock": [{"position": {"w": "w-20", "h": "h", "x": 10, "y": 0}, "text": text}],
            "anchors": ANCHORS_4DIR,
            "fontStyle": font_style,
            "title": "圆角矩形",
            "dataAttributes": [],
            "props": {"zindex": self._next_z(), "w": w, "h": h, "x": x, "angle": 0, "y": y},
            "path": PATH_ROUND_RECTANGLE,
            "lineStyle": {"lineWidth": 0},
            "children": [],
            "resizeDir": ["tl", "tr", "br", "bl"],
            "name": "roundRectangle",
            "fillStyle": fill_style,
            "attribute": ATTR_BASIC,
            "id": nid,
            "category": "basic",
            "locked": False
        }
        return nid

    def add_text(self, text, x, y, w=300, h=44, font_size=35, bold=True):
        """纯文本标签（无边框无背景，用于标题/注释）"""
        nid = gen_id()

        font_style = {"size": font_size}
        if bold:
            font_style["bold"] = True

        self.elements[nid] = {
            "parent": "",
            "link": "",
            "shapeStyle": {"alpha": 1},
            "textBlock": [{"position": {"w": "w", "h": "h", "x": 0, "y": 0}, "text": text}],
            "anchors": ANCHORS_4DIR,
            "fontStyle": font_style,
            "title": "文本",
            "dataAttributes": [],
            "props": {"zindex": self._next_z(), "w": w, "h": h, "x": x, "y": y, "angle": 0},
            "path": PATH_TEXT,
            "lineStyle": {},
            "children": [],
            "resizeDir": ["tl", "tr", "br", "bl"],
            "name": "text",
            "fillStyle": {},
            "attribute": ATTR_BASIC,
            "id": nid,
            "category": "basic",
            "locked": False,
            "group": ""
        }
        return nid

    # ==================== 泳道元素 ====================

    def add_vertical_pool(self, text, x=59, y=50, w=1800, h=3000, title_height=40):
        """泳道池（顶层容器）"""
        nid = gen_id()
        self.elements[nid] = {
            "parent": "",
            "link": "",
            "shapeStyle": {"alpha": 1},
            "textBlock": [{"position": {"w": "w-20", "x": 10, "h": "height[0]", "y": 0}, "text": text}],
            "anchors": [],
            "title": "泳池(垂直)",
            "fontStyle": {"size": 20},
            "dataAttributes": [],
            "props": {"zindex": -1, "w": w, "x": x, "h": h, "y": y, "angle": 0, "height": [title_height]},
            "path": PATH_VERTICAL_POOL,
            "lineStyle": {"lineWidth": 1.5},
            "children": [],
            "resizeDir": RESIZE_LANE,
            "name": "verticalPool",
            "fillStyle": {},
            "theme": {},
            "id": nid,
            "attribute": ATTR_CONTAINER,
            "category": "lane",
            "locked": False,
            "group": ""
        }
        return nid

    def add_vertical_lane(self, text, pool_id, x, y, w=250, h=3000, title_height=30):
        """垂直泳道（属于某个pool）"""
        nid = gen_id()
        self.elements[nid] = {
            "parent": pool_id,
            "link": "",
            "shapeStyle": {"alpha": 1},
            "textBlock": [{"position": {"w": "w-20", "x": 10, "h": "height[0]", "y": 0}, "text": text}],
            "anchors": [],
            "title": "泳道(垂直)",
            "fontStyle": {"size": 16},
            "dataAttributes": [],
            "props": {"zindex": -1, "w": w, "x": x, "h": h, "y": y, "angle": 0, "height": [title_height]},
            "path": PATH_VERTICAL_LANE,
            "lineStyle": {},
            "children": [],
            "resizeDir": RESIZE_LANE,
            "name": "verticalLane",
            "fillStyle": {},
            "theme": {},
            "id": nid,
            "attribute": ATTR_CONTAINER,
            "category": "lane",
            "locked": False,
            "group": ""
        }
        # 自动添加到pool的children
        if pool_id in self.elements:
            self.elements[pool_id]["children"].append(nid)
        return nid

    def add_vertical_separator_bar(self, pool_id, x, y, w=33.6, h=3000):
        """垂直分隔条（泳道池左侧标签区域）"""
        nid = gen_id()
        self.elements[nid] = {
            "parent": pool_id,
            "link": "",
            "shapeStyle": {"alpha": 1},
            "textBlock": [],
            "anchors": [],
            "title": "水平分隔条",
            "fontStyle": {},
            "dataAttributes": [],
            "props": {"zindex": self._next_z(), "w": w, "x": x, "h": h, "y": y, "angle": 0, "height": [w]},
            "path": PATH_SEPARATOR_BAR,
            "lineStyle": {},
            "children": [],
            "resizeDir": [],
            "name": "verticalSeparatorBar",
            "fillStyle": {},
            "theme": {},
            "id": nid,
            "attribute": ATTR_INVISIBLE,
            "category": "lane",
            "locked": False,
            "group": ""
        }
        if pool_id in self.elements:
            self.elements[pool_id]["children"].append(nid)
        return nid

    def add_horizontal_separator(self, text, pool_id, x, y, w, h, sep_width=33.6):
        """水平阶段分隔"""
        nid = gen_id()
        self.elements[nid] = {
            "parent": pool_id,
            "link": "",
            "shapeStyle": {"alpha": 1},
            "textBlock": [{"position": {"w": "height[0]", "x": 0, "h": "h-10", "y": 5}, "text": text}],
            "anchors": [],
            "title": "分隔符(水平)<br>需拖动到泳池泳道上",
            "fontStyle": {"orientation": "horizontal", "size": 20, "textAlign": "center", "bold": True, "vAlign": "middle"},
            "dataAttributes": [],
            "props": {"zindex": self._next_z(), "w": w, "x": x, "h": h, "y": y, "angle": 0, "height": [sep_width]},
            "path": PATH_HORIZONTAL_SEPARATOR,
            "lineStyle": {"lineWidth": 1.5},
            "children": [],
            "resizeDir": ["b"],
            "name": "horizontalSeparator",
            "fillStyle": {},
            "theme": {},
            "id": nid,
            "attribute": ATTR_SEPARATOR,
            "category": "lane",
            "locked": False,
            "group": ""
        }
        if pool_id in self.elements:
            self.elements[pool_id]["children"].append(nid)
        return nid

    # ==================== 连线 ====================

    def add_linker(self, from_id, to_id, label="", from_anchor=1, to_anchor=0,
                   end_arrow="solidArrow", begin_arrow="none"):
        """
        添加连接线
        anchor: 0=上, 1=下, 2=左, 3=右
        """
        lid = gen_id()

        from_el = self.elements[from_id]
        to_el = self.elements[to_id]
        from_props = from_el["props"]
        to_props = to_el["props"]

        def calc_anchor(props, idx):
            x, y, w, h = props["x"], props["y"], props["w"], props["h"]
            if idx == 0: return x + w / 2, y
            if idx == 1: return x + w / 2, y + h
            if idx == 2: return x, y + h / 2
            if idx == 3: return x + w, y + h / 2
            return x + w / 2, y + h

        fx, fy = calc_anchor(from_props, from_anchor)
        tx, ty = calc_anchor(to_props, to_anchor)

        # 根据锚点方向组合计算折线拐角点
        # 水平锚点: 2=左, 3=右；垂直锚点: 0=上, 1=下
        from_horizontal = from_anchor in (2, 3)
        to_horizontal = to_anchor in (2, 3)

        if from_horizontal and not to_horizontal:
            # 源水平出 → 目标垂直入（如右→上）：拐角在 (tx, fy)
            points = [{"x": tx, "y": fy}]
        elif not from_horizontal and to_horizontal:
            # 源垂直出 → 目标水平入（如下→左）：拐角在 (fx, ty)
            points = [{"x": fx, "y": ty}]
        elif from_horizontal and to_horizontal:
            # 源水平出 → 目标水平入（如右→左）：中间垂直段
            mid_x = (fx + tx) / 2
            points = [{"x": mid_x, "y": fy}, {"x": mid_x, "y": ty}]
        else:
            # 源垂直出 → 目标垂直入（如下→上）：中间水平段
            mid_y = (fy + ty) / 2
            points = [{"x": fx, "y": mid_y}, {"x": tx, "y": mid_y}]

        el = {
            "textBlock": [{"location": 0.5, "text": label}] if label else [],
            "fontStyle": {"size": 16, "bold": True} if label else {},
            "points": points,
            "dataAttributes": [],
            "props": {"zindex": self._next_z()},
            "linkerType": "broken",
            "lineStyle": {
                "lineWidth": 1.5,
                "beginArrowStyle": begin_arrow,
                "endArrowStyle": end_arrow
            },
            "name": "linker",
            "from": {"x": fx, "y": fy, "angle": ANCHOR_ANGLES[from_anchor], "id": from_id},
            "id": lid,
            "text": label,
            "to": {"x": tx, "y": ty, "angle": ANCHOR_ANGLES[to_anchor], "id": to_id},
            "locked": False,
            "group": ""
        }

        self.elements[lid] = el
        return lid

    # ==================== 构建和保存 ====================

    def build(self, title="流程图"):
        """构建完整的 .pos JSON 数据"""
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        # 计算画布大小
        max_x, max_y = 0, 0
        for el in self.elements.values():
            p = el.get("props", {})
            max_x = max(max_x, p.get("x", 0) + p.get("w", 0))
            max_y = max(max_y, p.get("y", 0) + p.get("h", 0))

        return {
            "diagram": {
                "elements": {
                    "editorVersion": "V1",
                    "comments": [],
                    "plugins": {},
                    "elements": self.elements,
                    "page": {
                        "padding": 20,
                        "backgroundColor": "transparent",
                        "orientation": "portrait",
                        "gridSize": 15,
                        "width": int(max_x + 100),
                        "showGrid": True,
                        "lineJumps": False,
                        "height": int(max_y + 100)
                    },
                    "version": 0,
                    "aiContainers": {}
                }
            },
            "meta": {
                "exportTime": now,
                "member": "",
                "diagramInfo": {
                    "creator": "",
                    "created": now,
                    "modified": now,
                    "title": title,
                    "category": "flow"
                },
                "id": uuid.uuid4().hex[:24],
                "type": "ProcessOn Schema File",
                "version": "5.0"
            }
        }

    @staticmethod
    def save(data, filepath):
        """保存为 .pos 文件（单行紧凑JSON）"""
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, separators=(',', ':'))
        size = os.path.getsize(filepath)
        print(f"[OK] 已保存: {filepath} ({size:,} bytes)")

    @staticmethod
    def verify(filepath):
        """验证 .pos 文件结构"""
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)

        els = data['diagram']['elements']['elements']
        meta = data['meta']

        # 统计
        shapes = {}
        linkers = 0
        for eid, el in els.items():
            name = el.get('name', 'unknown')
            if name == 'linker':
                linkers += 1
            else:
                shapes[name] = shapes.get(name, 0) + 1

        print(f"标题: {meta['diagramInfo']['title']}")
        print(f"类型: {meta['type']} v{meta['version']}")
        print(f"节点: {sum(shapes.values())}")
        for name, count in sorted(shapes.items()):
            print(f"  {name}: {count}")
        print(f"连线: {linkers}")

        # 验证泳道结构
        pools = {eid: el for eid, el in els.items() if el.get('name') == 'verticalPool'}
        if pools:
            for pid, pool in pools.items():
                children = pool.get('children', [])
                print(f"\n泳道池: {pool['textBlock'][0]['text']}")
                print(f"  children: {len(children)}")
                for cid in children:
                    child = els.get(cid, {})
                    cname = child.get('name', '?')
                    ctext = child.get('textBlock', [{}])
                    ct = ctext[0].get('text', '') if ctext else ''
                    print(f"    [{cname}] {ct}")

        # 验证连线引用
        broken_refs = 0
        for eid, el in els.items():
            if el.get('name') == 'linker':
                fid = el.get('from', {}).get('id', '')
                tid = el.get('to', {}).get('id', '')
                if fid not in els:
                    print(f"  [警告] 连线 {eid} 的 from 引用不存在: {fid}")
                    broken_refs += 1
                if tid not in els:
                    print(f"  [警告] 连线 {eid} 的 to 引用不存在: {tid}")
                    broken_refs += 1

        if broken_refs == 0:
            print("\n[OK] 所有连线引用有效")
        else:
            print(f"\n[警告] {broken_refs} 个无效连线引用")

        return broken_refs == 0


# ==================== 命令行入口 ====================

def demo_flowchart():
    """生成示例流程图"""
    B = PosBuilder()

    n_start = B.add_terminator("开始", 250, 50, 100, 45)
    n1 = B.add_process("步骤一：数据收集", 200, 130, 200, 50)
    d1 = B.add_decision("数据是否\n完整", 240, 220, 120, 70)
    n2 = B.add_process("步骤二：数据分析", 200, 330, 200, 50)
    n3 = B.add_process("步骤三：生成报告", 200, 420, 200, 50)
    n_end = B.add_terminator("结束", 250, 510, 100, 45)

    B.add_linker(n_start, n1)
    B.add_linker(n1, d1)
    B.add_linker(d1, n2, "是")
    B.add_linker(d1, n1, "否", from_anchor=3, to_anchor=3)
    B.add_linker(n2, n3)
    B.add_linker(n3, n_end)

    data = B.build("示例流程图")
    B.save(data, "demo_flowchart.pos")


def demo_swimlane():
    """生成示例泳道图"""
    B = PosBuilder()

    pool_x, pool_y = 59, 50
    pool_title_h = 40
    lane_title_h = 30
    lane_w = 250
    sep_bar_w = 33.6
    num_lanes = 3
    lane_names = ["客户", "客户经理", "审批人"]
    pool_w = sep_bar_w + lane_w * num_lanes
    pool_h = 800

    lane_y = pool_y + pool_title_h
    lane_h = pool_h - pool_title_h

    # 创建泳道池
    pool_id = B.add_vertical_pool("示例泳道流程图", pool_x, pool_y, pool_w, pool_h, pool_title_h)

    # 创建分隔条
    B.add_vertical_separator_bar(pool_id, pool_x, lane_y, sep_bar_w, lane_h)

    # 创建泳道
    lane_ids = []
    for i, name in enumerate(lane_names):
        lx = pool_x + sep_bar_w + i * lane_w
        lid = B.add_vertical_lane(name, pool_id, lx, lane_y, lane_w, lane_h, lane_title_h)
        lane_ids.append(lid)

    # 在泳道内添加节点
    def lane_center(lane_idx, node_w=150):
        lx = pool_x + sep_bar_w + lane_idx * lane_w
        return lx + (lane_w - node_w) / 2

    content_y = lane_y + lane_title_h + 30

    n1 = B.add_start("提交申请", lane_center(0), content_y, 150, 50, container=pool_id)
    content_y += 90
    n2 = B.add_process("审核资料", lane_center(1), content_y, 150, 50, container=pool_id)
    B.add_linker(n1, n2)
    content_y += 90
    d1 = B.add_decision("是否通过", lane_center(2, 120), content_y, 120, 70, container=pool_id)
    B.add_linker(n2, d1)
    content_y += 110
    n3 = B.add_process("办理业务", lane_center(1), content_y, 150, 50, container=pool_id)
    B.add_linker(d1, n3, "是")
    B.add_linker(d1, n1, "否", from_anchor=2, to_anchor=3)
    content_y += 90
    n4 = B.add_terminator("完成", lane_center(0, 100), content_y, 100, 45, container=pool_id)
    B.add_linker(n3, n4)

    data = B.build("示例泳道流程图")
    B.save(data, "demo_swimlane.pos")


def demo_architecture():
    """生成示例系统架构图"""
    B = PosBuilder()

    # 大标题
    B.add_text("示例系统架构", 350, 30, w=300, h=44, font_size=35)

    # 一级模块背景
    B.add_round_rectangle("", 100, 100, 400, 200, fill_color="116,186,245")
    B.add_round_rectangle("", 520, 100, 400, 200, fill_color="148,224,225")

    # 模块标题条
    B.add_round_rectangle("用户管理", 100, 100, 400, 25,
                          fill_color="41,143,227", font_color="255,255,255")
    B.add_round_rectangle("系统设置", 520, 100, 400, 25,
                          fill_color="35,172,193", font_color="255,255,255")

    # 子功能项（无填充）
    items_left = ["角色管理", "权限管理", "用户信息", "部门管理"]
    for i, name in enumerate(items_left):
        col = i % 2
        row = i // 2
        B.add_round_rectangle(name, 110 + col * 190, 140 + row * 45, 180, 36)

    items_right = ["参数配置", "日志管理", "消息中心", "审计中心"]
    for i, name in enumerate(items_right):
        col = i % 2
        row = i // 2
        B.add_round_rectangle(name, 530 + col * 190, 140 + row * 45, 180, 36)

    data = B.build("示例系统架构图")
    B.save(data, "demo_architecture.pos")


if __name__ == '__main__':
    if len(sys.argv) > 1 and sys.argv[1] == '--verify':
        if len(sys.argv) < 3:
            print("用法: python generate_pos.py --verify <文件路径>")
            sys.exit(1)
        PosBuilder.verify(sys.argv[2])
    elif len(sys.argv) > 1 and sys.argv[1] == '--demo-swimlane':
        demo_swimlane()
    elif len(sys.argv) > 1 and sys.argv[1] == '--demo-arch':
        demo_architecture()
    else:
        demo_flowchart()
        print("\n提示: 使用 --demo-swimlane 生成泳道图示例")
        print("      使用 --demo-arch 生成架构图示例")
        print("      使用 --verify <文件> 验证.pos文件")
