#!/usr/bin/env python
# Copyright (c) 2026--2030. Wang Weihua
# All rights reserved.
"""测试 core.decorators 模块."""

from typing import Any

import pytest

from reg_model.core.decorators import handle_errors, log_command


class TestHandleErrors:
    """测试 handle_errors 装饰器."""

    def test_success_path_returns_value(self) -> None:
        @handle_errors
        def ok_func(x: int) -> int:
            return x * 2

        assert ok_func(21) == 42

    def test_preserves_function_name(self) -> None:
        @handle_errors
        def my_func() -> None:
            pass

        assert my_func.__name__ == 'my_func'

    def test_exception_is_raised(self) -> None:
        @handle_errors
        def failing_func() -> None:
            raise ValueError('test error')

        with pytest.raises(ValueError, match='test error'):
            failing_func()


class TestLogCommand:
    """测试 log_command 装饰器."""

    def test_success_path_returns_value(self) -> None:
        @log_command('test_cmd')
        def ok_func(x: int) -> int:
            return x + 1

        assert ok_func(1) == 2

    def test_preserves_function_name(self) -> None:
        @log_command('test_cmd')
        def my_func() -> None:
            pass

        assert my_func.__name__ == 'my_func'

    def test_accepts_kwargs(self) -> None:
        @log_command('test_cmd')
        def kw_func(**kwargs: Any) -> dict[str, Any]:
            return kwargs

        result = kw_func(a=1, b=2)
        assert result == {'a': 1, 'b': 2}
