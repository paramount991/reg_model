#!/usr/bin/env python
# Copyright (c) 2026--2030. Wang Weihua
# All rights reserved.
"""配置文件管理-主配置类."""

from datetime import date, datetime
from decimal import Decimal
from enum import Enum
from functools import lru_cache
from pathlib import Path
from typing import Any

import tomli as tomllib
import tomli_w
from pydantic import Field, model_validator, ValidationError
from pydantic_settings import BaseSettings, SettingsConfigDict, PydanticBaseSettingsSource, TomlConfigSettingsSource

from reg_model.core import constants as const

from .app import AppConfig
from .base import EnvironmentConfig
from .database import DatabaseConfig
from .log import LogConfig

# 环境变量前缀
ENV_PREFIX = 'RegModel_'


class Settings(BaseSettings):
    """主配置类:聚合所有模块化配置."""

    model_config = SettingsConfigDict(
        case_sensitive=False,
        extra='ignore',
        validate_default=True,
        env_prefix=ENV_PREFIX,  # 环境变量前缀
        # 支持嵌套配置的环境变量覆盖
        env_nested_delimiter='_',  # 例如: DATABASE__HOST
    )

    # 应用配置
    app: AppConfig = Field(default_factory=AppConfig, description='应用配置')

    # 环境配置
    env: EnvironmentConfig = Field(
        default_factory=EnvironmentConfig, description='环境配置'
    )

    # 日志配置
    log: LogConfig = Field(default_factory=LogConfig, description='日志配置')

    # 数据库配置
    db: DatabaseConfig = Field(default_factory=DatabaseConfig, description='数据库配置')

    # 额外的自定义配置
    extra_config: dict[str, Any] = Field(default_factory=dict, description='额外配置')

    @model_validator(mode='after')
    def validate_environment_specific(self) -> 'Settings':
        """环境特定的验证."""
        if self.env.is_production():
            # 生产环境验证
            if self.env.debug:
                raise ValueError('生产环境不能启用调试模式')

            if self.db.host in ['localhost', '127.0.0.1']:
                # 警告但不阻止
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
                # 隐藏敏感字段
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
    @classmethod
    def from_toml(cls, toml_path: str | Path) -> 'Settings':
        """加载指定配置文件 (TOML).

        优先级：init 参数 > 环境变量 > TOML > 字段默认值.
        """
        # 直接从 TOML 文件加载配置数据
        import tomli
        with open(toml_path, 'rb') as f:
            toml_data = tomli.load(f)
        
        # 使用 model_validate 创建实例
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
        """指定配置优先级.

        优先级: 代码传入 > 环境变量 > TOML > 内置默认.
        """
        return (
            init_settings,
            env_settings,
            TomlConfigSettingsSource(settings_cls),
            file_secret_settings,
        )

# 内部使用的配置类
_ConfigClass = Settings
_current_settings: Settings | None = None


# 配置加载函数
@lru_cache(maxsize=1)
def load_settings(
    file_path: str | Path,
    encoding: str = 'utf-8',
) -> Settings:
    """从配置文件加载设置.

    Args:
        file_path: 配置文件路径
        encoding: 文件编码

    Returns:
        配置实例(同时缓存为当前激活的配置)

    Raises:
        FileNotFoundError: 文件不存在
        ValueError: 不支持的文件类型或解析错误
        ImportError: 缺少必要依赖
    """
    # 如果没有提供配置路径,使用默认路径
    global _current_settings

    file_path = Path(file_path)
    if not file_path.exists():
        raise FileNotFoundError(f'配置文件不存在: {file_path}')

    # 从配置文件创建配置实例
    try:
        instance = _ConfigClass.from_toml(file_path)
    except ValidationError as e:
        print(f'配置文件解析错误: {e}')
    except Exception as e:
        raise Exception(f'配置文件加载错误: {e}') from None

    _current_settings = instance

    return instance

@lru_cache(maxsize=1)
def get_settings(
    file_path: str | Path | None = None,
) -> Settings:
    """创建并返回一个配置实例.

    使用 @lru_cache 装饰器实现:
    1. 性能: 配置只在应用启动时被加载和解析一次。
    2. 一致性 (单例): 应用的任何部分调用此函数都将获得完全相同的配置对象实例。

    Args:
        file_path: 配置文件路径
    """
    global _current_settings

    if file_path is not None:
        load_settings(file_path)

    return _current_settings


def _sanitize_for_toml(obj: Any) -> Any:
    """转为 tomli-w 可写入的值:去掉 None,Path/Enum/日期等转为可编码类型."""
    if obj is None:
        return None
    if isinstance(obj, dict):
        out: dict[str, Any] = {}
        for k, v in obj.items():
            if v is None:
                continue
            sv = _sanitize_for_toml(v)
            if sv is None:
                continue
            out[str(k)] = sv
        return out
    if isinstance(obj, (list, tuple)):
        return [_sanitize_for_toml(v) for v in obj if v is not None]
    if isinstance(obj, Path):
        return str(obj)
    if isinstance(obj, Enum):
        return obj.value
    if isinstance(obj, Decimal):
        return float(obj)
    if isinstance(obj, (datetime, date)):
        return obj.isoformat()
    if isinstance(obj, (str, int, float, bool)):
        return obj
    return str(obj)


def save_default_config(
    file_path: str | Path,
    file_type: const.ConfigType = const.ConfigType.TOML,
    overwrite: bool = False,
    exclude_unset: bool = False,
    exclude_defaults: bool = False,
) -> Path:
    """生成缺省配置文件,使用配置类的默认值."""
    file_path = Path(file_path)
    if file_path.exists() and not overwrite:
        raise FileExistsError(f'文件已存在: {file_path}')

    # 避免校验必填字段
    instance = _ConfigClass.model_construct()
    # mode=json:让 Path/StrEnum 等转为 TOML 友好类型
    data = instance.model_dump(
        mode='json',
        exclude_unset=exclude_unset,
        exclude_defaults=exclude_defaults,
        exclude_none=True,
    )

    save_config_file(data, file_path)
    return file_path


def clear_settings() -> None:
    """清除当前配置."""
    global _current_settings
    _current_settings = None


def save_config_file(data: dict[str, Any], file_path: str | Path) -> None:
    """保存数据到配置文件(写入前做 TOML 安全清洗)."""
    # 创建目录
    file_path = Path(file_path)
    file_path.parent.mkdir(parents=True, exist_ok=True)

    safe = _sanitize_for_toml(data)
    if not isinstance(safe, dict):
        safe = {}

    if tomli_w is None:
        raise ImportError('写入 TOML 需要安装 tomli-w: pip install tomli-w')
    with open(file_path, 'wb') as f:
        tomli_w.dump(safe, f)