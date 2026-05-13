#!/usr/bin/env python
# Copyright (c) 2026--2030. Wang Weihua
# All rights reserved.
"""配置管理-应用核心配置."""

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

from reg_model.core.constants import PROJECT_DESC, PROJECT_NAME, PROJECT_VERSION

# 环境变量前缀
ENV_PREFIX = 'APP_'


class AppConfig(BaseSettings):
    """应用核心配置."""

    model_config = SettingsConfigDict(env_prefix=ENV_PREFIX, extra='ignore')

    # 应用基本信息
    name: str = Field(
        default=PROJECT_NAME, description='应用名称', validation_alias='APP_NAME'
    )
    version: str = Field(
        default=PROJECT_VERSION, description='应用版本',validation_alias='APP_VERSION'
    )
    description: str = Field(
        default=PROJECT_DESC, description='应用描述',  validation_alias='APP_DESCRIPTION'
    )
