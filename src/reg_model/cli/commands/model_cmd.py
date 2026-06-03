#!/usr/bin/env python
# Copyright (c) 2026--2030. Wang Weihua
# All rights reserved.
"""模型管理子命令."""

import json
from pathlib import Path

import typer

from reg_model.core import handle_errors, log_command
from reg_model.core.log import get_logger
from reg_model.model import (
    delete_model,
    list_models,
    load_model,
    save_model,
    tag_model,
)

log = get_logger()
app = typer.Typer(help='模型管理')


@app.command(help='保存模型到指定路径(自动版本标记)')
@handle_errors
@log_command('save')
def save(
    model_path: Path = typer.Argument(..., help='模型文件路径'),
    save_dir: Path = typer.Argument(..., help='保存目录'),
    metadata: str | None = typer.Option(
        None, '--metadata', '-m', help='模型元数据JSON字符串'
    ),
) -> None:
    """保存模型到指定路径(自动版本标记)."""
    log.info(f'保存模型: {model_path} -> {save_dir}')
    meta = None
    if metadata:
        try:
            meta = json.loads(metadata)
        except json.JSONDecodeError as e:
            raise typer.BadParameter(f'无效的 JSON: {metadata}') from e
    version = save_model(
        model_path=model_path,
        save_dir=save_dir,
        metadata=meta,
    )
    log.info(f'模型版本: {version}')


@app.command(help='加载模型并输出元信息')
@handle_errors
@log_command('load')
def load(
    model_version: str = typer.Argument(..., help='模型版本标识'),
    model_dir: Path = typer.Argument(..., help='模型目录'),
) -> None:
    """加载模型并输出元信息."""
    log.info(f'加载模型: {model_version} (目录: {model_dir})')
    result = load_model(model_version=model_version, model_dir=model_dir)
    # 不输出 model 对象本身
    display = {k: v for k, v in result.items() if k != 'model'}
    log.info(
        f'模型信息:\n{json.dumps(display, ensure_ascii=False, indent=2, default=str)}'
    )


@app.command(help='列出所有已注册模型', name='list')
@handle_errors
@log_command('list')
def list_models_cmd(
    model_dir: Path = typer.Argument(..., help='模型目录'),
    filter_tag: str | None = typer.Option(None, '--tag', '-t', help='过滤标签'),
) -> None:
    """列出所有已注册模型."""
    log.info(f'列出模型: {model_dir}')
    result = list_models(model_dir=model_dir, filter_tag=filter_tag)
    if result:
        for m in result:
            log.info(
                f'  {m["version"]} | {m.get("algorithm", "")} | tags: {m.get("tags", [])} | {m.get("saved_at", "")}'
            )
    else:
        log.info('  未找到模型')


@app.command(help='删除指定版本模型')
@handle_errors
@log_command('delete')
def delete(
    model_version: str = typer.Argument(..., help='模型版本标识'),
    model_dir: Path = typer.Argument(..., help='模型目录'),
) -> None:
    """删除指定版本模型."""
    log.info(f'删除模型: {model_version}')
    delete_model(model_version=model_version, model_dir=model_dir)


@app.command(help='打标签(如 "production", "staging")')
@handle_errors
@log_command('tag')
def tag(
    model_version: str = typer.Argument(..., help='模型版本标识'),
    model_dir: Path = typer.Argument(..., help='模型目录'),
    tag: str = typer.Option('production', '--tag', '-t', help='标签名称'),
) -> None:
    """打标签(如 "production", "staging")."""
    log.info(f'打标签: {model_version} -> {tag}')
    tag_model(model_version=model_version, model_dir=model_dir, tag=tag)
