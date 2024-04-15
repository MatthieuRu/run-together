from typing import List, Union
from dash.html import Span, Div
import plotly.graph_objects as go
from dash import dcc, html

from dash_apps.run_together.components.activity_map import get_activity_map
from dash_apps.run_together.strava_manager import StravaManager


def get_activity_details(activity_id: int) -> list[Union[Span, Div]]:
    strava_manager = StravaManager()
    activity_stream = strava_manager.get_activity_stream(activity_id=activity_id)

    activity_map = get_activity_map(
        activity_id=activity_id,
        activity_stream=activity_stream
    )

    fig = go.Figure()
    fig.add_trace(
        go.Scatter(
            x=[x / 1000 for x in activity_stream['distance']['data']], # Get the distance in km
            y=activity_stream['heartrate']['data'],
            mode='lines',
            name='lines'
        )
    )

    fig.add_trace(
        go.Scatter(
            x=[x / 1000 for x in activity_stream['distance']['data']], # Get the distance in km
            y=activity_stream['heartrate']['data'],
            mode='lines',
            name='lines'
        )
    )

    fig.update_xaxes(
        showspikes=True,
        spikecolor="green",
        spikesnap="cursor",
        spikemode="across",
        spikedash="solid",
    )

    grid = html.Div(
        children=[
            html.Div(
                className="activities-map-container",
                children=activity_map
            ),
            html.Div(
                className="activities-graph-container",
                children=dcc.Graph(
                    figure=fig,
                    config={'displayLogo': False},
                    responsive=True,
                    id="activities-graph"
                ),
            ),
        ],
        className="grid-activity-map-plot",  # CSS class for styling
    )

    return [
        html.Br(),
        grid,
        html.Div(
            id="hover",
            children="test"
        ),
    ]
