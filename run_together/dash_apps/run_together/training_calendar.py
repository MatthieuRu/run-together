from dash import html
import pandas as pd
from flask import session
import calendar
from datetime import datetime, date

from run_together.dash_apps.run_together.strava_manager import StravaManager
from run_together.dash_apps.run_together.strava_manager import (
    get_strava_activities_string,
)
from run_together.dash_apps.run_together.strava_manager import (
    get_strava_activities_pandas,
)
from run_together.dash_apps.run_together.strava_manager import seconds_to_h


def normalize(value, max_value):
    min_value = 0  # Minimum value in the original range
    min_range = 40  # Minimum value in the desired range
    max_range = 140  # Maximum value in the desired range
    return (value - min_value) / (max_value - min_value) * (
        max_range - min_range
    ) + min_range


def get_monday_of_week(year, week_number):
    # Create a date object for January 1 of the given year

    return date.fromisocalendar(year=year, week=week_number, day=1)


def get_sunday_of_week(year, week_number):
    # Get the Monday of the week
    return date.fromisocalendar(year=year, week=week_number, day=7)


def get_monthly_calendar(selected_year: int, selected_month: str):
    # Get the number of days in the selected month
    month_number = datetime.strptime(selected_month, "%b").month
    _, num_days = calendar.monthrange(selected_year, month_number)

    # Create a DataFrame with all days of the month
    all_days_selected_month = pd.date_range(
        f"{selected_year}-{month_number}-01", periods=num_days, freq="D"
    )

    first_monday_after = get_monday_of_week(
        year=all_days_selected_month[0].isocalendar()[0],
        week_number=all_days_selected_month[0].isocalendar()[
            1
        ],  # Get the ISO week number
    )

    first_sunday_before = get_sunday_of_week(
        year=all_days_selected_month[-1].isocalendar()[0],
        week_number=all_days_selected_month[-1].isocalendar()[
            1
        ],  # Get the ISO week number
    )

    all_days_selected_month = pd.date_range(
        first_monday_after, first_sunday_before, freq="d"
    )

    month_df = pd.DataFrame({"date": all_days_selected_month})
    # print(month_df)
    strava_manager = StravaManager()
    strava_manager.set_token_response(
        access_token=session["access_token"],
        refresh_token=session["refresh_token"],
        expires_at=session["expires_at"],
    )

    # get the first qnd the last day of the week associate
    activities = strava_manager.get_activities_between(
        start_date=first_monday_after, end_date=first_sunday_before
    )

    activities_dict = get_strava_activities_string(activities)
    activities_df = get_strava_activities_pandas(activities_dict)

    # Merge the DataFrame with activities and the one with all days to get a complete calendar
    month_df["date_str"] = month_df["date"].dt.strftime("%Y-%m-%d")
    activities_df["start_date_local_str"] = activities_df[
        "start_date_local"
    ].dt.strftime("%Y-%m-%d")

    full_calendar = pd.merge(
        left=month_df,
        right=activities_df,
        left_on="date_str",
        right_on="start_date_local_str",
        how="left",
    )

    # Calculate week_of_month based on start_date_local
    full_calendar["week_number"] = (
        full_calendar["date"].dt.to_period("W").apply(lambda x: x.week)
    )
    full_calendar["day"] = (
        full_calendar["date"].dt.to_period("D").apply(lambda x: x.day)
    )
    full_calendar["month"] = (
        full_calendar["date"].dt.to_period("M").apply(lambda x: x.month)
    )

    # Header of the table with each weekday
    calendar_day_head = []
    # for day in ["", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]:
    for day in [
        "Monday",
        "Tuesday",
        "Wednesday",
        "Thursday",
        "Friday",
        "Saturday",
        "Sunday",
    ]:
        calendar_day_head.append(
            html.Th(
                className="p-2 border-r h-10 xl:w-40 lg:w-30 md:w-30 sm:w-20 w-10 xl:text-sm text-xs",
                children=[
                    html.Span(
                        className="xl:block lg:block md:block sm:block hidden",
                        children=day,
                    ),
                    html.Span(
                        className="xl:hidden lg:hidden md:hidden sm:hidden block",
                        children=day,
                    ),
                ],
            )
        )

    # Iterate over each week of the specific month with a week_data pd subset for the week number
    month_table_children = []
    for week_number, week_data in full_calendar.groupby("week_number"):
        week_rows = []

        # Iterate over each day in the week
        for day in week_data.day.unique():
            print(day)
            day_activities = week_data[
                (week_data.day == day) & (~week_data.id.isna())
            ].copy()
            activity_div = []
            if len(day_activities) > 0:
                print("Got activities")
                print(day_activities)
                for _, activity in day_activities.iterrows():
                    print(activity)
                    activity_div.append(
                        html.Div(
                            className="event bg-[#F39C12] text-white rounded p-1 text-sm mb-1",
                            children=[
                                html.Span(
                                    className="event-name",
                                    children=f"{activity.type.upper()}: ",
                                ),
                                html.Span(
                                    className="event-time",
                                    children=f"{ int(activity.distance_km)} km",
                                ),
                            ],
                        )
                    )

            week_rows.append(
                html.Td(
                    className="border p-1 h-28 xl:w-40 lg:w-30 md:w-30 sm:w-20 w-10 "
                    "overflow-auto transition cursor-pointer duration-500 ease hover:bg-gray-300",
                    children=[
                        html.Div(
                            className="flex flex-col h-28 mx-auto xl:w-40 lg:w-30 md:w-30 "
                            "sm:w-full w-10 mx-auto overflow-hidden",
                            children=[
                                html.Div(
                                    className="top h-5 w-full",
                                    children=[
                                        html.Span(
                                            className="text-gray-500", children=day
                                        )
                                    ],
                                ),
                                html.Div(
                                    className="bottom flex-grow h-24 py-1 w-full cursor-pointer",
                                    children=activity_div,
                                ),
                            ],
                        )
                    ],
                )
            )
        week_row = html.Tr(className="text-center h-20", children=week_rows)
        month_table_children.append(week_row)

    month_calendar = html.Div(
        className="wrapper bg-white rounded shadow w-full",
        children=html.Div(
            children=[
                html.Table(
                    className="w-full",
                    children=[
                        html.Thead(children=html.Tr(children=calendar_day_head)),
                        html.Tbody(children=month_table_children),
                    ],
                )
            ]
        ),
    )

    year_selector = html.Div(
        className="year-selector",
        children=[
            html.Button("<", id={"type": "calendar-btn", "index": "prev-month"}),
            html.Div(className="month-name", children=f" {selected_month} "),
            html.Button(">", id={"type": "calendar-btn", "index": "next-month"}),
        ],
    )

    calendar_container = [
        html.Div(children=year_selector),
        html.Button(
            f"""Back {selected_year}""",
            id={"type": "calendar-btn", "index": "back-yearly-calendar"},
        ),
        month_calendar,
    ]
    return calendar_container


def get_yearly_calendar():
    # Get the data for the selected year
    strava_manager = StravaManager()
    activities_df = strava_manager.get_activities_for_year(session["selected_year"])

    months = [
        "JAN",
        "FEB",
        "MAR",
        "APR",
        "MAY",
        "JUN",
        "JUL",
        "AUG",
        "SEP",
        "OCT",
        "NOV",
        "DEC",
    ]

    # Set up an empty list which will be a List of List where each List is a row of the calendar
    rows = []

    # Group the DataFrame by 'year' and 'month_of_year', then sum the 'distance_km' for each group
    monthly_totals = (
        activities_df[activities_df.year == session["selected_year"]]
        .groupby(["year", "month_of_year"])[["distance_km", "moving_time"]]
        .sum()
        .reset_index()
    )

    # Set up an empty dict which is going to be use if there are no activity for this year
    all_months = {}

    # if there are at least one activity for the year
    if len(monthly_totals) > 0:
        max_value = monthly_totals["distance_km"].max()
        # Create a dictionary with month abbreviations as keys and aggregated distances as values
        activities_dict = {
            pd.to_datetime(f"{year}-{month}-01")
            .strftime("%b")
            .upper(): {"distance": distance, "moving_time": moving_time}
            for year, month, distance, moving_time in zip(
                monthly_totals["year"],
                monthly_totals["month_of_year"],
                monthly_totals["distance_km"],
                monthly_totals["moving_time"],
            )
        }

        # Initialize the activities dictionary with 0 for all months (to ensure all months are present)
        all_months = {
            pd.to_datetime(f"{year}-{month}-01").strftime("%b").upper(): 0
            for year in activities_df["year"].unique()
            for month in activities_df["month_of_year"].unique()
        }

        # Update the dictionary with the aggregated distances
        all_months.update(activities_dict)

    for i in range(0, len(months), 4):
        row_children = []

        for j in range(
            i, min(i + 4, len(months))
        ):  # Adjusted the range to ensure it doesn't exceed the list length
            month_name = months[j]
            # In case of no run at this month
            if month_name in all_months.keys():
                distance_run = int(all_months[month_name]["distance"])
                time_run = seconds_to_h(all_months[month_name]["moving_time"])
                circle_size = normalize(
                    distance_run, max_value
                )  # Adjust this based on your data
                label_hours_run = f"{distance_run} km"
            else:
                label_hours_run = ""
                circle_size = 10
                time_run = "0 Hour"
            # Create a calendar square
            square = html.Button(
                className="yearly-calendar-square",
                id={
                    "type": "select-month-btn",
                    "index": month_name,
                },  # Use a unique ID for each button
                children=[
                    html.Div(className="month-name", children=month_name),
                    html.Div(className="month-hours", children=f"{time_run}"),
                    html.Div(
                        className="yearly-calendar-circle",
                        children=[
                            label_hours_run,
                        ],
                        style={
                            "width": f"{circle_size}px",
                            "height": f"{circle_size}px",
                        },
                    ),
                ],
            )
            row_children.append(square)

        row = html.Div(className="yearly-calendar-row", children=row_children)
        rows.append(row)

    # Create navigation buttons for changing the year
    year_selector = html.Div(
        className="year-selector",
        children=[
            html.Button("<", id={"type": "calendar-btn", "index": "prev-year"}),
            html.Div(className="month-name", children=f" {session['selected_year']} "),
            html.Button(">", id={"type": "calendar-btn", "index": "next-year"}),
        ],
    )

    calendar_container = html.Div(
        children=[
            html.Div(children=" "),
            year_selector,
        ]
        + rows,
    )

    print(calendar_container)
    return calendar_container
