from typing import Dict
from dash import html
import plotly.graph_objects as go
from dash import dcc
import dash_mantine_components as dmc
from dash.html import Div


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


def get_activity_graph(activity_stream: Dict) -> Div:
    """
    Generate a Activity Pace graph.

    This function creates a heart rate graph based on the provided activity
    stream data,displaying heart rate values over distance.
    The graph is customized with specificstyling and hover interactions.

    :param activity_stream: Dictionary containing activity stream data.
    :return: dcc.Graph component representing the heart rate graph.
    """

    # Convert distance to km
    distance = [x / 1000 for x in activity_stream["distance"]["data"]]

    # paces = [
    #     {
    #         "pace": "5:50",
    #         "race": "EF",
    #         "color": 'rgb(19, 151, 158)'
    #     },
    #     {
    #         "pace": "4:00",
    #         "race": "marathon",
    #         "color": 'rgb(111, 231, 219)'
    #     },
    #     {
    #         "pace": "3:45",
    #         "race": "half-marathon",
    #         "color": 'rgb(131, 90, 241)'
    #     },
    #     {
    #         "pace": "3:30",
    #         "race": "10km",
    #         "color": 'rgb(184, 247, 212)'
    #     },
    # ]
    #
    #
    # for pace in paces:
    #     pace["pace"] = datetime.datetime.strptime(pace["pace"], "%M:%S")
    #     pace["pace_second"] = (pace["pace"].hour * 3600) + (pace["pace"].minute * 60) + pace["pace"].second
    #
    #     fig.add_trace(go.Scatter(
    #         x=distance,
    #         y=[pace["pace_second"] for i in distance],
    #         hoverinfo='skip',  # Disable hover information
    #         mode='lines',
    #         line=dict(width=10, color=pace['color']),
    #         name=pace['race']  # define stack group,
    #     ))

    fig = go.Figure()

    # Add heart rate data as a scatter plot
    fig.add_trace(
        go.Scatter(
            x=distance,
            y=activity_stream['pace']['minute_per_km'],
            mode="lines",
            line=dict(color="#F39C12"),
            hovertemplate="Pace: %{customdata} min/km<extra></extra>",  # Hover tooltip template with y / 60
            name="Pace",
            customdata=activity_stream['pace']['minute_second_per_km']
        )
    )

    # Update layout
    fig.update_layout(
        title='Pace',
        # xaxis_title='Points',
        yaxis_title='Pace min/km',
        # yaxis_tickvals=[pace for pace in activity_stream['pace']['second_per_km']],
        # yaxis_ticktext=[pace for pace in activity_stream['pace']['minute_second_per_km']],
        yaxis=dict(autorange='reversed'),
        # width=1000,
    )

    activity_graph = dcc.Graph(
                figure=fig,
                style={"width": "100%"},
                # width=1000,
                config={
                    "displayLogo": False,
                    "displayModeBar": False,
                },  # Disable display of logo and mode bar
                id="activities-graph",  # Set component ID
                className="graph-container"
        )

    range_slider = html.Div(
        children=dcc.Slider(
            min=0, max=100, step=1, value=50, id="myRange",
            className="range-slider-pace",
            # tooltip={"always_visible": True},
            marks={
                0: '0%',
                50: '50%',
                100: '100%'
            },
        ),
        className="div-range-slider-pace"
    )

    return html.Div(
        children=[
            html.Div(id="outputal", children="text"),
            html.Div(
                className="activities-graph-container",
                children=[
                    get_reference_race(),
                    activity_graph,
                    range_slider
                ]
            )
        ]
    )


