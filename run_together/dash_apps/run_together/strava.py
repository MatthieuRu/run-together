import pandas as pd
def get_strava_activities_pandas(activities):
    my_cols = ['name',
              'start_date_local',
              'type',
              'distance',
              'moving_time',
              'elapsed_time',
              'total_elevation_gain',
              'elev_high',
              'elev_low',
              'average_speed',
              'max_speed',
              'average_heartrate',
              'max_heartrate',
              'start_latlng']

    data = []
    for activity in activities:
        my_dict = activity.to_dict()
        data.append([activity.id] + [my_dict.get(x) for x in my_cols])

    # Add id to the beginning of the columns, used when selecting a specific activity
    my_cols.insert(0, 'id')

    df = pd.DataFrame(data, columns=my_cols)
    # Make all walks into hikes for consistency
    df['type'] = df['type'].replace('Walk','Hike')
    # Create a distance in km column
    df['distance_km'] = df['distance']/1e3
    # Convert dates to datetime type
    df['start_date_local'] = pd.to_datetime(df['start_date_local'])
    # Create a day of the week and month of the year columns
    df['day_of_week'] = df['start_date_local'].dt.day_name()
    df['month_of_year'] = df['start_date_local'].dt.month
    # Convert times to timedeltas
    df['moving_time'] = pd.to_timedelta(df['moving_time'])
    df['elapsed_time'] = pd.to_timedelta(df['elapsed_time'])
    # Convert timings to hours for plotting
    df['elapsed_time_hr'] = df['elapsed_time'] / 3600e9
    df['moving_time_hr'] = df['moving_time'] / 3600e9
    return df
