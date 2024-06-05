from typing import Union, Dict
from dash.html import Span, Div
from dash import html
import plotly.graph_objects as go
from dash import dcc
import logging
import dash_leaflet as dl
from flask import session
import dash_mantine_components as dmc

from dash_apps.run_together.strava_manager import StravaManager

import datetime


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


def calculate_speed(seconds, distances, range_points, p):
    """
    Calculate the speed in minutes per kilometer (min/km) for an athlete's run.

    Parameters:
    - seconds (list of int): List of time points in seconds.
    - distances (list of float): List of distances corresponding to each time point in meters.
    - range_points (int): Number of points before and after to consider for speed calculation.
    - p (float): Percentage of points to keep (between 0 and 100). E.g., 100% means all points, 50% means every other point.

    Returns:
    - list of float: Speeds in min/km for the given points.
    """

    # Ensure p is between 0 and 100
    if p < 0 or p > 100:
        raise ValueError("Parameter p must be between 0 and 100")

    # Initialize list to hold the speeds
    speeds = []

    # Convert meters to kilometers and seconds to minutes
    def meters_to_km(meters):
        return meters / 1000

    def seconds_to_minutes(seconds):
        return seconds / 60

    # Calculate speed for each point considering range_points
    for i in range(len(seconds)):
        start_index = max(0, i - range_points)
        end_index = min(len(seconds) - 1, i + range_points)

        total_time = seconds[end_index] - seconds[start_index]
        total_distance = distances[end_index] - distances[start_index]

        if total_distance == 0:
            speeds.append(float('inf'))
        else:
            total_time_min = seconds_to_minutes(total_time)
            total_distance_km = meters_to_km(total_distance)
            speed_min_per_km = total_time_min / total_distance_km
            speeds.append(speed_min_per_km)

    return speeds


def get_activity_map(activity_id: int, activity_stream: dict) -> dl.Map:
    """
        Return the Activity Map

    :param activity_id:
    :param activity_stream:
    :return: dl.Map ot the activity
    """

    # Manage the size of the map
    min_latitude = min([x[0] for x in activity_stream["latlng"]["data"]])
    max_latitude = max([x[0] for x in activity_stream["latlng"]["data"]])
    min_longitude = min([x[1] for x in activity_stream["latlng"]["data"]])
    max_longitude = max([x[1] for x in activity_stream["latlng"]["data"]])

    bounds_points = [
        [min_latitude, min_longitude],  # South West
        [max_latitude, max_longitude],  # North East
    ]
    session["bounds_activity_map"] = bounds_points

    # https://leaflet-extras.github.io/leaflet-providers/preview/
    url = "https://tiles.stadiamaps.com/tiles/outdoors/{z}/{x}/{y}{r}.png"
    # url = "https://tiles.stadiamaps.com/tiles/alidade_smooth/{z}/{x}/{y}{r}.png"
    logging.info(url)

    activity_map = dl.Map(
        style={"width": "500px", "height": "500px"},
        id={"type": "activity-map", "index": activity_id},
        bounds=bounds_points,
        children=[
            dl.TileLayer(
                url=url,
            ),
            dl.Polyline(
                positions=activity_stream["latlng"]["data"],
            ),
            dl.LayerGroup(id="marker-map", children=[]),
        ],
    )

    activity_map.viewport = dict(
        bounds=session["bounds_activity_map"], transition="flyToBounds"
    )

    return activity_map


def get_reference_race():
    """

    :return:
    """
    selection_reference_race = html.Div(
        [
            dmc.SegmentedControl(
                id="segmented",
                value="ng",
                data=[
                    {"value": "marathon", "label": "Marathon"},
                    {"value": "half_marathon", "label": "Half Marathon"},
                    {"value": "10km", "label": "10 km"},
                ],
                mb=10,
            ),
        ]
    )
    return selection_reference_race


def get_graph_heart_rate(activity_stream: Dict) -> dcc.Graph:
    """
    Generate a heart rate graph.

    This function creates a heart rate graph based on the provided activity
    stream data,displaying heart rate values over distance.
    The graph is customized with specificstyling and hover interactions.

    :param activity_stream: Dictionary containing activity stream data.
    :return: dcc.Graph component representing the heart rate graph.
    """
    # print(activity_stream)
    speed = calculate_speed(
        seconds=activity_stream['time']['data'][4:],
        distances=activity_stream['distance']['data'][4:],
        range_points=50,
        p=100
    )


    speed_format = [convert_min_to_min_sec(x) for x in speed]
    # speed_second = [(x.hour * 3600) + (x.minute * 60) + x.second for x in speed]
    speed_second = [x * 60 for x in speed]

    # print(speed)

    # Convert distance to km
    distance = [x / 1000 for x in activity_stream["distance"]["data"]]

    paces = [
        {
            "pace": "5:50",
            "race": "EF",
            "color": 'rgb(19, 151, 158)'
        },
        {
            "pace": "4:00",
            "race": "marathon",
            "color": 'rgb(111, 231, 219)'
        },
        {
            "pace": "3:45",
            "race": "half-marathon",
            "color": 'rgb(131, 90, 241)'
        },
        {
            "pace": "3:30",
            "race": "10km",
            "color": 'rgb(184, 247, 212)'
        },
    ]

    fig = go.Figure()

    for pace in paces:
        pace["pace"] = datetime.datetime.strptime(pace["pace"], "%M:%S")
        pace["pace_second"] = (pace["pace"].hour * 3600) + (pace["pace"].minute * 60) + pace["pace"].second

        fig.add_trace(go.Scatter(
            x=distance,
            y=[pace["pace_second"] for i in distance],
            hoverinfo='skip',  # Disable hover information
            mode='lines',
            line=dict(width=10, color=pace['color']),
            name=pace['race']  # define stack group,
        ))

    # Add heart rate data as a scatter plot
    fig.add_trace(
        go.Scatter(
            x=distance,
            y=speed_second,
            mode="lines",
            line=dict(color="#F39C12"),
            hovertemplate="Pace: %{customdata} min/km<extra></extra>",  # Hover tooltip template with y / 60
            name="Pace",
            customdata=speed_format
        )
    )

    # Update layout
    fig.update_layout(title='Pace',
                      # xaxis_title='Points',
                      yaxis_title='Pace min/km',
                      yaxis_tickvals=[pace["pace_second"] for pace in paces],
                      yaxis_ticktext=[pace["pace"].strftime("%M:%S") for pace in paces],
                      yaxis=dict(autorange='reversed'))

    # fig.update_layout(yaxis_range=(200, 350))

    return dcc.Graph(
        figure=fig,
        config={
            "displayLogo": False,
            "displayModeBar": False,
        },  # Disable display of logo and mode bar
        responsive=True,  # Enable responsiveness
        id="activities-graph",  # Set component ID
         )


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

    # Get activity map component
    activity_map = get_activity_map(
        activity_id=activity_id, activity_stream=activity_stream
    )

    # Get heart rate graph component
    heart_rate_graph = get_graph_heart_rate(activity_stream=activity_stream)


    # Create grid layout for displaying map and graph components
    grid = html.Div(
        children=[
            html.Div(className="activities-map-container", children=activity_map),
            html.Div(
                className="activities-graph-container",
                children=[
                    heart_rate_graph,
                    get_reference_race()
                ]
            ),
            # store the activity stream in a dash component to be used in the callbacl
            dcc.Store(id="activity-stream", data=activity_stream),
        ],
        className="grid-activity-map-plot",  # CSS class for styling
    )

    # Return list of HTML components for activity details
    return [
        html.Br(),
        html.Div(children=f"Activity id: {activity_id}"),
        grid,
        html.Div(id="hover", children="test"),
    ]
