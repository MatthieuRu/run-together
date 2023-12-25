import pandas as pd
from dotenv import load_dotenv
from datetime import datetime, timedelta, date
from os import environ as env
import logging

from stravalib.client import Client
from stravalib.client import BatchedResultsIterator
from stravalib.model import Athlete
from stravalib.model import Activity

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)

# Load .env file
load_dotenv()


def get_strava_activity_column():
    return [
        "name",
        "start_date_local",
        "type",
        "distance",
        "moving_time",
        "elapsed_time",
        "total_elevation_gain",
        "elev_high",
        "elev_low",
        "average_speed",
        "max_speed",
        "average_heartrate",
        "max_heartrate",
        "average_cadence",
        "start_latlng",
    ]


class StravaManager:
    """
    Class to manage all the interaction with Strava
        - Exchange of token
        - Get Activity
        - Reformatting of Strava data
    """

    def __init__(self):
        """Init Strava CLient"""
        self.strava_client_id = int(env["stravaClientId"])
        self.strava_client_secret = env["stravaClientSecret"]
        self.strava_activity_column = get_strava_activity_column()
        self.strava_client = Client()

    def set_token_response(
        self, access_token: str, refresh_token: str, expires_at: str
    ) -> None:
        # Now store that short-lived access token somewhere (a database?)
        logging.info(f"Set access_token to: {access_token}")
        self.strava_client.access_token = access_token

        # You must also store the refresh token to be used later on to obtain another valid access token
        # in case the current is already expired
        logging.info(f"Set refresh_token to: {refresh_token}")
        self.strava_client.refresh_token = refresh_token

        # An access_token is only valid for 6 hours, store expires_at somewhere and
        # check it before making an API call.
        logging.info(f"Set expires_at to: {expires_at}")
        self.strava_client.token_expires_at = expires_at

    def generate_token_response(self, strava_code: str) -> None:
        """
        Fill the Strava Client with the information about the token.
        This token need to be refreshed only if not valid.
        """
        token_response = self.strava_client.exchange_code_for_token(
            client_id=self.strava_client_id,
            client_secret=self.strava_client_secret,
            code=strava_code,
        )

        self.set_token_response(
            access_token=token_response["access_token"],
            refresh_token=token_response["refresh_token"],
            expires_at=token_response["expires_at"],
        )

    def get_athlete(self) -> Athlete:
        """
            Get Athlete from  STRAVA API:
            https://developers.strava.com/docs/reference/#api-Athletes

        Returns
        -------
        class:`stravalib.model.Athlete`
            The athlete model object.
        """
        athlete = self.strava_client.get_athlete()
        logging.info(f"Get athlete:{athlete}")
        return athlete

    def get_activities_for_year(self, year: int):
        """

        :param year:
        :return:
        """
        # Set the start date to the beginning of the year
        start_date = datetime(year, 1, 1, 0, 0, 0)

        # Set the end date to the end of the year
        end_date = datetime(year, 12, 31, 23, 59, 59)

        # Convert datetime objects to ISO format strings
        start_date_str = start_date.strftime('%Y-%m-%dT%H:%M:%SZ')
        end_date_str = end_date.strftime('%Y-%m-%dT%H:%M:%SZ')

        # Call the get_activities function with the calculated parameters
        activities = self.strava_client.get_activities(
            after=start_date_str,
            before=end_date_str,
        )

        return activities

    def get_activities_for_month(self, year: int, month: int) -> BatchedResultsIterator:
        # Set the start date to the beginning of the specified month
        start_date = datetime(year, month, 1, 0, 0, 0)

        # Calculate the end of the month by adding one month and subtracting one second
        end_date = (
               datetime(year, month, 1, 0, 0, 0) + timedelta(days=32)
        ).replace(day=1, second=0, microsecond=0) - timedelta(seconds=1)

        # Convert datetime objects to ISO format strings
        start_date_str = start_date.strftime('%Y-%m-%dT%H:%M:%SZ')
        end_date_str = end_date.strftime('%Y-%m-%dT%H:%M:%SZ')
        print("end_date_str", start_date_str, "end_date_str", end_date_str)
        # Call the get_activities function with the calculated parameters
        activities = self.strava_client.get_activities(after=start_date_str, before=end_date_str, limit=None)

        return activities

    def get_activities_between(self, start_date: date, end_date: date) -> BatchedResultsIterator:
        # Call the get_activities function with the calculated parameters
        start_date_str = start_date.strftime('%Y-%m-%dT%H:%M:%SZ')
        end_date_str = end_date.strftime('%Y-%m-%dT%H:%M:%SZ')
        print("start_date_str", start_date_str, "end_date_str", end_date_str)

        activities = self.strava_client.get_activities(after=start_date_str, before=end_date_str, limit=None)

        return activities



def get_strava_activities_string(activities: BatchedResultsIterator):
    data = []
    try:
        logging.info(
            f"""Retrieve {len(list(activities))} activities from the BatchedResultsIterator"""
        )
    except:
        logging.info(
            f"""Retrieve 0 activities from the BatchedResultsIterator"""
        )
        return data

    for activity in activities:
        my_dict = activity.dict()
        data.append([activity.id] + [my_dict.get(x) for x in get_strava_activity_column()])

    return data


def seconds_to_hms(seconds):
    # Calculate hours, minutes, and seconds
    hours, remainder = divmod(seconds, 3600)
    minutes, seconds = divmod(remainder, 60)

    # Format as HH:MM:SS
    formatted_time = "{:02}h{:02}min{:02}".format(int(hours), int(minutes), int(seconds))
    return formatted_time


def seconds_to_h(seconds):
    # Calculate hours, minutes, and seconds
    hours, remainder = divmod(seconds, 3600)

    # Format as HH:MM:SS
    formatted_time = "{:02} Hours".format(int(hours))
    return formatted_time


def get_strava_activities_pandas(activities):
    my_cols = get_strava_activity_column()
    # Add id to the beginning of the columns, used when selecting a specific activity
    my_cols.insert(0, "id")

    df = pd.DataFrame(activities, columns=my_cols)
    # Make all walks into hikes for consistency
    df["type"] = df["type"].replace("Walk", "Hike")
    # Create a distance in km column
    df["distance_km"] = df["distance"] / 1e3
    # Convert dates to datetime type
    df["start_date_local"] = pd.to_datetime(df["start_date_local"])
    # Create a day of the week and month of the year columns
    df["day_of_week"] = df["start_date_local"].dt.day_name()
    df["month_of_year"] = df["start_date_local"].dt.month
    df["year"] = df["start_date_local"].dt.year

    # Apply the function to the duration_seconds column
    df['moving_time_format'] = df['moving_time'].apply(seconds_to_hms)

    return df
