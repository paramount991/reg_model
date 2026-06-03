#!/usr/bin/env python
# Copyright (c) 2026--2030. Wang Weihua
# All rights reserved.
"""模型训练核心业务模块."""

from __future__ import annotations

from pathlib import Path  # noqa: TC003
from typing import Any

import joblib
from sklearn.ensemble import (
    BaggingRegressor,
    GradientBoostingRegressor,
    StackingRegressor,
)
from sklearn.linear_model import (
    ElasticNet,
    Lasso,
    LinearRegression,
    Ridge,
)
from sklearn.model_selection import (
    GridSearchCV,
    RandomizedSearchCV,
    cross_validate,
)
from sklearn.preprocessing import StandardScaler

from reg_model.core.log import get_logger
from reg_model.utils import ensure_dir, load_dataframe_with_target

log = get_logger()

# 支持的算法注册表
_ALGORITHM_REGISTRY: dict[str, type] = {
    'linear_regression': LinearRegression,
    'ridge': Ridge,
    'lasso': Lasso,
    'elastic_net': ElasticNet,
    'gradient_boosting': GradientBoostingRegressor,
}


def _get_estimator(algorithm: str, hyperparameters: dict[str, Any] | None = None):
    """根据算法名称获取估算器实例.

    Args:
        algorithm: 算法名称
        hyperparameters: 超参数字典

    Returns:
        sklearn 估算器实例
    """
    cls = _ALGORITHM_REGISTRY.get(algorithm)
    if cls is None:
        raise ValueError(
            f'不支持的算法: {algorithm}, 可用: {list(_ALGORITHM_REGISTRY)}'
        )
    params = hyperparameters or {}
    return cls(**params)


def train_model(
    data_path: Path,
    model_path: Path,
    algorithm: str = 'linear_regression',
    hyperparameters: dict[str, Any] | None = None,
    target_column: str = 'target',
) -> dict[str, Any]:
    """训练单个模型(可指定算法和超参数).

    Args:
        data_path: 训练数据文件路径
        model_path: 模型保存路径
        algorithm: 算法名称
        hyperparameters: 超参数字典
        target_column: 目标列名

    Returns:
        训练结果信息字典
    """
    log.info(f'加载训练数据: {data_path}')
    features, target = load_dataframe_with_target(data_path, target_column)
    log.info(f'数据维度: {features.shape}, 目标列: {target_column}')

    scaler = StandardScaler()
    features_scaled = scaler.fit_transform(features)
    feature_names = features.columns.tolist()

    log.info(f'创建模型: {algorithm}, 超参数: {hyperparameters or "默认"}')
    model = _get_estimator(algorithm, hyperparameters)

    log.info('开始训练...')
    model.fit(features_scaled, target)

    ensure_dir(model_path)
    bundle = {
        'model': model,
        'scaler': scaler,
        'feature_names': feature_names,
        'algorithm': algorithm,
        'target_column': target_column,
        'hyperparameters': hyperparameters,
    }
    save_path = model_path.with_suffix('.joblib')
    joblib.dump(bundle, save_path)
    log.info(f'模型已保存到: {save_path}')

    train_score = (
        model.score(features_scaled, target) if hasattr(model, 'score') else None
    )

    result: dict[str, Any] = {
        'algorithm': algorithm,
        'model_path': str(save_path),
        'feature_count': len(feature_names),
        'sample_count': len(target),
        'feature_names': feature_names,
        'train_r2': round(train_score, 4) if train_score is not None else None,
    }

    if hasattr(model, 'coef_'):
        coef_dict = dict(zip(feature_names, model.coef_.tolist(), strict=True))
        result['coefficients'] = coef_dict
        log.info(f'模型系数: {coef_dict}')
    if hasattr(model, 'intercept_'):
        result['intercept'] = float(model.intercept_)
        log.info(f'截距: {model.intercept_:.4f}')

    log.info(f'训练完成, R²={result["train_r2"]}')
    return result


def tune_hyperparameters(
    data_path: Path,
    model_path: Path,
    algorithm: str = 'linear_regression',
    search_method: str = 'grid',
    param_grid: dict[str, list[Any]] | None = None,
    target_column: str = 'target',
) -> dict[str, Any]:
    """超参数调优(网格搜索/随机搜索).

    Args:
        data_path: 训练数据文件路径
        model_path: 模型保存路径
        algorithm: 算法名称
        search_method: 搜索方法("grid", "random")
        param_grid: 参数网格字典
        target_column: 目标列名

    Returns:
        调优结果信息字典
    """
    log.info(f'加载训练数据: {data_path}')
    features, target = load_dataframe_with_target(data_path, target_column)
    scaler = StandardScaler()
    features_scaled = scaler.fit_transform(features)
    feature_names = features.columns.tolist()

    estimator = _get_estimator(algorithm)

    if param_grid is None:
        param_grid = _default_param_grid(algorithm)

    log.info(f'超参数搜索: 方法={search_method}, 参数网格={param_grid}')
    if search_method == 'grid':
        search = GridSearchCV(
            estimator, param_grid, cv=5, scoring='r2', n_jobs=-1, verbose=1
        )
    elif search_method == 'random':
        search = RandomizedSearchCV(
            estimator,
            param_grid,
            cv=5,
            scoring='r2',
            n_jobs=-1,
            n_iter=20,
            random_state=42,
            verbose=1,
        )
    else:
        raise ValueError(f'不支持的搜索方法: {search_method}, 可选: grid, random')

    search.fit(features_scaled, target)
    log.info(f'最佳参数: {search.best_params_}')
    log.info(f'最佳CV分数: {search.best_score_:.4f}')

    ensure_dir(model_path)
    save_path = model_path.with_suffix('.joblib')
    bundle = {
        'model': search.best_estimator_,
        'scaler': scaler,
        'feature_names': feature_names,
        'algorithm': algorithm,
        'target_column': target_column,
        'hyperparameters': search.best_params_,
    }
    joblib.dump(bundle, save_path)

    return {
        'algorithm': algorithm,
        'model_path': str(save_path),
        'best_params': search.best_params_,
        'best_cv_score': round(float(search.best_score_), 4),
        'feature_count': len(feature_names),
        'sample_count': len(target),
    }


def train_with_cross_validation(
    data_path: Path,
    model_path: Path,
    algorithm: str = 'linear_regression',
    cv_folds: int = 5,
    hyperparameters: dict[str, Any] | None = None,
    target_column: str = 'target',
) -> dict[str, Any]:
    """带交叉验证的训练, 输出验证分数.

    Args:
        data_path: 训练数据文件路径
        model_path: 模型保存路径
        algorithm: 算法名称
        cv_folds: 交叉验证折数
        hyperparameters: 超参数字典
        target_column: 目标列名

    Returns:
        交叉验证结果信息字典
    """
    log.info(f'加载训练数据: {data_path}')
    features, target = load_dataframe_with_target(data_path, target_column)
    scaler = StandardScaler()
    features_scaled = scaler.fit_transform(features)
    feature_names = features.columns.tolist()

    estimator = _get_estimator(algorithm, hyperparameters)

    log.info(f'{cv_folds}折交叉验证...')
    scoring = ['r2', 'neg_mean_squared_error', 'neg_mean_absolute_error']
    cv_results = cross_validate(
        estimator,
        features_scaled,
        target,
        cv=cv_folds,
        scoring=scoring,
        return_train_score=True,
    )

    summary = {
        'algorithm': algorithm,
        'cv_folds': cv_folds,
        'feature_count': len(feature_names),
        'sample_count': len(target),
        'test_r2_mean': round(float(cv_results['test_r2'].mean()), 4),
        'test_r2_std': round(float(cv_results['test_r2'].std()), 4),
        'test_rmse_mean': round(
            float((-cv_results['test_neg_mean_squared_error']).mean() ** 0.5), 4
        ),
        'test_mae_mean': round(
            float((-cv_results['test_neg_mean_absolute_error']).mean()), 4
        ),
        'train_r2_mean': round(float(cv_results['train_r2'].mean()), 4),
    }
    log.info(f'CV结果: {summary}')

    estimator.fit(features_scaled, target)
    ensure_dir(model_path)
    save_path = model_path.with_suffix('.joblib')
    bundle = {
        'model': estimator,
        'scaler': scaler,
        'feature_names': feature_names,
        'algorithm': algorithm,
        'target_column': target_column,
        'hyperparameters': hyperparameters,
    }
    joblib.dump(bundle, save_path)
    summary['model_path'] = str(save_path)

    return summary


def train_ensemble_model(
    data_path: Path,
    model_path: Path,
    ensemble_method: str = 'stacking',
    base_models: list[str] | None = None,
    target_column: str = 'target',
) -> dict[str, Any]:
    """训练集成模型(如 stacking, bagging, boosting).

    Args:
        data_path: 训练数据文件路径
        model_path: 模型保存路径
        ensemble_method: 集成方法
        base_models: 基础模型列表
        target_column: 目标列名

    Returns:
        集成训练结果信息字典
    """
    log.info(f'加载训练数据: {data_path}')
    features, target = load_dataframe_with_target(data_path, target_column)
    scaler = StandardScaler()
    features_scaled = scaler.fit_transform(features)
    feature_names = features.columns.tolist()

    if base_models is None:
        base_models = ['linear_regression', 'ridge', 'lasso']

    base_estimators = [(name, _get_estimator(name)) for name in base_models]

    log.info(f'集成方法: {ensemble_method}, 基模型: {base_models}')
    if ensemble_method == 'stacking':
        model = StackingRegressor(
            estimators=base_estimators,
            final_estimator=Ridge(),
            cv=5,
        )
    elif ensemble_method == 'bagging':
        base = _get_estimator(base_models[0])
        model = BaggingRegressor(estimator=base, n_estimators=10, random_state=42)
    elif ensemble_method == 'boosting':
        model = GradientBoostingRegressor(n_estimators=100, random_state=42)
    else:
        raise ValueError(
            f'不支持的集成方法: {ensemble_method}, 可选: stacking, bagging, boosting'
        )

    log.info('开始训练集成模型...')
    model.fit(features_scaled, target)

    ensure_dir(model_path)
    save_path = model_path.with_suffix('.joblib')
    bundle = {
        'model': model,
        'scaler': scaler,
        'feature_names': feature_names,
        'ensemble_method': ensemble_method,
        'base_models': base_models,
        'target_column': target_column,
    }
    joblib.dump(bundle, save_path)
    log.info(f'集成模型已保存到: {save_path}')

    train_score = (
        model.score(features_scaled, target) if hasattr(model, 'score') else None
    )

    return {
        'ensemble_method': ensemble_method,
        'base_models': base_models,
        'model_path': str(save_path),
        'feature_count': len(feature_names),
        'sample_count': len(target),
        'train_r2': round(train_score, 4) if train_score is not None else None,
    }


def _default_param_grid(algorithm: str) -> dict[str, list[Any]]:
    """为各算法提供默认参数网格."""
    grids = {
        'linear_regression': {
            'fit_intercept': [True, False],
        },
        'ridge': {
            'alpha': [0.01, 0.1, 1.0, 10.0, 100.0],
            'fit_intercept': [True, False],
        },
        'lasso': {
            'alpha': [0.0001, 0.001, 0.01, 0.1, 1.0],
            'fit_intercept': [True, False],
        },
        'elastic_net': {
            'alpha': [0.01, 0.1, 1.0, 10.0],
            'l1_ratio': [0.1, 0.3, 0.5, 0.7, 0.9],
        },
        'gradient_boosting': {
            'n_estimators': [50, 100, 200],
            'learning_rate': [0.01, 0.05, 0.1],
            'max_depth': [3, 5, 7],
        },
    }
    return grids.get(algorithm, {})
