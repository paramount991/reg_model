#!/usr/bin/env python
# Copyright (c) 2026--2030. Wang Weihua
# All rights reserved.
"""CLI 应用程序."""

import typer

from reg_model.core import constants as const

from .callbacks.global_options import global_options
from .commands.config_cmd import app as config_app
from .commands.data_cmd import app as data_app
# from .commands.evaluate_cmd import app as evaluate_app
# from .commands.feature_cmd import app as feature_app
# from .commands.model_cmd import app as model_app
# from .commands.predict_cmd import app as predict_app
# from .commands.serve_cmd import app as serve_app
# from .commands.train_cmd import app as train_app
from .commands.version_cmd import app as version_app
# from .commands.viz_cmd import app as viz_app

app = typer.Typer(
    no_args_is_help=True, help=const.PROJECT_DESC, callback=global_options
)

app.add_typer(config_app, name='config', help='配置文件管理')
app.add_typer(data_app, name='data', help='数据文件管理')
# app.add_typer(evaluate_app, name='evaluate', help='模型评估')
# app.add_typer(feature_app, name='feature', help='特征工程')
# app.add_typer(model_app, name='model', help='模型管理')
# app.add_typer(predict_app, name='predict', help='预测')
# app.add_typer(serve_app, name='serve', help='服务部署')
# app.add_typer(train_app, name='train', help='模型训练')
app.add_typer(version_app, help='显示版本信息')
# app.add_typer(viz_app, name='viz', help='可视化')
