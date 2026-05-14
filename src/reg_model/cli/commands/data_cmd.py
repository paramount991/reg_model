from pathlib import Path

import typer

from reg_model.core import handle_errors, log_command
from reg_model.core.log import get_logger
from reg_model.data import manager

log = get_logger()

app = typer.Typer(help='数据文件管理')


@app.command(help='从远程/数据库获取数据')
@handle_errors
@log_command('fetch')
def fetch(
    output_path: Path | None = typer.Option(
        None, '--output', '-o', help='输出文件路径'
    ),
    source: str | None = typer.Option(
        None, '--source', '-s', help='数据源标识/连接信息'
    ),
) -> None:
    """从远程或数据库获取原始数据.

    Args:
        output_path: 输出文件保存路径,默认使用配置文件中的路径
        source: 数据源标识,不指定则使用默认数据源
    """
    manager.fetch_data(output_path=output_path, source=source)


@app.command(help='验证数据格式与字段完整性')
@handle_errors
@log_command('validate')
def validate(
    input_path: Path = typer.Argument(..., help='输入数据文件路径'),
    schema_path: Path | None = typer.Option(
        None, '--schema', '-s', help='数据schema文件路径'
    ),
    strict: bool = typer.Option(False, '--strict', help='严格模式，验证失败立即退出'),
) -> None:
    """验证数据格式与字段完整性.

    Args:
        input_path: 待验证的数据文件路径
        schema_path: schema定义文件路径，默认使用项目内置schema
        strict: 是否启用严格验证模式
    """
    manager.validate_data(input_path=input_path, schema_path=schema_path, strict=strict)


@app.command(help='按比例/时间列拆分训练、验证、测试集')
@handle_errors
@log_command('split')
def split(
    input_path: Path = typer.Argument(..., help='输入完整数据集路径'),
    output_dir: Path = typer.Argument(..., help='输出拆分数据集目录'),
    ratio: str = typer.Option(
        '70:20:10', '--ratio', '-r', help='训练:验证:测试 比例，例如 70:20:10'
    ),
    time_column: str | None = typer.Option(
        None, '--time-col', '-t', help='按时间列拆分的列名'
    ),
    stratify: str | None = typer.Option(None, '--stratify', help='分层拆分的标签列名'),
    random_seed: int = typer.Option(42, '--seed', help='随机种子'),
) -> None:
    """按比例或时间列拆分训练/验证/测试集.

    Args:
        input_path: 完整数据集文件路径
        output_dir: 输出拆分后数据集的目录
        ratio: 训练集、验证集、测试集比例
        time_column: 如果按时间拆分，指定时间列名
        stratify: 分层拆分的标签列，保持类别分布一致
        random_seed: 随机拆分的随机种子
    """
    manager.split_dataset(
        input_path=input_path,
        output_dir=output_dir,
        ratio=ratio,
        time_column=time_column,
        stratify=stratify,
        random_seed=random_seed,
    )


@app.command(help='输出数据统计概要')
@handle_errors
@log_command('describe')
def describe(
    input_path: Path = typer.Argument(..., help='输入数据文件路径'),
    output_path: Path | None = typer.Option(
        None, '--output', '-o', help='统计报告输出路径'
    ),
) -> None:
    """输出数据统计概要.

    Args:
        input_path: 待统计的数据文件路径
        output_path: 统计报告输出文件,默认输出到控制台
    """
    manager.describe_data(input_path=input_path, output_path=output_path)


@app.command(help='执行缺省或自定义的清洗规则')
@handle_errors
@log_command('clean')
def clean(
    input_path: Path = typer.Argument(..., help='输入原始数据路径'),
    output_path: Path = typer.Argument(..., help='输出清洗后数据路径'),
    config_path: Path | None = typer.Option(
        None, '--config', '-c', help='清洗规则配置文件路径'
    ),
) -> None:
    """执行默认或自定义清洗规则.

    Args:
        input_path: 原始数据文件路径
        output_path: 清洗后数据输出路径
        config_path: 自定义清洗规则配置文件，默认使用内置规则
    """
    manager.clean_data(
        input_path=input_path,
        output_path=output_path,
        config_path=config_path,
    )


@app.command(help='数据预处理/特征工程')
@handle_errors
@log_command('preprocess')
def preprocess(
    input_path: Path = typer.Argument(..., help='输入清洗后数据路径'),
    output_dir: Path = typer.Argument(..., help='预处理输出目录'),
    config_path: Path | None = typer.Option(
        None, '--config', '-c', help='预处理配置文件路径'
    ),
) -> None:
    """执行数据预处理和特征工程.

    Args:
        input_path: 清洗后的数据文件路径
        output_dir: 预处理输出目录（包含处理器和处理后的数据）
        config_path: 预处理配置文件路径
    """
    manager.preprocess_data(
        input_path=input_path,
        output_dir=output_dir,
        config_path=config_path,
    )


@app.command(help='导出处理好的数据')
@handle_errors
@log_command('export')
def export(
    input_path: Path = typer.Argument(..., help='输入处理后数据路径'),
    output_path: Path = typer.Argument(..., help='导出目标路径'),
    format: str = typer.Option(
        'csv', '--format', '-f', help='导出格式: csv, parquet, json'
    ),
) -> None:
    """导出处理好的数据到指定格式.

    Args:
        input_path: 处理好的数据文件路径
        output_path: 导出文件路径
        format: 导出文件格式
    """
    manager.export_data(input_path=input_path, output_path=output_path, format=format)
