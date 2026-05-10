import dash
from dash import html, dcc, Input, Output, State
import dash_bootstrap_components as dbc
import pandas as pd
import os
import io
from datetime import datetime, timedelta
import base64
from dash import ALL


STATUS = ["present", "absent", "leave", "holiday"]

def get_layout():
    return dbc.Container(
        [
            html.Div(
                [
                    # 🔹 Page Title
                    html.Div(
                        [
                            html.H2(
                                "🎓 Teacher Management",
                                style={
                                    "fontWeight": "600",
                                    "color": "#2e3a59",
                                    "marginBottom": "5px",
                                },
                            ),
                            html.P(
                                "Manage teacher records, search profiles, and upload logs",
                                style={"color": "#6c757d", "fontSize": "14px"},
                            ),
                        ],
                        className="mb-4",
                    ),
                    # 🔹 Tabs Section
                    dbc.Card(
                        [
                            dbc.CardBody(
                                [
                                    dbc.Tabs(
                                        [
                                            dbc.Tab(
                                                label="➕ Create Teacher",
                                                tab_id="create-teacher",
                                                tab_class_name="custom-tab",
                                                active_tab_class_name="custom-tab-active",
                                            ),
                                            dbc.Tab(
                                                label="🔍 Search Teacher",
                                                tab_id="search-teacher",
                                                tab_class_name="custom-tab",
                                                active_tab_class_name="custom-tab-active",
                                            ),
                                            dbc.Tab(
                                                label="⬆ Upload Teacher Log",
                                                tab_id="upload-teacher",
                                                tab_class_name="custom-tab",
                                                active_tab_class_name="custom-tab-active",
                                            ),
                                            dbc.Tab(
                                                label="📅 Teacher Attendance",
                                                tab_id="teacher-attendance",
                                                tab_class_name="custom-tab",
                                                active_tab_class_name="custom-tab-active",
                                            ),
                                        ],
                                        id="teacher-tabs",
                                        active_tab="create-teacher",
                                        class_name="custom-tabs",  # 👈 SAME AS STUDENT
                                    ),
                                    html.Div(
                                        create_teacher_form(),
                                        id="teacher-tab-content",
                                        className="mt-4",
                                    ),
                                ]
                            )
                        ],
                        id="teacher-card-wrapper",
                        style={
                            "borderRadius": "12px",
                            "boxShadow": "0px 6px 18px rgba(0,0,0,0.08)",
                            "border": "none",
                        },
                    ),
                ],
                style={
                    "backgroundColor": "#ffffff",
                    "padding": "30px",
                    "borderRadius": "15px",
                },
            )
        ],
        fluid=True,
        style={
            "marginTop": "25px",
            "marginBottom": "40px",
        },
    )

def teacher_attendance_layout(SessionData):

    teachers = get_teacher_names(SessionData)

    return dbc.Container(
        [
            dbc.Row(
                [
                    dbc.Col(html.H5("Teacher Attendance Board"), md=4),

                    dbc.Col(
                        dbc.Button(
                            "Load Attendance Board",
                            id="load-attendance-board",
                            color="primary",
                        ),
                        md="auto",
                    ),

                    dbc.Col(
                        dbc.Button(
                            "💾 Save Attendance",
                            id="save-attendance-btn",
                            color="success",
                        ),
                        md="auto",
                    ),
                ],
                className="mb-3 align-items-center",
            ),

            html.Div(id="attendance-save-status"),

            dcc.Store(id="attendance-store", data={}),

            html.Div(id="attendance-board"),
        ],
        fluid=True,
    )

def build_attendance_board(data, teachers):

    data = data or {}

    today = datetime.today().date()

    dates = [
        today + timedelta(days=i)
        for i in range(-15, 16)
    ]

    header = [html.Div("Teacher", className="att-cell att-header")]

    for d in dates:
        header.append(
            html.Div(d.strftime("%d-%b"), className="att-cell att-header")
        )

    rows = [html.Div(header, className="att-row")]

    for teacher in teachers:

        row = [html.Div(teacher, className="att-cell att-teacher")]

        for d in dates:

            date_str = d.strftime("%Y-%m-%d")
            key = f"{teacher}_{date_str}"

            status = data.get(key, "NA")

            # normalize status
            if not isinstance(status, str) or status.strip() == "" or status.lower() == "nan":
                status = "NA"

            display = "NA" if status == "NA" else status[0].upper()

            row.append(
                html.Div(
                    display,
                    id={
                        "type": "att-cell",
                        "teacher": teacher,
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

def create_teacher_form():
    return dbc.Form(
        [
            dbc.Row(
                [
                    dbc.Col([dbc.Label("Full Name"), dbc.Input(id="t-name")], md=6),
                    dbc.Col(
                        [dbc.Label("DOB"), dbc.Input(type="date", id="t-dob")], md=6
                    ),
                ],
                className="mb-2",
            ),
            dbc.Row(
                [
                    dbc.Col(
                        [
                            dbc.Label("Gender"),
                            dcc.Dropdown(
                                options=["Male", "Female", "Other"], id="t-gender"
                            ),
                        ],
                        md=6,
                    ),
                    dbc.Col(
                        [
                            dbc.Label("Marital Status"),
                            dcc.Dropdown(options=["Single", "Married"], id="t-marital"),
                        ],
                        md=6,
                    ),
                ],
                className="mb-2",
            ),
            dbc.Row(
                [
                    dbc.Col(
                        [dbc.Label("Nationality"), dbc.Input(id="t-nationality")], md=6
                    ),
                    dbc.Col(
                        [dbc.Label("Aadhaar / ID"), dbc.Input(id="t-aadhaar")], md=6
                    ),
                ],
                className="mb-2",
            ),
            html.Hr(),
            dbc.Row(
                [
                    dbc.Col([dbc.Label("Mobile"), dbc.Input(id="t-mobile")], md=6),
                    dbc.Col(
                        [dbc.Label("Alternate Mobile"), dbc.Input(id="t-alt-mobile")],
                        md=6,
                    ),
                ],
                className="mb-2",
            ),
            dbc.Label("Email"),
            dbc.Input(id="t-email", className="mb-3"),
            html.Hr(),
            dbc.Label("Permanent Address"),
            dbc.Textarea(id="t-perm-address", rows=2, className="mb-2"),
            dbc.Label("Current Address"),
            dbc.Textarea(id="t-curr-address", rows=2, className="mb-2"),
            dbc.Row(
                [
                    dbc.Col([dbc.Label("City"), dbc.Input(id="t-city")], md=4),
                    dbc.Col([dbc.Label("State"), dbc.Input(id="t-state")], md=4),
                    dbc.Col([dbc.Label("Pin"), dbc.Input(id="t-pin")], md=4),
                ],
                className="mb-3",
            ),
            html.Hr(),
            dbc.Label("Educational Qualifications"),
            dbc.Textarea(id="t-qualification", rows=2, className="mb-2"),
            dbc.Label("Training Qualification (B.Ed / D.El.Ed / M.Ed)"),
            dbc.Input(id="t-training", className="mb-2"),
            dbc.Row(
                [
                    dbc.Col(
                        [
                            dbc.Label("Teaching Experience (Years)"),
                            dbc.Input(id="t-exp"),
                        ],
                        md=6,
                    ),
                    dbc.Col(
                        [
                            dbc.Label("Subjects Able to Teach"),
                            dbc.Input(id="t-subjects"),
                        ],
                        md=6,
                    ),
                ],
                className="mb-2",
            ),
            html.Hr(),

            dbc.Row(
                [
                    dbc.Col(
                        [dbc.Label("PAN Number"), dbc.Input(id="t-pan")],
                        md=6,
                    ),
                    dbc.Col(
                        [dbc.Label("UAN"), dbc.Input(id="t-uan")],
                        md=6,
                    ),
                ],
                className="mb-2",
            ),
            
            dbc.Row(
                [
                    dbc.Col(
                        [dbc.Label("Bank Account Number"), dbc.Input(id="t-bank-account")],
                        md=6,
                    ),
                    dbc.Col(
                        [dbc.Label("Bank Name"), dbc.Input(id="t-bank-name")],
                        md=6,
                    ),
                ],
                className="mb-2",
            ),
            
            dbc.Label("Salary"),
            dbc.Input(id="t-salary", className="mb-3"),
            dbc.Label("Classes Preferred"),
            dbc.Input(id="t-classes", className="mb-3"),
            dbc.Label("Employment History"),
            dbc.Textarea(id="t-history", rows=2, className="mb-3"),
            dbc.Row(
                [
                    dbc.Col(
                        [
                            dbc.Label("Computer Knowledge"),
                            dcc.Dropdown(options=["Yes", "No"], id="t-computer"),
                        ],
                        md=6,
                    ),
                    dbc.Col(
                        [
                            dbc.Label("Online Teaching Experience"),
                            dcc.Dropdown(options=["Yes", "No"], id="t-online"),
                        ],
                        md=6,
                    ),
                ],
                className="mb-3",
            ),
            dbc.Label("Other Certifications"),
            dbc.Textarea(id="t-certifications", rows=2, className="mb-3"),
            html.Hr(),
            dbc.Label("Emergency Contact Name"),
            dbc.Input(id="t-emer-name", className="mb-2"),
            dbc.Input(id="t-emer-relation", placeholder="Relation", className="mb-2"),
            dbc.Input(
                id="t-emer-mobile", placeholder="Contact Number", className="mb-3"
            ),
            dbc.Label("Documents Submitted"),
            dbc.Textarea(id="t-docs", rows=2, className="mb-3"),
            dbc.Row(
                [
                    dbc.Col(
                        dbc.Button(
                            "Save Teacher", id="submit-teacher", color="success"
                        ),
                        width="auto",
                    ),
                    dbc.Col(
                        html.Div(id="teacher-message"),
                        width="auto",
                        className="ms-3 d-flex align-items-center",
                    ),
                ],
                className="mt-3",
                align="center",
            ),
        ]
    )


def search_teacher_layout(SessionData):
    teacher_names = get_teacher_names(SessionData)

    return dbc.Container(
        [
            dbc.Row(
                [
                    dbc.Col(
                        dcc.Dropdown(
                            id="search-teacher-name",  # same id use kar lo
                            options=[
                                {"label": name, "value": name} for name in teacher_names
                            ],
                            placeholder="Search or Select Teacher",
                            searchable=True,  # type bhi kar sakte ho
                            clearable=True,
                        ),
                        md=6,
                    ),
                    dbc.Col(
                        dbc.Button(
                            "Download Teacher Log + Salary",
                            id="download-teacher-btn",
                            color="primary",
                        ),
                        md=4,
                    ),
                ],
                className="mb-3",
            ),
            dcc.Download(id="download-teacher-file"),
            html.H5("Teacher Profile"),
            dash.dash_table.DataTable(id="teacher-profile-table", page_size=5),
            html.Hr(),
            html.H5("Salary History"),
            dash.dash_table.DataTable(id="teacher-salary-table", page_size=5),
        ],
        fluid=True,
    )


def upload_teacher_layout():
    return dbc.Container(
        [
            html.Div(
                [
                    # Main Title
                    html.H5(
                        "Upload Data",
                        style={
                            "color": "#2e7d32",
                            "fontWeight": "600",
                            "marginBottom": "20px",
                        },
                    ),
                    html.Hr(),
                    # Section Title
                    html.H6(
                        "Teacher Log Upload",
                        style={
                            "color": "#2e7d32",
                            "fontWeight": "500",
                            "marginBottom": "15px",
                        },
                    ),
                    # Buttons Row
                    dbc.Row(
                        [
                            dbc.Col(
                                dcc.Upload(
                                    id="upload-teacher-file",
                                    children=dbc.Button(
                                        "Upload Teacher CSV / Excel",
                                        style={
                                            "backgroundColor": "#2e7d32",
                                            "border": "none",
                                            "color": "white",
                                            "padding": "10px 24px",
                                            "borderRadius": "6px",
                                        },
                                    ),
                                    multiple=False,
                                ),
                                md=4,
                            ),
                            dbc.Col(
                                dbc.Button(
                                    "Download Sample Teacher CSV",
                                    id="download-teacher-sample",
                                    outline=True,
                                    color="secondary",
                                    style={
                                        "padding": "10px 24px",
                                        "borderRadius": "6px",
                                    },
                                ),
                                md=4,
                            ),
                        ],
                        className="mb-3",
                    ),
                    html.Hr(),
                    # Salary Upload Section
html.H6(
    "Salary Log Upload",
    style={
        "color": "#2e7d32",
        "fontWeight": "500",
        "marginBottom": "15px",
        "marginTop": "25px",
    },
),

dbc.Row(
    [
        dbc.Col(
            dcc.Upload(
                id="upload-salary-file",
                children=dbc.Button(
                    "Upload Salary CSV / Excel",
                    style={
                        "backgroundColor": "#2e7d32",
                        "border": "none",
                        "color": "white",
                        "padding": "10px 24px",
                        "borderRadius": "6px",
                    },
                ),
                multiple=False,
            ),
            md=4,
        ),

        dbc.Col(
            dbc.Button(
                "Download Sample Salary CSV",
                id="download-salary-sample",
                outline=True,
                color="secondary",
                style={
                    "padding": "10px 24px",
                    "borderRadius": "6px",
                },
            ),
            md=4,
        ),
    ],
    className="mb-3",
),

html.Div(id="upload-salary-status"),

dcc.Download(id="download-salary-sample-file"),
                    html.Div(id="upload-teacher-status"),
                    dcc.Download(id="download-teacher-sample-file"),
                ],
                style={
                    "backgroundColor": "white",
                    "padding": "25px",
                    "borderRadius": "10px",
                    "boxShadow": "0px 4px 12px rgba(0,0,0,0.06)",
                },
            )
        ],
        fluid=True,
        style={"marginTop": "30px", "marginBottom": "40px"},
    )


def get_teacher_names(SessionData):
    path = "/var/Data/" + str(SessionData["username"]) + "/teacher_log.csv"

    if os.path.exists(path):
        teachers = pd.read_csv(path)

        if "full_name" in teachers.columns:
            teacher_names = teachers["full_name"].dropna().tolist()
        else:
            teacher_names = []
    else:
        teacher_names = []

    return teacher_names


def register_callbacks(app):

    @app.callback(
        Output("teacher-tab-content", "children"),
        Input("teacher-tabs", "active_tab"),
        State("session", "data"),
    )
    def render_teacher_tab(tab, SessionData):
        if tab == "create-teacher":
            return create_teacher_form()
        elif tab == "search-teacher":
            return search_teacher_layout(SessionData)
        elif tab == "upload-teacher":
            return upload_teacher_layout()
        elif tab == "teacher-attendance":
            return teacher_attendance_layout(SessionData)

    # 🔧 FIX 2: Add Output + return value
    @app.callback(
        Output("teacher-message", "children"),
        Input("submit-teacher", "n_clicks"),
        State("t-name", "value"),
        State("t-dob", "value"),
        State("t-gender", "value"),
        State("t-marital", "value"),
        State("t-nationality", "value"),
        State("t-aadhaar", "value"),
        State("t-mobile", "value"),
        State("t-alt-mobile", "value"),
        State("t-email", "value"),
        State("t-perm-address", "value"),
        State("t-curr-address", "value"),
        State("t-city", "value"),
        State("t-state", "value"),
        State("t-pin", "value"),
        State("t-qualification", "value"),
        State("t-training", "value"),
        State("t-exp", "value"),
        State("t-subjects", "value"),
        State("t-classes", "value"),
        State("t-history", "value"),
        State("t-computer", "value"),
        State("t-online", "value"),
        State("t-certifications", "value"),
        State("t-emer-name", "value"),
        State("t-emer-relation", "value"),
        State("t-emer-mobile", "value"),
        State("t-docs", "value"),
        State("t-pan", "value"),
        State("t-uan", "value"),
        State("t-bank-account", "value"),
        State("t-bank-name", "value"),
        State("t-salary", "value"),
        State("session", "data"),
        prevent_initial_call=True,
    )
    def save_teacher(n, *vals):
        SessionData = vals[-1]
        teacher_vals = vals[:-1]  # all form fields, in order

        if not n or not vals[0]:
            return dash.no_update

        os.makedirs("/var/Data/" + str(SessionData["username"]), exist_ok=True)

        row = {
            "teacher_id": f"TCH_{datetime.now().strftime('%Y%m%d%H%M%S%f')}",
            "full_name": vals[0],
            "dob": vals[1],
            "gender": vals[2],
            "marital_status": vals[3],
            "nationality": vals[4],
            "aadhaar": vals[5],
            "mobile": vals[6],
            "alternate_mobile": vals[7],
            "email": vals[8],
            "permanent_address": vals[9],
            "current_address": vals[10],
            "city": vals[11],
            "state": vals[12],
            "pincode": vals[13],
            "qualification": vals[14],
            "training_qualification": vals[15],
            "teaching_experience_years": vals[16],
            "subjects": vals[17],
            "classes_preferred": vals[18],
            "employment_history": vals[19],
            "computer_knowledge": vals[20],
            "online_teaching": vals[21],
            "other_certifications": vals[22],
            "emergency_contact_name": vals[23],
            "emergency_contact_relation": vals[24],
            "emergency_contact_number": vals[25],
            "documents_submitted": vals[26],
            "pan_number": vals[27],
            "uan": vals[28],
            "bank_account_number": vals[29],
            "bank_name": vals[30],
            "salary": vals[31],
            "created_at": datetime.now().isoformat(),
        }

        pd.DataFrame([row]).to_csv(
            "/var/Data/" + str(SessionData["username"]) + "/teacher_log.csv",
            mode="a",
            index=False,
            header=not os.path.exists(
                "/var/Data/" + str(SessionData["username"]) + "/teacher_log.csv"
            ),
        )

        return dbc.Alert(
            "✅ Teacher Saved Successfully!",
            color="success",
            dismissable=True,
            duration=3000,
        )

    # 🔧 REQUIRED return

    @app.callback(
        Output("teacher-profile-table", "data"),
        Output("teacher-profile-table", "columns"),
        Output("teacher-salary-table", "data"),
        Output("teacher-salary-table", "columns"),
        Input("search-teacher-name", "value"),
        State("session", "data"),
    )
    def search_teacher(name, SessionData):
        if not name:
            return [], [], [], []

        teachers = pd.read_csv(
            "/var/Data/" + str(SessionData["username"]) + "/teacher_log.csv"
        )
        salary = (
            pd.read_csv(
                "/var/Data/" + str(SessionData["username"]) + "/salary_ledger.csv"
            )
            if os.path.exists(
                "/var/Data/" + str(SessionData["username"]) + "/salary_ledger.csv"
            )
            else pd.DataFrame()
        )

        t = teachers[teachers["full_name"].str.contains(name, case=False, na=False)]
        if not salary.empty and "account_name" in salary.columns:
            s = salary[salary["account_name"].str.contains(name, case=False, na=False)]
        else:
            s = pd.DataFrame()

        return (
            t.to_dict("records"),
            [{"name": c, "id": c} for c in t.columns],
            s.to_dict("records"),
            [{"name": c, "id": c} for c in s.columns] if not s.empty else [],
        )

    @app.callback(
        Output("search-teacher-name", "value"),
        Input("teacher-list-dropdown", "value"),
        prevent_initial_call=True,
    )
    def sync_dropdown_to_input(selected_name):
        if selected_name:
            return selected_name
        return dash.no_update

    @app.callback(
        Output("download-teacher-file", "data"),
        Input("download-teacher-btn", "n_clicks"),
        State("search-teacher-name", "value"),
        State("session", "data"),
        prevent_initial_call=True,
    )
    def download_teacher(n, name, SessionData):
        if not n or not name:
            raise dash.exceptions.PreventUpdate

        teachers = pd.read_csv(
            "/var/Data/" + str(SessionData["username"]) + "/teacher_log.csv"
        )
        salary = (
            pd.read_csv(
                "/var/Data/" + str(SessionData["username"]) + "/salary_ledger.csv"
            )
            if os.path.exists(
                "/var/Data/" + str(SessionData["username"]) + "/salary_ledger.csv"
            )
            else pd.DataFrame()
        )

        t = teachers[teachers["full_name"].str.contains(name, case=False, na=False)]
        if not salary.empty and "account_name" in salary.columns:
            s = salary[salary["account_name"].str.contains(name, case=False, na=False)]
        else:
            s = pd.DataFrame()

        output = io.BytesIO()
        with pd.ExcelWriter(output, engine="xlsxwriter") as writer:
            t.to_excel(writer, index=False, sheet_name="Teacher Log")
            if not s.empty:
                s.to_excel(writer, index=False, sheet_name="Salary Ledger")

        output.seek(0)
        return dcc.send_bytes(
            output.read(), f"{name.replace(' ', '_')}_teacher_log.xlsx"
        )

    @app.callback(
        Output("upload-teacher-status", "children"),
        Input("upload-teacher-file", "contents"),
        State("upload-teacher-file", "filename"),
        State("session", "data"),
        prevent_initial_call=True,
    )
    def upload_teacher(contents, filename, SessionData):

        if not contents:
            raise dash.exceptions.PreventUpdate

        content_type, content_string = contents.split(",")
        decoded = base64.b64decode(content_string)

        os.makedirs("/var/Data/" + str(SessionData["username"]), exist_ok=True)
        file_path = "/var/Data/" + str(SessionData["username"]) + "/teacher_log.csv"

        try:
            if filename.endswith(".csv"):
                df = pd.read_csv(io.StringIO(decoded.decode("utf-8")))
            elif filename.endswith(".xlsx"):
                df = pd.read_excel(io.BytesIO(decoded))
            else:
                return dbc.Alert("❌ Unsupported file format!", color="danger")

            # 🔹 If file exists → append without duplicate teacher_id
            if os.path.exists(file_path):
                existing_df = pd.read_csv(file_path)

                if "teacher_id" in df.columns and "teacher_id" in existing_df.columns:
                    df = df[~df["teacher_id"].isin(existing_df["teacher_id"])]

                updated_df = pd.concat([existing_df, df], ignore_index=True)
            else:
                updated_df = df

            updated_df.to_csv(file_path, index=False)

            return dbc.Alert(
                "✅ Teacher Log Updated Successfully!",
                color="success",
                dismissable=True,
                duration=3000,
            )

        except Exception as e:
            return dbc.Alert(f"❌ Error: {str(e)}", color="danger")

    @app.callback(
        Output("download-teacher-sample-file", "data"),
        Input("download-teacher-sample", "n_clicks"),
        prevent_initial_call=True,
    )
    def download_sample(n):

        sample_data = pd.DataFrame(
            [
                {
                    "teacher_id": "TCH_20260220123000123456",
                    "full_name": "Rohit Verma",
                    "dob": "1992-08-15",
                    "gender": "Male",
                    "marital_status": "Married",
                    "nationality": "Indian",
                    "aadhaar": "458732145896",
                    "mobile": "9876543210",
                    "alternate_mobile": "9123456780",
                    "email": "rohit.verma@example.com",
                    "permanent_address": "H-24, Sector 15, Noida",
                    "current_address": "H-24, Sector 15, Noida",
                    "city": "Noida",
                    "state": "Uttar Pradesh",
                    "pincode": "201301",
                    "qualification": "M.Sc (Mathematics)",
                    "training_qualification": "B.Ed",
                    "teaching_experience_years": "8",
                    "subjects": "Mathematics, Physics",
                    "classes_preferred": "8-12",
                    "employment_history": "ABC Public School (2016-2022)",
                    "computer_knowledge": "Yes",
                    "pan_number": "ABCDE1234F",
                    "uan": "100200300400",
                    "bank_account_number": "123456789012",
                    "bank_name": "State Bank of India",
                    "salary": "45000",
                    "online_teaching": "Yes",
                    "other_certifications": "CTET Qualified",
                    "emergency_contact_name": "Sunita Verma",
                    "emergency_contact_relation": "Spouse",
                    "emergency_contact_number": "9812345678",
                    "documents_submitted": "Aadhaar, Degree Certificates",
                    "created_at": "2026-02-20T12:30:00.000000",
                }
            ]
        )

        return dcc.send_data_frame(
            sample_data.to_csv, "sample_teacher_log.csv", index=False
        )
    



    @app.callback(
    Output("upload-salary-status", "children"),
    Input("upload-salary-file", "contents"),
    State("upload-salary-file", "filename"),
    State("session", "data"),
    prevent_initial_call=True,
)
    def upload_salary(contents, filename, SessionData):

     if not contents:
        raise dash.exceptions.PreventUpdate

     content_type, content_string = contents.split(",")
     decoded = base64.b64decode(content_string)

     base_path = f"/var/Data/{SessionData['username']}"
     os.makedirs(base_path, exist_ok=True)

     file_path = f"{base_path}/salary_ledger.csv"

     try:

        # Read uploaded file
        if filename.endswith(".csv"):
            df = pd.read_csv(io.StringIO(decoded.decode("utf-8")))
        elif filename.endswith(".xlsx"):
            df = pd.read_excel(io.BytesIO(decoded))
        else:
            return dbc.Alert("❌ Unsupported file format!", color="danger")

        # If file already exists → append
        if os.path.exists(file_path):

            existing_df = pd.read_csv(file_path)

            # remove duplicates using entry_id
            if "entry_id" in df.columns and "entry_id" in existing_df.columns:
                df = df[~df["entry_id"].isin(existing_df["entry_id"])]

            updated_df = pd.concat([existing_df, df], ignore_index=True)

        else:
            updated_df = df

        # Save updated file
        updated_df.to_csv(file_path, index=False)

        return dbc.Alert(
            f"✅ Salary Ledger Updated! {len(df)} new records added.",
            color="success",
            dismissable=True,
            duration=3000,
        )

     except Exception as e:
        return dbc.Alert(f"❌ Error: {str(e)}", color="danger")

    @app.callback(
    Output("download-salary-sample-file", "data"),
    Input("download-salary-sample", "n_clicks"),
    prevent_initial_call=True,
)
    def download_salary_sample(n):

     sample_data = pd.DataFrame(
        [
            {
                "entry_id": "SAL_20260101205129887757",
                "form_name": "SALARY PAYMENT",
                "ledger_name": "Salary Expense",
                "account_name": "Yash",
                "ledger_group": "Salary & Wages Expense",
                "cash_amount": 1224.52,
                "bank1_amount": 0,
                "bank2_amount": 0,
                "total_amount": 1224.52,
                "transaction_date": "2026-01-01",
                "details": "Salary payment to Yash",
                "created_at": "2026-01-01T20:51:29.888203",
            }
        ]
    )

    @app.callback(
        Output("attendance-board", "children"),
        Input("load-attendance-board", "n_clicks"),
        Input("attendance-store", "data"),
        State("session", "data"),
        prevent_initial_call=True,
    )
    def render_attendance_board(n, data, SessionData):
    
        base_path = f"/var/Data/{SessionData['username']}"
        file_path = f"{base_path}/teacher_attendance.csv"
    
        # Load saved attendance
        saved_data = {}
    
        if os.path.exists(file_path):
    
            df = pd.read_csv(file_path)
    
            for _, row in df.iterrows():
                key = f"{row['teacher']}_{row['date']}"
                saved_data[key] = row["status"]
    
        # Merge saved + current store
        data = {**saved_data, **(data or {})}
    
        teachers = get_teacher_names(SessionData)
    
        if not teachers:
            return dbc.Alert("No teachers found in teacher_log.csv", color="warning")
    
        return build_attendance_board(data, teachers)        
    @app.callback(
        Output("attendance-store", "data"),
        Input({"type": "att-cell", "teacher": ALL, "date": ALL}, "n_clicks"),
        State("attendance-store", "data"),
        prevent_initial_call=True,
    )
    def change_status(_, data):
    
        data = data or {}
    
        ctx = dash.ctx
        trigger = ctx.triggered_id
    
        if not trigger:
            raise dash.exceptions.PreventUpdate
    
        teacher = trigger["teacher"]
        date = trigger["date"]
    
        key = f"{teacher}_{date}"
    
        current = data.get(key, "present")
    
        i = STATUS.index(current)
        new_status = STATUS[(i + 1) % len(STATUS)]
    
        data[key] = new_status
    
        print("Status changed:", teacher, date, new_status)
    
        return data
        
    @app.callback(
        Output("attendance-save-status", "children"),
        Input("save-attendance-btn", "n_clicks"),
        State("attendance-store", "data"),
        State("session", "data"),
        prevent_initial_call=True,
    )
    def save_attendance(n, data, SessionData):
    
        if not n:
            raise dash.exceptions.PreventUpdate
    
        if not data:
            return dbc.Alert("Nothing to save.", color="warning")
    
        base_path = f"/var/Data/{SessionData['username']}"
        os.makedirs(base_path, exist_ok=True)
    
        file_path = f"{base_path}/teacher_attendance.csv"
    
        # Convert store data → dataframe
        rows = []
    
        for key, status in data.items():
    
            if "_" not in key:
                continue
    
            teacher, date = key.rsplit("_", 1)
    
            rows.append({
                "teacher": teacher,
                "date": date,
                "status": status
            })
    
        new_df = pd.DataFrame(rows)
    
        # Load historical attendance
        if os.path.exists(file_path):
    
            existing_df = pd.read_csv(file_path)
    
            merged_df = pd.concat([existing_df, new_df], ignore_index=True)
    
            merged_df = merged_df.drop_duplicates(
                subset=["teacher", "date"],
                keep="last"
            )
    
        else:
    
            merged_df = new_df
    
        merged_df = merged_df.sort_values(["teacher", "date"])
    
        merged_df.to_csv(file_path, index=False)
    
        return dbc.Alert(
            f"✅ Attendance saved successfully ({len(new_df)} updates)",
            color="success",
            dismissable=True,
            duration=3000,
        )


