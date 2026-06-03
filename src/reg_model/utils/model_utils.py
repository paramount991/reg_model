#!/usr/bin/env python
# Copyright (c) 2026--2030. Wang Weihua
# All rights reserved.
"""共享模型工具函数."""

from __future__ import annotations

from pathlib import Path  # noqa: TC003

import joblib


def load_model_bundle(model_path: Path) -> dict:
    """加载 joblib 模型包.

    自动补全 .joblib 后缀.

    Args:
        model_path: 模型文件路径

    Returns:
        模型包字典, 包含 model, scaler, feature_names 等

    Raises:
        FileNotFoundError: 模型文件不存在
    """
    if model_path.suffix != '.joblib':
        model_path = model_path.with_suffix('.joblib')
    if not model_path.exists():
        raise FileNotFoundError(f'模型文件不存在: {model_path}')
    return joblib.load(model_path)
