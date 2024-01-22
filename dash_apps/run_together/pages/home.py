import dash_mantine_components as dmc
from datetime import datetime

from dash import html

from dash_apps.run_together.layout.header import get_header
from dash_apps.run_together.layout.footer import get_footer
from dash_apps.run_together.layout.body import get_body

from flask import session
from dash_apps.run_together.strava_manager import StravaManager


def get_home_layout() -> html:
    strava_manager = StravaManager(session=False)

    # If Token need to be refreshed
    # strava_manager.generate_token_response(strava_code=session["strava_code"])

    strava_manager.set_token_from_env()

    current_year = datetime.now().year
    session["selected_year"] = current_year

    # Add in the session the current athlete
    athlete = strava_manager.get_athlete()
    session["user_profile_picture"] = athlete.profile

    header = get_header()
    body = get_body(year=session["selected_year"])

    footer = get_footer()

    basic_components = [
        header,
        dmc.Space(h=10),
        body,
        footer,
    ]

    return html.Div(children=basic_components)
