#!/usr/bin/env python
# Copyright (c) 2026--2030. Wang Weihua
# All rights reserved.
"""测试 core.config.settings 模块."""

from pathlib import Path

import pytest
import tomli_w

from reg_model.core.config.base import EnvironmentConfig
from reg_model.core.config.database import DatabaseConfig
from reg_model.core.config.settings import (
    Settings,
    _deep_merge,
    clear_settings,
    get_settings,
    load_settings,
)
from reg_model.core.constants import EnvironmentType


class TestSettingsDefaults:
    """测试 Settings 默认构造."""

    def test_default_construction(self) -> None:
        settings = Settings()
        assert settings.app is not None
        assert settings.env is not None
        assert settings.log is not None
        assert settings.db is not None

    def test_extra_config_defaults_to_empty_dict(self) -> None:
        settings = Settings()
        assert settings.extra_config == {}

    def test_database_url_delegates_to_db(self) -> None:
        settings = Settings()
        url = settings.get_database_url()
        assert 'postgresql://' in url


class TestSettingsValidation:
    """测试 Settings 验证逻辑."""

    def test_production_with_debug_raises(self) -> None:
        with pytest.raises(ValueError, match='生产环境不能启用调试模式'):
            Settings(
                env=EnvironmentConfig(
                    environment=EnvironmentType.PRODUCTION, debug=True
                )
            )

    def test_production_without_debug_ok(self) -> None:
        settings = Settings(
            env=EnvironmentConfig(
                environment=EnvironmentType.PRODUCTION, debug=False
            )
        )
        assert settings.env.is_production()

    def test_development_with_debug_ok(self) -> None:
        settings = Settings(
            env=EnvironmentConfig(
                environment=EnvironmentType.DEVELOPMENT, debug=True
            )
        )
        assert settings.env.debug is True


class TestDictWithoutSensitive:
    """测试 dict_without_sensitive 方法."""

    def test_password_masked(self) -> None:
        settings = Settings(
            db=DatabaseConfig(password='my-secret-password'),
        )
        result = settings.dict_without_sensitive()
        assert result['db']['password'] == '********'

    def test_non_sensitive_fields_preserved(self) -> None:
        settings = Settings(
            db=DatabaseConfig(host='db.example.com', username='admin'),
        )
        result = settings.dict_without_sensitive()
        assert result['db']['host'] == 'db.example.com'
        assert result['db']['username'] == 'admin'

    def test_nested_sensitive_keys_masked(self) -> None:
        settings = Settings(
            extra_config={'api_key': 'abc123', 'name': 'test'}
        )
        result = settings.dict_without_sensitive()
        assert result['extra_config']['api_key'] == '********'
        assert result['extra_config']['name'] == 'test'


class TestDeepMerge:
    """测试 _deep_merge 函数."""

    def test_override_simple_values(self) -> None:
        base = {'a': 1, 'b': 2}
        override = {'b': 3}
        result = _deep_merge(base, override)
        assert result == {'a': 1, 'b': 3}

    def test_nested_merge(self) -> None:
        base = {'db': {'host': 'localhost', 'port': 5432}}
        override = {'db': {'host': 'prod.example.com'}}
        result = _deep_merge(base, override)
        assert result['db']['host'] == 'prod.example.com'
        assert result['db']['port'] == 5432

    def test_override_adds_new_keys(self) -> None:
        base = {'a': 1}
        override = {'b': 2}
        result = _deep_merge(base, override)
        assert result == {'a': 1, 'b': 2}


class TestLoadSettingsFromToml:
    """测试从 TOML 文件加载 Settings."""

    def test_load_from_valid_toml(self, tmp_config_file: Path) -> None:
        settings = load_settings(tmp_config_file)
        assert settings.app.name == 'test-app'
        assert settings.db.type.value == 'sqlite'

    def test_load_nonexistent_file_raises(self) -> None:
        with pytest.raises(FileNotFoundError, match='配置文件不存在'):
            load_settings(Path('/nonexistent/config.toml'))

    def test_load_with_override(
        self, tmp_config_file: Path, tmp_path: Path
    ) -> None:
        override_data = {'app': {'name': 'overridden-app'}}
        override_path = tmp_path / 'override.toml'
        with open(override_path, 'wb') as f:
            tomli_w.dump(override_data, f)
        settings = load_settings(tmp_config_file, override_path)
        assert settings.app.name == 'overridden-app'


class TestSettingsSingleton:
    """测试 Settings 单例行为."""

    def test_get_settings_returns_same_instance(self) -> None:
        clear_settings()
        s1 = get_settings()
        s2 = get_settings()
        assert s1 is s2

    def test_get_settings_with_path_forces_reload(
        self, tmp_config_file: Path
    ) -> None:
        settings = get_settings(tmp_config_file)
        assert settings.app.name == 'test-app'

    def test_clear_settings_resets_cache(self) -> None:
        clear_settings()
        s1 = get_settings()
        clear_settings()
        s2 = get_settings()
        assert s1 is not s2
