#!/usr/bin/env python
# Copyright (c) 2026--2030. Wang Weihua
# All rights reserved.
"""version: 版本信息子命令."""

import typer

from reg_model.core import constants as const

app = typer.Typer()


@app.command()
def version():  # noqa: D103
    typer.echo(f"{const.PROJECT_DESC} V{const.PROJECT_VERSION}")
