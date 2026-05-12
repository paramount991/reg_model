#!/usr/bin/env python
# Copyright (c) 2026--2030. Wang Weihua
# All rights reserved.
"""主程序."""
from reg_model.cli.callbacks.help_decorator import support_help_at_end
from .cli import app

@support_help_at_end
def main() -> None:
    """主函数."""
    app()


if __name__ == '__main__':
    main()
