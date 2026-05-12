import typer
from typing_extensions import Annotated
from pathlib import Path
from reg_model.core.log import get_logger
log = get_logger()

app = typer.Typer(
    no_args_is_help=True,
    help='数据文件管理',
)

data_app = typer.Typer(help="数据文件管理")
app.add_typer(data_app, name="data")

@data_app.command(help="从远程/数据库获取数据")
def fetch() -> None:
    log.info("从远程/数据库获取数据")
    pass  # TODO: fetch data from remote or database

@data_app.command(help="验证数据格式与字段完整性")
def validate() -> None:
    log.info("验证数据格式与字段完整性")
    pass  # TODO: validate data format and field completeness

@data_app.command(help="按比例/时间列拆分训练、验证、测试集")
def split() -> None:
    log.info("按比例/时间列拆分训练、验证、测试集")
    pass  # TODO: split dataset by ratio or time column

@data_app.command(help="输出数据统计概要")
def describe() -> None:
    log.info("输出数据统计概要")
    pass  # TODO: output data statistics summary

@data_app.command(help="执行缺省或自定义的清洗规则")
def clean() -> None:
    log.info("执行缺省或自定义的清洗规则")
    pass  # TODO: apply default or custom cleaning rules