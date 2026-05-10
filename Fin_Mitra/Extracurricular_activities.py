import dash_table
import pandas as pd
import os
from dash import html, dcc, Input,State, Output
import dash_bootstrap_components as dbc

from dash import callback_context


def get_sports_layout(SessionData):

    file_path = f"/var/Data/{SessionData['username']}/student_log.csv"

    if not os.path.exists(file_path):
        return html.Div("No data file found")

    df = pd.read_csv(file_path)

    # ✅ Only students having activities
    df = df[df["extracurricular_activities"].notna()]

    # Clean columns
    sports_df = df[
        [
            "admission_no",
            "student_name",
            "studying_class",
            "extracurricular_activities",
        ]
    ].copy()

    sports_df.columns = ["Roll No", "Student Name", "Class", "Activities"]

    # ✅ Clean activities (capitalize + remove spaces)
    sports_df["Activities"] = sports_df["Activities"].apply(
        lambda x: ", ".join([i.strip().title() for i in str(x).split(",")])
    )

    # ✅ Dropdown options dynamically
    all_activities = set()
    for acts in sports_df["Activities"]:
        for a in acts.split(","):
            all_activities.add(a.strip())

    dropdown_options = [{"label": a, "value": a} for a in sorted(all_activities)]

    return dbc.Container(
        [
            html.H4("🏆 Sports & Extracurricular Activities", className="mb-3"),

            # 🔍 Filters Row
            dbc.Row(
                [
                    dbc.Col(
                        dcc.Input(
                            id="sports-search",
                            placeholder="Search Roll No / Name / Class",
                            type="text",
                            style={"width": "100%"},
                        ),
                        md=6,
                    ),
                    dbc.Col(
                        dcc.Dropdown(
                            id="sports-activity-filter",
                            options=dropdown_options,
                            multi=True,
                            placeholder="Filter by Activities",
                        ),
                        md=6,
                    ),
                ],
                className="mb-3",
            ),
            dcc.Store(id="sports-full-data", data=sports_df.to_dict("records")),
            dash_table.DataTable(
                id="sports-table",
                data=sports_df.to_dict("records"),
                columns=[{"name": i, "id": i} for i in sports_df.columns],

                page_size=10,
                filter_action="none",
                sort_action="native",

                style_table={"overflowX": "auto"},
                style_cell={
                    "textAlign": "center",
                    "padding": "8px",
                },
                style_header={
                    "backgroundColor": "#198754",
                    "color": "white",
                    "fontWeight": "bold",
                },
            ),
        ],
        fluid=True,
    )


def register_sports_callbacks(app):

    @app.callback(
    Output("sports-table", "data"),
    Input("sports-search", "value"),
    Input("sports-activity-filter", "value"),
    State("sports-full-data", "data"),  # ✅ change here
)
    def filter_sports(search_value, selected_activities, full_data):
    
        df = pd.DataFrame(full_data)
    
        if df.empty:
            return df.to_dict("records")
    
        # 🔍 Search filter
        if search_value:
            search_value = str(search_value).lower()
    
            df = df[
                df["Roll No"].astype(str).str.lower().str.contains(search_value)
                | df["Student Name"].str.lower().str.contains(search_value)
                | df["Class"].astype(str).str.lower().str.contains(search_value)
            ]
    
        # 🎯 Activity filter
        if selected_activities:
            df = df[
                df["Activities"].apply(
                    lambda x: any(act in x for act in selected_activities)
                )
            ]
    
        return df.to_dict("records")