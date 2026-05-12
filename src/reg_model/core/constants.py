#!/usr/bin/env python
# Copyright (c) 2026--2030. Wang Weihua
# All rights reserved.
"""应用软件的常量定义."""

from enum import StrEnum
from importlib import metadata
from pathlib import Path

from platformdirs import user_config_dir

__version__ = '0.1.0-20260508'
__project_name__ = 'reg_model'


# 软件包名称
PACKAGE_NAME = 'reg_model'
# 项目名称
PROJECT_NAME = __project_name__
# 项目描述
PROJECT_DESC = 'reg_model_回归分析'
# 项目根目录
ROOT_PATH = Path(__file__).parent.parent
# 缺省配置文件类型
DEFAULT_CONFIG_TYPE = 'toml'


# 环境类型
class EnvironmentType(StrEnum):
    """环境类型."""

    DEVELOPMENT = 'development'
    STAGING = 'staging'
    PRODUCTION = 'production'
    TESTING = 'testing'


# 日志级别
class LogLevel(StrEnum):
    """日志级别."""

    DEBUG = 'DEBUG'
    INFO = 'INFO'
    WARNING = 'WARNING'
    ERROR = 'ERROR'
    CRITICAL = 'CRITICAL'


# 数据库类型
class DatabaseType(StrEnum):
    """数据库类型."""

    POSTGRESQL = 'postgresql'
    MYSQL = 'mysql'
    SQLITE = 'sqlite'


# 日志级别
class ConfigType(StrEnum):
    """配置类型."""

    TOML = 'toml'
    YAML = 'yaml'
    ENV = 'ENV'


def get_project_version(project_name=PROJECT_NAME) -> str:
    """动态读取项目版本号(pyproject.toml)."""
    try:
        # pyproject.toml 中定义的 project name
        return metadata.version(project_name)
    except metadata.PackageNotFoundError:
        # 提供一个合理的回退值。
        return __version__


def get_default_config_path(config_type: str = DEFAULT_CONFIG_TYPE) -> Path:
    """返回缺省配置文件路径."""
    default_config_file = f'{PROJECT_NAME}.{config_type}'
    config_dir = user_config_dir(PACKAGE_NAME, appauthor=False)
    return Path(config_dir) / default_config_file


# 项目版本
PROJECT_VERSION = get_project_version()
# 缺省配置文件
DEFAULT_CONFIG_PATH = get_default_config_path()
