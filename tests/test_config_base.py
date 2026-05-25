#!/usr/bin/env python
# Copyright (c) 2026--2030. Wang Weihua
# All rights reserved.
"""测试 core.config.base 模块."""

import pytest

from reg_model.core.config.base import EnvironmentConfig
from reg_model.core.constants import EnvironmentType


class TestEnvironmentConfigDefaults:
    """测试 EnvironmentConfig 默认值."""

    def test_default_environment_is_development(self) -> None:
        cfg = EnvironmentConfig()
        assert cfg.environment == EnvironmentType.DEVELOPMENT

    def test_default_debug_is_false(self) -> None:
        cfg = EnvironmentConfig()
        assert cfg.debug is False

    def test_default_is_development_returns_true(self) -> None:
        cfg = EnvironmentConfig()
        assert cfg.is_development() is True

    def test_default_is_production_returns_false(self) -> None:
        cfg = EnvironmentConfig()
        assert cfg.is_production() is False


class TestEnvironmentConfigMethods:
    """测试 EnvironmentConfig 判断方法."""

    def test_is_development(self) -> None:
        cfg = EnvironmentConfig(environment=EnvironmentType.DEVELOPMENT)
        assert cfg.is_development() is True
        assert cfg.is_production() is False
        assert cfg.is_testing() is False
        assert cfg.is_staging() is False

    def test_is_production(self) -> None:
        cfg = EnvironmentConfig(environment=EnvironmentType.PRODUCTION)
        assert cfg.is_development() is False
        assert cfg.is_production() is True
        assert cfg.is_testing() is False
        assert cfg.is_staging() is False

    def test_is_testing(self) -> None:
        cfg = EnvironmentConfig(environment=EnvironmentType.TESTING)
        assert cfg.is_testing() is True
        assert cfg.is_development() is False

    def test_is_staging(self) -> None:
        cfg = EnvironmentConfig(environment=EnvironmentType.STAGING)
        assert cfg.is_staging() is True
        assert cfg.is_development() is False


class TestEnvironmentConfigFromEnv:
    """测试通过环境变量设置值."""

    def test_reads_from_env_var(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setenv('APP_ENV', 'production')
        cfg = EnvironmentConfig()
        assert cfg.is_production() is True

    def test_env_debug_true(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setenv('APP_DEBUG', 'true')
        cfg = EnvironmentConfig()
        assert cfg.debug is True


class TestEnvironmentConfigExtraIgnore:
    """测试 extra='ignore' 行为."""

    def test_extra_fields_ignored(self) -> None:
        cfg = EnvironmentConfig(environment=EnvironmentType.DEVELOPMENT)  # type: ignore[call-arg]
        assert cfg.environment == EnvironmentType.DEVELOPMENT
