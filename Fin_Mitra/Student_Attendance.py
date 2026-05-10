
import dash
from dash import html, dcc, Input, Output, State, ALL
import dash_bootstrap_components as dbc
import pandas as pd
import os
from datetime import datetime, timedelta

STATUS = ["present", "absent", "holiday"]

# -------------------------
# HELPERS
# -------------------------

def get_class_options(username):
    path = f"/var/Data/{username}/fee_structure_static.csv"

    if not os.path.exists(path):
        return []

    df = pd.read_csv(path)

    return [
        {"label": row["standard"], "value": row["studying_class"]}
        for _, row in df.iterrows()
    ]


def get_students(SessionData, class_val):
    path = f"/var/Data/{SessionData['username']}/student_log.csv"

    if not os.path.exists(path):
        return []

    df = pd.read_csv(path)
    df["studying_class"] = df["studying_class"].astype(str)

    df = df[df["studying_class"] == str(class_val)]

    return df[["student_name", "admission_no"]].to_dict("records")


# -------------------------
# LAYOUT
# -------------------------

def student_attendance_layout(SessionData):

    return dbc.Container(
        [
            dbc.Row(
                [
                    dbc.Col(html.H5("Student Attendance Board"), md=3),

                    dbc.Col(
                        dcc.Dropdown(
                            id="student-att-class",
                            options=get_class_options(SessionData["username"]),
                            placeholder="Select Class",
                        ),
                        md=3,
                    ),

                    dbc.Col(
                        dbc.Button(
                            "Load Attendance Board",
                            id="load-student-attendance",
                            color="primary",
                        ),
                        md="auto",
                    ),

                    dbc.Col(
                        dbc.Button(
                            "💾 Save Attendance",
                            id="save-student-attendance",
                            color="success",
                        ),
                        md="auto",
                    ),
                ],
                className="mb-3 align-items-center",
            ),

            html.Div(id="student-attendance-save-status"),

            dcc.Store(id="student-attendance-store", data={}),
            dcc.Input(
                id="student-search",
                placeholder="Search student...",
                type="text",
                debounce=True,
                style={"width": "300px", "marginBottom": "10px"}
            ),
            html.Div(id="student-attendance-board"),
        ],
        fluid=True,
    )


# -------------------------
# GRID BUILDER
# -------------------------

def build_student_board(data, students):

    data = data or {}

    today = datetime.today().date()
    dates = [today + timedelta(days=i) for i in range(-15, 16)]

    header = [
        html.Div("Student", className="att-cell att-header"),
        html.Div("Adm No", className="att-cell att-header"),  
    ]

    for d in dates:
        header.append(html.Div(d.strftime("%d-%b"), className="att-cell att-header"))

    rows = [html.Div(header, className="att-row")]

    for student in students:

        name = str(student["student_name"])
        adm = str(student["admission_no"])

        row = [
            html.Div(name, className="att-cell att-teacher"),
            html.Div(adm, className="att-cell att-adm"),  # ✅ NEW
        ]

        for d in dates:

            date_str = d.strftime("%Y-%m-%d")
            key = f"{name}**{adm}**{date_str}"

            status = data.get(key, "NA")

            if not isinstance(status, str) or status.strip() == "":
                status = "NA"

            display = "NA" if status == "NA" else status[0].upper()

            row.append(
                html.Div(
                    display,
                    id={
                        "type": "student-att-cell",
                        "name": name,
                        "adm": adm,
                        "date": date_str,
                    },
                    n_clicks=0,
                    className=f"att-cell att-{status}",
                )
            )

        rows.append(html.Div(row, className="att-row"))

    return html.Div(
        html.Div(rows, className="att-grid"),
        style={"overflowX": "auto"}
    )


# -------------------------
# CALLBACKS
# -------------------------

def register_callbacks(app):

    # 🔹 LOAD BOARD
    @app.callback(
        Output("student-attendance-board", "children"),
        Input("student-att-class", "value"),
        Input("student-attendance-store", "data"),
        Input("student-search", "value"),
        State("session", "data"),
    )
    def render_student_board(class_val, data, search, SessionData):

        if class_val is None:
            return dbc.Alert("Select class first", color="warning")

        username = SessionData["username"]
        file_path = f"/var/Data/{username}/student_attendance.csv"

        saved_data = {}

        if os.path.exists(file_path):
            df = pd.read_csv(file_path)

            # ✅ CRITICAL FIX
            df["student"] = df["student"].astype(str)
            df["admission_no"] = df["admission_no"].astype(str)
            df["class"] = df["class"].astype(str)

            df = df[df["class"] == str(class_val)]

            for _, row in df.iterrows():
                key = f"{row['student']}**{row['admission_no']}**{row['date']}"
                saved_data[key] = row["status"]

        data = {**saved_data, **(data or {})}

        students = get_students(SessionData, class_val)

        if search:
            search = search.lower()
            students = [
                s for s in students
                if search in str(s["student_name"]).lower()
                or search in str(s["admission_no"])
            ]

        if not students:
            return dbc.Alert("No students found", color="warning")

        return build_student_board(data, students)


    # 🔹 CLICK STATUS CHANGE
    @app.callback(
        Output("student-attendance-store", "data"),
        Input({"type": "student-att-cell", "name": ALL, "adm": ALL, "date": ALL}, "n_clicks"),
        State("student-attendance-store", "data"),
        prevent_initial_call=True,
    )
    def change_status(_, data):

        data = data or {}

        ctx = dash.ctx
        trigger = ctx.triggered_id

        if not trigger:
            raise dash.exceptions.PreventUpdate

        name = trigger["name"]
        adm = trigger["adm"]
        date = trigger["date"]

        key = f"{name}**{adm}**{date}"

        current = data.get(key, "present")

        i = STATUS.index(current)
        new_status = STATUS[(i + 1) % len(STATUS)]

        data[key] = new_status

        return data


    # 🔹 SAVE ATTENDANCE
    @app.callback(
        Output("student-attendance-save-status", "children"),
        Input("save-student-attendance", "n_clicks"),
        State("student-attendance-store", "data"),
        State("student-att-class", "value"),
        State("session", "data"),
        prevent_initial_call=True,
    )
    def save_student_attendance(n, data, class_val, SessionData):

        if not data:
            return dbc.Alert("Nothing to save", color="warning")

        username = SessionData["username"]
        file_path = f"/var/Data/{username}/student_attendance.csv"

        rows = []

        for key, status in data.items():

            parts = key.split("**")

            if len(parts) != 3:
                continue
            
            name, adm, date = parts

            if len(parts) < 3:
                continue

            name = parts[0]
            adm = parts[1]
            date = parts[2]

            rows.append({
                "student": name,
                "admission_no": adm,
                "class": class_val,
                "date": date,
                "status": status
            })

        new_df = pd.DataFrame(rows)

        if os.path.exists(file_path):

            existing_df = pd.read_csv(file_path)

            merged_df = pd.concat([existing_df, new_df], ignore_index=True)

            merged_df = merged_df.drop_duplicates(
                subset=["student", "admission_no", "date"],
                keep="last"
            )

        else:
            merged_df = new_df

        merged_df = merged_df.sort_values(["class", "student", "date"])

        merged_df.to_csv(file_path, index=False)

        return dbc.Alert(
            f"✅ Attendance saved ({len(new_df)} records)",
            color="success",
            dismissable=True,
            duration=3000,
        )
