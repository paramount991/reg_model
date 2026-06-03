#!/usr/bin/env python
# Copyright (c) 2026--2030. Wang Weihua
# All rights reserved.
"""共享数据 I/O 工具函数."""

from __future__ import annotations

from pathlib import Path  # noqa: TC003

import pandas as pd


def load_dataframe(data_path: Path) -> pd.DataFrame:
    """根据文件后缀加载 DataFrame.

    支持 .csv, .xlsx/.xls, .parquet.

    Args:
        data_path: 数据文件路径

    Returns:
        加载的 DataFrame

    Raises:
        ValueError: 不支持的文件格式
    """
    if data_path.suffix == '.csv':
        return pd.read_csv(data_path)
    if data_path.suffix in ('.xlsx', '.xls'):
        return pd.read_excel(data_path)
    if data_path.suffix == '.parquet':
        return pd.read_parquet(data_path)
    raise ValueError(f'不支持的文件格式: {data_path.suffix}')


def load_dataframe_with_target(
    data_path: Path,
    target_column: str,
) -> tuple[pd.DataFrame, pd.Series]:
    """加载数据并分离特征和目标列.

    Args:
        data_path: 数据文件路径
        target_column: 目标列名

    Returns:
        (特征 DataFrame, 目标 Series)

    Raises:
        ValueError: 目标列不在数据中
    """
    df = load_dataframe(data_path)
    if target_column not in df.columns:
        raise ValueError(
            f'目标列 "{target_column}" 不在数据中, 可用: {list(df.columns)}'
        )
    features = df.drop(columns=[target_column])
    target = df[target_column]
    return features, target


def save_dataframe(df: pd.DataFrame, output_path: Path) -> None:
    """根据后缀保存 DataFrame.

    支持 .csv, .xlsx/.xls, .parquet; 其他后缀默认 CSV.

    Args:
        df: 要保存的 DataFrame
        output_path: 输出文件路径
    """
    if output_path.suffix == '.csv':
        df.to_csv(output_path, index=False)
    elif output_path.suffix in ('.xlsx', '.xls'):
        df.to_excel(output_path, index=False)
    elif output_path.suffix == '.parquet':
        df.to_parquet(output_path, index=False)
    else:
        df.to_csv(output_path.with_suffix('.csv'), index=False)


def ensure_dir(path: Path) -> None:
    """确保文件父目录存在.

    Args:
        path: 目标文件路径
    """
    path.parent.mkdir(parents=True, exist_ok=True)
