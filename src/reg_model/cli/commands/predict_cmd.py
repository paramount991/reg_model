#!/usr/bin/env python
# Copyright (c) 2026--2030. Wang Weihua
# All rights reserved.
from pathlib import Path

import typer

from reg_model.core import handle_errors, log_command
from reg_model.core.log import get_logger
from reg_model.predict import (
    explain_prediction,
    predict_batch,
)

log = get_logger()
app = typer.Typer(help='预测')


@app.command(help='批量预测并输出 CSV/Excel')
@handle_errors
@log_command('predict')
def predict(
    model_path: Path = typer.Argument(..., help='模型文件路径'),
    data_path: Path = typer.Argument(..., help='预测数据文件路径'),
    output_path: Path = typer.Argument(..., help='预测结果输出文件路径'),
    output_format: str = typer.Option('csv', '--format', '-f', help='输出格式'),
) -> None:
    """批量预测并输出 CSV/Excel."""
    log.info(f'批量预测: {model_path} -> {output_path} (格式: {output_format})')
    predict_batch(
        model_path=model_path,
        data_path=data_path,
        output_path=output_path,
        format=output_format,
    )


@app.command(help='对给定样本输出 SHAP 等解释')
@handle_errors
@log_command('explain')
def explain(
    model_path: Path = typer.Argument(..., help='模型文件路径'),
    sample_data_path: Path = typer.Argument(..., help='样本数据文件路径'),
    output_path: Path = typer.Argument(..., help='解释结果输出文件路径'),
    method: str = typer.Option('shap', '--method', '-m', help='解释方法'),
) -> None:
    """对给定样本输出 SHAP 等解释."""
    log.info(f'预测解释: {model_path} -> {output_path} (方法: {method})')
    explain_prediction(
        model_path=model_path,
        sample_data_path=sample_data_path,
        output_path=output_path,
        method=method,
    )
