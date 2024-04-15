from dash import html
import pandas as pd
from typing import List


def get_last_activities(activities_df: pd.DataFrame) -> List[html.Button]:
    """
        logic to generate the left column content goes from the body
        with the activities from the datafram as input

    :param activities_df:
    :return:
    """
    # This could be fetching data, generating a navigation menu, or displaying additional informatio
    records = activities_df.to_dict("records")
    last_activities = []  # List to store the left column components for each Run

    for run in records:
        # First row with the title
        name_activity = html.Div(
            # Make sure the name is not longer that what can be display
            children=html.Div(children=f"{run['name'][0:43]}"),
            style={"margin-bottom": "10px"},
            className="h3"
        )

        # Second row with three columns and icons
        kpi_icons = html.Div(
            children=[
                html.Div(
                    children=[
                        html.I(className="fas fa-heart"),
                        f"{run['average_heartrate']} bpm",
                    ],
                    className="kpi-icons",
                ),
                html.Div(
                    children=[
                        html.I(className="fas fa-tachometer-alt"),
                        f"{run['average_speed']} /km",
                    ],
                    className="kpi-icons",
                ),
                html.Div(
                    children=[
                        html.I(className="fas fa-shoe-prints"),
                        f"{run['average_cadence']} ppm",
                    ],
                    className="kpi-icons",
                ),
            ],
            className="card_grid",
        )

        # Third row with the "KM" text
        distance_km = html.Div(
            children=[f"{round(run['distance_km'], 2)} KM"],
            style={"margin-top": "10px"},
            className="h2"
        )

        # Combine all rows into a left column grid layout
        activity_card = html.Button(
            children=[name_activity, kpi_icons, distance_km],
            className="activity-card",
            id={
                "type": "select-activity-btn",
                "index":  run['id']
            }
        )

        last_activities.append(activity_card)

    return last_activities
