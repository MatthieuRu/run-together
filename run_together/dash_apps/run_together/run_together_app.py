import dash
from dash import Input, Output, ctx, ALL
from dash_extensions.enrich import DashProxy
from flask import session
from datetime import datetime, date

from run_together.dash_apps.run_together.strava_manager import StravaManager
from run_together.dash_apps.run_together.strava_manager import get_strava_activities_pandas
from run_together.dash_apps.run_together.strava_manager import get_strava_activities_string
from run_together.dash_apps.run_together.training_calendar import get_week_calendar
from run_together.dash_apps.run_together.training_calendar import get_training_calendar
from run_together.dash_apps.run_together.pages.home import get_layout


def run_together_callbacks(
        dash_app: DashProxy,
        app_path: str,
) -> object:
    dash.register_page(
        __name__,
        layout=get_layout,
        path=app_path
    )

    @dash_app.callback(
        Output("calendar-training-container", "children", allow_duplicate=True),

        Input({"type": "select-month-btn", "index": ALL}, "n_clicks"),
        Input({"type": "select-month-btn", "index": ALL}, "children"),

        Input({"type": "calendar-btn", "index": ALL}, "n_clicks"),

        prevent_initial_call=True,
    )
    def update_year_calendar_training(
            month_n_clicks,
            month_children,
            calendar_n_clicks,
    ):
        print("session", session)
        triggered_id = ctx.triggered_id
        print("ctx", ctx)
        print("triggered_id", triggered_id)
        print(month_children)

        # Case we are in the monthly calendar & user select previous month
        if triggered_id.index == "prev-month":

            # Update the selected month based on the direction
            if session["selected_month"] == "JAN":
                session["selected_month"] = "DEC"
                session["selected_year"] = session["selected_year"] - 1
            else:
                month_number = datetime.strptime(session["selected_month"], '%b').month - 1
                session["selected_month"] = datetime.strftime(
                    date(session["selected_year"], month_number, 1),
                    '%b'
                ).upper()

            return get_week_calendar(
                selected_year=session["selected_year"],
                selected_month=session["selected_month"]
            )

        # Case we are in the monthly calendar & user next previous month
        if triggered_id.index == "next-month":
            # Update the selected month based on the direction
            if session["selected_month"] == "DEC":
                session["selected_month"] = "JAN"
                session["selected_year"] = session["selected_year"] + 1
            else:
                month_number = datetime.strptime(session["selected_month"], '%b').month + 1
                session["selected_month"] = datetime.strftime(
                    date(session["selected_year"], month_number, 1),
                    '%b'
                ).upper()

            return get_week_calendar(
                selected_year=session["selected_year"],
                selected_month=session["selected_month"]
            )

        # Case we are in the yearly calendar & user click on specific  month
        if triggered_id["type"] == "select-month-btn":
            session["selected_month"] = month_children[triggered_id["index"]][0]["props"]["children"]

            return get_week_calendar(
                selected_year=session["selected_year"],
                selected_month=session["selected_month"]
            )

        # Case we are in the yearly calendar & user click on previous year
        if triggered_id.index == "prev-year":
            session["selected_year"] = session["selected_year"] - 1

        # Case we are in the yearly calendar & user click on previous year
        if triggered_id.index == "next-year":
            session["selected_year"] = session["selected_year"] + 1

        strava_manager = StravaManager()
        strava_manager.set_token_response(
            access_token=session["access_token"],
            refresh_token=session["refresh_token"],
            expires_at=session["expires_at"],
        )

        activities = strava_manager.get_activities_for_year(session["selected_year"])
        activities_dict = get_strava_activities_string(activities)
        activities_df = get_strava_activities_pandas(activities_dict)

        year_calendar_training = get_training_calendar(
            activities_df=activities_df,
            year=session["selected_year"]
        )
        return year_calendar_training


