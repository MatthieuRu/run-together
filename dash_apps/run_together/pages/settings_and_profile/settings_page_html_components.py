from dash import html, dcc

user_settings_div = html.Div(
    children=[
            html.P(id="user-settings-name"),
            html.P(id="user-settings-email"),
            html.P(id="user-settings-birthday")
    ],
    className="user-settings-display",
    id="display-user-settings-div"
)


user_settings_form = html.Div(
    children=[
        html.Form([
            html.Div([
                html.Label("Name:"),
                dcc.Input(
                    type="text", id="name-input",
                    className="user-input-field",
                    placeholder="Enter your name",
                    value='',
                    required=True
                ),
            ]),
            html.Div([
                html.Label("Email Address:"),
                dcc.Input(
                    type="email", id="email-input",
                    className="user-input-field",
                    placeholder="Enter your email",
                    value='',
                    required=True)
            ]),
            html.Div([
                html.Label("Birthday:"),
                dcc.DatePickerSingle(
                    id="birthday-input",
                    display_format="DD-MM-YYYY",
                    placeholder="Select your birthday",
                    className="user-input-field",
                    date=''
                )
            ]),
        ]),
        html.Button("Submit", id="submit-button-user-form", n_clicks=0)
    ],
    id='form-div',
    className="user-settings-form-container",
    style={"display": "none"}
)
