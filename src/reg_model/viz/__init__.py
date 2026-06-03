#!/usr/bin/env python
# Copyright (c) 2026--2030. Wang Weihua
# All rights reserved.
"""可视化模块."""

from .manager import (
    plot_correlation_matrix,
    plot_feature_importance,
    plot_prediction_scatter,
)

__all__ = [
    'plot_correlation_matrix',
    'plot_feature_importance',
    'plot_prediction_scatter',
]
