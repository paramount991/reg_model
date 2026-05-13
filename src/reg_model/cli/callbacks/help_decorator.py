import sys
from functools import wraps


def support_help_at_end(func):
    """支持 command subcommand help 语法."""

    @wraps(func)
    def wrapper(*args, **kwargs):
        if sys.argv[-1] == 'help':  # 只检查最后一个参数
            sys.argv[-1] = '--help'
        return func(*args, **kwargs)

    return wrapper
