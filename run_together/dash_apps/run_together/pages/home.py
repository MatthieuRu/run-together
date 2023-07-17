import dash_mantine_components as dmc
import dash_bootstrap_components as dbc
from dash_extensions.enrich import DashProxy
from dash import html
import dash
from flask import session
from stravalib.client import Client
from os import environ as env
from dotenv import load_dotenv
from run_together.dash_apps.run_together.strava import get_strava_activities_pandas
import dash_ag_grid as dag

# Load .env file
load_dotenv()
strava_client_id = env['stravaClientId']
strava_client_secret = env['stravaClientSecret']


def layout() -> html:
    client = Client()
    token_response = client.exchange_code_for_token(
        client_id=strava_client_id,
        client_secret=strava_client_secret,
        code=session["strava_code"]
    )

    # Now store that short-lived access token somewhere (a database?)
    client.access_token = token_response['access_token']
    # You must also store the refresh token to be used later on to obtain another valid access token
    # in case the current is already expired
    client.refresh_token = token_response['refresh_token']

    # An access_token is only valid for 6 hours, store expires_at somewhere and
    # check it before making an API call.
    client.token_expires_at = token_response['expires_at']

    # Get the athlete in a pandas file
    athlete = client.get_athlete()
    activities = client.get_activities(limit=100)
    activities_df = get_strava_activities_pandas(activities)

    # Build the table with all the activities
    records = activities_df.to_dict('records')
    column_defs = []
    for col in list(activities_df):
        column_defs.append({"field": col})

    grid = dag.AgGrid(
        id="activity-table",
        rowData=records,
        columnDefs=column_defs,
        defaultColDef={
            "resizable": True,
            "sortable": True,
            "filter": True,
            "minWidth": 125,
            "editable": False,
        },
        columnSize="sizeToFit",
        dashGridOptions={"rowSelection": "single"},
    )

    basic_components = [
        dmc.Space(h=10),
        dbc.Row(dbc.Col(html.H3(children="Run Together", id="app_name"))),
        dbc.Row(dbc.Col(html.Div(html.P(children=f"Welcome {athlete.firstname}"), className='heading'))),
        grid
   ]

    return dbc.Container(
        [
            html.Div(children=basic_components)
        ], fluid=True)


def run_together_callbacks(dash_app: DashProxy,
                           app_path: str,
                           app_title: str) -> object:

    dash.register_page(
        __name__,
        layout=layout,
        path=app_path,
        title=app_title
    )

