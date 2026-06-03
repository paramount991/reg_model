#!/usr/bin/env python
# Copyright (c) 2026--2030. Wang Weihua
# All rights reserved.
"""特征工程核心业务模块."""

from __future__ import annotations

import json
from pathlib import Path  # noqa: TC003

import numpy as np
import pandas as pd
from sklearn.feature_selection import SelectKBest, mutual_info_regression
from sklearn.linear_model import Lasso
from sklearn.preprocessing import (
    MinMaxScaler,
    PolynomialFeatures,
    RobustScaler,
    StandardScaler,
)

from reg_model.core.log import get_logger

log = get_logger()


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


def list_features(
    data_path: Path,
    config_path: Path | None = None,
) -> dict[str, str]:
    """列出当前使用的特征及类型.

    Args:
        data_path: 数据文件路径
        config_path: 特征配置文件路径(可选)

    Returns:
        特征名称到数据类型的映射字典
    """
    log.info(f'加载数据: {data_path}')
    df = _load_data(data_path)

    feature_types: dict[str, str] = {}
    for col in df.columns:
        dtype = df[col].dtype
        if pd.api.types.is_numeric_dtype(dtype):
            feature_types[col] = 'numeric'
        elif pd.api.types.is_datetime64_any_dtype(dtype):
            feature_types[col] = 'datetime'
        elif pd.api.types.is_categorical_dtype(dtype) or dtype == 'object':
            feature_types[col] = 'categorical'
        elif pd.api.types.is_bool_dtype(dtype):
            feature_types[col] = 'boolean'
        else:
            feature_types[col] = str(dtype)

    missing = df.isnull().sum()
    for col in feature_types:
        if missing[col] > 0:
            feature_types[col] += f' (缺失: {missing[col]}/{len(df)})'

    log.info(f'共 {len(feature_types)} 个特征')
    for name, ftype in feature_types.items():
        log.info(f'  {name}: {ftype}')

    return feature_types


def generate_features(
    data_path: Path,
    output_path: Path,
    recipe: str = 'polynomial',
    config_path: Path | None = None,
) -> None:
    """根据预定义配方生成新特征.

    Args:
        data_path: 输入数据文件路径
        output_path: 输出特征数据路径
        recipe: 特征生成配方("polynomial", "datetime")
        config_path: 配方配置文件路径
    """
    log.info(f'加载数据: {data_path}')
    df = _load_data(data_path)
    numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()

    if recipe == 'polynomial':
        degree = 2
        if config_path and config_path.exists():
            with open(config_path, encoding='utf-8') as f:
                cfg = json.load(f)
            degree = cfg.get('degree', 2)

        log.info(f'生成 {degree} 阶多项式特征({len(numeric_cols)} 列)...')
        poly = PolynomialFeatures(degree=degree, include_bias=False)
        poly_features = poly.fit_transform(df[numeric_cols])
        poly_names = poly.get_feature_names_out(numeric_cols)

        df_out = df.drop(columns=numeric_cols)
        poly_df = pd.DataFrame(poly_features, columns=poly_names, index=df.index)
        df_out = pd.concat([df_out, poly_df], axis=1)
        log.info(f'多项式特征完成: {len(numeric_cols)} → {len(poly_names)} 列')

    elif recipe == 'datetime':
        datetime_cols = list(df.select_dtypes(include=['datetime64']).columns)
        for col in df.select_dtypes(include=['object']).columns:
            try:
                converted = pd.to_datetime(df[col])
                if converted.notna().sum() > 0.5 * len(df):
                    datetime_cols.append(col)
                    df[col] = converted
            except (ValueError, TypeError):
                pass

        if not datetime_cols:
            log.warning('未找到日期列')
            df_out = df
        else:
            log.info(f'日期列: {datetime_cols}')
            df_out = df.copy()
            for col in datetime_cols:
                dt = df[col]
                df_out[f'{col}_year'] = dt.dt.year
                df_out[f'{col}_month'] = dt.dt.month
                df_out[f'{col}_day'] = dt.dt.day
                df_out[f'{col}_dayofweek'] = dt.dt.dayofweek
                df_out[f'{col}_quarter'] = dt.dt.quarter
                df_out[f'{col}_is_weekend'] = dt.dt.dayofweek.isin([5, 6]).astype(int)
            log.info(f'日期特征完成: {len(df_out.columns)} 列')
    else:
        raise ValueError(f'不支持的特征配方: {recipe},可选: polynomial, datetime')

    output_path.parent.mkdir(parents=True, exist_ok=True)
    _save_df(df_out, output_path)
    log.info(f'特征数据已保存: {output_path}')


def select_features(
    data_path: Path,
    output_path: Path,
    method: str = 'correlation',
    target_column: str | None = None,
    n_features: int | None = None,
) -> None:
    """执行特征选择算法并保留选中特征.

    Args:
        data_path: 输入数据文件路径
        output_path: 输出特征数据路径
        method: 特征选择方法("correlation", "mutual_info", "lasso")
        target_column: 目标列名
        n_features: 要保留的特征数量
    """
    log.info(f'加载数据: {data_path}')
    df = _load_data(data_path)

    if target_column is None:
        raise ValueError('特征选择需要指定目标列 (target_column)')
    if target_column not in df.columns:
        raise ValueError(f'目标列 "{target_column}" 不在数据中')

    features = df.drop(columns=[target_column])
    target = df[target_column]

    numeric_mask = features.dtypes.apply(lambda d: pd.api.types.is_numeric_dtype(d))
    numeric_cols = features.columns[numeric_mask].tolist()
    numeric_features = features[numeric_cols]

    if n_features is None:
        n_features = min(10, len(numeric_cols))
    n_features = min(n_features, len(numeric_cols))

    log.info(f'特征选择: method={method}, n_features={n_features}')

    if method == 'correlation':
        correlations = (
            numeric_features.corrwith(target).abs().sort_values(ascending=False)
        )
        selected_cols = correlations.head(n_features).index.tolist()
        scores = correlations[selected_cols].to_dict()
    elif method == 'mutual_info':
        selector = SelectKBest(mutual_info_regression, k=n_features)
        selector.fit(numeric_features.fillna(0), target)
        mask = selector.get_support()
        selected_cols = [numeric_cols[i] for i in range(len(numeric_cols)) if mask[i]]
        scores = dict(zip(selected_cols, selector.scores_[mask].tolist(), strict=True))
    elif method == 'lasso':
        scaler = StandardScaler()
        features_scaled = scaler.fit_transform(numeric_features.fillna(0))
        lasso = Lasso(alpha=0.01, random_state=42)
        lasso.fit(features_scaled, target)
        coef_abs = np.abs(lasso.coef_)
        top_indices = np.argsort(coef_abs)[-n_features:][::-1]
        selected_cols = [numeric_cols[i] for i in top_indices if coef_abs[i] > 0]
        scores = {numeric_cols[i]: float(coef_abs[i]) for i in top_indices}
    else:
        raise ValueError(
            f'不支持的特征选择方法: {method},可选: correlation, mutual_info, lasso'
        )

    log.info(f'选中特征: {selected_cols}')
    df_out = df[[*selected_cols, target_column]]

    output_path.parent.mkdir(parents=True, exist_ok=True)
    _save_df(df_out, output_path)

    detail_path = output_path.with_suffix('.json')
    with open(detail_path, 'w', encoding='utf-8') as f:
        json.dump(
            {
                'method': method,
                'n_features': n_features,
                'selected_features': selected_cols,
                'scores': {
                    k: round(v, 6) if isinstance(v, float) else v
                    for k, v in scores.items()
                },
            },
            f,
            ensure_ascii=False,
            indent=2,
        )
    log.info(f'特征选择结果已保存: {output_path}')


def transform_features(
    data_path: Path,
    output_path: Path,
    method: str = 'standardize',
    config_path: Path | None = None,
) -> None:
    """应用标准化/归一化等变换.

    Args:
        data_path: 输入数据文件路径
        output_path: 输出变换后数据路径
        method: 变换方法("standardize", "normalize", "robust")
        config_path: 变换配置文件路径
    """
    log.info(f'加载数据: {data_path}')
    df = _load_data(data_path)

    numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
    if not numeric_cols:
        log.warning('数据中没有数值列,跳过变换')
        return

    log.info(f'对 {len(numeric_cols)} 列应用 "{method}" 变换')

    if method == 'standardize':
        scaler = StandardScaler()
    elif method == 'normalize':
        scaler = MinMaxScaler()
    elif method == 'robust':
        scaler = RobustScaler()
    else:
        raise ValueError(
            f'不支持的变换方法: {method},可选: standardize, normalize, robust'
        )

    df_out = df.copy()
    df_out[numeric_cols] = scaler.fit_transform(df[numeric_cols])

    output_path.parent.mkdir(parents=True, exist_ok=True)
    _save_df(df_out, output_path)
    log.info(f'变换后数据已保存: {output_path}')


def _save_df(df: pd.DataFrame, output_path: Path) -> None:
    """根据后缀保存 DataFrame."""
    if output_path.suffix == '.csv':
        df.to_csv(output_path, index=False)
    elif output_path.suffix in ('.xlsx', '.xls'):
        df.to_excel(output_path, index=False)
    elif output_path.suffix == '.parquet':
        df.to_parquet(output_path, index=False)
    else:
        df.to_csv(output_path.with_suffix('.csv'), index=False)
