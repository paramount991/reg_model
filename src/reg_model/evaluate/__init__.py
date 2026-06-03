#!/usr/bin/env python
# Copyright (c) 2026--2030. Wang Weihua
# All rights reserved.
"""模型评估模块."""

from .manager import (
    analyze_residuals,
    compare_models,
    evaluate_model,
)

__all__ = [
    'analyze_residuals',
    'compare_models',
    'evaluate_model',
]
