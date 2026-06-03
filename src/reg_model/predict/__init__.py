#!/usr/bin/env python
# Copyright (c) 2026--2030. Wang Weihua
# All rights reserved.
"""预测模块."""

from .manager import (
    explain_prediction,
    predict_batch,
)

__all__ = [
    'explain_prediction',
    'predict_batch',
]
