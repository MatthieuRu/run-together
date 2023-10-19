from run_together.blueprints.login.login import login_blueprint
from run_together.dash_apps.run_together.pages.home import run_together_callbacks

from flask import Flask
from dash_extensions.enrich import DashProxy, MultiplexerTransform

import os
from pathlib import Path

# python -m run_together.app

# Create the Flask App
app = Flask(__name__)
app.register_blueprint(login_blueprint)

# Register the Dash App Run Together
app_name = "run_together"

dash_app = DashProxy(
    __name__,
    server=app,
    title="Run Together",
    transforms=[MultiplexerTransform()],
    pages_folder="./dash_apps/run_together/pages/",
    routes_pathname_prefix="/run-together/",
    use_pages=True,
    assets_folder="./static",

)

run_together_callbacks(dash_app=dash_app, app_path="/home")


if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=8502) # use_reloader=False
