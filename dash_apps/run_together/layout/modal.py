from dash import html


def get_modal_box() -> html.Div:
    """
    Returns a modal box for displaying content.

    This function creates a modal box with a close button ("x") and an empty modal body.
    The modal box is initially hidden.

    Returns:
    html.Div: A modal box for displaying content.
    """

    # Create the modal box containing modal content
    modal_box = html.Div(
        children=[
            html.Div(
                children=[
                    # Close button for the modal box
                    html.Span(children="x", className="close", id="close-modal-btn"),
                    # Placeholder for modal body content
                    html.Div(id="modal-body"),
                ],
                # Styling for the modal content
                className="modal-content-style",
                id="modal-content",
            )
        ],
        # Styling for the modal box
        className="modal-style",
        id="modal",
        hidden=True,  # Initially hide the modal box
    )
    return modal_box
