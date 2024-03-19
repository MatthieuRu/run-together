import logging
import dash_leaflet as dl
from flask import session
from typing import List


def get_activity_map(activity_id: int, activity_stream: dict):
    """
        Return the Activity Map

    :param activity_id:
    :param activity_stream:
    :return:
    """

    # Manage the size of the map
    min_latitude = min([x[0] for x in activity_stream['latlng']['data']])
    max_latitude = max([x[0] for x in activity_stream['latlng']['data']])
    min_longitude = min([x[1] for x in activity_stream['latlng']['data']])
    max_longitude = max([x[1] for x in activity_stream['latlng']['data']])

    bounds_points = [
        [min_latitude, min_longitude],  # South West
        [max_latitude, max_longitude]  # North East
    ]
    session["bounds_activity_map"] = bounds_points

    # https://leaflet-extras.github.io/leaflet-providers/preview/
    url = "https://tiles.stadiamaps.com/tiles/outdoors/{z}/{x}/{y}{r}.png"
    logging.info(url)

    activity_map = dl.Map(
        style={'width': '500px', 'height': '500px'},
        id={
            "type": "select-activity-btn",
            "index":  activity_id
        },
        bounds=bounds_points,
        children=[
            dl.TileLayer(
                url=url,
            ),
            dl.Polyline(
                positions=activity_stream['latlng']['data'],
            ),
            dl.Marker(position=bounds_points[0]),
            dl.Marker(position=bounds_points[1]),
        ]
    )

    activity_map.viewport = dict(
        bounds=session["bounds_activity_map"],
        transition="flyToBounds"
    )
    return activity_map
