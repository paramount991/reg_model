#!/usr/bin/env python
# Copyright (c) 2026--2030. Wang Weihua
# All rights reserved.
"""CLI 全局选项解析."""

import typer
from pydantic import BaseModel, ConfigDict

from reg_model.core import constants as const

from .bootstrap import bootstrap_app


class GlobalOptions(BaseModel):
    """命令行全局选项快照, 存入 ctx.obj 供子命令读取."""

    model_config = ConfigDict(frozen=True, extra='forbid')

    config_file: str | None
    log_file: str | None
    msg_level: const.LogLevel
    verbose: bool
    quiet: bool


def _version_callback(value: bool) -> None:
    """--version / -V 回调."""
    if value:
        typer.echo(f'{const.PROJECT_DESC} V{const.PROJECT_VERSION}')
        raise typer.Exit()


def _resolve_log_level(
    verbose: bool,
    quiet: bool,
    cli_level: const.LogLevel,
) -> const.LogLevel:
    """根据 --verbose / --quiet 覆写日志级别."""
    if verbose:
        return const.LogLevel.DEBUG
    if quiet:
        return const.LogLevel.ERROR
    return cli_level


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
        callback=_version_callback,
        is_eager=True,
        help='显示版本信息',
        rich_help_panel='全局选项',
    ),
) -> None:
    """全局选项回调: 解析参数, 存入上下文, 按需启动应用."""
    msg_level = _resolve_log_level(verbose, quiet, msg_level)

    ctx.obj = GlobalOptions(
        config_file=config_file,
        log_file=log_file,
        msg_level=msg_level,
        verbose=verbose,
        quiet=quiet,
    )

    sub_command = ctx.invoked_subcommand
    if sub_command is None:
        typer.echo('请使用子命令 help 查看帮助')
        raise typer.Exit()

    if sub_command not in ('config', 'version'):
        typer.echo(f'加载配置文件 {config_file}')
        bootstrap_app(
            config_file=config_file,
            msg_level=msg_level,
            log_file=log_file,
        )
