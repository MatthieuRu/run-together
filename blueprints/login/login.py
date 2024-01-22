from os import environ as env
from dotenv import load_dotenv
from flask import Blueprint, render_template
from stravalib import client
from flask import request, redirect, session

# Create the Blueprint Login
login_blueprint = Blueprint(
    "login",
    __name__,
    template_folder="templates",  # Find the HTML template folder
    static_folder="static",  # Find the CSS file style folder
)

# Load .env file where are stored my strava credential
load_dotenv()
strava_client_id = env["stravaClientId"]
strava_client_secret = env["stravaClientSecret"]

# Strava Lib Client
client = client.Client()


@login_blueprint.route("/")
def landing():
    """Get the URL needed to authorize your application to access a Strava
    user's information.
    Add this URL as a parameter of my HTML file login.html as redirect of the login Button
    """
    authorize_url = client.authorization_url(
        client_id=strava_client_id,
        redirect_uri="http://127.0.0.1:8502/run-together/callback",
        scope=["read_all", "profile:read_all", "activity:read_all"],
    )

    return render_template("login.html", authorize_url=authorize_url)


@login_blueprint.route("/run-together/callback")
def strava_callback():
    """Strava the code needed to get the user's data in Callback in the following ULR:
    http://127.0.0.1:8502/run-together/?state=&code={code}&scope=read,activity:read_all,profile:read_all,read_all
    This function get the code, put it in the Flash Session.
    Redirect to the Dash
        Add this URL as a parameter of my HTML file login.html as redirect of the login Button
    """

    # Get the code parameter from the URL
    code = request.args.get("code")

    # add in to the Flask Session
    session["strava_code"] = code

    # After obtaining the access token, you can redirect the user to your DASH application page
    return redirect("/run-together/home")
