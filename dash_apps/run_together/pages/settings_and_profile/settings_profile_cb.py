from flask import session
import dash
from dash import Output, Input, State, html, no_update, dcc
from dash_extensions.enrich import DashProxy
import logging
from datetime import datetime
from dash_apps.run_together.pages.settings_and_profile.settings_profile_helper_method import which_race_button, which_race_distance
from connections.update_data_mongo import update_user_record
from dash_apps.run_together.utils.conversion import (
    convert_birthday_back, convert_birthday, marathon_pace, calculate_speed_max)
from dash_apps.run_together.utils.conversion import calculate_age


def settings_profile_cb(dash_app: DashProxy):
    @dash_app.callback(
        Output("user-settings-name", "children"),
        Output("user-settings-email", "children"),
        Output("user-settings-birthday", "children"),
        Input("url", "pathname"),
    )
    def toggle_form(url_path):
        user_values = session.get("run_together_user", {})
        if url_path == "/settings":
            name = f"Name: {user_values['name']}"
            email = f"Email: {user_values['email']}"
            birthday = f"Birthday: {user_values['birthday']}"

            return name, email, birthday
        return no_update

    @dash_app.callback(
        Output("display-user-settings-div", "style"),
        Output("name-input", "value"),
        Output("email-input", "value"),
        Output("birthday-input", "date"),
        Output("form-div", "style"),
        Output("change-button", "style"),
        Input("change-button", "n_clicks"),
        prevent_initial_call=True
    )
    def display_user_form(n_clicks):
        if n_clicks:
            user_values = session.get("run_together_user", {})
            name_input = user_values["name"]
            email_input = user_values["email"]
            birthday_input = convert_birthday_back(user_values["birthday"])

            date_object = datetime.strptime(birthday_input, "%Y-%m-%d")

            return ({"display": "none"}, name_input, email_input,
                    date_object, {"display": "block"}, {"display": "none"}
                    )
        return no_update

    @dash_app.callback(
        Output("user-settings-name", "children"),
        Output("user-settings-email", "children"),
        Output("user-settings-birthday", "children"),
        Output("display-user-settings-div", "style"),
        Output("form-div", "style"),
        Output("change-button", "style"),
        Input('submit-button-user-form', 'n_clicks'),
        State("name-input", "value"),
        State("email-input", "value"),
        State("birthday-input", "date"),
        prevent_initial_call=True
    )
    def update_output(submit_clicks, name, email, birthday):
        if submit_clicks != 0:
            ctx = dash.callback_context
            if not ctx.triggered:
                return no_update
            else:
                button_id = ctx.triggered[0]["prop_id"].split(".")[0]
            if button_id == "submit-button-user-form":
                converted_bd = convert_birthday(birthday)

                max_bpm = 220 - calculate_age(
                    converted_bd)

                update_user_record(session, {
                    "birthday": converted_bd,
                    "name": name,
                    "email": email,
                    "max_bpm": max_bpm}
                )
                session["run_together_user"]["max_bpm"] = max_bpm
                session["run_together_user"]["birthday"] = converted_bd
                session["run_together_user"]["name"] = name
                session["run_together_user"]["email"] = email
                session.modified = True

                name = f"Name: {name}"
                email = f"Email: {email}"
                birthday = f"Birthday: {converted_bd}"

                return name, email, birthday, {"display": "block"}, {"display": "none"}, {"display": "block"}

        return no_update

    @dash_app.callback(
        Output("max-bpm", "children"),
        Output("calculated-pace", "children"),
        Output("speed-max", "children"),
        Input("url", "pathname")
    )
    def calculate_max_bpm(url: str):
        if url == '/settings':
            max_bpm = session["run_together_user"]["max_bpm"]
            pace = session["run_together_user"].get("pace", 0)
            speed_max = session["run_together_user"].get("speed_max", 0)
            race_distance = session["run_together_user"].get("race_distance", 0)
            target_time = session["run_together_user"].get("target_time", {
                    "hours": 0, "minutes": 0, "seconds": 0})

            if (
                pace == 0 or speed_max == 0 or race_distance == 0 or
                target_time == {"hours": 0, "minutes": 0, "seconds": 0}
            ):
                return '', html.P("Please fill in your target time and click the race you plan to run"), html.P("")
            else:
                pace_min, pace_sec = marathon_pace(
                    target_time["hours"], target_time["minutes"],
                    target_time["seconds"], race_distance)

                return max_bpm, html.P(f'Min:{pace_min} Seconds:{pace_sec} for {race_distance}'), html.P(f"{speed_max}")
        else:
            no_update

    @dash_app.callback(
        Output("calculated-pace", "children"),
        Output("speed-max", "children"),
        Output("max-bpm", "children"),
        Input('ten-k-button', 'n_clicks'),
        Input('semi-button', 'n_clicks'),
        Input('full-button', 'n_clicks'),
        State("seconds-dropdown", "value"),
        State("minutes-dropdown", "value"),
        State("hours-dropdown", "value"),
        prevent_initial_call=True
    )
    def calculate_pace_and_save(distance_ten, distance_semi, distance_full, seconds, minutes, hours):
        ctx = dash.callback_context

        if not ctx.triggered:
            button_id = 'No clicks yet'
            distance = None
            return no_update
        else:
            button_id = ctx.triggered[0]['prop_id'].split('.')[0]
            distance, coefficient = which_race_button(button_id)

        if hours is None or minutes is None or seconds is None:
            return html.P("Please fill in all the dropdowns")
        else:
            min, sec = marathon_pace(hours, minutes, seconds, distance)
            pace = min+(sec/60)

            speed_max = calculate_speed_max((min+(sec/60)), coefficient)
            race_distance = which_race_distance(button_id)

            update_user_record(session, {
                "speed_max": speed_max,
                "pace": pace,
                "race_distance": distance,
                "target_time": {
                    "hours": hours, "minutes": minutes, "seconds": seconds}
                }
            )
            max_bpm = session["run_together_user"]["max_bpm"]
            session["run_together_user"]["target_time"] = (hours, minutes, seconds)
            session["run_together_user"]["speed_max"] = speed_max
            session["run_together_user"]["pace"] = pace
            session["run_together_user"]["race_distance"] = distance
            session["run_together_user"]["race"] = race_distance
            session.modified = True

            return html.P(f'Min:{min} Seconds:{sec} for {race_distance}'), html.P(f"{speed_max}"), max_bpm
