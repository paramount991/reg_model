"""核心装饰器模块."""

from collections.abc import Callable
from functools import wraps
from typing import ParamSpec, TypeVar

from .log import get_logger

P = ParamSpec('P')
T = TypeVar('T')


def log_command(cmd_name: str):
    """标准日志装饰器."""
    log = get_logger()

    def decorator(func: Callable[P, T]) -> Callable[P, T]:
        @wraps(func)
        def wrapper(*args: P.args, **kwargs: P.kwargs) -> T:
            log.info(f'执行命令: {cmd_name}')
            log.info(f'参数: {kwargs}')
            return func(*args, **kwargs)

        return wrapper

    return decorator


def handle_errors[**P, T](func: Callable[P, T]) -> Callable[P, T]:
    """统一错误处理装饰器."""
    log = get_logger()

    @wraps(func)
    def wrapper(*args: P.args, **kwargs: P.kwargs) -> T | None:
        try:
            return func(*args, **kwargs)
        except Exception as e:
            log.error(f'命令执行失败: {e}', exc_info=True)
            raise

    return wrapper
