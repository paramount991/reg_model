#!/usr/bin/env python
# Copyright (c) 2026--2030. Wang Weihua
# All rights reserved.
"""日志管理模块."""

from __future__ import annotations

import logging
import sys
from logging.handlers import TimedRotatingFileHandler
from pathlib import Path
from typing import Any

import structlog

_INITIALIZED = False


def init_logging(config: dict[str, Any]) -> None:
    """设置日志系统.

    功能:
    - 控制台彩色输出
    - 可选文件输出
    - 文件按天轮转(每天一个日志文件)
    - 保留 backup_count 天历史日志

    Args:
        config: 日志级别

    """
    global _INITIALIZED
    if _INITIALIZED:
        return

    level: str = config.get('level', 'INFO')
    # json: bool = config.get('json', False)
    log_file: str | Path | None = config.get('file_path')
    backup_count: int = config.get('backup_count', 365)
    log_level = getattr(logging, level.upper(), logging.INFO)

    root = logging.getLogger()
    root.setLevel(log_level)
    # 清理已有 handler,避免重复初始化
    root.handlers.clear()

    # 控制台 handler: 彩色输出
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(log_level)
    console_formatter = structlog.stdlib.ProcessorFormatter(
        # 关闭/缩小 ConsoleRenderer 的对齐填充,输出更紧凑、好看
        processor=structlog.dev.ConsoleRenderer(
            colors=True, pad_level=False, pad_event_to=0
        ),
    )
    console_handler.setFormatter(console_formatter)
    root.addHandler(console_handler)

    # 文件 handler,按天轮转,
    if log_file is not None:
        log_path = Path(log_file)
        log_path.parent.mkdir(parents=True, exist_ok=True)

        file_formatter = structlog.stdlib.ProcessorFormatter(
            processors=[
                # 移除 ProcessorFormatter 注入的元字段(例如 `_record`).
                structlog.stdlib.ProcessorFormatter.remove_processors_meta,
                # 添加源码文件名与行号。
                structlog.processors.CallsiteParameterAdder(
                    {
                        structlog.processors.CallsiteParameter.FILENAME,
                        structlog.processors.CallsiteParameter.LINENO,
                    }
                ),
                structlog.processors.JSONRenderer(serializer=_json_dumps_utf8),
            ],
        )

        file_handler = TimedRotatingFileHandler(
            filename=str(log_path),
            when='midnight',  # 每天午夜轮转
            interval=1,
            backupCount=backup_count,
            encoding='utf-8',
            delay=True,
        )

        file_handler.setLevel(log_level)
        # 轮转文件名日期后缀,如 *.log.2026-03-26
        file_handler.suffix = '%Y-%m-%d'
        # 纯 JSON 格式输出
        file_handler.setFormatter(file_formatter)
        root.addHandler(file_handler)

    # 配置 structlog
    processors: list = [
        structlog.contextvars.merge_contextvars,
        structlog.stdlib.filter_by_level,
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.processors.TimeStamper(fmt='%Y-%m-%d %H:%M:%S', utc=False),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.stdlib.add_log_level,
        structlog.stdlib.ProcessorFormatter.wrap_for_formatter,
    ]

    structlog.configure(
        processors=processors,
        wrapper_class=structlog.stdlib.BoundLogger,
        logger_factory=structlog.stdlib.LoggerFactory(),
        cache_logger_on_first_use=True,
    )

    _INITIALIZED = True


def get_logger(name: str | None = None) -> structlog.stdlib.BoundLogger:
    """获取日志记录器.

    Args:
        name: 日志记录器名称

    Returns:
        structlog.BoundLogger: 日志记录器
    """
    return structlog.get_logger(name) if name else structlog.get_logger()


def _json_dumps_utf8(obj, **kwargs) -> str:
    """将对象序列化为 UTF-8 编码的 JSON 字符串."""
    import json

    return json.dumps(obj, ensure_ascii=False, **kwargs)
