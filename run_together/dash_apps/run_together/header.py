import dash_mantine_components as dmc
from dash import html


header_style = {
    "display": "flex",  # Use Flexbox layout
    "justifyContent": "space-between",  # Align children with space between (left and right)
    "alignItems": "center",  # Center the content vertically (top and bottom)
    "border-bottom": "solid grey 3px",
    "border": f"1px solid {dmc.theme.DEFAULT_COLORS['green'][4]}",
    "background-color": "#f7f7fa",
}

container_style = {
    "display": "flex",  # Use Flexbox layout
    "justifyContent": "space-between",  # Align children with space between (left and right)
    "width": "90%",  # Stretch container to 100% of the page width
    "height": "100%",  # Stretch container to 100% of the page width
    "border": f"1px solid {dmc.theme.DEFAULT_COLORS['blue'][4]}",
}

avatar_style = {
    "margin-left": "auto",  # Display the avatar on the right side of the container
    "height": "60%",
    "padding-top": "15px",
    "border-radius": "50%",  # Create curve around the picture
}


def get_header(url_pricture_strava: str):
    header = dmc.Header(
        height=80,
        children=[
            dmc.Container(
                children=[
                    html.Img(
                        src="../../static/running_shoe.png",
                        alt="Running Shoe",
                        style={"margin-left": "5px"},
                    ),
                    html.H2(
                        children="Run Together",
                        style={"margin-left": "20px", "padding-top": "-5px"},
                    ),
                    html.Img(
                        src=url_pricture_strava, alt="Running Shoe", style=avatar_style
                    ),
                ],
                size="xl",
                px="xl",
                style=container_style,
            ),
        ],
        style=header_style,
    )

    return header
