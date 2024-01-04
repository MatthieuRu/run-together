from run_together.blueprints.login.login import login_blueprint
from run_together.dash_apps.run_together.run_together_app import run_together_app
from os import environ as env
from flask import Flask
from dash_extensions.enrich import DashProxy, MultiplexerTransform

# python -m run_together.app

# Create the Flask App
app = Flask(__name__)
app.config["SECRET_KEY"] = env["cookiePassword"]

app.register_blueprint(login_blueprint)

# To use the small icon in the app
external_stylesheets = [
    "https://cdnjs.cloudflare.com/ajax/libs/font-awesome/5.15.3/css/all.min.css",
    "./static/css/style.css",  # Add the path to style.css
    "./static/css/login-page-style.css",  # Add the path to login-page-style.css
]

# Adding the tailwind css script in the application setuo
external_script = ["https://tailwindcss.com/", {"src": "https://cdn.tailwindcss.com"}]

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
    external_scripts=external_script,
)

run_together_app(dash_app=dash_app, app_path="/home")


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=8502)  # use_reloader=False
