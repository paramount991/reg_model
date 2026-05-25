#!/usr/bin/env python
# Copyright (c) 2026--2030. Wang Weihua
# All rights reserved.
"""pytest 共享 fixtures."""

from collections.abc import Generator
from pathlib import Path

import pytest
import tomli_w

from reg_model.core.config.base import EnvironmentConfig
from reg_model.core.config.settings import Settings, clear_settings
from reg_model.core.constants import EnvironmentType


@pytest.fixture
def tmp_config_file(tmp_path: Path) -> Path:
    """在临时目录创建最小 TOML 配置文件."""
    data = {
        'app': {'name': 'test-app'},
        'env': {'environment': 'development', 'debug': False},
        'log': {'level': 'INFO'},
        'db': {
            'type': 'sqlite',
            'host': 'localhost',
            'port': 5432,
            'username': 'test',
            'password': 'secret123',
            'database': 'test_db',
        },
    }
    path = tmp_path / 'test_config.toml'
    with open(path, 'wb') as f:
        tomli_w.dump(data, f)
    return path


@pytest.fixture
def sample_settings() -> Settings:
    """返回默认 Settings 实例, 并确保单例干净."""
    clear_settings()
    return Settings()


@pytest.fixture
def prod_settings() -> Settings:
    """返回生产环境 Settings."""
    return Settings(
        env=EnvironmentConfig(
            environment=EnvironmentType.PRODUCTION, debug=False
        ),
    )


@pytest.fixture(autouse=True)
def _reset_settings() -> Generator[None, None, None]:
    """每个测试后自动清除 Settings 单例缓存."""
    yield
    clear_settings()
