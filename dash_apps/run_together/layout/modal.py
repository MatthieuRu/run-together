from dash import html
from typing import Optional


def get_modal_box() -> html.Div:

    modal_box = html.Div(
        children=[
            html.Div(
                children=[
                    html.Span(
                        children="x",
                        className="close",
                        id="close-modal-btn"
                    ),
                    html.Div(id="modal-body")
                ],
                className="modal-content-style",
                id="modal-content"
            )
        ],
        className="modal-style",
        id="modal",
        hidden=True,
    )
    return modal_box
