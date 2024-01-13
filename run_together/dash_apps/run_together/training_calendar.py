from dash import html
import pandas as pd
import calendar
from datetime import datetime, date
from typing import List

from run_together.dash_apps.run_together.strava_manager import StravaManager


def get_month_list() -> List[str]:
    return [
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


def normalize(value: int, max_value: int) -> float:
    """Return a normalize value between from min range and max range for the value"""
    min_value = 0  # Minimum value in the original range
    min_range = 40  # Minimum value in the desired range
    max_range = 140  # Maximum value in the desired range
    return (value - min_value) / (max_value - min_value) * (
        max_range - min_range
    ) + min_range


def get_monday_of_week(year, week_number) -> date:
    # Create a date object for January 1 of the given year
    return date.fromisocalendar(year=year, week=week_number, day=1)


def get_sunday_of_week(year, week_number) -> date:
    # Get the Monday of the week
    return date.fromisocalendar(year=year, week=week_number, day=7)


def get_monthly_calendar(year: int, month: str) -> html.Div:
    """
    Return the monthly calendar for the specified year and month.

    Args:
        year (int): The selected year by the user.
        month (str): The selected month by the user.

    Returns:
        html.Div: The children of the "calendar-training-container" in the body.
    """
    # Get the number of days in the selectede month
    month_number = datetime.strptime(month, "%b").month
    weekday, num_days = calendar.monthrange(year, month_number)

    # Create a DataFrame with all days of the month (get the following num_days from the 1st of the month)
    all_days_selected_month = pd.date_range(
        start=f"{year}-{month_number}-01", periods=num_days, freq="D"
    )

    # Get the Monday of the first week
    first_monday_before_first_day = date.fromisocalendar(
        year=all_days_selected_month[0].isocalendar()[0],
        week=all_days_selected_month[0].isocalendar()[1],
        day=1,
    )

    # Get the Sunday of the last week
    first_sunday_after_last_day = date.fromisocalendar(
        year=all_days_selected_month[-1].isocalendar()[0],
        week=all_days_selected_month[-1].isocalendar()[1],
        day=7,
    )

    # Get all day between both day & add it to a DataFrame
    all_days_selected_month = pd.date_range(
        start=first_monday_before_first_day, end=first_sunday_after_last_day, freq="d"
    )
    month_df = pd.DataFrame({"date": all_days_selected_month})

    # Get the activities from STRAVA between these both days
    strava_manager = StravaManager()
    activities_df = strava_manager.get_activities_between(
        start_date=first_monday_before_first_day, end_date=first_sunday_after_last_day
    )

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

    # Calculate week_number & day associate to each date
    full_calendar["week_number"] = (
        full_calendar["date"].dt.to_period("W").apply(lambda x: x.week)
    )
    full_calendar["day"] = (
        full_calendar["date"].dt.to_period("D").apply(lambda x: x.day)
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
                        children=day[0:3].upper(),
                    ),
                ],
            )
        )

    # Body of the table
    # Iterate over each week of the specific month with a week_data pd subset for the week number
    month_table_children = []

    for week_number, week_data in full_calendar.groupby("week_number"):
        week_rows = []

        # Iterate over each day in the week
        for day in week_data.day.unique():
            # Extract activities for the current day
            day_activities = week_data[
                (week_data.day == day) & (~week_data.id.isna())
            ].copy()
            activity_div = []

            if len(day_activities) > 0:
                # Append the Activity List
                for index, activity in day_activities.iterrows():
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
                                    children=f"{int(activity.distance_km)} km",
                                ),
                            ],
                        )
                    )

            # Create a table cell for the day and add it to the week's row list
            week_rows.append(
                html.Td(
                    className="border p-1 h-28 xl:w-40 lg:w-30 md:w-30 sm:w-20 w-10 "
                    "overflow-auto transition cursor-pointer duration-500 ease hover:bg-gray-300",
                    children=[
                        html.Div(
                            className="flex flex-col h-28 mx-auto xl:w-40 lg:w-30 md:w-30 "
                            "sm:w-full w-10 mx-auto overflow-hidden",
                            children=[
                                # Top part with day name
                                html.Div(
                                    className="top h-5 w-full",
                                    children=[
                                        html.Span(
                                            className="text-gray-500", children=day
                                        )
                                    ],
                                ),
                                # Bottom part with activity details
                                html.Div(
                                    className="bottom flex-grow h-24 py-1 w-full cursor-pointer",
                                    children=activity_div,
                                ),
                            ],
                        )
                    ],
                )
            )

        # Create a table row for the week
        week_row = html.Tr(className="text-center h-20", children=week_rows)

        # Add the list of cells into the html element (tr: represents a table row)
        month_table_children.append(week_row)

    # Create the overall HTML structure for the month's calendar
    month_calendar = html.Div(
        className="wrapper bg-white rounded shadow w-full",
        children=html.Div(
            children=[
                html.Table(
                    className="w-full",
                    children=[
                        # Table header with day names
                        html.Thead(children=html.Tr(children=calendar_day_head)),
                        # Table body with week rows and day cells
                        html.Tbody(children=month_table_children),
                    ],
                )
            ]
        ),
    )

    year_selector = html.Div(
        className="calendar-selector",
        children=[
            html.Button("<", id={"type": "calendar-btn", "index": "prev-month"}),
            html.Div(className="current-selection", children=f" {month} "),
            html.Button(">", id={"type": "calendar-btn", "index": "next-month"}),
        ],
    )

    calendar_container = [
        html.Div(children=year_selector),
        html.Button(
            f"""Back {year}""",
            id={"type": "calendar-btn", "index": "back-yearly-calendar"},
        ),
        month_calendar,
    ]
    return calendar_container


def get_yearly_calendar(year: int) -> html.Div:
    """
    Generate the yearly calendar for the specified selected year.

    :param year: int - Currently selected year by the user
    :return: HTML Div - Children of "calendar-training-container" in the body
    """
    # Get the data for the selected year
    strava_manager = StravaManager()
    activities_df = strava_manager.get_activities_for_year(year)

    # Group the DataFrame by 'year' and 'month_of_year', then sum the 'distance_km' for each group
    monthly_totals = (
        activities_df[activities_df.year == year]
        .groupby(["year", "month_of_year"])[["distance_km", "moving_time"]]
        .sum()
        .reset_index()
    )

    print(monthly_totals)
    # Set up an empty dict which is going to be use if there are no activity for this year
    activities_dict = {}
    max_value = 0

    # if there are at least one activity for the year
    if len(monthly_totals) > 0:
        max_value = int(monthly_totals["distance_km"].max())
        # Create a dictionary with month abbreviations as keys and aggregated distances as values
        activities_dict = {
            pd.to_datetime(f"{year}-{month}-01")
            .strftime("%b")
            .upper(): {
                "distance": int(distance),
                "moving_time": int(divmod(moving_time, 3600)[0]),
            }
            for year, month, distance, moving_time in zip(
                monthly_totals["year"],
                monthly_totals["month_of_year"],
                monthly_totals["distance_km"],
                monthly_totals["moving_time"],
            )
        }

    months = get_month_list()

    # Set up an empty list which will be a List of List where each List is a row of the calendar
    rows = []

    # Iterate over months in groups of 4 for calendar rows
    for i in range(0, len(months), 4):
        row_children = []

        # Iterate over each month in the current row
        for j in range(i, min(i + 4, len(months))):
            month_name = months[j]

            # Check if there are activities for the current month
            if month_name in activities_dict.keys():
                # Set up variables for distance and time run
                distance_run = activities_dict[month_name]["distance"]
                time_run = activities_dict[month_name]["moving_time"]

                # Normalize circle size based on distance run
                circle_size = normalize(value=distance_run, max_value=max_value)
                label_hours_run = f"{distance_run} km"
            else:
                # Set defaults for months with no runs
                label_hours_run = ""
                circle_size = 10
                time_run = 0

            # Create a calendar square with a button
            square = html.Button(
                className="yearly-calendar-square",
                id={
                    "type": "select-month-btn",
                    "index": month_name,
                },  # Unique ID for each button
                children=[
                    html.Div(className="month-name", children=month_name),
                    html.Div(className="month-hours", children=f"{time_run} Hours"),
                    html.Div(
                        className="yearly-calendar-circle",
                        children=label_hours_run,
                        style={
                            "width": f"{circle_size}px",
                            "height": f"{circle_size}px",
                        },
                    ),
                ],
            )
            row_children.append(square)

        # Create a row div for the calendar
        row = html.Div(className="yearly-calendar-row", children=row_children)
        rows.append(row)

    # Create navigation buttons for changing the year
    year_selector = html.Div(
        className="calendar-selector",
        children=[
            html.Button("<", id={"type": "calendar-btn", "index": "prev-year"}),
            html.Div(className="current-selection", children=f" {year} "),
            html.Button(">", id={"type": "calendar-btn", "index": "next-year"}),
        ],
    )

    # Create the overall calendar container with navigation buttons and rows
    calendar_container = html.Div(
        children=[
            html.Div(children=" "),
            year_selector,
        ]
        + rows,
    )

    return calendar_container
