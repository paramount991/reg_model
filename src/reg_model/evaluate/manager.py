#!/usr/bin/env python
# Copyright (c) 2026--2030. Wang Weihua
# All rights reserved.
"""Model evaluation core module."""

from __future__ import annotations

import json
from pathlib import Path
from typing import TYPE_CHECKING

import matplotlib.pyplot as plt

if TYPE_CHECKING:
    import numpy as np
    import pandas as pd
from sklearn.metrics import (
    explained_variance_score,
    max_error,
    mean_absolute_error,
    mean_squared_error,
    r2_score,
)

from reg_model.core.log import get_logger
from reg_model.utils import (
    ensure_dir,
    load_dataframe_with_target,
    load_model_bundle,
    setup_matplotlib_agg,
)

setup_matplotlib_agg()
log = get_logger()

_METRIC_FUNCTIONS = {
    'rmse': lambda y_true, y_pred: float(mean_squared_error(y_true, y_pred) ** 0.5),
    'mse': lambda y_true, y_pred: float(mean_squared_error(y_true, y_pred)),
    'mae': lambda y_true, y_pred: float(mean_absolute_error(y_true, y_pred)),
    'r2': lambda y_true, y_pred: float(r2_score(y_true, y_pred)),
    'explained_variance': lambda y_true, y_pred: float(
        explained_variance_score(y_true, y_pred)
    ),
    'max_error': lambda y_true, y_pred: float(max_error(y_true, y_pred)),
}


def evaluate_model(
    model_path: Path,
    test_data_path: Path,
    metrics: list[str] | None = None,
    output_path: Path | None = None,
) -> dict[str, float]:
    """Evaluate model on test dataset.

    Args:
        model_path: Path to model file
        test_data_path: Path to test data file
        metrics: List of metric names (e.g. ["rmse", "mae", "r2"])
        output_path: Path to save evaluation results

    Returns:
        Dict mapping metric name to value
    """
    bundle = load_model_bundle(model_path)
    log.info(f'Loaded model: {model_path}, algo: {bundle.get("algorithm", "unknown")}')
    model = bundle['model']
    scaler = bundle['scaler']
    feature_names = bundle['feature_names']
    target_column = bundle.get('target_column', 'target')

    log.info(f'Loading test data: {test_data_path}')
    features, true_target = load_dataframe_with_target(test_data_path, target_column)

    features = features[feature_names]
    features_scaled = scaler.transform(features)
    predicted_target = model.predict(features_scaled)

    if metrics is None or len(metrics) == 0:
        metrics = ['rmse', 'mae', 'r2']

    results: dict[str, float] = {}
    for metric_name in metrics:
        metric_name = metric_name.strip().lower()
        if metric_name in _METRIC_FUNCTIONS:
            results[metric_name] = _METRIC_FUNCTIONS[metric_name](
                true_target, predicted_target
            )
        else:
            log.warning(f'Unknown metric: {metric_name}, skipped')

    log.info(f'Evaluation results: {results}')

    if output_path:
        ensure_dir(output_path)
        output_data = {
            'metrics': results,
            'model_path': str(model_path),
            'test_data_path': str(test_data_path),
            'sample_count': len(true_target),
        }
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(output_data, f, ensure_ascii=False, indent=2)
        log.info(f'Results saved to: {output_path}')

    return results


def analyze_residuals(
    model_path: Path,
    test_data_path: Path,
    output_dir: Path,
    plot_types: list[str] | None = None,
) -> None:
    """Generate residual analysis plots.

    Args:
        model_path: Path to model file
        test_data_path: Path to test data file
        output_dir: Directory for plot output
        plot_types: List of plot types (e.g. ["histogram", "scatter", "qq"])
    """
    bundle = load_model_bundle(model_path)
    model = bundle['model']
    scaler = bundle['scaler']
    feature_names = bundle['feature_names']
    target_column = bundle.get('target_column', 'target')

    features, true_target = load_dataframe_with_target(test_data_path, target_column)
    features = features[feature_names]
    features_scaled = scaler.transform(features)
    predicted_target = model.predict(features_scaled)
    residuals = true_target.values - predicted_target

    if plot_types is None or len(plot_types) == 0:
        plot_types = ['histogram', 'scatter']

    ensure_dir(output_dir)

    for plot_type in plot_types:
        plot_type = plot_type.strip().lower()
        if plot_type == 'histogram':
            _plot_residual_histogram(residuals, output_dir)
        elif plot_type == 'scatter':
            _plot_residual_scatter(true_target, predicted_target, residuals, output_dir)
        elif plot_type == 'qq':
            _plot_qq(residuals, output_dir)
        else:
            log.warning(f'Unknown plot type: {plot_type}, skipped')


def _plot_residual_histogram(residuals: np.ndarray, output_dir: Path) -> None:
    """Plot residual histogram."""
    fig, ax = plt.subplots(figsize=(8, 5))
    ax.hist(residuals, bins=30, edgecolor='black', alpha=0.7, color='steelblue')
    ax.axvline(x=0, color='red', linestyle='--', linewidth=1.5, label='Zero residual')
    ax.set_xlabel('Residual')
    ax.set_ylabel('Frequency')
    ax.set_title('Residual Distribution')
    ax.legend()
    fig.tight_layout()
    fig.savefig(output_dir / 'residual_histogram.png', dpi=150)
    plt.close(fig)
    log.info(f'Histogram saved: {output_dir / "residual_histogram.png"}')


def _plot_residual_scatter(
    true_target: pd.Series,
    predicted_target: np.ndarray,
    residuals: np.ndarray,
    output_dir: Path,
) -> None:
    """Plot residual scatter plots."""
    fig, axes = plt.subplots(1, 2, figsize=(14, 5))

    axes[0].scatter(
        true_target, predicted_target, alpha=0.5, edgecolors='k', linewidth=0.3
    )
    lims = [
        min(true_target.min(), predicted_target.min()),
        max(true_target.max(), predicted_target.max()),
    ]
    axes[0].plot(lims, lims, 'r--', linewidth=1.5, label='Ideal')
    axes[0].set_xlabel('True')
    axes[0].set_ylabel('Predicted')
    axes[0].set_title('Predicted vs True')
    axes[0].legend()

    axes[1].scatter(
        predicted_target, residuals, alpha=0.5, edgecolors='k', linewidth=0.3
    )
    axes[1].axhline(y=0, color='r', linestyle='--', linewidth=1.5)
    axes[1].set_xlabel('Predicted')
    axes[1].set_ylabel('Residual')
    axes[1].set_title('Residual vs Predicted')

    fig.tight_layout()
    fig.savefig(output_dir / 'residual_scatter.png', dpi=150)
    plt.close(fig)
    log.info(f'Scatter saved: {output_dir / "residual_scatter.png"}')


def _plot_qq(residuals: np.ndarray, output_dir: Path) -> None:
    """Plot Q-Q plot."""
    from scipy import stats

    fig, ax = plt.subplots(figsize=(8, 5))
    stats.probplot(residuals, dist='norm', plot=ax)
    ax.set_title('Q-Q Plot')
    fig.tight_layout()
    fig.savefig(output_dir / 'residual_qq.png', dpi=150)
    plt.close(fig)
    log.info(f'Q-Q plot saved: {output_dir / "residual_qq.png"}')


def compare_models(
    model_paths: list[Path],
    test_data_path: Path,
    metrics: list[str] | None = None,
    output_path: Path | None = None,
) -> dict[str, dict[str, float]]:
    """Compare performance of two or more models.

    Args:
        model_paths: List of model file paths
        test_data_path: Path to test data file
        metrics: List of metric names
        output_path: Path to save comparison results

    Returns:
        Dict mapping model name to metrics dict
    """
    if metrics is None or len(metrics) == 0:
        metrics = ['rmse', 'mae', 'r2']

    results: dict[str, dict[str, float]] = {}

    for mp in model_paths:
        mp = Path(mp)
        if not mp.exists():
            log.warning(f'Model file not found, skipping: {mp}')
            continue
        model_name = mp.stem
        log.info(f'Evaluating model: {model_name}')
        try:
            model_results = evaluate_model(
                model_path=mp,
                test_data_path=test_data_path,
                metrics=metrics,
                output_path=None,
            )
            results[model_name] = model_results
        except Exception as e:
            log.error(f'Model {model_name} evaluation failed: {e}')
            results[model_name] = {'error': float('nan')}

    log.info('Model comparison results:')
    for name, scores in results.items():
        log.info(f'  {name}: {scores}')

    if output_path:
        ensure_dir(output_path)
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(results, f, ensure_ascii=False, indent=2)
        log.info(f'Comparison saved to: {output_path}')

    return results
