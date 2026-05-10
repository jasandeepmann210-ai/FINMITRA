import dash
from dash import html, dcc, Input, Output, ALL, State
import datetime
import os
import dash_bootstrap_components as dbc
import base64
import io
import pandas as pd

# KPMG Colors
KPMG_BLUE = "#1F3A5F"
KPMG_LIGHT_BLUE = "#6BBF59"
WHITE = "#FFFFFF"
CARD_BORDER = "#E3EAF0"


# =========================================================
# HELPERS
# =========================================================
def list_report_files(SessionData):

    username = SessionData["username"]

    base_dir = f"/var/Data/{username}"

    files = []

    # -------- Root files --------
    if os.path.exists(base_dir):

        for f in os.listdir(base_dir):

            path = os.path.join(base_dir, f)

            if os.path.isfile(path):
                files.append(f)

    # -------- Marks folder files --------
    marks_dir = os.path.join(base_dir, "marks")
    
    if os.path.exists(marks_dir):
    
        for f in os.listdir(marks_dir):
    
            path = os.path.join(marks_dir, f)
    
            if os.path.isfile(path) and f.endswith(".csv"):
    
                files.append(f"marks/{f}")

    return sorted(files)


# =========================================================
# LAYOUT
# =========================================================
def get_layout(SessionData):
    current_time = datetime.datetime.now()
    report_files = list_report_files(SessionData)

    return html.Div(
        style={
            "backgroundColor": WHITE,
            "padding": "40px 20px",
            "fontFamily": "Segoe UI, Arial, sans-serif",
            "minHeight": "80vh",
        },
        children=[
            html.Div(
                style={"maxWidth": "1200px", "margin": "0 auto"},
                children=[
                    # ================= WELCOME CARD =================
                    html.Div(
                        style={
                            "textAlign": "center",
                            "padding": "60px 40px",
                            "marginBottom": "40px",
                            "background": f"linear-gradient(135deg, {WHITE} 0%, #f0f7ff 100%)",
                            "borderRadius": "10px",
                        },
                        children=[
                            html.Img(
                                src="/assets/logo.png",
                                style={"height": "100px", "marginBottom": "30px"},
                            ),
                            html.H1(
                                "Welcome to FinMitra",
                                style={
                                    "color": KPMG_BLUE,
                                    "fontSize": "42px",
                                    "fontWeight": "700",
                                    "marginBottom": "20px",
                                },
                            ),
                            html.Div(
                                "FinMitra Dashboard Platform",
                                style={
                                    "fontSize": "20px",
                                    "color": "#666",
                                    "fontWeight": "500",
                                    "marginBottom": "15px",
                                },
                            ),
                            html.Div(
                                current_time.strftime("%A, %B %d, %Y"),
                                style={
                                    "fontSize": "16px",
                                    "color": "#999",
                                },
                            ),
                        ],
                    ),
                    # ================= REPORT DOWNLOAD =================
                    html.Div(
                        style={
                            "padding": "30px",
                            "border": f"1px solid {CARD_BORDER}",
                            "borderRadius": "10px",
                            "backgroundColor": "#FAFFFB",
                        },
                        children=[
                            html.H4(
                                "Reports",
                                style={
                                    "color": KPMG_BLUE,
                                    "fontWeight": "600",
                                    "marginBottom": "20px",
                                },
                            ),
                            html.Div(
                                [
                                    dbc.Button(
                                        [
                                            html.I(className="bi bi-download me-2"),
                                            file,
                                        ],
                                        id={
                                            "type": "download-report-btn",
                                            "index": file,
                                        },
                                        color="success",
                                        outline=True,
                                        className="me-2 mb-2",
                                    )
                                    for file in report_files
                                ]
                                if report_files
                                else html.Div(
                                    "No reports available.",
                                    style={"color": "#999"},
                                )
                            ),
                            dcc.Download(id="download-report-file"),
                            # ===== SUBADMIN LEDGER UPLOAD (ONLY IF SUBADMIN) =====
                            (
                                html.Div(
                                    style={
                                        "marginTop": "30px",
                                        "paddingTop": "20px",
                                        "borderTop": f"1px dashed {CARD_BORDER}",
                                    },
                                    children=[
                                        html.H5(
                                            "Upload Ledgers (Sub-Admin Only)",
                                            style={
                                                "color": "#1B5E20",
                                                "fontWeight": "600",
                                                "marginBottom": "15px",
                                            },
                                        ),
                                        dbc.Row(
                                            [
                                                dbc.Col(
                                                    dcc.Upload(
                                                        id="upload-master-ledger",
                                                        children=dbc.Button(
                                                            "Upload Master Ledger",
                                                            color="success",
                                                            outline=True,
                                                        ),
                                                        multiple=False,
                                                    ),
                                                    md=4,
                                                ),
                                                dbc.Col(
                                                    dcc.Upload(
                                                        id="upload-journal-ledger",
                                                        children=dbc.Button(
                                                            "Upload Journal Ledger",
                                                            color="success",
                                                            outline=True,
                                                        ),
                                                        multiple=False,
                                                    ),
                                                    md=4,
                                                ),
                                            ]
                                        ),
                                        html.Div(
                                            id="ledger-upload-status",
                                            className="mt-3",
                                        ),
                                    ],
                                )
                                if SessionData.get("role") == "SubAdmin"
                                else None
                            ),
                        ],
                    ),
                    # ===== SCHOOL FEES LOGO UPLOAD =====
                    html.Div(
                        style={
                            "marginTop": "30px",
                            "paddingTop": "20px",
                            "borderTop": f"1px dashed {CARD_BORDER}",
                        },
                        children=[
                            html.H5(
                                "Upload School Fees Logo",
                                style={
                                    "color": "#1B5E20",
                                    "fontWeight": "600",
                                    "marginBottom": "15px",
                                },
                            ),
                            dcc.Upload(
                                id="upload-school-logo",
                                children=dbc.Button(
                                    "Upload PNG Logo",
                                    color="success",
                                    outline=True,
                                ),
                                multiple=False,
                                accept=".png",
                            ),
                            html.Div(
                                id="logo-upload-status",
                                className="mt-3",
                            ),
                            dbc.Row(
                                [
                                    dbc.Col(
                                        [
                                            dbc.Label("School Name"),
                                            dbc.Input(
                                                id="school-name",
                                                placeholder="Enter School Name",
                                            ),
                                        ],
                                        md=4,
                                    ),
                                    dbc.Col(
                                        [
                                            dbc.Label("School Address"),
                                            dbc.Input(
                                                id="school-address",
                                                placeholder="Enter Address",
                                            ),
                                        ],
                                        md=4,
                                    ),
                                    dbc.Col(
                                        [
                                            dbc.Label("PAN Number"),
                                            dbc.Input(
                                                id="school-pan",
                                                placeholder="Enter PAN Number",
                                            ),
                                        ],
                                        md=4,
                                    ),
                                ]
                            ),
                            dbc.Button(
                                "Save School Info",
                                id="save-school-info-btn",
                                color="primary",
                                className="mt-3",
                            ),
                            html.Div(id="school-info-status", className="mt-3"),
                            html.Hr(),
                            html.H5(
                                "School Events",
                                style={
                                    "color": "#1B5E20",
                                    "fontWeight": "600",
                                    "marginBottom": "15px",
                                    "marginTop": "20px",
                                },
                            ),
                            # -------- CSV Upload --------
                            dbc.Row(
                                [
                                    dbc.Col(
                                        dcc.Upload(
                                            id="upload-events-csv",
                                            children=dbc.Button(
                                                "Upload Events CSV",
                                                color="success",
                                                outline=True,
                                            ),
                                            multiple=False,
                                        ),
                                        md="auto",
                                    ),
                                    dbc.Col(
                                        dbc.Button(
                                            "Download Sample CSV",
                                            id="download-sample-events",
                                            color="secondary",
                                            outline=True,
                                        ),
                                        md="auto",
                                    ),
                                ],
                                className="g-2",
                            ),
                            dcc.Download(id="download-sample-events-file"),
                            html.Div(id="events-upload-status", className="mt-3"),
                            html.Hr(),
                            # -------- Manual Event Entry --------
                            dbc.Row(
                                [
                                    dbc.Col(
                                        [
                                            dbc.Label("Event Name"),
                                            dbc.Input(
                                                id="event-title",
                                                placeholder="Example: Annual Function",
                                            ),
                                        ],
                                        md=6,
                                    ),
                                    dbc.Col(
                                        [
                                            dbc.Label("Event Date"),
                                            dbc.Input(
                                                id="event-date",
                                                type="date",
                                            ),
                                        ],
                                        md=6,
                                    ),
                                ]
                            ),
                            dbc.Button(
                                "Add Event",
                                id="add-event-btn",
                                color="primary",
                                className="mt-3",
                            ),
                            html.Div(id="event-add-status", className="mt-3"),
                        ],
                    ),
                ],
            )
        ],
    )


# =========================================================
# CALLBACKS
# =========================================================
# =========================================================
# SUBADMIN LEDGER UPLOAD CALLBACKS (REPLACE MODE)
# =========================================================


dropdown_values = {
    "stu-gender": {"Boy": "1", "Girl": "2", "Other/Transgender": "3"},
    "stu-caste": {"GEN": "1", "SC": "2", "ST": "3", "OBC": "4", "SBC": "5"},
    "stu-religion": {
        "Hindu": "0",
        "Muslim": "5",
        "Christian": "6",
        "Sikh": "7",
        "Buddhist": "8",
        "Parsi": "9",
        "Jain": "10",
        "Others": "11",
    },
    "stu-mother-tongue": {
        "--Select--": "-1",
        "Hindi": "4",
        "English": "19",
        "Rajasthani": "56",
        "Urdu": "18",
        "Sanskrit": "14",
        "Sindhi": "15",
        "Punjabi": "13",
        "Gujarati": "3",
        "Bengali": "2",
        "Kannada": "5",
        "Kashmiri": "6",
        "Konkani": "7",
        "Malayalam": "8",
        "Manipuri": "9",
        "Marathi": "10",
        "Nepali": "11",
        "Oriya": "12",
        "Tamil": "16",
        "Telugu": "17",
        "Assamese": "1",
        "Bodo": "20",
        "Mising": "21",
        "Dogri": "22",
        "Khasi": "23",
        "Garo": "24",
        "Mizo": "25",
        "Bhutia": "26",
        "Lepcha": "27",
        "Limboo": "28",
        "French": "29",
        "Angami": "41",
        "Ao": "42",
        "Arabic": "43",
        "Bhoti": "44",
        "Bodhi": "45",
        "German": "46",
        "Kakbarak": "47",
        "Konyak": "48",
        "Laddakhi": "49",
        "Lotha": "50",
        "Maithili": "51",
        "Nicobaree": "52",
        "Oriya(lower)": "53",
        "Persian": "54",
        "Portuguese": "55",
        "Russian": "57",
        "Sema": "58",
        "Spanish": "59",
        "Tibetan": "60",
        "Zeliang": "61",
        "Other languages": "99",
    },
    "stu-rural-urban": {"Rural": "R", "Urban": "U"},
    "stu-bpl": {"Yes": "1", "No": "2"},
    "stu-disadvantage": {"Yes": "1", "No": "2"},
    "stu-rte": {"Not Applicable": "0", "Yes": "1", "No": "2"},
    "stu-class": {
        "PP.3+": "0",
        "PP.4+": "1",
        "PP.5+": "2",
        "First": "3",
        "Second": "4",
        "Third": "5",
        "Fourth": "6",
        "Fifth": "7",
        "Sixth": "8",
        "Seventh": "9",
        "Eight": "10",
        "Ninth": "11",
        "Tenth": "12",
        "Eleventh": "13",
        "Twelth": "14",
    },
    "stu-prev-class": {
        "PP.3+": "0",
        "PP.4+": "1",
        "PP.5+": "2",
        "First": "3",
        "Second": "4",
        "Third": "5",
        "Fourth": "6",
        "Fifth": "7",
        "Sixth": "8",
        "Seventh": "9",
        "Eight": "10",
        "Ninth": "11",
        "Tenth": "12",
        "Eleventh": "13",
        "Twelth": "14",
        "None": "99",
    },
    "stu-class1-status": {
        "NOT APPLICABLE": "0",
        "SAME SCHOOL": "1",
        "ANOTHER SCHOOL": "2",
        "ANGANWADI/ECCE": "3",
        "NONE": "4",
    },
    "stu-medium": {"Hindi": "4", "English": "19"},
    "stu-disability": {
        "Not Applicable": "0",
        "Blindness": "1",
        "Low-vision": "2",
        "Hearing": "3",
        "Speech": "4",
        "Loco Motor": "5",
        "Mental Retardation": "6",
        "Learning Disability": "7",
        "Cerebral Palsy": "8",
        "Autism": "9",
        "Multiple Disabilities": "10",
        "Mental Illness": "12",
        "Acid Attack Victim": "13",
        "Dwarfism": "14",
        "Muscular Dystrophy": "15",
        "Leprosy Cured Persons": "16",
        "Parkinson & Disease": "17",
        "Sickle Cell Disease": "18",
        "Thalassemia": "19",
        "Chronic Neurological Conditions": "20",
        "Hemophilia": "21",
        "Multiple Sclerosis": "22",
    },
    "stu-cwsn": {
        "Not Applicable": "0",
        "Braille Books": "1",
        "Braille Kit": "2",
        "Low vision kit": "3",
        "Hearing Aid": "4",
        "Braces": "5",
        "Crutches": "6",
        "Wheel chair": "7",
        "Tri-cycle": "8",
        "Calliper": "9",
        "Others": "10",
    },
    "stu-uniform": {"None": "0", "One Set": "1", "Two Set": "2", "Partial": "3"},
    "stu-textbook": {"Not Applicable": "0", "Yes": "1", "No": "2"},
    "stu-transport": {"Not Applicable": "0", "Yes": "1", "No": "2"},
    "stu-bicycle": {"Not Applicable": "0", "Yes": "1", "No": "2"},
    "stu-escort": {"Not Applicable": "0", "Yes": "1", "No": "2"},
    "stu-midday-meal": {"Not Applicable": "0", "Yes": "1", "No": "2"},
    "stu-hostel": {
        "Not Applicable": "0",
        "KGBV": "1",
        "Non KGBV (Government)": "2",
        "Girls Hostel": "3",
        "Others": "4",
        "None": "5",
    },
    "stu-special-training": {
        "Not Applicable": "0",
        "Residential": "1",
        "Non Residential": "2",
    },
    "stu-homeless": {
        "NA": "0",
        "With Parent/Guardian": "1",
        "Without Adult Protection": "2",
    },
    "stu-appeared-exam": {"Yes": "1", "No": "2", "NA": "3"},
    "stu-passed-exam": {"Yes": "1", "No": "2", "NA": "3"},
    "stu-stream": {
        "Not Applicable": "0",
        "Arts": "1",
        "Science": "2",
        "Commerce": "3",
        "Vocational": "4",
        "Other stream": "5",
    },
    "stu-trade": {
        "Not Applicable": "0",
        "Agriculture": "61",
        "Apparel": "62",
        "Automotive": "63",
        "Beauty & Wellness": "64",
        "Banking Financial Services and Insurance (BFSI)": "65",
        "Construction": "66",
        "Electronics": "67",
        "Healthcare": "68",
        "IT-ITES": "69",
        "Logistics": "70",
        "Capital Goods": "71",
        "Media & Entertainment": "72",
        "Multi-Skilling": "73",
        "Retail": "74",
        "Security": "75",
        "Sports": "76",
        "Telecom": "77",
        "Tourism & Hospitality": "78",
    },
    "stu-iron-folic": {"Not Applicable": "0", "Yes": "1", "No": "2"},
    "stu-deworming": {"Not Applicable": "0", "Yes": "1", "No": "2"},
    "stu-vitamin-a": {"Not Applicable": "0", "Yes": "1", "No": "2"},
    "stu-previous-year-status": {
        "Not Applicable": "0",
        "Same School": "1",
        "Another School": "2",
        "Anganwadi/ECCE": "3",
        "None": "4",
    },
}


def apply_dropdown_mapping(df):

    field_map = {
        "gender": "stu-gender",
        "caste_category": "stu-caste",
        "religion": "stu-religion",
        "rural_urban": "stu-rural-urban",
        "mother_tongue": "stu-mother-tongue",
        "bpl": "stu-bpl",
        "previous_year_status": "stu-previous-year-status",
        "disability_type": "stu-disability",
        "cwsn_facility": "stu-cwsn",
        "disadvantaged_group": "stu-disadvantage",
        "trade": "stu-trade",
        "hostel_facility": "stu-hostel",
        "is_RTE": "stu-rte",
        "studying_class": "stu-class",
        "previous_class": "stu-prev-class",
        "medium": "stu-medium",
        "uniform_sets": "stu-uniform",
        "textbook_set": "stu-textbook",
        "transport_facility": "stu-transport",
        "bicycle_facility": "stu-bicycle",
        "escort_facility": "stu-escort",
        "midday_meal": "stu-midday-meal",
        "special_training": "stu-special-training",
        "homeless_status": "stu-homeless",
        "appeared_last_exam": "stu-appeared-exam",
        "passed_last_exam": "stu-passed-exam",
        "stream": "stu-stream",
        "iron_tablets": "stu-iron-folic",
        "deworming_tablets": "stu-deworming",
        "vitamin_a": "stu-vitamin-a",
    }

    for col, dropdown_key in field_map.items():

        if col in df.columns and dropdown_key in dropdown_values:

            # 🔥 reverse mapping (value → label)
            mapping = {str(v): k for k, v in dropdown_values[dropdown_key].items()}

            df[col] = df[col].astype(str).map(mapping).fillna(df[col])

    return df


def register_callbacks(app):

    # ---------------- DOWNLOAD REPORT ----------------
    @app.callback(
        Output("download-report-file", "data"),
        Input({"type": "download-report-btn", "index": ALL}, "n_clicks"),
        State("session", "data"),
        prevent_initial_call=True,
    )
    def download_report(_, SessionData):

        REPORTS_DIR = "/var/Data/" + str(SessionData["username"])

        ctx = dash.callback_context
        if not ctx.triggered:
            return None

        triggered_id = ctx.triggered_id
        if not triggered_id:
            return None

        filename = triggered_id["index"]

        base_dir = f"/var/Data/{SessionData['username']}"
        
        # supports nested paths like marks/Class1/file.csv
        file_path = os.path.join(base_dir, filename)

        if not os.path.exists(file_path):
            return None

        # -------- ONLY FOR STUDENT LOG --------
        if filename in ["student_log.csv", "student_log_history.csv"]:

            df = pd.read_csv(file_path)

            # 🔥 APPLY FULL AUTO MAPPING
            df = apply_dropdown_mapping(df)

            return dcc.send_data_frame(df.to_csv, filename, index=False)

        return dcc.send_file(file_path)

    # ---------------- MASTER LEDGER UPLOAD ----------------
    @app.callback(
        Output("ledger-upload-status", "children", allow_duplicate=True),
        Input("upload-master-ledger", "contents"),
        State("upload-master-ledger", "filename"),
        State("session", "data"),
        prevent_initial_call=True,
    )
    def upload_master_ledger(contents, filename, SessionData):

        if SessionData.get("role") != "SubAdmin":
            raise dash.exceptions.PreventUpdate

        if not contents or not filename:
            raise dash.exceptions.PreventUpdate

        try:
            decoded = base64.b64decode(contents.split(",")[1])
            base_dir = f"/var/Data/{SessionData['username']}"
            os.makedirs(base_dir, exist_ok=True)

            if filename.lower().endswith(".csv"):
                df = pd.read_csv(io.StringIO(decoded.decode("utf-8")))
            elif filename.lower().endswith(".xlsx"):
                df = pd.read_excel(io.BytesIO(decoded))
            else:
                return dbc.Alert("❌ Only CSV or Excel allowed", color="danger")

            target = os.path.join(base_dir, "master_ledger.csv")

            # 🔥 REPLACE MODE
            df.to_csv(target, index=False)

            return dbc.Alert(
                f"✅ Master Ledger replaced successfully ({len(df)} rows)",
                color="success",
                dismissable=True,
            )

        except Exception as e:
            return dbc.Alert(f"❌ Error: {e}", color="danger", dismissable=True)

    # ---------------- JOURNAL LEDGER UPLOAD ----------------
    @app.callback(
        Output("ledger-upload-status", "children", allow_duplicate=True),
        Input("upload-journal-ledger", "contents"),
        State("upload-journal-ledger", "filename"),
        State("session", "data"),
        prevent_initial_call=True,
    )
    def upload_journal_ledger(contents, filename, SessionData):

        if SessionData.get("role") != "SubAdmin":
            raise dash.exceptions.PreventUpdate

        if not contents or not filename:
            raise dash.exceptions.PreventUpdate

        try:
            decoded = base64.b64decode(contents.split(",")[1])
            base_dir = f"/var/Data/{SessionData['username']}"
            os.makedirs(base_dir, exist_ok=True)

            if filename.lower().endswith(".csv"):
                df = pd.read_csv(io.StringIO(decoded.decode("utf-8")))
            elif filename.lower().endswith(".xlsx"):
                df = pd.read_excel(io.BytesIO(decoded))
            else:
                return dbc.Alert("❌ Only CSV or Excel allowed", color="danger")

            target = os.path.join(base_dir, "journal_ledger.csv")

            # 🔥 REPLACE MODE
            df.to_csv(target, index=False)

            return dbc.Alert(
                f"✅ Journal Ledger replaced successfully ({len(df)} rows)",
                color="success",
                dismissable=True,
            )

        except Exception as e:
            return dbc.Alert(f"❌ Error: {e}", color="danger", dismissable=True)

    # ---------------- SCHOOL FEES LOGO UPLOAD ----------------
    @app.callback(
        Output("logo-upload-status", "children"),
        Output("logo-refresh-trigger", "data"),
        Input("upload-school-logo", "contents"),
        State("upload-school-logo", "filename"),
        State("session", "data"),
        prevent_initial_call=True,
    )
    def upload_school_logo(contents, filename, SessionData):

        if not contents or not filename:
            raise dash.exceptions.PreventUpdate

        allowed_extensions = (".png", ".jpg", ".jpeg", ".gif", ".webp")

        if not filename.lower().endswith(allowed_extensions):
            return (
                dbc.Alert(
                    "❌ Only image files allowed (PNG, JPG, JPEG, GIF, WEBP)",
                    color="danger",
                    dismissable=True,
                ),
                str(datetime.datetime.now()),
            )

        try:
            decoded = base64.b64decode(contents.split(",")[1])

            assets_dir = "/var/Data/" + str(SessionData["username"])
            os.makedirs(assets_dir, exist_ok=True)

            # Always save as PNG internally for consistency
            target_path = os.path.join(assets_dir, "school_fees_logo.png")

            with open(target_path, "wb") as f:
                f.write(decoded)

            return (
                dbc.Alert(
                    "✅ Logo uploaded successfully",
                    color="success",
                    dismissable=True,
                ),
                str(datetime.datetime.now()),
            )

        except Exception as e:
            return (
                dbc.Alert(f"❌ Error: {e}", color="danger", dismissable=True),
                str(datetime.datetime.now()),
            )

    @app.callback(
        Output("school-info-status", "children"),
        Input("save-school-info-btn", "n_clicks"),
        State("school-name", "value"),
        State("school-address", "value"),
        State("school-pan", "value"),
        State("session", "data"),
        prevent_initial_call=True,
    )
    def save_school_info(n, name, address, pan, SessionData):

        if not name:
            return dbc.Alert("Enter school name", color="warning")

        base_dir = f"/var/Data/{SessionData['username']}"
        os.makedirs(base_dir, exist_ok=True)

        path = os.path.join(base_dir, "school_info.csv")

        df = pd.DataFrame(
            [{"school_name": name, "address": address, "pan_number": pan}]
        )

        df.to_csv(path, index=False)

        return dbc.Alert("✅ School info saved successfully", color="success")

    @app.callback(
        Output("events-upload-status", "children"),
        Input("upload-events-csv", "contents"),
        State("upload-events-csv", "filename"),
        State("session", "data"),
        prevent_initial_call=True,
    )
    def upload_events_csv(contents, filename, SessionData):

        if not contents:
            raise dash.exceptions.PreventUpdate

        try:
            decoded = base64.b64decode(contents.split(",")[1])

            base_dir = f"/var/Data/{SessionData['username']}"
            os.makedirs(base_dir, exist_ok=True)

            path = os.path.join(base_dir, "events.csv")

            new_df = pd.read_csv(io.StringIO(decoded.decode("utf-8")))

            # check format
            if not {"event", "date"}.issubset(new_df.columns):
                return dbc.Alert(
                    "CSV must contain columns: event, date",
                    color="danger",
                )

            # -------- UPDATE MODE --------
            if os.path.exists(path):

                old_df = pd.read_csv(path)

                df = pd.concat([old_df, new_df], ignore_index=True)

                # duplicate remove (same event + date)
                df = df.drop_duplicates(subset=["event", "date"])

            else:

                df = new_df

            df.to_csv(path, index=False)

            return dbc.Alert(
                f"✅ {len(new_df)} events added successfully",
                color="success",
            )

        except Exception as e:
            return dbc.Alert(f"❌ Error: {e}", color="danger")

    @app.callback(
        Output("event-add-status", "children"),
        Input("add-event-btn", "n_clicks"),
        State("event-title", "value"),
        State("event-date", "value"),
        State("session", "data"),
        prevent_initial_call=True,
    )
    def add_event(n, title, date, SessionData):

        if not title or not date:
            return dbc.Alert("Enter event name and date", color="warning")

        base_dir = f"/var/Data/{SessionData['username']}"
        os.makedirs(base_dir, exist_ok=True)

        path = os.path.join(base_dir, "events.csv")

        new_row = pd.DataFrame([{"event": title, "date": date}])

        if os.path.exists(path):
            old = pd.read_csv(path)
            df = pd.concat([old, new_row], ignore_index=True)
        else:
            df = new_row

        df.to_csv(path, index=False)

        return dbc.Alert("✅ Event added successfully", color="success")

    # ---------------- DOWNLOAD SAMPLE EVENTS CSV ----------------
    @app.callback(
        Output("download-sample-events-file", "data"),
        Input("download-sample-events", "n_clicks"),
        prevent_initial_call=True,
    )
    def download_sample_events(n):

        sample_df = pd.DataFrame(
            [
                {"event": "Annual Function", "date": "2026-03-25"},
                {"event": "Sports Day", "date": "2026-04-10"},
            ]
        )

        return dcc.send_data_frame(
            sample_df.to_csv,
            "sample_events.csv",
            index=False,
        )

    @app.callback(
        Output("school-name", "value"),
        Output("school-address", "value"),
        Output("school-pan", "value"),
        Input("session", "data"),
    )
    def load_school_info(SessionData):
    
        if not SessionData:
            raise dash.exceptions.PreventUpdate
    
        base_dir = f"/var/Data/{SessionData['username']}"
        path = os.path.join(base_dir, "school_info.csv")
    
        if not os.path.exists(path):
            return "", "", ""
    
        try:
            df = pd.read_csv(path)
    
            if df.empty:
                return "", "", ""
    
            row = df.iloc[0]
    
            return (
                row.get("school_name", ""),
                row.get("address", ""),
                row.get("pan_number", ""),
            )
    
        except Exception as e:
            print("Error loading school info:", e)
            return "", "", ""
