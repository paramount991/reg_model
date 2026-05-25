#!/usr/bin/env python
# Copyright (c) 2026--2030. Wang Weihua
# All rights reserved.
"""配置序列化工具."""

from pathlib import Path
from typing import Any

import tomli_w

from reg_model.core import constants as const


def save_config_file(data: dict[str, Any], file_path: str | Path) -> None:
    """保存数据到配置文件.

    调用方应已通过 model_dump(mode='json') 确保数据为 TOML 兼容类型.
    """
    file_path = Path(file_path)
    file_path.parent.mkdir(parents=True, exist_ok=True)
    with open(file_path, 'wb') as f:
        tomli_w.dump(data, f)


def save_default_config(
    file_path: str | Path,
    file_type: const.ConfigType = const.ConfigType.TOML,
    overwrite: bool = False,
    exclude_unset: bool = False,
    exclude_defaults: bool = False,
) -> Path:
    """生成缺省配置文件,使用配置类的默认值."""
    from .settings import Settings

    file_path = Path(file_path)
    if file_path.exists() and not overwrite:
        raise FileExistsError(f'文件已存在: {file_path}')
    instance = Settings.model_construct()
    data = instance.model_dump(
        mode='json',
        exclude_unset=exclude_unset,
        exclude_defaults=exclude_defaults,
        exclude_none=True,
    )
    save_config_file(data, file_path)
    return file_path
