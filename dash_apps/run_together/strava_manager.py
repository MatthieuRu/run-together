import pandas as pd
from dotenv import load_dotenv
from datetime import datetime, timedelta, date
from os import environ as env
import logging
from typing import List
from flask import session


import requests
from stravalib.client import Client
from stravalib.client import BatchedResultsIterator
from stravalib.model import Athlete, Activity

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

    def __init__(self, session=True):
        """Init Strava CLient"""
        self.strava_client_id = int(env["stravaClientId"])
        self.strava_client_secret = env["stravaClientSecret"]
        self.strava_activity_column = get_strava_activity_column()
        self.strava_client = Client()
        if session:
            self.set_token_from_session()

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

    def set_token_from_env(self):
        """
        Fill the Strava Client with the information about the token.
        Information save in the .env file at the root of the file see .env.example
        This token need to be refreshed only if not valid.
        """
        session["access_token"] = env["access_token"]
        session["refresh_token"] = env["refresh_token"]
        session["expires_at"] = env["expires_at"]

        self.set_token_response(
            access_token=session["access_token"],
            refresh_token=session["refresh_token"],
            expires_at=session["expires_at"],
        )

    def set_token_from_session(self):
        """
        Fill the Strava Client with the information about the token.
        Information save in Flask Session
        This token need to be refreshed only if not valid.
        """
        self.set_token_response(
            access_token=session["access_token"],
            refresh_token=session["refresh_token"],
            expires_at=session["expires_at"],
        )

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

        session["access_token"] = token_response["access_token"]
        session["refresh_token"] = token_response["refresh_token"]
        session["expires_at"] = token_response["expires_at"]

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

    def get_activity(self, activity_id: int) -> Activity:
        """
            Get Activity from  STRAVA API:
            https://developers.strava.com/docs/reference/#api-activity

        Returns
        -------
        class:`stravalib.model.Activity`
            The Activity model object.
        """

        url = f"https://www.strava.com/api/v3/activities/{activity_id}?include_all_efforts="

        headers = {
            "Authorization": f"Bearer {self.strava_client.access_token}"
        }

        response = requests.get(url, headers=headers)

        if response.status_code == 200:
            activity = response.json()

        else:
            raise Exception(f"Error: {response.status_code} - {response.text}")

        return activity

    def get_activity_stream(self, activity_id: int) -> dict:
        """
            Get Activity Stream from STRAVA API:
            https://developers.strava.com/docs/reference/#api-Streams-getActivityStreams

        Returns
        -------
        Dict stream From Strava V3
        """

        url = f"https://www.strava.com/api/v3/activities/{activity_id}/streams?keys=time,heartrate,latlng&key_by_type=true"

        headers = {
            "Authorization": f"Bearer {self.strava_client.access_token}"
        }

        response = requests.get(url, headers=headers)

        if response.status_code == 200:
            activity_stream = response.json()
            return activity_stream

        else:
            logging.info(f"Error: {response.status_code} - {response.text}")
            raise Exception(f"Error: {response.status_code} - {response.text}")



    def get_activities_for_year(self, year: int) -> pd.DataFrame:
        """
        :param year:
        :return: pandas with all the activities from one year
        """
        # Set the start date to the beginning of the year
        start_date = datetime(year, 1, 1, 0, 0, 0)

        # Set the end date to the end of the year
        end_date = datetime(year, 12, 31, 23, 59, 59)

        # Convert datetime objects to ISO format strings
        start_date_str = start_date.strftime("%Y-%m-%dT%H:%M:%SZ")
        end_date_str = end_date.strftime("%Y-%m-%dT%H:%M:%SZ")

        # Call the get_activities function with the calculated parameters
        activities = self.strava_client.get_activities(
            after=start_date_str,
            before=end_date_str,
        )

        # Format to have a DataFrame
        activities_dict = get_strava_activities_string(activities)
        activities_df = get_strava_activities_pandas(activities_dict)

        return activities_df

    def get_activities_for_month(self, year: int, month: int) -> BatchedResultsIterator:
        # Set the start date to the beginning of the specified month
        start_date = datetime(year, month, 1, 0, 0, 0)

        # Calculate the end of the month by adding one month and subtracting one second
        end_date = (datetime(year, month, 1, 0, 0, 0) + timedelta(days=32)).replace(
            day=1, second=0, microsecond=0
        ) - timedelta(seconds=1)

        # Convert datetime objects to ISO format strings
        start_date_str = start_date.strftime("%Y-%m-%dT%H:%M:%SZ")
        end_date_str = end_date.strftime("%Y-%m-%dT%H:%M:%SZ")

        # Call the get_activities function with the calculated parameters
        activities = self.strava_client.get_activities(
            after=start_date_str, before=end_date_str, limit=None
        )

        return activities

    def get_activities_between(
        self, start_date: date, end_date: date
    ) -> pd.DataFrame:
        # Call the get_activities function with the calculated parameters
        start_date_str = start_date.strftime("%Y-%m-%dT%H:%M:%SZ")
        end_date_str = end_date.strftime("%Y-%m-%dT%H:%M:%SZ")

        activities = self.strava_client.get_activities(
            after=start_date_str, before=end_date_str, limit=None
        )

        # Format to have a DataFrame
        activities_dict = get_strava_activities_string(activities)
        activities_df = get_strava_activities_pandas(activities_dict)

        return activities_df


def get_strava_activities_string(activities: BatchedResultsIterator) -> List:
    """
        Return from a Batch from Strava API into a list of activity dictionary
    :param BatchedResultsIterator activities: Batch
    :return: data
    """
    data = []
    try:
        logging.info(
            f"""Retrieve {len(list(activities))} activities from the BatchedResultsIterator"""
        )
    except:
        logging.info("Retrieve 0 activities from the BatchedResultsIterator")
        return data

    for activity in activities:
        my_dict = activity.dict()
        data.append(
            [activity.id] + [my_dict.get(x) for x in get_strava_activity_column()]
        )

    return data


def seconds_to_hms(seconds: int) -> str:
    """
        Convert a time in second into HH:MM:SS format
    :param seconds: number of second
    :return: formatted_time: string of time
    """
    # Calculate hours, minutes, and seconds
    hours, remainder = divmod(seconds, 3600)
    minutes, seconds = divmod(remainder, 60)

    # Format as HH:MM:SS
    formatted_time = "{:02}h{:02}min{:02}".format(
        int(hours), int(minutes), int(seconds)
    )
    return formatted_time


def seconds_to_h(seconds: int) -> str:
    """
        Convert a time in second into HH Hours format (keep only the hour element)
    :param seconds: number of second
    :return: formatted_time: string of time
    """
    # Calculate hours, minutes, and seconds
    hours, remainder = divmod(seconds, 3600)

    return int(hours)


def get_strava_activities_pandas(activities: List) -> pd.DataFrame:
    """
        Convert the list of activities to a pandas dataframe
    :param activities:
    :return:
    """
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
    df["moving_time_format"] = df["moving_time"].apply(seconds_to_hms)

    # Keep only runs
    return df[df.type == "Run"]
