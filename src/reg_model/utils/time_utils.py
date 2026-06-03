#!/usr/bin/env python
# Copyright (c) 2026--2030. Wang Weihua
# All rights reserved.
"""时间工具类 - 企业项目通用.

时区默认:Asia/Shanghai (UTC+8)
"""

from __future__ import annotations

import time
from datetime import date, datetime, timedelta
from zoneinfo import ZoneInfo

# 统一时区
TZ_SHANGHAI = ZoneInfo('Asia/Shanghai')
DATE_FORMAT = '%Y-%m-%d'
DATETIME_FORMAT = '%Y-%m-%d %H:%M:%S'
DATETIME_MS_FORMAT = '%Y-%m-%d %H:%M:%S.%f'


def now() -> datetime:
    """当前北京时间 datetime 对象."""
    return datetime.now(tz=TZ_SHANGHAI)


def now_str(fmt: str = DATETIME_FORMAT) -> str:
    """当前时间字符串."""
    return now().strftime(fmt)


def today() -> date:
    """今天日期对象."""
    return now().date()


def today_str(fmt: str = DATE_FORMAT) -> str:
    """今天日期字符串."""
    return today().strftime(fmt)


def get_timestamp(ms: bool = False) -> int:
    """获取当前时间戳.

    Args:
        ms: 是否毫秒
    """
    ts = time.time()
    return int(ts * 1000) if ms else int(ts)


def str_to_datetime(
    dt_str: str,
    fmt: str = DATETIME_FORMAT,
    tz: ZoneInfo = TZ_SHANGHAI,
) -> datetime | None:
    """时间字符串转 datetime."""
    try:
        return datetime.strptime(dt_str, fmt).replace(tzinfo=tz)
    except (ValueError, TypeError):
        return None


def datetime_to_str(dt: datetime, fmt: str = DATETIME_FORMAT) -> str:
    """Datetime 转字符串."""
    return dt.astimezone(TZ_SHANGHAI).strftime(fmt)


def timestamp_to_datetime(
    ts: int | float,
    ms: bool = True,
    tz: ZoneInfo = TZ_SHANGHAI,
) -> datetime:
    """时间戳转 datetime.

    Args:
        ts: 时间戳
        ms: 传入是否毫秒
        tz: 时区, 默认 Asia/Shanghai
    """
    if ms:
        ts /= 1000
    return datetime.fromtimestamp(ts, tz=tz)


def get_day_start(dt: datetime | None = None) -> datetime:
    """获取某天 00:00:00."""
    if dt is None:
        dt = now()
    return dt.astimezone(TZ_SHANGHAI).replace(hour=0, minute=0, second=0, microsecond=0)


def get_day_end(dt: datetime | None = None) -> datetime:
    """获取某天 23:59:59.999 ."""
    if dt is None:
        dt = now()
    return get_day_start(dt) + timedelta(days=1) - timedelta(microseconds=1)


def get_relative_day(days: int) -> date:
    """获取相对今天的日期.

    Args:
        days: 偏移天数,-1=昨天,1=明天
    """
    return today() + timedelta(days=days)


def get_week_start(dt: datetime | None = None) -> datetime:
    """获取本周周一 0点."""
    if dt is None:
        dt = now()
    dt = dt.astimezone(TZ_SHANGHAI)
    monday = dt - timedelta(days=dt.weekday())
    return get_day_start(monday)


def get_week_end(dt: datetime | None = None) -> datetime:
    """获取本周周日 23:59:59.999 ."""
    return get_week_start(dt) + timedelta(days=7) - timedelta(microseconds=1)


def is_same_day(dt1: datetime, dt2: datetime) -> bool:
    """判断两个时间是否同一天."""
    return dt1.astimezone(TZ_SHANGHAI).date() == dt2.astimezone(TZ_SHANGHAI).date()
