#!/usr/bin/env python
# Copyright (c) 2026--2030. Wang Weihua
# All rights reserved.
"""模型训练子命令."""

import json
from pathlib import Path
from typing import Any

import typer

from reg_model.core import handle_errors, log_command
from reg_model.core.log import get_logger
from reg_model.train import (
    train_ensemble_model,
    train_model,
    train_with_cross_validation,
    tune_hyperparameters,
)

log = get_logger()
app = typer.Typer(help='模型训练')


def _parse_json(raw: str | None, label: str) -> Any:
    """安全解析 JSON 字符串."""
    if raw is None:
        return None
    try:
        return json.loads(raw)
    except json.JSONDecodeError as e:
        log.error(f'解析 {label} 失败: {e}')
        raise typer.BadParameter(f'无效的 JSON: {raw}') from e


@app.command(help='训练单个模型(可指定算法和超参数)')
@handle_errors
@log_command('train')
def train(
    data_path: Path = typer.Argument(..., help='训练数据文件路径'),
    model_path: Path = typer.Argument(..., help='模型保存路径'),
    algorithm: str = typer.Option(
        'linear_regression', '--algorithm', '-a', help='算法名称'
    ),
    hyperparameters: str | None = typer.Option(
        None, '--hyperparameters', '-H', help='超参数字典JSON字符串'
    ),
    target_column: str = typer.Option('target', '--target', '-t', help='目标列名'),
) -> None:
    """训练单个模型(可指定算法和超参数)."""
    log.info(f'训练模型: {data_path} -> {model_path} (算法: {algorithm})')
    hyperparams = _parse_json(hyperparameters, 'hyperparameters')
    result = train_model(
        data_path=data_path,
        model_path=model_path,
        algorithm=algorithm,
        hyperparameters=hyperparams,
        target_column=target_column,
    )
    _print_result(result)


@app.command(help='超参数调优(网格搜索/随机搜索)')
@handle_errors
@log_command('tune')
def tune(
    data_path: Path = typer.Argument(..., help='训练数据文件路径'),
    model_path: Path = typer.Argument(..., help='模型保存路径'),
    algorithm: str = typer.Option(
        'linear_regression', '--algorithm', '-a', help='算法名称'
    ),
    search_method: str = typer.Option('grid', '--method', '-m', help='搜索方法'),
    param_grid: str | None = typer.Option(
        None, '--param-grid', '-p', help='参数网格字典JSON字符串'
    ),
    target_column: str = typer.Option('target', '--target', '-t', help='目标列名'),
) -> None:
    """超参数调优(网格搜索/随机搜索)."""
    log.info(f'超参数调优: {data_path} -> {model_path} (方法: {search_method})')
    param_grid_parsed = _parse_json(param_grid, 'param_grid')
    result = tune_hyperparameters(
        data_path=data_path,
        model_path=model_path,
        algorithm=algorithm,
        search_method=search_method,
        param_grid=param_grid_parsed,
        target_column=target_column,
    )
    _print_result(result)


@app.command(help='带交叉验证的训练,输出验证分数')
@handle_errors
@log_command('cv')
def cv(
    data_path: Path = typer.Argument(..., help='训练数据文件路径'),
    model_path: Path = typer.Argument(..., help='模型保存路径'),
    algorithm: str = typer.Option(
        'linear_regression', '--algorithm', '-a', help='算法名称'
    ),
    cv_folds: int = typer.Option(5, '--folds', '-f', help='交叉验证折数'),
    hyperparameters: str | None = typer.Option(
        None, '--hyperparameters', '-H', help='超参数字典JSON字符串'
    ),
    target_column: str = typer.Option('target', '--target', '-t', help='目标列名'),
) -> None:
    """带交叉验证的训练,输出验证分数."""
    log.info(f'交叉验证训练: {data_path} -> {model_path} (折数: {cv_folds})')
    hyperparams = _parse_json(hyperparameters, 'hyperparameters')
    result = train_with_cross_validation(
        data_path=data_path,
        model_path=model_path,
        algorithm=algorithm,
        cv_folds=cv_folds,
        hyperparameters=hyperparams,
        target_column=target_column,
    )
    _print_result(result)


@app.command(help='训练集成模型(如 stacking)')
@handle_errors
@log_command('ensemble')
def ensemble(
    data_path: Path = typer.Argument(..., help='训练数据文件路径'),
    model_path: Path = typer.Argument(..., help='模型保存路径'),
    ensemble_method: str = typer.Option('stacking', '--method', '-m', help='集成方法'),
    base_models: str | None = typer.Option(
        None, '--base-models', '-b', help='基础模型列表JSON字符串'
    ),
    target_column: str = typer.Option('target', '--target', '-t', help='目标列名'),
) -> None:
    """训练集成模型(如 stacking)."""
    log.info(f'集成训练: {data_path} -> {model_path} (方法: {ensemble_method})')
    base_models_parsed = _parse_json(base_models, 'base_models')
    result = train_ensemble_model(
        data_path=data_path,
        model_path=model_path,
        ensemble_method=ensemble_method,
        base_models=base_models_parsed,
        target_column=target_column,
    )
    _print_result(result)


def _print_result(result: dict) -> None:
    """打印训练结果摘要."""
    import json as _json

    log.info(
        f'训练结果:\n{_json.dumps(result, ensure_ascii=False, indent=2, default=str)}'
    )
