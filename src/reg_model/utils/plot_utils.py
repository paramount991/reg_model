#!/usr/bin/env python
# Copyright (c) 2026--2030. Wang Weihua
# All rights reserved.
"""共享绑图工具函数."""

from __future__ import annotations

import matplotlib
import matplotlib.pyplot as plt


def setup_matplotlib_agg() -> None:
    """设置 matplotlib 为无 GUI 后端并配置中文字体."""
    matplotlib.use('Agg')
    plt.rcParams['font.sans-serif'] = ['SimHei', 'DejaVu Sans']
    plt.rcParams['axes.unicode_minus'] = False
