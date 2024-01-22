from dash import html
from flask import session


container_style = {
    "display": "flex",  # Use Flexbox layout
    "justifyContent": "space-between",  # Align children with space between (left and right)
    "border": "1px solid blue",
    "height": "80px",
    "margin-left": "30px",
    "margin-right": "30px",
}

avatar_style = {
    "margin-left": "auto",  # Display the avatar on the right side of the container
    "height": "95%",
    "border-radius": "40%",  # Create a circular border
    # "padding-right": "60px",   # with margin left auto need to have one here
}


menu_style = {
    "display": "none",  # Initially hide the menu
    "position": "absolute",
    "top": "110%",  # Position the menu just below the image
    "right": 0,  # Position the menu on the right
    "border": "1px solid #ccc",
    "background-color": "white",
    "z-index": 1,  # Ensure the menu appears above other content
}

menu_item_style = {
    "padding": "5px",
    "border-bottom": "1px solid #ccc",
    "cursor": "pointer",
}

name_application = {
    "margin-left": "20px",
    "padding-top": "17px",
    "font-size": "30px",
    "font-weight": "bold",
}


def get_header():
    header = html.Div(
        children=[
            html.Img(
                src="../../../static/img/running_shoe.png",
                alt="Running Shoe",
            ),
            html.Div(
                children="Run Together",
                style=name_application,
            ),
            html.Img(
                src=session["user_profile_picture"],
                alt="Running Shoe",
                style=avatar_style,
            ),
            html.Div(
                id="menu",
                style=menu_style,
                children=[
                    html.Div("Setting", style=menu_item_style),
                    html.Div("My Profile", style=menu_item_style),
                    html.Div("Log Out", style=menu_item_style),
                ],
            ),
        ],
        style=container_style,
    )

    return header
