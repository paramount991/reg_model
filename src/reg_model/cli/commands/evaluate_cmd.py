#!/usr/bin/env python
# Copyright (c) 2026--2030. Wang Weihua
# All rights reserved.
"""模型评估子命令."""

import json
from pathlib import Path

import typer

from reg_model.core import handle_errors, log_command
from reg_model.core.log import get_logger
from reg_model.evaluate import (
    analyze_residuals,
    compare_models,
    evaluate_model,
)

log = get_logger()
app = typer.Typer(help='模型评估')


def _parse_list(raw: str | None) -> list:
    """解析逗号分隔的字符串为列表."""
    if raw is None:
        return []
    return [item.strip() for item in raw.split(',') if item.strip()]


@app.command(help='在测试集上计算评估指标')
@handle_errors
@log_command('evaluate')
def evaluate(
    model_path: Path = typer.Argument(..., help='模型文件路径'),
    test_data_path: Path = typer.Argument(..., help='测试数据文件路径'),
    metrics: str | None = typer.Option(
        'rmse,mae,r2', '--metrics', '-m', help='评估指标列表'
    ),
    output_path: Path | None = typer.Option(
        None, '--output', '-o', help='评估结果输出文件路径'
    ),
) -> None:
    """在测试集上计算评估指标."""
    log.info(f'评估模型: {model_path} (测试数据: {test_data_path})')
    metrics_list = _parse_list(metrics)
    result = evaluate_model(
        model_path=model_path,
        test_data_path=test_data_path,
        metrics=metrics_list,
        output_path=output_path,
    )
    log.info(f'评估结果:\n{json.dumps(result, ensure_ascii=False, indent=2)}')


@app.command(help='输出残差分析图表')
@handle_errors
@log_command('residuals')
def residuals(
    model_path: Path = typer.Argument(..., help='模型文件路径'),
    test_data_path: Path = typer.Argument(..., help='测试数据文件路径'),
    output_dir: Path = typer.Argument(..., help='图表输出目录'),
    plot_types: str | None = typer.Option(
        'histogram,scatter', '--plots', '-p', help='图表类型列表'
    ),
) -> None:
    """输出残差分析图表."""
    log.info(f'残差分析: {model_path} -> {output_dir}')
    plot_types_list = _parse_list(plot_types)
    analyze_residuals(
        model_path=model_path,
        test_data_path=test_data_path,
        output_dir=output_dir,
        plot_types=plot_types_list,
    )


@app.command(help='对比两个或多个已保存模型的性能')
@handle_errors
@log_command('compare')
def compare(
    model_paths: str | None = typer.Option(
        None, '--models', '-M', help='模型文件路径列表JSON字符串'
    ),
    test_data_path: Path = typer.Argument(..., help='测试数据文件路径'),
    metrics: str | None = typer.Option(
        'rmse,mae,r2', '--metrics', '-m', help='评估指标列表'
    ),
    output_path: Path | None = typer.Option(
        None, '--output', '-o', help='对比结果输出文件路径'
    ),
) -> None:
    """对比两个或多个已保存模型的性能."""
    log.info(f'模型对比: {test_data_path}')
    model_paths_list = _parse_model_paths(model_paths)
    metrics_list = _parse_list(metrics)
    result = compare_models(
        model_paths=model_paths_list,
        test_data_path=test_data_path,
        metrics=metrics_list,
        output_path=output_path,
    )
    log.info(f'对比结果:\n{json.dumps(result, ensure_ascii=False, indent=2)}')


def _parse_model_paths(raw: str | None) -> list[Path]:
    """解析以逗号分隔的模型路径列表."""
    if raw is None:
        return []
    return [Path(p.strip()) for p in raw.split(',') if p.strip()]
