#!/usr/bin/env python
# Copyright (c) 2026--2030. Wang Weihua
# All rights reserved.
"""配置文件管理-主配置类."""

from pathlib import Path
from typing import Any

import tomli
from pydantic import Field, ValidationError, model_validator
from pydantic_settings import (
    BaseSettings,
    PydanticBaseSettingsSource,
    SettingsConfigDict,
    TomlConfigSettingsSource,
)
from pydantic_settings.sources import EnvSettingsSource

from .app import AppConfig
from .base import EnvironmentConfig
from .database import DatabaseConfig
from .log import LogConfig

# 环境变量前缀
ENV_PREFIX = 'RegModel_'

# 模块级单例缓存
_current_settings: 'Settings | None' = None


class Settings(BaseSettings):
    """主配置类: 聚合所有模块化配置."""

    model_config = SettingsConfigDict(
        case_sensitive=False,
        extra='ignore',
        validate_default=True,
        env_prefix=ENV_PREFIX,
        env_nested_delimiter='_',
    )

    app: AppConfig = Field(default_factory=AppConfig, description='应用配置')
    env: EnvironmentConfig = Field(
        default_factory=EnvironmentConfig, description='环境配置'
    )
    log: LogConfig = Field(default_factory=LogConfig, description='日志配置')
    db: DatabaseConfig = Field(default_factory=DatabaseConfig, description='数据库配置')
    extra_config: dict[str, Any] = Field(default_factory=dict, description='额外配置')

    @model_validator(mode='after')
    def validate_environment_specific(self) -> 'Settings':
        """环境特定的验证."""
        if self.env.is_production():
            if self.env.debug:
                raise ValueError('生产环境不能启用调试模式')
            if self.db.host in ['localhost', '127.0.0.1']:
                print('警告: 生产环境使用本地数据库')
        return self

    def get_database_url(self) -> str:
        """获取数据库URL."""
        return self.db.url

    def dict_without_sensitive(self) -> dict[str, Any]:
        """返回不含敏感信息的配置字典."""
        config_dict = self.model_dump()

        def remove_sensitive(data: Any) -> Any:
            if isinstance(data, dict):
                sensitive_keys = ['password', 'secret', 'key', 'token']
                return {
                    k: '********'
                    if any(s in k.lower() for s in sensitive_keys)
                    else remove_sensitive(v)
                    for k, v in data.items()
                }
            elif isinstance(data, list):
                return [remove_sensitive(item) for item in data]
            return data

        return remove_sensitive(config_dict)

    @classmethod
    def from_toml(cls, toml_path: str | Path) -> 'Settings':
        """加载 TOML 配置文件, 环境变量自动覆盖同名配置项."""
        with open(toml_path, 'rb') as f:
            toml_data = tomli.load(f)
        env_overrides = _read_env_overrides()
        if env_overrides:
            toml_data = _deep_merge(toml_data, env_overrides)
        return cls.model_validate(toml_data)

    @classmethod
    def settings_customise_sources(
        cls,
        settings_cls: type[BaseSettings],
        init_settings: PydanticBaseSettingsSource,
        env_settings: PydanticBaseSettingsSource,
        dotenv_settings: PydanticBaseSettingsSource,
        file_secret_settings: PydanticBaseSettingsSource,
    ) -> tuple[PydanticBaseSettingsSource, ...]:
        """配置来源优先级: 代码传入 > 环境变量 > .env > TOML > secrets."""
        return (
            init_settings,
            env_settings,
            dotenv_settings,
            TomlConfigSettingsSource(settings_cls),
            file_secret_settings,
        )


def _read_env_overrides() -> dict[str, Any]:
    """读取与 Settings 模型匹配的环境变量, 返回嵌套 dict.

    仅返回被环境变量覆盖的字段, 不包含默认值.
    """
    source = EnvSettingsSource(
        settings_cls=Settings,
        case_sensitive=False,
        env_prefix=ENV_PREFIX,
        env_nested_delimiter='_',
    )
    return source()


def _deep_merge(base: dict[str, Any], override: dict[str, Any]) -> dict[str, Any]:
    """深度合并两个字典, override 中的值优先."""
    result = base.copy()
    for key, value in override.items():
        if key in result and isinstance(result[key], dict) and isinstance(value, dict):
            result[key] = _deep_merge(result[key], value)
        else:
            result[key] = value
    return result


def load_settings(
    file_path: str | Path | None = None,
    override_path: str | Path | None = None,
) -> Settings:
    """从配置文件加载设置, 并缓存为当前激活配置.

    Args:
        file_path: 基础配置文件路径, None 则使用默认值.
        override_path: 覆盖配置文件, 深度合并到基础配置之上 (如 dev/prod 覆盖).
    """
    global _current_settings

    if file_path is None:
        settings: Settings = Settings()
    else:
        file_path = Path(file_path)
        if not file_path.exists():
            raise FileNotFoundError(f'配置文件不存在: {file_path}')
        try:
            settings = Settings.from_toml(file_path)
        except ValidationError as e:
            raise ValueError(f'配置文件解析错误: {e}') from e
        except Exception as e:
            raise ValueError(f'配置文件加载错误: {e}') from e

    if override_path is not None:
        override_path = Path(override_path)
        if not override_path.exists():
            raise FileNotFoundError(f'覆盖配置文件不存在: {override_path}')
        with open(override_path, 'rb') as f:
            override_data = tomli.load(f)
        merged = _deep_merge(settings.model_dump(mode='json'), override_data)
        settings = Settings.model_validate(merged)

    _current_settings = settings
    return settings


def get_settings(
    file_path: str | Path | None = None,
) -> Settings:
    """获取配置实例 (单例模式).

    首次调用返回默认配置或从文件加载, 后续返回缓存实例.
    传入 file_path 会强制重新加载.
    """
    global _current_settings

    if file_path is not None:
        return load_settings(file_path)

    settings = _current_settings
    if settings is None:
        settings = Settings()
        _current_settings = settings

    return settings


def clear_settings() -> None:
    """清除配置缓存, 下次调用 get_settings 将重新创建."""
    global _current_settings
    _current_settings = None
