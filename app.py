from blueprints.login.login import login_blueprint
from dash_apps.run_together.run_together_app import run_together_app
from os import environ as env
from flask import Flask
from dash_extensions.enrich import DashProxy, MultiplexerTransform

# python -m run_together.app

# Create the Flask App
app = Flask(__name__)

app.config["SECRET_KEY"] = env["cookiePassword"]

app.register_blueprint(login_blueprint)
# To use the small icon in the app & use static file in a sub-folder of static
# Define external stylesheets, including Font Awesome and a local CSS file
external_stylesheets = [
    "https://cdnjs.cloudflare.com/ajax/libs/font-awesome/5.15.3/css/all.min.css",
    "./static/css/style.css",  # Add the path to style.css
]

# Adding the Tailwind CSS script in the application setup
# Define external scripts, including the Tailwind CSS framework
external_script = ["https://tailwindcss.com/", {"src": "https://cdn.tailwindcss.com"}]

# Configure DashProxy instance for the Dash application
dash_app = DashProxy(
    __name__,  # Set the name of the Dash application
    server=app,  # Connect the Dash application to the Flask app
    title="Run Together",  # Set the title of the Dash application
    transforms=[
        MultiplexerTransform()
    ],  # Apply the MultiplexerTransform for performance optimization
    pages_folder="./dash_apps/run_together/pages/",  # Specify the folder containing Dash pages
    routes_pathname_prefix="/run-together/",  # Set the URL prefix for Dash routes
    use_pages=True,  # Enable the use of pages for organizing Dash layouts
    assets_folder="./static",  # Specify the folder for static assets (e.g., CSS, images)
    external_stylesheets=external_stylesheets,  # Add external stylesheets to the Dash application
    external_scripts=external_script,  # Add external scripts to the Dash application
)

server = dash_app.server

# Initialize the Run Together Dash application using the configured DashProxy instance
run_together_app(dash_app=dash_app, app_path="/home")



if __name__ == "__main__":
    # Run the Flask app when the script is executed
    app.run(debug=True, host="0.0.0.0", port=8502)  # use_reloader=False
