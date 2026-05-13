#!/usr/bin/env python
# Copyright (c) 2026--2030. Wang Weihua
# All rights reserved.
"""CLI 应用程序."""

import typer

from reg_model.core import constants as const

from .callbacks.global_options import global_options
from reg_model.cli.commands.config_cmd import app as config_app
from reg_model.cli.commands.help_cmd import app as help_app
from reg_model.cli.commands.version_cmd import app as version_app
from reg_model.cli.commands.data_cmd import app as data_app

app = typer.Typer(
    no_args_is_help=True, help=const.PROJECT_DESC, callback=global_options
)

app.add_typer(config_app, name='config', help='配置文件管理')
app.add_typer(version_app, help='显示版本信息')
app.add_typer(help_app, help='显示帮助信息')
app.add_typer(data_app, help='显示数据信息')
