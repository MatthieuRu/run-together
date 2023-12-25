import dash_mantine_components as dmc
from datetime import datetime

from dash import html

from run_together.dash_apps.run_together.layout.header import get_header
from run_together.dash_apps.run_together.layout.footer import get_footer
from run_together.dash_apps.run_together.layout.body import get_body
from os import environ as env

from flask import session
from run_together.dash_apps.run_together.strava_manager import StravaManager


def get_layout() -> html:
    strava_manager = StravaManager()

    # strava_manager.generate_token_response(strava_code=session["strava_code"])
    session["access_token"] = env['access_token']
    session["refresh_token"] = env['refresh_token']
    session["expires_at"] = env['expires_at']

    strava_manager.set_token_response(
        access_token=session["access_token"],
        refresh_token=session["refresh_token"],
        expires_at=session["expires_at"],
    )

    current_year = datetime.now().year
    session["selected_year"] = current_year

    # Add in the session the current athlete
    athlete = strava_manager.get_athlete()
    session["user_profile_picture"] = athlete.profile

    header = get_header()
    grid = get_body(year=2023)

    footer = get_footer()

    basic_components = [
        header,
        dmc.Space(h=10),
        grid,
        footer,
    ]

    return html.Div(children=basic_components)
