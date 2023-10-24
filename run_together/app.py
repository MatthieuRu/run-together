from run_together.blueprints.login.login import login_blueprint
from run_together.dash_apps.run_together.run_together_app import run_together_callbacks

from flask import Flask
from dash_extensions.enrich import DashProxy, MultiplexerTransform

# python -m run_together.app

# Create the Flask App
app = Flask(__name__)
app.register_blueprint(login_blueprint)

# To use the small icon in the app
external_stylesheets = [
    "https://cdnjs.cloudflare.com/ajax/libs/font-awesome/5.15.3/css/all.min.css"
]


dash_app = DashProxy(
    __name__,
    server=app,
    title="Run Together",
    transforms=[MultiplexerTransform()],
    pages_folder="./dash_apps/run_together/pages/",
    routes_pathname_prefix="/run-together/",
    use_pages=True,
    assets_folder="./static",
    external_stylesheets=external_stylesheets,
)

run_together_callbacks(dash_app=dash_app, app_path="/home")


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=8502)  # use_reloader=False
