#!/usr/bin/env python
# Copyright (c) 2026--2030. Wang Weihua
# All rights reserved.
"""配置管理-日志配置."""

from pydantic import Field
from pydantic_settings import SettingsConfigDict

from reg_model.core.constants import LogLevel

from .base import BaseConfig

# 环境变量前缀
ENV_PREFIX = 'LOG_'


class LogConfig(BaseConfig):
    """日志配置."""

    model_config = SettingsConfigDict(env_prefix=ENV_PREFIX, validate_default=False)

    # 日志级别
    level: LogLevel = Field(
        default=LogLevel.INFO, description='日志级别',  # validation_alias='LOG_LEVEL'  # 注释掉以支持 TOML 直接加载
    )

    # 日志格式
    format: str = Field(
        default='json', description='日志格式(json/text)',  # validation_alias='LOG_FORMAT'  # 注释掉以支持 TOML 直接加载
    )

    # 日志输出
    output: str = Field(
        default='console',
        description='日志输出(console/file/both)',
        # validation_alias='LOG_OUTPUT'  # 注释掉以支持 TOML 直接加载,
    )

    # 日志文件目录 (环境变量: LOG_DIR_NAME)
    dir_name: str = Field(default='logs', description='日志文件所在目录')
    # 日志文件名 (环境变量: LOG_FILE_NAME)
    file_name: str = Field(default='app.log', description='日志文件名')

    # 日志轮转
    max_bytes: int = Field(
        default=10 * 1024 * 1024,  # 10MB
        description='最大文件大小',
        # validation_alias='LOG_MAX_BYTES'  # 注释掉以支持 TOML 直接加载,
    )

    backup_count: int = Field(
        default=5, description='备份文件数量',  # validation_alias='LOG_BACKUP_COUNT'  # 注释掉以支持 TOML 直接加载
    )
