import dash_mantine_components as dmc
import dash_html_components as html
from dash_iconify import DashIconify

import os
from pathlib import Path

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parents[2]
STATIC_DIR = os.path.join(BASE_DIR, "static")

header_style = {
    "display": "flex",  # Use Flexbox layout
    "justifyContent": "space-between",  # Align children with space between (left and right)
    "alignItems": "center",  # Center the content vertically (top and bottom)
    "border-bottom": "solid grey 3px",
    "border": f"1px solid {dmc.theme.DEFAULT_COLORS['indigo'][4]}",
    "background-color": "#f7f7fa",
}

container_style = {
    "display": "flex",  # Use Flexbox layout
    "justifyContent": "space-between",  # Align children with space between (left and right)
    "width": "90%",  # Stretch container to 100% of the page width
    "height": "100%",  # Stretch container to 100% of the page width
    "border": f"1px solid {dmc.theme.DEFAULT_COLORS['blue'][4]}",
}


def get_header():
    header = dmc.Header(
        height=80,
        children=[
            dmc.Container(
                children=[
                    html.Img(src="../../static/running_shoe.png", alt="Running Shoe", style={"margin-left": "5px"}),
                    html.H2(children="Run Together", style={"margin-left": "20px", "padding-top": "-5px"}),
                    html.Img(
                        src="https://graph.facebook.com/10225408464183608/picture?height=256&width=256",
                        alt="Running Shoe",
                        style={"margin-left": "auto", "height": "60%", "padding-top": "15px", "border-radius": "50%"}
                    ),

                ], size="xl", px="xl", style=container_style,
            ),
            dmc.Divider(size="100")
        ], style=header_style,
    )

    return header
