import logging
from typing import Union, List
from dash.html import Span, Div
from dash import html, dcc
from dash_apps.run_together.components.activity_map import get_activity_map
from dash_apps.run_together.components.activity_graph import get_activity_graph

from dash_apps.run_together.strava_manager import StravaManager


def convert_min_to_min_sec(minutes):
    """
    Convert a float value in minutes to a string in "M:S" format with minutes and seconds.

    Parameters:
    - minutes (float): Time in minutes.

    Returns:
    - str: Time in "M:S" format.
    """
    # Separate the integer part (minutes) from the fractional part (seconds)
    mins = int(minutes)
    secs = (minutes - mins) * 60
    return f"{mins}:{int(secs):02d}"


def calculate_pace(seconds: List[int], distances: List[float], range_points: int) -> List[float]:
    """
    Calculate the speed in minutes per kilometer (min/km) for an athlete's run.

    Parameters:
    - seconds (list of int): List of time points in seconds.
    - distances (list of float): List of distances corresponding to each time point in meters.
    - range_points (int): Number of points before and after to consider for pace calculation.

    Returns:
    - list of float: Speeds in min/km for the given points. it provides a float time minute  and not MM:SS
    """
    # Initialize list to hold the speeds
    paces = []

    # Calculate speed for each point considering range_points
    for i in range(len(seconds)):
        start_index = max(0, i - range_points)
        end_index = min(len(seconds) - 1, i + range_points)

        # TIme and distance from the point i + N and j + N
        total_time = seconds[end_index] - seconds[start_index]
        total_distance = distances[end_index] - distances[start_index]

        if total_distance == 0:
            paces.append(float('inf'))
        else:
            # Convert second to kilometers and seconds to minutes
            total_time_min = total_time / 60
            total_distance_km = total_distance / 1000
            # Calculation of the pace
            speed_min_per_km = total_time_min / total_distance_km
            paces.append(speed_min_per_km)

    return paces


def get_activity_details(activity_id: int) -> list[Union[Span, Div]]:
    """
    Retrieve activity details.

    This function retrieves activity details for a given activity ID,
    including the activity stream, activity map, heart rate graph,
    and grid layout for displaying map and graph components.

    :param activity_id: ID of the activity.
    :return: List containing HTML components for activity details.
    """
    # Retrieve activity stream data
    strava_manager = StravaManager()
    activity_stream = strava_manager.get_activity_stream(activity_id=activity_id)

    # Get also the pace in both format (MM.2f use for the real y value and MM:SS for the better display)
    activity_stream['pace'] = {}
    activity_stream['pace']['minute_per_km'] = calculate_pace(
        seconds=activity_stream['time']['data'][0:],
        distances=activity_stream['distance']['data'][0:],
        range_points=50,
    )
    activity_stream['pace']['minute_second_per_km'] = [
        convert_min_to_min_sec(x) for x in activity_stream['pace']['minute_per_km']
    ]

    # Get activity map component
    activity_map = get_activity_map(
        activity_id=activity_id, activity_stream=activity_stream
    )

    # Create grid layout for displaying map and graph components
    grid = html.Div(
        children=[
            html.Div(className="activities-map-container", children=activity_map),
            html.Div(
                className="activities-analyze-container",
                children=get_activity_graph(activity_stream=activity_stream)
            ),
            # store the activity stream in a dash component to be used in the callbacl
        ],
        className="grid-activity-details",  # CSS class for styling
    )

    # Return list of HTML components for activity details
    return [
        html.Br(),
        dcc.Interval(
            id='interval-component',
            interval=10,  # in milliseconds
            n_intervals=0
        ),
        dcc.Store(id='window-size'),
        # html.Div(id="output-interval", children="text"),
        html.Div(children=f"Activity id: {activity_id}"),

        dcc.Store(id="activity-stream", data=activity_stream),

        grid,
    ]
