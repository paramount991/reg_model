#!/usr/bin/env python
# Copyright (c) 2026--2030. Wang Weihua
# All rights reserved.
"""测试 core.config.database 模块."""

import warnings

import pytest

from reg_model.core.config.database import DatabaseConfig
from reg_model.core.constants import DatabaseType


class TestDatabaseConfigDefaults:
    """测试 DatabaseConfig 默认值."""

    def test_default_type_is_postgresql(self) -> None:
        cfg = DatabaseConfig()
        assert cfg.type == DatabaseType.POSTGRESQL

    def test_default_host(self) -> None:
        cfg = DatabaseConfig()
        assert cfg.host == 'localhost'

    def test_default_port(self) -> None:
        cfg = DatabaseConfig()
        assert cfg.port == 5432

    def test_default_pool_values(self) -> None:
        cfg = DatabaseConfig()
        assert cfg.pool_size == 20
        assert cfg.max_overflow == 10
        assert cfg.pool_timeout == 30
        assert cfg.pool_recycle == 3600


class TestDatabaseUrl:
    """测试 url 属性."""

    def test_postgresql_url(self) -> None:
        cfg = DatabaseConfig(
            type=DatabaseType.POSTGRESQL,
            username='user',
            password='pass',
            host='db.example.com',
            port=5432,
            database='mydb',
        )
        assert cfg.url == 'postgresql://user:pass@db.example.com:5432/mydb'

    def test_mysql_url(self) -> None:
        cfg = DatabaseConfig(
            type=DatabaseType.MYSQL,
            username='root',
            password='secret',
            host='mysql.local',
            port=3306,
            database='app',
        )
        assert cfg.url == 'mysql://root:secret@mysql.local:3306/app'

    def test_sqlite_url(self) -> None:
        cfg = DatabaseConfig(
            type=DatabaseType.SQLITE,
            database='app',
        )
        assert cfg.url == 'sqlite:///app.db'


class TestPortValidation:
    """测试端口验证器."""

    def test_non_default_postgresql_port_warns(self) -> None:
        with pytest.warns(UserWarning, match='非默认端口'):
            DatabaseConfig(type=DatabaseType.POSTGRESQL, port=9999)

    def test_non_default_mysql_port_warns(self) -> None:
        with pytest.warns(UserWarning, match='非默认MySQL端口'):
            DatabaseConfig(type=DatabaseType.MYSQL, port=9999)

    def test_default_port_no_warning(self) -> None:
        with warnings.catch_warnings(record=True) as w:
            DatabaseConfig(type=DatabaseType.POSTGRESQL, port=5432)
        assert len(w) == 0
