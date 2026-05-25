#!/usr/bin/env python
# Copyright (c) 2026--2030. Wang Weihua
# All rights reserved.
"""config: 配置文件管理子命令."""

import shutil
from pathlib import Path
from typing import Any

import tomli_w
import tomlkit
import typer

from reg_model.cli.callbacks.global_options import GlobalOptions
from reg_model.core import constants as const
from reg_model.core.config.serializer import (
    save_default_config,
)
from reg_model.core.config.settings import Settings, load_settings

app = typer.Typer(
    no_args_is_help=True,
    help='配置文件管理',
)


@app.command('init', help='写入默认配置到配置文件')
def init_config(
    ctx: typer.Context,
    force: bool = typer.Option(False, '--force', '-f', help='覆盖写入配置文件'),
) -> None:
    """写入默认配置到配置文件."""
    config_path = _resolved_config_path(ctx)
    _check_overwrite(config_path, force)
    typer.echo(f'初始化配置文件{config_path}...')
    save_default_config(config_path, overwrite=True)
    typer.echo('配置文件初始化成功')


@app.command('copy', help='复制预定义配置文件')
def copy_config(
    ctx: typer.Context,
    force: bool = typer.Option(False, '--force', '-f', help='覆盖写入配置文件'),
) -> None:
    """复制预定义配置文件."""
    config_path = _resolved_config_path(ctx)
    _check_overwrite(config_path, force)

    _repo_root = Path(__file__).resolve().parent.parent.parent.parent.parent
    config_src_path = _repo_root / 'install' / 'reg_model.toml'
    typer.echo(f'复制预定义配置文件{config_src_path}到{config_path}...')
    config_path.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy(config_src_path, config_path)
    typer.echo('配置文件复制成功')


@app.command('list', help='列出配置文件内容(同 show 命令)')
@app.command('show', help='列出配置文件内容(同 list 命令)')
def list_or_show_config(ctx: typer.Context) -> None:
    """列出配置文件内容."""
    config_path = _resolved_config_path(ctx)
    _list_or_show(config_path)


@app.command('validate', help='校验配置文件')
def validate_config(ctx: typer.Context) -> None:
    """校验配置文件."""
    config_path = _resolved_config_path(ctx)
    if not config_path.exists():
        typer.secho(f'配置文件不存在: {config_path}', fg=typer.colors.RED)
        raise typer.Exit(code=1)

    typer.echo(f'验证配置文件 {config_path}...')
    try:
        load_settings(config_path)
    except Exception as e:
        typer.secho(str(e), fg=typer.colors.RED)
        raise typer.Exit(code=1) from None
    typer.echo(f'配置文件 {config_path} 正确无误.')


@app.command('set', help='修改单个配置项并写回文件')
def set_config_item(
    ctx: typer.Context,
    key: str = typer.Argument(..., help='字段名,例如 database.host'),
    value: str = typer.Argument(
        ...,
        help='新值,可用 true/false、数字或带引号的字符串等字面量',
    ),
) -> None:
    """修改单个配置项并写回文件."""
    config_path = _resolved_config_path(ctx)
    cfg = load_settings(config_path)

    # 通过 pydantic 模型验证 key 路径并推断值类型
    parts = key.split('.')
    parent = cfg
    for part in parts[:-1]:
        try:
            parent = getattr(parent, part)
        except AttributeError:
            typer.secho(f'未知配置项: {key}', fg=typer.colors.RED)
            raise typer.Exit(code=1) from None

    field_name = parts[-1]
    try:
        old_value = getattr(parent, field_name)
    except AttributeError:
        typer.secho(f'未知配置字段: {key}', fg=typer.colors.RED)
        raise typer.Exit(code=1) from None

    typed_value = _coerce_value(value, type(old_value))
    typer.echo(f'更新 {key} = {typed_value}')

    # 用 tomlkit 原地编辑 TOML 文件以保留注释和格式
    doc = tomlkit.parse(config_path.read_text(encoding='utf-8'))
    node = doc
    for part in parts[:-1]:
        node = node[part]
    node[field_name] = typed_value
    config_path.write_text(tomlkit.dumps(doc), encoding='utf-8')
    typer.echo(f'配置文件 {config_path} 更新成功')


@app.command('get', help='读取单个配置项')
def get_config_item(
    ctx: typer.Context,
    key: str = typer.Argument(..., help='字段名,例如 database.host'),
) -> None:
    """读取单个配置项."""
    config_path = _resolved_config_path(ctx)
    cfg = load_settings(config_path)

    parts = key.split('.')
    current: Any = cfg.model_dump()
    for part in parts:
        if not isinstance(current, dict) or part not in current:
            typer.secho(f'未知配置项: {key}', fg=typer.colors.RED)
            raise typer.Exit(code=1)
        current = current[part]

    typer.echo(f'{key} = {current}')


@app.command('path', help='打印当前配置文件路径')
def get_config_path(ctx: typer.Context) -> None:
    """打印当前配置文件路径."""
    config_path = _resolved_config_path(ctx)
    typer.echo(str(config_path))


def _check_overwrite(config_path: Path, force: bool) -> None:
    """如果配置文件已存在且未强制覆盖则报错."""
    if config_path.exists() and not force:
        typer.secho(
            f'配置文件{config_path}已存在: 使用 --force 可覆盖。',
            fg=typer.colors.RED,
        )
        raise typer.Exit(code=1)


def _coerce_value(raw: str, target_type: type) -> Any:
    """将字符串值转为目标类型."""
    if target_type is bool:
        return raw.lower() in ('true', '1', 'yes', 'on')
    if target_type is int:
        return int(raw)
    if target_type is float:
        return float(raw)
    if target_type is str:
        return raw
    return raw


def _resolved_config_path(ctx: typer.Context) -> Path:
    """得到实际配置文件路径."""
    root = ctx.find_root()
    opts = root.obj
    if isinstance(opts, GlobalOptions) and opts.config_file:
        return Path(opts.config_file).expanduser().resolve()
    return const.DEFAULT_CONFIG_PATH


def _list_or_show(config_path: Path) -> None:
    """加载 Settings 并打印为 TOML."""
    if not config_path.exists():
        typer.secho(f'配置文件不存在: {config_path}', fg=typer.colors.YELLOW)
        raise typer.Exit(code=1)

    cfg = load_settings(config_path)
    _print_as_toml(cfg)


def _print_as_toml(cfg: Settings) -> None:
    """将 Settings 序列化为 TOML 文本输出."""
    data = cfg.model_dump(mode='json', exclude_none=True)
    typer.echo(tomli_w.dumps(data).rstrip())
