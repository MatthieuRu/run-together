import dash_mantine_components as dmc
from dash_extensions.enrich import DashProxy
from dash import html
import dash
from flask import session
from run_together.dash_apps.run_together.strava_manager import get_strava_activities_pandas
from run_together.dash_apps.run_together.strava_manager import StravaManager
from run_together.dash_apps.run_together.header import get_header
from run_together.dash_apps.run_together.body_generator import get_body

import dash_ag_grid as dag


def layout() -> html:

    # Create the Strava Client
    # print("strava_code:", session['strava_code'])
    strava_manager = StravaManager()
    print(session)
    if "strava_code" in session.keys():
        print("Create a a new session with the Strava Code")
        strava_manager.generate_token_response(
            strava_code=session['strava_code']
        )
    # Locally to keep the same token when no session.
    else:
        strava_manager.set_token_response(
            access_token="b67b74da345925c51e1daa5e542bbf7f282abba8",
            refresh_token="5104e377ddea013d94ce12f7504681e2a76aa017",
            expires_at="1690247956"
        )

    # Get the athlete in a pandas file
    # athlete = strava_manager.get_athlete()

    activities = strava_manager.strava_client.get_activities(limit=5)
    activities_df = get_strava_activities_pandas(activities)

    header = get_header()
    grid = get_body(activities_df)

    basic_components = [
        header,
        dmc.Space(h=10),
        grid

        # dbc.Row(dbc.Col(html.H3(children="Run Together", id="app_name"))),
        # dbc.Row(dbc.Col(html.Div(html.P(children=f"Welcome {athlete.firstname}"), className='heading'))),
        # grid
   ]

    return html.Div(children=basic_components)

def run_together_callbacks(dash_app: DashProxy,
                           app_path: str,
                           app_title: str) -> object:

    dash.register_page(
        __name__,
        layout=layout,
        path=app_path,
        title=app_title
    )

