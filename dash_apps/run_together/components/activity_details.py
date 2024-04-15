from typing import Union, Dict
from dash.html import Span, Div
from dash import html
import plotly.graph_objects as go
from dash import dcc
import logging
import dash_leaflet as dl
from flask import session

from dash_apps.run_together.strava_manager import StravaManager


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


def get_graph_heart_rate(activity_stream: Dict) -> dcc.Graph:
    """
    Generate a heart rate graph.

    This function creates a heart rate graph based on the provided activity
    stream data,displaying heart rate values over distance.
    The graph is customized with specificstyling and hover interactions.

    :param activity_stream: Dictionary containing activity stream data.
    :return: dcc.Graph component representing the heart rate graph.
    """
    # Create a new Plotly figure
    fig = go.Figure()

    # Add heart rate data as a scatter plot
    fig.add_trace(
        go.Scatter(
            x=[
                x / 1000 for x in activity_stream["distance"]["data"]
            ],  # Convert distance to km
            y=activity_stream["heartrate"]["data"],
            mode="lines",
            line=dict(color="#F39C12"),
            hovertemplate="Heart Rate: %{y} bpm<extra></extra>",  # Hover tooltip template
        )
    )

    # Customize layout of the graph
    fig.update_layout(
        title=dict(
            text="Heart Rate",
            font=dict(size=50),
        ),
        plot_bgcolor="rgba(0,0,0,0)",  # Set plot background color
    )

    # Customize x-axis appearance
    fig.update_xaxes(
        showspikes=True,
        spikecolor="#F39C12",
        spikesnap="cursor",
        spikemode="across",
        spikedash="solid",
    )

    # Return dcc.Graph component with the generated figure
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
                children=heart_rate_graph,
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
