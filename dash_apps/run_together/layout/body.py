import dash_ag_grid as dag
from dash import html
import pandas as pd

from dash_apps.run_together.components.calendar_training import get_yearly_calendar
from dash_apps.run_together.components.last_activities import get_last_activities
from dash_apps.run_together.strava_manager import StravaManager


def generate_central_column_bis(activities_df: pd.DataFrame):
    # TODO: To never display in production
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
    # Add in the session the current activities
    strava_manager = StravaManager()
    activities_df = strava_manager.get_activities_for_year(year=year)

    grid = html.Div(
        children=[
            html.Div(
                className="last-activities-container",
                # style={"border": "1px solid pink"},
                children=get_last_activities(
                    activities_df=activities_df.iloc[[1, 3, 5],]
                ),
            ),
            html.Div(
                className="calendar-container",
                children=[
                    html.Div(
                        style={"font-size": "24px", "font-weight": "bold"},
                        children="Training Calendar",
                    ),
                    html.Div(
                        children=get_yearly_calendar(year=year),
                        id="calendar-training-container",
                    ),
                ],
            ),
        ],
        className="grid",  # CSS class for styling
    )

    return html.Div(
        children=[
            grid,
            # generate_central_column_bis(
            #     activities_df=activities_df
            # ),
        ]
    )
