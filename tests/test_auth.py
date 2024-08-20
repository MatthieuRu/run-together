import requests
from os import environ as env
from dotenv import load_dotenv
import logging
import time
load_dotenv()


auth_endpoint: str = "https://www.strava.com/oauth/token"
activites_endpoint: str = "https://www.strava.com/api/v3/athlete/activities"


# def test_get_acces_token():
#     # these params needs to be passed to get access
#     # token used for retrieveing actual data
#     payload: dict = {
#         'client_id': env['stravaClientId'],
#         'client_secret': env['stravaClientSecret'],
#         'refresh_token': env['refresh_token'],
#         'grant_type': "refresh_token",
#         'f': 'json'
#     }
#     res = requests.post(auth_endpoint, data=payload, verify=False)
#     print(res, flush=True)
#     print(10* '------------------------')
#     access_token = res.json()['access_token']
#     return access_token


from pymongo import MongoClient

def test_mongo():
    # Connect to MongoDB
    client = MongoClient("mongodb://localhost:27017/")

    # Create or connect to a database
    db = client["mydatabase"]

    # Create or connect to a collection
    collection = db["mycollection"]

    # Verify the insertion
    for document in collection.find():
        print(document, flush=True)

    collection.delete_one({'strava_id': 81493658})


# from datetime import timedelta, datetime
# from dash_apps.run_together.model.strava_manager import StravaManager
# from dash_apps.run_together.model.user import User


# def test_list_athlete_activities():
#     """
#     Method that fetches a list of the athletes 30 most recent activities
#     """
#     current_datetime = datetime.now()

#     current_year = current_datetime.year
#     print(year, month)

#     strava_client = StravaManager(session=False)
#     activities_last_thirty_days = strava_client.get_activities_for_month(
#         year=year, month=month)

#     print(activities_last_thirty_days)
#     return activities_last_thirty_days
