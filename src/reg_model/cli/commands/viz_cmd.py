#!/usr/bin/env python
# Copyright (c) 2026--2030. Wang Weihua
# All rights reserved.
from pathlib import Path

import typer

from reg_model.core import handle_errors, log_command
from reg_model.core.log import get_logger
from reg_model.viz import (
    plot_correlation_matrix,
    plot_feature_importance,
    plot_prediction_scatter,
)

log = get_logger()
app = typer.Typer(help='可视化')


@app.command(help='绘制特征相关性矩阵')
@handle_errors
@log_command('correlation')
def correlation(
    data_path: Path = typer.Argument(..., help='数据文件路径'),
    output_path: Path = typer.Argument(..., help='图表输出文件路径'),
    method: str = typer.Option('pearson', '--method', '-m', help='相关性计算方法'),
    figsize: str | None = typer.Option(None, '--figsize', '-f', help='图表尺寸字符串'),
) -> None:
    """绘制特征相关性矩阵."""
    log.info(f'相关性矩阵: {data_path} -> {output_path}')
    figsize_parsed = _parse_figsize(figsize)
    plot_correlation_matrix(
        data_path=data_path,
        output_path=output_path,
        method=method,
        figsize=figsize_parsed,
    )


@app.command(help='绘制特征重要性条形图')
@handle_errors
@log_command('importance')
def importance(
    model_path: Path = typer.Argument(..., help='模型文件路径'),
    output_path: Path = typer.Argument(..., help='图表输出文件路径'),
    top_n: int | None = typer.Option(None, '--top-n', '-n', help='显示前N个重要特征'),
) -> None:
    """绘制特征重要性条形图."""
    log.info(f'特征重要性: {model_path} -> {output_path}')
    plot_feature_importance(
        model_path=model_path,
        output_path=output_path,
        top_n=top_n,
    )


@app.command(help='绘制预测值 vs 真实值散点图')
@handle_errors
@log_command('prediction')
def prediction(
    predictions_path: Path = typer.Argument(..., help='预测值文件路径'),
    actuals_path: Path = typer.Argument(..., help='真实值文件路径'),
    output_path: Path = typer.Argument(..., help='图表输出文件路径'),
) -> None:
    """绘制预测值 vs 真实值散点图."""
    log.info(f'预测散点图: {predictions_path} vs {actuals_path} -> {output_path}')
    plot_prediction_scatter(
        predictions_path=predictions_path,
        actuals_path=actuals_path,
        output_path=output_path,
    )


def _parse_figsize(raw: str | None) -> tuple | None:
    """解析 "宽,高" 格式的字符串为 tuple."""
    if raw is None:
        return None
    try:
        parts = [float(x.strip()) for x in raw.split(',')]
        if len(parts) != 2:
            raise ValueError('需要两个数值')
        return tuple(parts)
    except (ValueError, TypeError) as e:
        log.error(f'解析 figsize 失败: {e}')
        raise typer.BadParameter(f'无效的 figsize: {raw},示例: "12,8"') from e
