#!/usr/bin/env python
# Copyright (c) 2026--2030. Wang Weihua
# All rights reserved.
"""CLI 回调函数包."""

from .global_options import GlobalOptions, global_options
from .help_decorator import support_help_at_end

__all__ = ['GlobalOptions', 'global_options', 'support_help_at_end']
