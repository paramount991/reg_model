#!/usr/bin/env python
# Copyright (c) 2026--2030. Wang Weihua
# All rights reserved.
"""测试 cli.callbacks.global_options 模块."""

import pydantic
import pytest

from reg_model.cli.callbacks.global_options import (
    GlobalOptions,
    _resolve_log_level,
)
from reg_model.core.constants import LogLevel


class TestGlobalOptions:
    """测试 GlobalOptions 模型."""

    def test_create_default(self) -> None:
        opts = GlobalOptions(
            config_file=None,
            log_file=None,
            msg_level=LogLevel.INFO,
            verbose=False,
            quiet=False,
        )
        assert opts.msg_level == LogLevel.INFO
        assert opts.verbose is False
        assert opts.quiet is False

    def test_model_is_frozen(self) -> None:
        opts = GlobalOptions(
            config_file=None,
            log_file=None,
            msg_level=LogLevel.INFO,
            verbose=False,
            quiet=False,
        )
        with pytest.raises(pydantic.ValidationError):
            opts.verbose = True  # type: ignore[misc]

    def test_extra_fields_forbidden(self) -> None:
        with pytest.raises(pydantic.ValidationError):
            kwargs: dict[str, object] = {
                'config_file': None,
                'log_file': None,
                'msg_level': LogLevel.INFO,
                'verbose': False,
                'quiet': False,
                'unknown_field': 'not allowed',
            }
            GlobalOptions(**kwargs)  # type: ignore[arg-type]


class TestResolveLogLevel:
    """测试 _resolve_log_level 纯函数."""

    @pytest.mark.parametrize(
        'verbose,quiet,cli_level,expected',
        [
            (True, False, LogLevel.INFO, LogLevel.DEBUG),
            (False, True, LogLevel.INFO, LogLevel.ERROR),
            (False, False, LogLevel.INFO, LogLevel.INFO),
            (False, False, LogLevel.DEBUG, LogLevel.DEBUG),
            (False, False, LogLevel.WARNING, LogLevel.WARNING),
            (True, True, LogLevel.INFO, LogLevel.DEBUG),
        ],
    )
    def test_resolve(
        self,
        verbose: bool,
        quiet: bool,
        cli_level: LogLevel,
        expected: LogLevel,
    ) -> None:
        assert _resolve_log_level(verbose, quiet, cli_level) == expected
