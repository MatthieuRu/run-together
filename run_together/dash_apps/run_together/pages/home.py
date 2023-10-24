import dash_mantine_components as dmc
import logging
from dash import html
from flask import session
from run_together.dash_apps.run_together.strava_manager import (
    get_strava_activities_pandas,
)
from run_together.dash_apps.run_together.strava_manager import StravaManager
from run_together.dash_apps.run_together.header import get_header
from run_together.dash_apps.run_together.footer import get_footer
from run_together.dash_apps.run_together.body import get_body


def layout() -> html:
    # Create the Strava Client
    strava_manager = StravaManager()
    if "strava_code" in session.keys():
        logging.info("Create a new session with the Strava Code")
        strava_manager.generate_token_response(strava_code=session["strava_code"])
    # Locally to keep the same token when no session.
    else:
        strava_manager.set_token_response(
            access_token="6059e41d580fda7af9a1703fccb8cc4e01737b9e",
            refresh_token="5104e377ddea013d94ce12f7504681e2a76aa017",
            expires_at="1698104802",
        )

    # Get the athlete in a pandas file
    athlete = strava_manager.get_athlete()
    print(athlete.profile)

    activities = strava_manager.strava_client.get_activities(limit=50)
    activities_df = get_strava_activities_pandas(activities)

    header = get_header(athlete.profile)
    # grid = get_body(activities_df)
    grid = get_body()

    footer = get_footer()

    basic_components = [
        header,
        dmc.Space(h=10),
        grid,
        footer,
    ]

    return html.Div(children=basic_components)
