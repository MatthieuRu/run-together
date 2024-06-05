from datetime import datetime
import time

from dash import html

from dash_apps.run_together.layout.header import get_header
from dash_apps.run_together.layout.footer import get_footer
from dash_apps.run_together.layout.body import get_body
from dash_apps.run_together.layout.modal import get_modal_box

from flask import session
from dash_apps.run_together.strava_manager import StravaManager


def get_home_layout() -> html:
    strava_manager = StravaManager(session=False)

    # no token yet associate to the session
    if "expires_at" not in session:
        strava_manager.generate_token_response(strava_code=session["strava_code"])
    # token expired
    elif time.time() > session["expires_at"]:
        strava_manager.generate_token_response(strava_code=session["strava_code"])
    else:
        strava_manager.set_token_from_session()

    session["selected_year"] = datetime.now().year
    session["selected_month"] = datetime.now().strftime('%b').upper()

    # Add in the session the current athlete
    athlete = strava_manager.get_athlete()
    session["user_profile_picture"] = athlete.profile

    header = get_header()
    body = get_body(year=session["selected_year"], month=session["selected_month"])
    modal_box = get_modal_box()

    footer = get_footer()

    basic_components = [header, html.Br(), body, html.Br(), footer, modal_box]

    return html.Div(children=basic_components)
