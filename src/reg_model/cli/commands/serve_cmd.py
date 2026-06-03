#!/usr/bin/env python
# Copyright (c) 2026--2030. Wang Weihua
# All rights reserved.
from pathlib import Path

import typer

from reg_model.core import handle_errors, log_command
from reg_model.core.log import get_logger
from reg_model.serve import (
    check_service_status,
    start_service,
    stop_service,
)

log = get_logger()
app = typer.Typer(help='服务部署')


@app.command(help='启动在线预测 API 服务')
@handle_errors
@log_command('start')
def start(
    model_path: Path = typer.Argument(..., help='模型文件路径'),
    host: str = typer.Option('localhost', '--host', '-H', help='服务主机地址'),
    port: int = typer.Option(8000, '--port', '-p', help='服务端口'),
    config_path: Path | None = typer.Option(
        None, '--config', '-c', help='服务配置文件路径'
    ),
) -> None:
    """启动在线预测 API 服务."""
    log.info(f'启动服务: {model_path} (地址: {host}:{port})')
    start_service(
        model_path=model_path,
        host=host,
        port=port,
        config_path=config_path,
    )


@app.command(help='停止服务')
@handle_errors
@log_command('stop')
def stop(
    service_id: str | None = typer.Argument(
        None, help='服务标识(PID),默认从PID文件读取'
    ),
) -> None:
    """停止服务."""
    log.info(f'停止服务: {service_id or "从PID文件"}')
    success = stop_service(service_id=service_id)
    if success:
        log.info('服务已停止')
    else:
        log.warning('没有正在运行的服务')


@app.command(help='查看服务状态')
@handle_errors
@log_command('status')
def status(
    service_id: str | None = typer.Argument(
        None, help='服务标识(PID),默认从PID文件读取'
    ),
) -> None:
    """查看服务状态."""
    result = check_service_status(service_id=service_id)
    log.info(f'状态: {result}')
