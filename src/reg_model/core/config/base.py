#!/usr/bin/env python
# Copyright (c) 2026--2030. Wang Weihua
# All rights reserved.
"""配置管理-环境配置."""

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

from reg_model.core.constants import EnvironmentType


class BaseConfig(BaseSettings):
    """基础配置类."""

    # 配置 Pydantic 行为
    model_config = SettingsConfigDict(
        case_sensitive=False,
        extra='ignore',  # 忽略多余的字段
        validate_default=True,
        arbitrary_types_allowed=True,
    )


class EnvironmentConfig(BaseConfig):
    """环境配置."""

    # 运行环境
    environment: EnvironmentType = Field(
        default=EnvironmentType.DEVELOPMENT,
        description='运行环境',
        validation_alias='APP_ENV',
    )

    # 调试模式
    debug: bool = Field(
        default=False, description='调试模式', validation_alias='APP_DEBUG'
    )

    def is_development(self) -> bool:
        """判断是否为开发环境."""
        return self.environment == EnvironmentType.DEVELOPMENT

    def is_production(self) -> bool:
        """判断是否为生产环境."""
        return self.environment == EnvironmentType.PRODUCTION

    def is_testing(self) -> bool:
        """判断是否为测试环境."""
        return self.environment == EnvironmentType.TESTING

    def is_staging(self) -> bool:
        """判断是否为预发布环境."""
        return self.environment == EnvironmentType.STAGING
