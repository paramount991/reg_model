#!/usr/bin/env python
# Copyright (c) 2026--2030. Wang Weihua
# All rights reserved.
"""可视化核心业务模块."""

from __future__ import annotations

from pathlib import Path  # noqa: TC003

import joblib
import matplotlib
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_squared_error, r2_score

from reg_model.core.log import get_logger

matplotlib.use('Agg')
log = get_logger()

plt.rcParams['font.sans-serif'] = ['SimHei', 'DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False


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


def plot_correlation_matrix(
    data_path: Path,
    output_path: Path,
    method: str = 'pearson',
    figsize: tuple | None = None,
) -> None:
    """绘制特征相关性矩阵热力图.

    Args:
        data_path: 数据文件路径
        output_path: 图表输出文件路径
        method: 相关性计算方法("pearson", "spearman", "kendall")
        figsize: 图表尺寸
    """
    log.info(f'加载数据: {data_path}')
    df = _load_data(data_path)
    numeric_df = df.select_dtypes(include=[np.number])

    if numeric_df.empty:
        log.warning('数据中没有数值列')
        return

    n_cols = len(numeric_df.columns)
    log.info(f'计算 {method} 相关性矩阵 ({n_cols} 个特征)...')
    corr_matrix = numeric_df.corr(method=method)  # type: ignore  # str literal for corr method

    if figsize is None:
        size = max(8, min(20, n_cols * 1.2))
        figsize = (size, size)

    fig, ax = plt.subplots(figsize=figsize)
    mask = np.triu(np.ones_like(corr_matrix, dtype=bool), k=1)
    cmap = sns.diverging_palette(250, 15, s=75, l=40, n=16, center='light')

    sns.heatmap(
        corr_matrix,
        mask=mask,
        cmap=cmap,
        center=0,
        annot=n_cols <= 20,
        fmt='.2f',
        square=True,
        linewidths=0.5,
        cbar_kws={'shrink': 0.8},
        ax=ax,
    )
    ax.set_title(
        f'Feature Correlation Matrix ({method})', fontsize=14, fontweight='bold'
    )

    output_path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(output_path, dpi=150, bbox_inches='tight')
    plt.close(fig)
    log.info(f'相关性矩阵图已保存: {output_path}')


def plot_feature_importance(
    model_path: Path,
    output_path: Path,
    top_n: int | None = None,
) -> None:
    """绘制特征重要性条形图.

    Args:
        model_path: 模型文件路径
        output_path: 图表输出文件路径
        top_n: 显示前N个重要特征
    """
    path = (
        model_path.with_suffix('.joblib')
        if model_path.suffix != '.joblib'
        else model_path
    )
    if not path.exists():
        raise FileNotFoundError(f'模型文件不存在: {path}')

    bundle = joblib.load(path)
    model = bundle['model']
    feature_names = bundle.get('feature_names', [])

    importance: np.ndarray | None = None
    importance_type = '|Coefficient|'

    if hasattr(model, 'coef_'):
        importance = np.abs(model.coef_)
        if importance.ndim > 1:
            importance = importance.flatten()
    elif hasattr(model, 'feature_importances_'):
        importance = model.feature_importances_
        importance_type = 'Feature Importance'

    if importance is None:
        log.warning('该模型不支持特征重要性提取')
        return

    if not feature_names:
        feature_names = [f'Feature_{i}' for i in range(len(importance))]

    sorted_idx = np.argsort(importance)[::-1]
    if top_n:
        sorted_idx = sorted_idx[:top_n]

    sorted_names = [feature_names[i] for i in sorted_idx]
    sorted_importance = importance[sorted_idx]

    fig, ax = plt.subplots(figsize=(10, max(6, len(sorted_names) * 0.4)))
    colors = plt.get_cmap('Blues')(
        0.3 + 0.7 * sorted_importance / sorted_importance.max()
    )
    ax.barh(
        range(len(sorted_names)),
        sorted_importance,
        color=colors,
        edgecolor='black',
        linewidth=0.5,
    )
    ax.set_yticks(range(len(sorted_names)))
    ax.set_yticklabels(sorted_names)
    ax.invert_yaxis()
    ax.set_xlabel(importance_type)
    ax.set_title(
        f'Feature Importance ({importance_type})', fontsize=14, fontweight='bold'
    )

    for i, v in enumerate(sorted_importance):
        ax.text(
            v + sorted_importance.max() * 0.01, i, f'{v:.4f}', va='center', fontsize=8
        )

    fig.tight_layout()
    output_path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(output_path, dpi=150, bbox_inches='tight')
    plt.close(fig)
    log.info(f'特征重要性图已保存: {output_path}')


def plot_prediction_scatter(
    predictions_path: Path,
    actuals_path: Path,
    output_path: Path,
) -> None:
    """绘制预测值 vs 真实值散点图.

    Args:
        predictions_path: 预测值文件路径
        actuals_path: 真实值文件路径
        output_path: 图表输出文件路径
    """
    log.info(f'加载预测值: {predictions_path}')
    pred_df = _load_data(predictions_path)
    log.info(f'加载真实值: {actuals_path}')
    actual_df = _load_data(actuals_path)

    if 'prediction' in pred_df.columns:
        y_pred = pred_df['prediction'].values
    else:
        y_pred = pred_df.iloc[:, 0].values

    if 'target' in actual_df.columns:
        y_true = actual_df['target'].values
    elif len(actual_df.columns) == 1:
        y_true = actual_df.iloc[:, 0].values
    else:
        y_true = actual_df.select_dtypes(include=[np.number]).iloc[:, 0].values

    min_len = min(len(y_pred), len(y_true))
    y_pred = y_pred[:min_len]
    y_true = y_true[:min_len]

    fig, ax = plt.subplots(figsize=(8, 7))
    ax.scatter(y_true, y_pred, alpha=0.5, edgecolors='k', linewidth=0.3, s=30)

    all_vals = np.concatenate([y_true, y_pred])
    lims = [all_vals.min(), all_vals.max()]
    ax.plot(lims, lims, 'r--', linewidth=2, label='Ideal (y=x)')

    lr = LinearRegression()
    lr.fit(y_true.reshape(-1, 1), y_pred)
    x_line = np.linspace(lims[0], lims[1], 100)
    ax.plot(
        x_line,
        lr.predict(x_line.reshape(-1, 1)),
        'b-',
        linewidth=1.5,
        label=f'Fit (slope={lr.coef_[0]:.3f})',
    )

    ax.set_xlabel('True Values', fontsize=12)
    ax.set_ylabel('Predicted Values', fontsize=12)
    ax.set_title('Predicted vs True', fontsize=14, fontweight='bold')
    ax.legend()
    ax.set_aspect('equal')
    ax.grid(True, alpha=0.3)

    rmse = float(mean_squared_error(y_true, y_pred) ** 0.5)
    r2 = float(r2_score(y_true, y_pred))
    ax.text(
        0.05,
        0.95,
        f'RMSE = {rmse:.4f}\nR² = {r2:.4f}\nn = {min_len}',
        transform=ax.transAxes,
        verticalalignment='top',
        bbox={'boxstyle': 'round', 'facecolor': 'wheat', 'alpha': 0.8},
        fontsize=10,
    )

    fig.tight_layout()
    output_path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(output_path, dpi=150, bbox_inches='tight')
    plt.close(fig)
    log.info(f'预测散点图已保存: {output_path}')
