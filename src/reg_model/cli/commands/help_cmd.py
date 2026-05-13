#!/usr/bin/env python
# Copyright (c) 2026--2030. Wang Weihua
# All rights reserved.
"""help: 帮助信息子命令."""

import click
import typer

app = typer.Typer()


@app.command(name='help', help='显示帮助信息')
def help_command(
    ctx: typer.Context,
    command: str | None = typer.Argument(None, help='要查看帮助的子命令名称'),
):
    """显示帮助信息."""
    # 根上下文对应整个命令行程序
    root_ctx = ctx.find_root()
    root_group = root_ctx.command

    if command is None:
        typer.echo(root_group.get_help(root_ctx))
    else:
        sub_command = root_group.get_command(root_ctx, command)
        if sub_command:
            sub_ctx = click.Context(sub_command, info_name=command, parent=root_ctx)
            typer.echo(sub_command.get_help(sub_ctx))
        else:
            typer.echo(f"子命令 '{command}' 不存在")
