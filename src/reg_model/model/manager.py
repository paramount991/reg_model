#!/usr/bin/env python
# Copyright (c) 2026--2030. Wang Weihua
# All rights reserved.
"""模型管理核心业务模块."""

from __future__ import annotations

import json
import shutil
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import joblib

from reg_model.core.log import get_logger

log = get_logger()

_META_FILE = 'metadata.json'
_TAGS_FILE = 'tags.json'


def _generate_version() -> str:
    """生成版本标识(UTC时间戳)."""
    return datetime.now(tz=UTC).strftime('%Y%m%dT%H%M%S')


def save_model(
    model_path: Path,
    save_dir: Path,
    metadata: dict[str, Any] | None = None,
) -> str:
    """保存模型到指定路径(自动版本标记).

    Args:
        model_path: 模型文件路径(.joblib)
        save_dir: 保存目录
        metadata: 模型元数据

    Returns:
        模型版本标识
    """
    model_path = Path(model_path)
    if not model_path.exists():
        raise FileNotFoundError(f'模型文件不存在: {model_path}')

    save_dir = Path(save_dir)
    save_dir.mkdir(parents=True, exist_ok=True)

    version = _generate_version()
    version_dir = save_dir / version
    version_dir.mkdir(parents=True, exist_ok=True)

    dest_path = version_dir / 'model.joblib'
    shutil.copy2(model_path, dest_path)
    log.info(f'模型文件已复制: {model_path} -> {dest_path}')

    meta = {
        'version': version,
        'saved_at': datetime.now(tz=UTC).isoformat(),
        'original_path': str(model_path),
        'model_file': str(dest_path),
        **(metadata or {}),
    }
    with open(version_dir / _META_FILE, 'w', encoding='utf-8') as f:
        json.dump(meta, f, ensure_ascii=False, indent=2)

    # 更新标签
    tags_path = save_dir / _TAGS_FILE
    tags: dict[str, list[str]] = {}
    if tags_path.exists():
        with open(tags_path, encoding='utf-8') as f:
            tags = json.load(f)
    if version not in tags:
        tags[version] = []
    with open(tags_path, 'w', encoding='utf-8') as f:
        json.dump(tags, f, ensure_ascii=False, indent=2)

    log.info(f'模型版本: {version}')
    return version


def load_model(
    model_version: str,
    model_dir: Path,
) -> dict[str, Any]:
    """加载指定版本模型并输出元信息.

    Args:
        model_version: 模型版本标识
        model_dir: 模型目录

    Returns:
        模型信息和元数据字典
    """
    model_dir = Path(model_dir)
    version_dir = model_dir / model_version
    if not version_dir.exists():
        raise FileNotFoundError(f'模型版本不存在: {version_dir}')

    model_file = version_dir / 'model.joblib'
    if not model_file.exists():
        raise FileNotFoundError(f'模型文件不存在: {model_file}')

    bundle = joblib.load(model_file)
    log.info(f'已加载模型: {model_version}')

    meta_path = version_dir / _META_FILE
    metadata = {}
    if meta_path.exists():
        with open(meta_path, encoding='utf-8') as f:
            metadata = json.load(f)

    tags_path = model_dir / _TAGS_FILE
    tags: list[str] = []
    if tags_path.exists():
        with open(tags_path, encoding='utf-8') as f:
            all_tags = json.load(f)
        tags = all_tags.get(model_version, [])

    return {
        'version': model_version,
        'model': bundle['model'],
        'scaler': bundle.get('scaler'),
        'feature_names': bundle.get('feature_names', []),
        'algorithm': bundle.get('algorithm', 'unknown'),
        'metadata': metadata,
        'tags': tags,
    }


def list_models(
    model_dir: Path,
    filter_tag: str | None = None,
) -> list[dict[str, Any]]:
    """列出所有已注册模型.

    Args:
        model_dir: 模型目录
        filter_tag: 过滤标签(如 "production")

    Returns:
        模型信息列表
    """
    model_dir = Path(model_dir)
    if not model_dir.exists():
        log.warning(f'模型目录不存在: {model_dir}')
        return []

    tags_path = model_dir / _TAGS_FILE
    all_tags: dict[str, list[str]] = {}
    if tags_path.exists():
        with open(tags_path, encoding='utf-8') as f:
            all_tags = json.load(f)

    models = []
    for version_dir in sorted(model_dir.iterdir(), reverse=True):
        if not version_dir.is_dir():
            continue
        version = version_dir.name
        meta_path = version_dir / _META_FILE
        if not meta_path.exists():
            continue

        tags = all_tags.get(version, [])
        if filter_tag and filter_tag not in tags:
            continue

        with open(meta_path, encoding='utf-8') as f:
            meta = json.load(f)

        models.append(
            {
                'version': version,
                'saved_at': meta.get('saved_at', ''),
                'algorithm': meta.get('algorithm', ''),
                'tags': tags,
            }
        )

    log.info(f'找到 {len(models)} 个模型版本')
    return models


def delete_model(
    model_version: str,
    model_dir: Path,
) -> bool:
    """删除指定版本模型.

    Args:
        model_version: 模型版本标识
        model_dir: 模型目录

    Returns:
        是否成功删除
    """
    model_dir = Path(model_dir)
    version_dir = model_dir / model_version

    if not version_dir.exists():
        log.warning(f'模型版本不存在: {version_dir}')
        return False

    shutil.rmtree(version_dir)
    log.info(f'已删除模型版本: {model_version}')

    tags_path = model_dir / _TAGS_FILE
    if tags_path.exists():
        with open(tags_path, encoding='utf-8') as f:
            all_tags = json.load(f)
        if model_version in all_tags:
            del all_tags[model_version]
            with open(tags_path, 'w', encoding='utf-8') as f:
                json.dump(all_tags, f, ensure_ascii=False, indent=2)

    return True


def tag_model(
    model_version: str,
    model_dir: Path,
    tag: str,
) -> bool:
    """为指定版本模型打标签(如 "production", "staging").

    Args:
        model_version: 模型版本标识
        model_dir: 模型目录
        tag: 标签名称

    Returns:
        是否成功打标签
    """
    model_dir = Path(model_dir)
    version_dir = model_dir / model_version

    if not version_dir.exists():
        log.error(f'模型版本不存在: {version_dir}')
        return False

    tags_path = model_dir / _TAGS_FILE
    all_tags: dict[str, list[str]] = {}
    if tags_path.exists():
        with open(tags_path, encoding='utf-8') as f:
            all_tags = json.load(f)

    if model_version not in all_tags:
        all_tags[model_version] = []

    if tag not in all_tags[model_version]:
        all_tags[model_version].append(tag)
        log.info(f'已为模型 {model_version} 添加标签: {tag}')
    else:
        log.info(f'标签已存在: {tag}')

    # production 标签互斥
    if tag == 'production':
        for ver, ver_tags in all_tags.items():
            if ver != model_version and 'production' in ver_tags:
                ver_tags.remove('production')
                log.info(f'已移除 {ver} 的 production 标签')

    with open(tags_path, 'w', encoding='utf-8') as f:
        json.dump(all_tags, f, ensure_ascii=False, indent=2)

    return True
