#!/usr/bin/env python
# Copyright (c) 2026--2030. Wang Weihua
# All rights reserved.
"""服务部署核心业务模块."""

from __future__ import annotations

import os
import signal
import subprocess
import sys
import tempfile
import time
from pathlib import Path
from typing import Any

from reg_model.core.log import get_logger

log = get_logger()

_PID_FILE = Path(tempfile.gettempdir()) / 'reg_model_serve.pid'


def start_service(
    model_path: Path,
    host: str = 'localhost',
    port: int = 8000,
    config_path: Path | None = None,
) -> dict[str, Any]:
    """启动在线预测 API 服务.

    使用 Flask 启动 HTTP API 服务,支持 /predict、/health、/info 端点。

    Args:
        model_path: 模型文件路径
        host: 服务主机地址
        port: 服务端口
        config_path: 服务配置文件路径(预留)

    Returns:
        服务启动信息字典
    """
    model_path = Path(model_path)
    if not model_path.exists():
        raise FileNotFoundError(f'模型文件不存在: {model_path}')

    if _is_running():
        pid = _read_pid()
        log.warning(f'服务已在运行 (PID: {pid})')
        return {
            'status': 'already_running',
            'pid': pid,
            'host': host,
            'port': port,
        }

    log.info(f'启动预测服务: {model_path}')
    log.info(f'地址: http://{host}:{port}')

    server_code = _generate_server_code(model_path, host, port)

    with tempfile.NamedTemporaryFile(
        mode='w',
        suffix='.py',
        delete=False,
        encoding='utf-8',
    ) as f:
        f.write(server_code)
        server_file = f.name

    try:
        import flask  # type: ignore  # noqa: F401  # flask optional dep
    except ImportError:
        log.error('请安装 Flask: pip install flask')
        raise

    proc = subprocess.Popen(
        [sys.executable, server_file],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    _PID_FILE.write_text(str(proc.pid))

    time.sleep(1)  # 等待服务启动

    result = {
        'status': 'started' if _is_running() else 'start_failed',
        'pid': proc.pid,
        'host': host,
        'port': port,
        'endpoints': {
            'predict': f'http://{host}:{port}/predict',
            'health': f'http://{host}:{port}/health',
            'info': f'http://{host}:{port}/info',
        },
    }
    log.info(f'服务已启动 (PID: {proc.pid})')
    return result


def stop_service(
    service_id: str | None = None,
) -> bool:
    """停止模型预测服务.

    Args:
        service_id: 服务标识(PID 字符串),None 则从 PID 文件读取

    Returns:
        是否成功停止
    """
    pid = int(service_id) if service_id else _read_pid()
    if pid is None:
        log.warning('没有正在运行的服务')
        return False

    try:
        if sys.platform == 'win32':
            subprocess.run(['taskkill', '/PID', str(pid), '/F'], check=False)
        else:
            os.kill(pid, signal.SIGTERM)
        log.info(f'已停止服务 (PID: {pid})')
        _clear_pid()
        return True
    except ProcessLookupError:
        log.warning(f'进程 {pid} 已不存在')
        _clear_pid()
        return True
    except Exception as e:
        log.error(f'停止服务失败: {e}')
        return False


def check_service_status(
    service_id: str | None = None,
) -> dict[str, Any]:
    """查看服务运行状态.

    Args:
        service_id: 服务标识(PID),None 则从 PID 文件读取

    Returns:
        服务状态信息字典
    """
    pid = int(service_id) if service_id else _read_pid()
    running = _is_running() if pid else False

    status: dict[str, Any] = {
        'running': running,
        'pid': pid,
        'pid_file': str(_PID_FILE) if _PID_FILE.exists() else None,
    }
    log.info(f'服务状态: {"运行中" if running else "已停止"}')
    return status


def _is_running() -> bool:
    """检查 PID 文件中的进程是否在运行."""
    pid = _read_pid()
    if pid is None:
        return False
    try:
        if sys.platform == 'win32':
            result = subprocess.run(
                ['tasklist', '/FI', f'PID eq {pid}'],
                capture_output=True,
                text=True,
            )
            return str(pid) in result.stdout
        else:
            os.kill(pid, 0)
            return True
    except (ProcessLookupError, OSError):
        return False


def _read_pid() -> int | None:
    """读取 PID 文件."""
    if not _PID_FILE.exists():
        return None
    try:
        return int(_PID_FILE.read_text().strip())
    except (ValueError, FileNotFoundError):
        return None


def _clear_pid() -> None:
    """清除 PID 文件."""
    if _PID_FILE.exists():
        _PID_FILE.unlink()


def _generate_server_code(model_path: Path, host: str, port: int) -> str:
    """生成启动 Flask 服务的启动脚本.

    使用 serve/flask_app.py 模块, 不再内联生成代码。
    """
    return f"""
import os
os.environ["MODEL_PATH"] = {model_path.as_posix()!r}
from reg_model.serve.flask_app import create_app
app = create_app()
app.run(host={host!r}, port={port}, debug=False)
"""
