#!/usr/bin/env python
# Copyright (c) 2026--2030. Wang Weihua
# All rights reserved.
"""CLI 应用程序."""

import typer

from reg_model.core import constants as const

from .callbacks.global_options import global_options
from .commands.config_cmd import app as config_app
from .commands.data_cmd import app as data_app
from .commands.version_cmd import app as version_app

app = typer.Typer(
    no_args_is_help=True, help=const.PROJECT_DESC, callback=global_options
)

app.add_typer(config_app, name='config', help='配置文件管理')
app.add_typer(version_app, help='显示版本信息')
app.add_typer(data_app, name='data', help='显示数据信息')
