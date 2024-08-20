from dash import html, register_page, dcc
import dash_bootstrap_components as dbc

from dash_apps.run_together.layout.header import get_header
from dash_apps.run_together.layout.footer import get_footer
from dash_apps.run_together.pages.settings_and_profile.settings_page_html_components import (
    user_settings_div, user_settings_form)

register_page(
    __name__,
    name='Settings',
    top_nav=True,
    path='/settings'
)

card_style = {
    "color": "black",
    "fontSize": "15px"
}

hours_options = [{'label': str(i), 'value': i} for i in range(6)]
minutes_seconds_options = [{'label': str(i), 'value': i} for i in range(61)]


def get_settings():
    settings_tab = html.Div(
        style={
            'display': 'flex',
            'flexDirection': 'column',
            'justifyContent': 'center',
            'alignItems': 'center',
            'height': '100vh',
            'padding': '20px',
        },
        children=[
            html.Div([
                html.H1('User Information'),
                user_settings_div,
                user_settings_form,
                html.Button('Change', id='change-button', n_clicks=0)
            ])
        ]
    )

    profile_tab = dbc.Card(
        dbc.CardBody(
            [
                html.Div(
                    style={
                        'display': 'flex',
                        'flexDirection': 'column',
                        'justifyContent': 'center',
                        'alignItems': 'center',
                        'height': '100vh',
                        'padding': '20px',
                    },
                    children=[
                        # Buttons in the middle of the body
                        html.Div(
                            style={
                                'display': 'flex',
                                'justifyContent': 'center',
                                'alignItems': 'center',
                                'marginBottom': '20px',
                            },
                            children=[
                                dbc.Button("10 kilometers", id="ten-k-button",
                                           color="secondary", className="mr-2"),
                                dbc.Button("Semi-marathon", id="semi-button",
                                           color="secondary", className="mr-2"),
                                dbc.Button("Marathon", id="full-button",
                                           color="secondary"),
                            ]
                        ),
                        html.Div(
                            children=[
                                html.Div(
                                    children=[
                                        html.Label("Target time:"),
                                        dcc.Dropdown(
                                            id='hours-dropdown',
                                            options=hours_options,
                                            placeholder="Hours",
                                            className="time-goal-dropdown"
                                        ),
                                        dcc.Dropdown(
                                            id='minutes-dropdown',
                                            options=minutes_seconds_options,
                                            placeholder="Minutes",
                                            className="time-goal-dropdown"
                                        ),
                                        dcc.Dropdown(
                                            id='seconds-dropdown',
                                            options=minutes_seconds_options,
                                            placeholder="Seconds",
                                            className="time-goal-dropdown"
                                        )
                                    ],
                                    className='time-dropdowns'
                                ),
                                html.Div(
                                    children=[
                                        html.P("Pace:"),
                                        html.P(id="calculated-pace"),
                                        html.P("Speed max"),
                                        html.P(id="speed-max"),
                                    ],
                                    className='calculated-pace'
                                ),
                                html.Div(
                                    children=[
                                        html.P("Max BPM:"),
                                        html.P(
                                            id="max-bpm"
                                        )
                                    ],
                                    className='max-bpm'
                                )
                            ],
                            id="styled-numeric-input"
                        )
                    ]
                )
            ]
        )
    )

    tabs = dbc.Tabs(
        [
            dbc.Tab(
                settings_tab, label="Settings", label_style=card_style,
                tab_id='settings-tab'),
            dbc.Tab(
                profile_tab, label="Profile", label_style=card_style,
                tab_id='profile-tab')
        ],
        id='settings-tabs',
        active_tab='settings-tab'
    )
    return tabs


def layout():
    header = get_header()
    body = get_settings()
    footer = get_footer()

    basic_components = [
        header,
        html.Div(
            children=[body, dcc.Location(id="url", refresh=False)],
            style={
                "flex": "1",
                "padding": "20px"
            }
        ),
        footer,
    ]

    return html.Div(
        style={
            'display': 'flex',
            'flexDirection': 'column',
            'minHeight': '100vh'
        },
        children=basic_components)
