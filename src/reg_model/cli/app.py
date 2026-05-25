from typer import Typer

from .commands import (
    config_app,
    data_app,
    version_app,
)

app = Typer(pretty_exceptions_show_locals=False)

app.add_typer(config_app, name="config")
app.add_typer(data_app, name="data")
app.add_typer(version_app, name="version")