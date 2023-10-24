import pandas as pd
from dotenv import load_dotenv
from os import environ as env
import logging
from stravalib.client import Client
from stravalib.model import Athlete

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)

# Load .env file
load_dotenv()


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

        self.strava_client = Client()

    def set_token_response(
        self, access_token: str, refresh_token: str, expires_at: str
    ) -> None:
        # Now store that short-lived access token somewhere (a database?)
        logging.info(f"Set access_token to:{access_token}")
        self.strava_client.access_token = access_token

        # You must also store the refresh token to be used later on to obtain another valid access token
        # in case the current is already expired
        logging.info(f"Set refresh_token to:{refresh_token}")
        self.strava_client.refresh_token = refresh_token

        # An access_token is only valid for 6 hours, store expires_at somewhere and
        # check it before making an API call.
        logging.info(f"Set expires_at to:{expires_at}")
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


def get_strava_activities_pandas(activities):
    my_cols = [
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
    data = []
    for activity in activities:
        my_dict = activity.to_dict()
        data.append([activity.id] + [my_dict.get(x) for x in my_cols])

    # Add id to the beginning of the columns, used when selecting a specific activity
    my_cols.insert(0, "id")

    df = pd.DataFrame(data, columns=my_cols)
    # Make all walks into hikes for consistency
    df["type"] = df["type"].replace("Walk", "Hike")
    # Create a distance in km column
    df["distance_km"] = df["distance"] / 1e3
    # Convert dates to datetime type
    df["start_date_local"] = pd.to_datetime(df["start_date_local"])
    # Create a day of the week and month of the year columns
    df["day_of_week"] = df["start_date_local"].dt.day_name()
    df["month_of_year"] = df["start_date_local"].dt.month
    # Convert times to timedeltas
    df["moving_time"] = pd.to_timedelta(df["moving_time"])
    df["elapsed_time"] = pd.to_timedelta(df["elapsed_time"])
    # Convert timings to hours for plotting
    df["elapsed_time_hr"] = df["elapsed_time"] / 3600e9
    df["moving_time_hr"] = df["moving_time"] / 3600e9
    return df
