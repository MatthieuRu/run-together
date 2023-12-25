import dash_ag_grid as dag
from dash import html
import pandas as pd
from flask import session
from run_together.dash_apps.run_together.training_calendar import get_training_calendar
from run_together.dash_apps.run_together.strava_manager import get_strava_activities_pandas

from run_together.dash_apps.run_together.strava_manager import StravaManager
from run_together.dash_apps.run_together.strava_manager import get_strava_activities_string


def generate_left_column(activities_df: pd.DataFrame):
    # Your logic to generate the left column content goes here
    # This could be fetching data, generating a navigation menu, or displaying additional information

    records = activities_df.to_dict("records")

    left_columns = []  # List to store the left column components for each Run

    for run in records:
        # First row with the title
        first_row = html.Div(
            children=[
                # html.H4(f"Menu Item {run.run_id}")
                html.Div(
                    className="h2",
                    children=f"{run['name']}"
                )
            ]
        )

        # Second row with three columns and icons
        second_row = html.Div(
            children=[
                html.Div(
                    children=[
                        html.I(className="fas fa-heart"),
                        f"{run['average_heartrate']} bpm",
                    ],
                    className="column",
                ),
                html.Div(
                    children=[
                        html.I(className="fas fa-tachometer-alt"),
                        f"{run['average_speed']} /km",
                    ],
                    className="column",
                ),
                html.Div(
                    children=[
                        html.I(className="fas fa-shoe-prints"),
                        f"{run['average_cadence']} ppm",
                    ],
                    className="column",
                ),
            ],
            className="card_grid",
        )

        # Third row with the "KM" text
        third_row = html.Div(children=[f"{round(run['distance_km'], 2)} KM"])

        # Combine all rows into a left column grid layout
        left_column_content = html.Div(
            children=[first_row, second_row, third_row], className="left-column"
        )

        left_columns.append(
            left_column_content
        )  # Add the generated component to the list

    return left_columns


def generate_central_column_bis(activities_df: pd.DataFrame):
    # Your logic to generate the central column content goes here
    # This could be fetching the main content from a database or processing user input

    # Build the table with all the activities
    records = activities_df.to_dict("records")
    column_defs = []
    for col in list(activities_df):
        column_defs.append({"field": col})

    central_column_content = dag.AgGrid(
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

    return central_column_content


def get_body(year: int):
    strava_manager = StravaManager()

    strava_manager.set_token_response(
        access_token=session["access_token"],
        refresh_token=session["refresh_token"],
        expires_at=session["expires_at"],
    )

    # Add in the session the current activities
    activities = strava_manager.get_activities_for_year(year)

    activities_dict = get_strava_activities_string(activities)
    activities_df = get_strava_activities_pandas(activities_dict)

    grid = html.Div(
        children=[
            html.Div(
                children=generate_left_column(activities_df=activities_df.head(3)),
            ),
            html.Div(
                className="calendar-container",
                children=[
                    html.Div(className="month-name", children=f"Training Calendar"),
                    html.Div(
                        children=get_training_calendar(
                            activities_df=activities_df,
                            year=year
                        ),
                        # style={"height": "400px"},
                        id="calendar-training-container"
                    ),
                ]
            )
        ],
        className="grid",  # You can define a CSS class for styling
    )
    return html.Div(children=[grid])

    # return html.Div(children=[grid, generate_central_column_bis(activities_df=activities_df)])