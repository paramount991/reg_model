#!/usr/bin/env python
# Copyright (c) 2026--2030. Wang Weihua
# All rights reserved.
"""Typer 主应用,注册所有子命令."""

from typer import Typer

from .commands import (
    config_app,
    data_app,
    evaluate_app,
    feature_app,
    model_app,
    predict_app,
    serve_app,
    train_app,
    version_app,
    viz_app,
)

app = Typer(pretty_exceptions_show_locals=False)

app.add_typer(config_app, name='config')
app.add_typer(data_app, name='data')
app.add_typer(evaluate_app, name='evaluate')
app.add_typer(feature_app, name='feature')
app.add_typer(model_app, name='model')
app.add_typer(predict_app, name='predict')
app.add_typer(serve_app, name='serve')
app.add_typer(train_app, name='train')
app.add_typer(version_app, name='version')
app.add_typer(viz_app, name='viz')
