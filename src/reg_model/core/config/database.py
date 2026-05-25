#!/usr/bin/env python
# Copyright (c) 2026--2030. Wang Weihua
# All rights reserved.
"""配置管理-数据库配置."""

import warnings

from pydantic import Field, ValidationInfo, field_validator
from pydantic_settings import SettingsConfigDict

from reg_model.core.constants import DatabaseType

from .base import BaseConfig

# 环境变量前缀
ENV_PREFIX = 'DB_'


class DatabaseConfig(BaseConfig):
    """数据库配置."""

    model_config = SettingsConfigDict(env_prefix=ENV_PREFIX)

    # 数据库类型 (环境变量: DB_TYPE)
    type: DatabaseType = Field(
        default=DatabaseType.POSTGRESQL, description='数据库类型'
    )

    # 连接信息
    host: str = Field(default='localhost', description='数据库主机')
    port: int = Field(default=5432, description='数据库端口')
    username: str = Field(default='postgres', description='数据库用户名')
    password: str = Field(default='', description='数据库密码')
    database: str = Field(default='app', description='数据库名称')

    # 连接池配置
    pool_size: int = Field(default=20, description='连接池大小')
    max_overflow: int = Field(default=10, description='最大溢出连接数')
    pool_timeout: int = Field(default=30, description='连接池超时(秒)')
    pool_recycle: int = Field(default=3600, description='连接回收时间(秒)')

    # 连接 URL
    @property
    def url(self) -> str:
        """获取数据库连接URL."""
        if self.type == DatabaseType.POSTGRESQL:
            return f'postgresql://{self.username}:{self.password}@{self.host}:{self.port}/{self.database}'
        elif self.type == DatabaseType.MYSQL:
            return f'mysql://{self.username}:{self.password}@{self.host}:{self.port}/{self.database}'
        elif self.type == DatabaseType.SQLITE:
            return f'sqlite:///{self.database}.db'
        else:
            raise ValueError(f'Unsupported database type: {self.type}')

    @field_validator('port')
    def validate_port(cls, v: int, info: ValidationInfo) -> int:
        """根据数据库类型验证端口."""
        db_type = info.data.get('type')
        if db_type == DatabaseType.POSTGRESQL and v != 5432:
            # 允许非默认端口
            warnings.warn(f'非默认端口: {v}', stacklevel=2)
        elif db_type == DatabaseType.MYSQL and v != 3306:
            # 允许非默认端口
            warnings.warn(f'非默认MySQL端口: {v}', stacklevel=2)
        return v
