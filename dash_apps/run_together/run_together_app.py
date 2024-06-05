import dash
from dash import Input, Output, ctx, ALL, no_update
from dash_extensions.enrich import DashProxy
from flask import session
from datetime import datetime, date
import logging
import dash_leaflet as dl

from dash_apps.run_together.components.calendar_training import get_monthly_calendar
from dash_apps.run_together.components.calendar_training import get_yearly_calendar
from dash_apps.run_together.pages.home import get_home_layout
from dash_apps.run_together.components.activity_details import get_activity_details


def run_together_app(
    dash_app: DashProxy,
    app_path: str,
) -> object:
    dash.register_page(__name__, layout=get_home_layout, path=app_path)

    @dash_app.callback(
        Output("marker-map", "children"),
        Input("activities-graph", "hoverData"),
        Input("activity-stream", "data"),
        prevent_initial_call=True,
    )
    def display_hover_data(hover_data, activity_stream):
        index = hover_data["points"][0]["pointIndex"]
        position = activity_stream["latlng"]["data"][index]

        return [dl.Marker(position=position)]

    @dash_app.callback(
        Output("modal", "hidden"),
        Output("modal-body", "children"),
        Input({"type": "select-activity-btn", "index": ALL}, "n_clicks"),
        prevent_initial_call=True,
    )
    def display_modal_box(n_clicks):
        """
        Open the Modal box when user click on one activity
        :param n_clicks:  User Clicking on the activity
        :return: Hidden = True for the model Component
        """
        logging.info(n_clicks)
        # When the Component is build it can trigger the callbakc to avoid it
        # check that n_click is not None
        if all(x is None for x in n_clicks):
            return no_update, no_update

        session["displayed_activity_id"] = ctx.triggered_id["index"]
        logging.info(
            f"User Action: select-activity-btn. Get Activity: "
            f"id={session['displayed_activity_id']}"
        )

        activity_details_modal_content = get_activity_details(
            activity_id=session["displayed_activity_id"]
        )

        return False, activity_details_modal_content

    @dash_app.callback(
        Output("modal", "hidden"),
        Input("close-modal-btn", "n_clicks"),
        prevent_initial_call=True,
    )
    def close_modal_box(n_clicks):
        """
        Clost the Modal box when user click on the cross
        :param n_clicks:  User Clicking on the cross
        :return: Hidden = True for the model Component
        """

        logging.info("User Action: close-modal-btn. Close Modal Box")
        return True

    @dash_app.callback(
        Output("calendar-training-container", "children"),
        Input({"type": "select-month-btn", "index": ALL}, "n_clicks"),
        Input({"type": "calendar-btn", "index": ALL}, "n_clicks"),
        prevent_initial_call=True,
    )
    def update_calendar_training_container(
        month_n_clicks,
        calendar_n_clicks,
    ):
        triggered_id = ctx.triggered_id
        logging.info(f"1 {ctx.triggered_id}")

        # Case: the user select the months on the monthly calendar
        if triggered_id["type"] == "select-month-btn":
            # Change the value for the selected month according to the user selection
            session["selected_month"] = triggered_id["index"]
            logging.info(
                f"User Action: select-month-btn. Get Monthly Calendar: "
                f"year={session['selected_year']} & month={session['selected_month']}"
            )

            return get_monthly_calendar(
                year=session["selected_year"],
                month=session["selected_month"],
            )

        # Case: the user click on the previous month on the monthly calendar
        if triggered_id.index == "prev-month":
            # If Month is JAN, update the year to the previous one
            if session["selected_month"] == "JAN":
                session["selected_month"] = "DEC"
                session["selected_year"] = session["selected_year"] - 1
            # Else get the previous month in the correct format JAN, FEB etc
            else:
                month_number = (
                    datetime.strptime(session["selected_month"], "%b").month - 1
                )
                session["selected_month"] = datetime.strftime(
                    date(session["selected_year"], month_number, 1), "%b"
                ).upper()

            logging.info(
                f"User Action: prev-month. Get Monthly Calendar: "
                f"year={session['selected_year']} & month={session['selected_month']}"
            )
            return get_monthly_calendar(
                year=session["selected_year"],
                month=session["selected_month"],
            )

        # Case: the user click on the next month on the monthly calendar
        if triggered_id.index == "next-month":
            # If Month is DEC, update the year to the next one
            if session["selected_month"] == "DEC":
                session["selected_month"] = "JAN"
                session["selected_year"] = session["selected_year"] + 1
            # Else get the next month in the correct format JAN, FEB et
            else:
                month_number = (
                    datetime.strptime(session["selected_month"], "%b").month + 1
                )
                session["selected_month"] = datetime.strftime(
                    date(session["selected_year"], month_number, 1), "%b"
                ).upper()

            logging.info(
                f"User Action: next-month. Get Monthly Calendar: "
                f"year={session['selected_year']} & month={session['selected_month']}"
            )
            return get_monthly_calendar(
                year=session["selected_year"],
                month=session["selected_month"],
            )

        # Case: the user click on `back to yearly calendar` from the monthly calendar
        if triggered_id.index == "back-yearly-calendar":
            logging.info(
                f"User Action: back-yearly-calendar. Get yearly Calendar: "
                f"year={session['selected_year']}"
            )
            return get_yearly_calendar(year=session["selected_year"])

        # Case: the user click on the previous year on the yearly calendar
        if triggered_id.index == "prev-year":
            session["selected_year"] = session["selected_year"] - 1

            logging.info(
                f"User Action: prev-year. Get yearly Calendar: year={session['selected_year']}"
            )
            return get_yearly_calendar(year=session["selected_year"])

        # Case: the user click on the next year on the yearly calendar
        if triggered_id.index == "next-year":
            session["selected_year"] = session["selected_year"] + 1

            logging.info(
                f"User Action: next-year. Get yearly Calendar: year={session['selected_year']}"
            )
            return get_yearly_calendar(year=session["selected_year"])
