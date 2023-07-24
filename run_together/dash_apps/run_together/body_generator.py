import dash_mantine_components as dmc
import pandas as pd
import dash_ag_grid as dag
from dash import html

container_style = {
    "width": "100%",  # Stretch container to 100% of the page width
    "height": "100%",  # Stretch container to 100% of the page width
    "border": f"1px solid {dmc.theme.DEFAULT_COLORS['green'][4]}",
}

style = {
    "border": f"1px solid {dmc.theme.DEFAULT_COLORS['red'][4]}",
}


def generate_left_column(activities_df: pd.DataFrame):
    # Your logic to generate the left column content goes here
    # This could be fetching data, generating a navigation menu, or displaying additional information

    records = activities_df.to_dict('records')

    left_columns = []  # List to store the left column components for each Run

    for run in records:
        print(run['id'])
        # First row with the title
        first_row = html.Div(
            children=[
                # html.H4(f"Menu Item {run.run_id}")
                html.H4(f"{run['name']}")
            ]
        )

        # Second row with three columns and icons
        second_row = html.Div(
            children=[
                html.Div(
                    children=[
                        html.I(className="fas fa-heart"),
                        f"{run['average_heartrate']} bpm"
                    ],
                    className="column"
                ),
                html.Div(
                    children=[
                        html.I(className="fas fa-tachometer-alt"),
                        f"{run['average_speed']} /km"

                    ],
                    className="column"
                ),
                html.Div(
                    children=[
                        html.I(className="fas fa-shoe-prints"),
                        f"{run['average_cadence']} ppm"

                    ],
                    className="column"
                )
            ],
            className="grid"
        )

        # Third row with the "KM" text
        third_row = html.Div(
            children=[
                f"{round(run['distance_km'], 2)} KM"
            ]
        )

        # Combine all rows into a left column grid layout
        left_column_content = html.Div(
            children=[first_row, second_row, third_row],
            className='left-column'
        )

        left_columns.append(left_column_content)  # Add the generated component to the list

    return left_columns


def generate_central_column(activities_df: pd.DataFrame):
    # Your logic to generate the central column content goes here
    # This could be fetching the main content from a database or processing user input

    # Build the table with all the activities
    records = activities_df.to_dict('records')
    column_defs = []
    for col in list(activities_df):
        column_defs.append({"field": col})

    central_column_content = dag.AgGrid(
        id="activity-table",
        rowData=records,
        columnDefs=column_defs,
        defaultColDef={
            "resizable": True,
            "sortable": True,
            "filter": True,
            "minWidth": 125,
            "editable": False,
        },
        columnSize="sizeToFit",
        dashGridOptions={"rowSelection": "single"},
    )

    return central_column_content


def get_body(activities_df: pd.DataFrame):




    grid = dmc.Container(
        dmc.Grid(
            children=[
                dmc.Col(generate_left_column(activities_df=activities_df), span="auto", style=style),
                dmc.Col(generate_central_column(activities_df=activities_df), span=6, style=style),
                # dmc.Col(html.Div("span=auto"), span="auto", style=style),
            ],
            gutter="xl",
            grow=True,
            style=style
        ),
        size="xl", px="xl",  style=container_style
    )

    return grid
