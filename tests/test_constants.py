#!/usr/bin/env python
# Copyright (c) 2026--2030. Wang Weihua
# All rights reserved.
"""测试 core.constants 模块."""

from pathlib import Path

from reg_model.core.constants import (
    PROJECT_DESC,
    PROJECT_NAME,
    PROJECT_VERSION,
    ConfigType,
    DatabaseType,
    EnvironmentType,
    LogLevel,
    get_default_config_path,
    get_project_version,
)


class TestEnums:
    """测试枚举类型."""

    def test_environment_type_values(self) -> None:
        assert EnvironmentType.DEVELOPMENT == 'development'
        assert EnvironmentType.STAGING == 'staging'
        assert EnvironmentType.PRODUCTION == 'production'
        assert EnvironmentType.TESTING == 'testing'

    def test_log_level_values(self) -> None:
        assert LogLevel.DEBUG == 'DEBUG'
        assert LogLevel.INFO == 'INFO'
        assert LogLevel.WARNING == 'WARNING'
        assert LogLevel.ERROR == 'ERROR'
        assert LogLevel.CRITICAL == 'CRITICAL'

    def test_database_type_values(self) -> None:
        assert DatabaseType.POSTGRESQL == 'postgresql'
        assert DatabaseType.MYSQL == 'mysql'
        assert DatabaseType.SQLITE == 'sqlite'

    def test_config_type_values(self) -> None:
        assert ConfigType.TOML == 'toml'
        assert ConfigType.YAML == 'yaml'
        assert ConfigType.ENV == 'ENV'


class TestGetProjectVersion:
    """测试 get_project_version 函数."""

    def test_returns_string(self) -> None:
        version = get_project_version()
        assert isinstance(version, str)
        assert len(version) > 0

    def test_returns_version_for_valid_package(self) -> None:
        version = get_project_version('reg_model')
        assert isinstance(version, str)

    def test_fallback_for_unknown_package(self) -> None:
        version = get_project_version('nonexistent_package_xyz')
        assert isinstance(version, str)


class TestGetDefaultConfigPath:
    """测试 get_default_config_path 函数."""

    def test_returns_path(self) -> None:
        path = get_default_config_path()
        assert isinstance(path, Path)

    def test_default_uses_toml_extension(self) -> None:
        path = get_default_config_path()
        assert path.suffix == '.toml'

    def test_custom_config_type(self) -> None:
        path = get_default_config_path('yaml')
        assert path.suffix == '.yaml'


class TestModuleConstants:
    """测试模块级常量."""

    def test_project_name(self) -> None:
        assert PROJECT_NAME == 'reg_model'

    def test_project_desc_not_empty(self) -> None:
        assert len(PROJECT_DESC) > 0

    def test_project_version_not_empty(self) -> None:
        assert len(PROJECT_VERSION) > 0
