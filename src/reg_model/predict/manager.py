#!/usr/bin/env python
# Copyright (c) 2026--2030. Wang Weihua
# All rights reserved.
"""预测核心业务模块."""

from __future__ import annotations

import json
from pathlib import Path  # noqa: TC003
from typing import Any

import joblib
import numpy as np
import pandas as pd

from reg_model.core.log import get_logger

log = get_logger()


def _load_model_bundle(model_path: Path) -> dict:
    """加载模型包."""
    path = (
        model_path.with_suffix('.joblib')
        if model_path.suffix != '.joblib'
        else model_path
    )
    if not path.exists():
        raise FileNotFoundError(f'模型文件不存在: {path}')
    return joblib.load(path)


def _load_data(data_path: Path) -> pd.DataFrame:
    """加载数据文件."""
    if data_path.suffix == '.csv':
        return pd.read_csv(data_path)
    elif data_path.suffix in ('.xlsx', '.xls'):
        return pd.read_excel(data_path)
    elif data_path.suffix == '.parquet':
        return pd.read_parquet(data_path)
    else:
        raise ValueError(f'不支持的文件格式: {data_path.suffix}')


def predict_batch(
    model_path: Path,
    data_path: Path,
    output_path: Path,
    format: str = 'csv',
) -> None:
    """批量预测并输出 CSV/Excel/JSON.

    Args:
        model_path: 模型文件路径
        data_path: 预测数据文件路径
        output_path: 预测结果输出文件路径
        format: 输出格式("csv", "excel", "json")
    """
    bundle = _load_model_bundle(model_path)
    model = bundle['model']
    scaler = bundle['scaler']
    feature_names = bundle['feature_names']

    log.info(f'加载预测数据: {data_path}')
    df = _load_data(data_path)

    missing_cols = set(feature_names) - set(df.columns)
    if missing_cols:
        raise ValueError(f'数据缺少特征列: {missing_cols}')
    features = df[feature_names]
    features_scaled = scaler.transform(features)

    log.info(f'开始预测,样本数: {len(features)}')
    predictions = model.predict(features_scaled)

    result_df = df.copy()
    result_df['prediction'] = predictions

    output_path.parent.mkdir(parents=True, exist_ok=True)

    if format == 'csv':
        result_df.to_csv(output_path.with_suffix('.csv'), index=False)
    elif format in ('excel', 'xlsx'):
        result_df.to_excel(output_path.with_suffix('.xlsx'), index=False)
    elif format == 'json':
        result_df.to_json(
            output_path.with_suffix('.json'), orient='records', force_ascii=False
        )
    else:
        raise ValueError(f'不支持的输出格式: {format},可选: csv, excel, json')

    log.info(f'预测结果已保存到: {output_path.with_suffix("." + format)}')


def explain_prediction(
    model_path: Path,
    sample_data_path: Path,
    output_path: Path,
    method: str = 'shap',
) -> dict[str, Any]:
    """对给定样本输出特征重要性解释.

    支持 SHAP 和内置 feature_importance 两种方法。

    Args:
        model_path: 模型文件路径
        sample_data_path: 样本数据文件路径
        output_path: 解释结果输出文件路径
        method: 解释方法("shap", "feature_importance")

    Returns:
        解释结果字典
    """
    bundle = _load_model_bundle(model_path)
    model = bundle['model']
    scaler = bundle['scaler']
    feature_names = bundle['feature_names']

    df = _load_data(sample_data_path)
    features = df[feature_names]
    features_scaled = scaler.transform(features)

    explanation: dict[str, Any] = {
        'method': method,
        'feature_names': feature_names,
        'sample_count': len(features),
    }

    if method == 'shap':
        try:
            import matplotlib
            import shap

            matplotlib.use('Agg')
            import matplotlib.pyplot as plt

            # 使用部分样本做 SHAP 以提高性能
            bg_size = min(100, len(features_scaled))
            background = features_scaled[:bg_size]
            explainer = shap.Explainer(model.predict, background)
            shap_values = explainer(background)

            output_dir = output_path.parent
            output_dir.mkdir(parents=True, exist_ok=True)

            fig, _ = plt.subplots(figsize=(10, 6))
            shap.summary_plot(
                shap_values, background, feature_names=feature_names, show=False
            )
            fig.savefig(output_dir / 'shap_summary.png', dpi=150, bbox_inches='tight')
            plt.close(fig)
            log.info(f'SHAP摘要图已保存: {output_dir / "shap_summary.png"}')

            mean_shap = np.abs(shap_values.values).mean(axis=0)  # type: ignore  # shap Explanation union
            importance = dict(zip(feature_names, mean_shap.tolist(), strict=True))
            explanation['feature_importance'] = dict(
                sorted(importance.items(), key=lambda x: abs(x[1]), reverse=True)
            )
        except ImportError:
            log.warning('shap 库未安装,回退到内置方法')
            method = 'feature_importance'

    if method == 'feature_importance':
        if hasattr(model, 'coef_'):
            coefs = model.coef_
            if coefs.ndim > 1:
                coefs = coefs.flatten()
            importance = dict(zip(feature_names, np.abs(coefs).tolist(), strict=True))
            explanation['feature_importance'] = dict(
                sorted(importance.items(), key=lambda x: abs(x[1]), reverse=True)
            )
        elif hasattr(model, 'feature_importances_'):
            importance = dict(
                zip(feature_names, model.feature_importances_.tolist(), strict=True)
            )
            explanation['feature_importance'] = dict(
                sorted(importance.items(), key=lambda x: abs(x[1]), reverse=True)
            )
        else:
            explanation['error'] = '该模型不支持特征重要性提取'

    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path.with_suffix('.json'), 'w', encoding='utf-8') as f:
        json.dump(explanation, f, ensure_ascii=False, indent=2)
    log.info(f'解释结果已保存: {output_path.with_suffix(".json")}')

    return explanation
