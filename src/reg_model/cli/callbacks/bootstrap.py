#!/usr/bin/env python
# Copyright (c) 2026--2030. Wang Weihua
# All rights reserved.
"""应用启动: 加载配置并初始化日志."""

from pathlib import Path

from reg_model.core import constants as const
from reg_model.core.config.settings import Settings, load_settings
from reg_model.core.log import init_logging


def bootstrap_app(
    config_file: str | None = None,
    msg_level: const.LogLevel = const.LogLevel.INFO,
    log_file: str | None = None,
) -> Settings:
    """加载配置, 注入 CLI 覆盖, 初始化日志.

    优先级: CLI 参数 > 环境变量 > TOML 文件 > 默认值.
    """
    cfg = load_settings(config_file)

    # CLI 参数作为最高优先级覆盖
    cfg.log.level = msg_level

    # 日志文件路径
    log_file_path = log_file or (
        Path(cfg.log.dir_name) / cfg.log.file_name
        if cfg.log.dir_name and cfg.log.file_name
        else None
    )

    log_config = cfg.log.model_dump()
    log_config['file_path'] = str(log_file_path) if log_file_path else None
    init_logging(log_config)

    return cfg
