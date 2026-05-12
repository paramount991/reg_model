#!/usr/bin/env python
# Copyright (c) 2026--2030. Wang Weihua
# All rights reserved.
"""使用回调函数实现全局选项."""

from pathlib import Path
import sys

import typer
from pydantic import BaseModel, ConfigDict

from reg_model.core import constants as const
from reg_model.core.config.settings import load_settings
from reg_model.core.log import init_logging


class GlobalOptions(BaseModel):
    """命令行全局选项快照."""

    model_config = ConfigDict(frozen=True, extra='forbid')

    config_file: str | None
    log_file: str | None
    msg_level: const.LogLevel
    verbose: bool
    quiet: bool


def version_callback(value: bool):
    """版本回调."""
    if value:
        typer.echo(f'{const.PROJECT_DESC} V{const.PROJECT_VERSION}')
        raise typer.Exit()


# 全局主回调
def global_options(
    ctx: typer.Context,
    config_file: str | None = typer.Option(
        str(const.DEFAULT_CONFIG_PATH),
        '--config',
        help='指定配置文件',
        rich_help_panel='全局选项',
    ),
    log_file: str | None = typer.Option(
        None,
        '--logfile',
        metavar='FILE',
        help='日志文件',
        rich_help_panel='全局选项',
    ),
    msg_level: const.LogLevel = typer.Option(
        const.LogLevel.INFO,
        '--msglevel',
        '-m',
        metavar='LEVEL',
        help='日志级别',
        rich_help_panel='全局选项',
    ),
    verbose: bool = typer.Option(
        False,
        '--verbose',
        help='详细日志',
        rich_help_panel='全局选项',
    ),
    quiet: bool = typer.Option(
        False, '--quiet', help='安静模式', rich_help_panel='全局选项'
    ),
    version: bool = typer.Option(
        None,
        '--version',
        '-V',
        callback=version_callback,
        is_eager=True,
        help='显示版本信息',
        rich_help_panel='全局选项',
    ),
):
    """全局选项:所有子命令都能显示."""
    # 根据 verbose 和 quiet 覆盖日志级别
    if verbose:
        msg_level = const.LogLevel.DEBUG
    elif quiet:
        msg_level = const.LogLevel.ERROR

    # 存入上下文,所有子命令共享
    ctx.obj = GlobalOptions(
        config_file=config_file,
        log_file=log_file,
        msg_level=str(msg_level),
        verbose=verbose,
        quiet=quiet,
    )

    # 获取当前子命令
    sub_command = ctx.invoked_subcommand
    if sub_command is None:
        # 没传子命令,则显示帮助
        typer.echo('请使用子命令 help 查看帮助')
        raise typer.Exit()

    # 子命令不是 config
    if sub_command not in ['config', 'help', 'version']:
        typer.echo(f'加载配置文件{config_file}')
        cfg = load_settings(config_file)

        log_file_path = log_file
        if (
            log_file_path is None
            and cfg.log.dir_name is not None
            and cfg.log.file_name is not None
        ):
            log_file_path = Path(cfg.log.dir_name) / cfg.log.file_name

        log_config = cfg.log.model_dump()
        log_config['file_path'] = str(log_file_path)
        log_config['level'] = str(msg_level)
        typer.echo(f'设置日志记录器:{log_config}')
        init_logging(log_config)