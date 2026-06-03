#!/usr/bin/env python
# Copyright (c) 2026--2030. Wang Weihua
# All rights reserved.
from pathlib import Path

import typer

from reg_model.core import handle_errors, log_command
from reg_model.core.log import get_logger
from reg_model.feature import (
    generate_features,
    list_features,
    select_features,
    transform_features,
)

log = get_logger()
app = typer.Typer(help='特征工程')


@app.command(help='列出当前使用的特征及类型', name='list')
@handle_errors
@log_command('list')
def list_features_cmd(
    data_path: Path = typer.Argument(..., help='数据文件路径'),
    config_path: Path | None = typer.Option(
        None, '--config', '-c', help='特征配置文件路径'
    ),
) -> None:
    """列出当前使用的特征及类型."""
    log.info(f'列出特征: {data_path}')
    result = list_features(data_path=data_path, config_path=config_path)
    if result:
        for name, ftype in result.items():
            typer.echo(f'  {name}: {ftype}')
    else:
        typer.echo('  未找到特征')


@app.command(help='根据预定义配方生成新特征')
@handle_errors
@log_command('generate')
def generate(
    data_path: Path = typer.Argument(..., help='输入数据文件路径'),
    output_path: Path = typer.Argument(..., help='输出特征数据路径'),
    recipe: str = typer.Option('default', '--recipe', '-r', help='特征生成配方名称'),
    config_path: Path | None = typer.Option(
        None, '--config', '-c', help='配方配置文件路径'
    ),
) -> None:
    """根据预定义配方生成新特征(例如多项式、日期分解)."""
    log.info(f'生成特征: {data_path} -> {output_path} (配方: {recipe})')
    generate_features(
        data_path=data_path,
        output_path=output_path,
        recipe=recipe,
        config_path=config_path,
    )


@app.command(help='执行特征选择算法并保留选中特征')
@handle_errors
@log_command('select')
def select(
    data_path: Path = typer.Argument(..., help='输入数据文件路径'),
    output_path: Path = typer.Argument(..., help='输出特征数据路径'),
    method: str = typer.Option('correlation', '--method', '-m', help='特征选择方法'),
    target_column: str | None = typer.Option(None, '--target', '-t', help='目标列名'),
    n_features: int | None = typer.Option(
        None, '--n-features', '-n', help='要保留的特征数量'
    ),
) -> None:
    """执行特征选择算法并保留选中特征."""
    log.info(f'特征选择: {data_path} -> {output_path} (方法: {method})')
    select_features(
        data_path=data_path,
        output_path=output_path,
        method=method,
        target_column=target_column,
        n_features=n_features,
    )


@app.command(help='应用标准化/归一化等变换')
@handle_errors
@log_command('transform')
def transform(
    data_path: Path = typer.Argument(..., help='输入数据文件路径'),
    output_path: Path = typer.Argument(..., help='输出变换后数据路径'),
    method: str = typer.Option('standardize', '--method', '-m', help='变换方法'),
    config_path: Path | None = typer.Option(
        None, '--config', '-c', help='变换配置文件路径'
    ),
) -> None:
    """应用标准化/归一化等变换."""
    log.info(f'特征变换: {data_path} -> {output_path} (方法: {method})')
    transform_features(
        data_path=data_path,
        output_path=output_path,
        method=method,
        config_path=config_path,
    )
