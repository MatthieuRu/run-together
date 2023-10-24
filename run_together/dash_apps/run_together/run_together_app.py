import dash
from dash_extensions.enrich import DashProxy
from run_together.dash_apps.run_together.pages.home import layout


def run_together_callbacks(
    dash_app: DashProxy,
    app_path: str,
) -> object:
    dash.register_page(__name__, layout=layout, path=app_path)
