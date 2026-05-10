import os
import io
import base64
import dash
import pandas as pd
import dash_bootstrap_components as dbc
from dash import ctx, html, dcc, Input, Output, State


# ---- PORTAL EXACT VALUE MAPS ----


STUDENT_CONDUCT_MAP = {
    "Excellent": "1",
    "Very Good": "2",
    "Good": "3",
    "Satisfactory": "4",
    "Not Good": "5",
}
TC_REASON_MAP = {
    "Reasons for studying elsewhere": "2",
    "Reasons for higher studies": "5",
    "Due to lack of faculty in the school": "6",
    "Distance of school from residence": "7",
    "Due to persistent absence": "8",
    "Transfer of parents": "9",
    "Disciplinary reasons": "10",
    "Due to lack of qualifications": "13",
    "Due to persistent absence after promotion": "14",
}
TC_EXPECTED_COLUMNS = [
    "tc_number",
    "dob",
    "first_admission_class",
    "total_working_days",
    "attendance_days",
    "test_result",
    "fail_count",
    "result_date",
    "tc_reason",
    "student_conduct",
    "issued_by",
    "issued_at",
]
TC_REASON_MAP_REVERSE = {
    "reasons for studying elsewhere": 2,
    "reasons for higher studies": 5,
    "due to lack of faculty in the school": 6,
    "distance of school from residence": 7,
    "due to persistent absence": 8,
    "transfer of parents": 9,
    "disciplinary reasons": 10,
    "due to lack of qualifications": 13,
    "due to persistent absence after promotion": 14,
}
STUDENT_CONDUCT_MAP_REVERSE = {
    "excellent": 1,
    "very good": 2,
    "good": 3,
    "satisfactory": 4,
    "not good": 5,
}


def load_class_mapping(username):
    file_path = f"/var/Data/{username}/fee_structure_static.csv"

    if not os.path.exists(file_path):
        return {}

    df = pd.read_csv(file_path)

    mapping = {}

    for _, row in df.iterrows():
        key = str(row["standard"]).strip().lower()
        value = int(row["studying_class"])

        # multiple formats support
        mapping[key] = value
        mapping[key.replace("class ", "")] = value
        mapping[str(value)] = value

    return mapping


# ==================================================
# LAYOUT
# ==================================================
def get_upload_content(SessionData):
    return dbc.Card(
        dbc.CardBody(
            [
                html.H5("Upload Data", style={"color": "#1B5E20", "fontWeight": "600"}),
                html.Hr(),
                # ============ STUDENT UPLOAD ============
                html.H6("Student Log Upload", style={"color": "#388E3C"}),
                dbc.Row(
                    [
                        dbc.Col(
                            dcc.Upload(
                                id="upload-student-file",
                                children=dbc.Button(
                                    "Upload Student CSV / Excel",
                                    color="success",
                                    className="w-100",
                                ),
                                multiple=False,
                            ),
                            md=4,
                        ),
                       dbc.Col(
    [
        # 🔴 STEP 1: separate button (click detect hoga)
        dbc.Button(
            "Overwrite Student Data",
            id="overwrite-btn",
            color="danger",
            className="w-100",
        ),

        # 📂 STEP 2: upload (hidden initially)
        dcc.Upload(
            id="upload-student-overwrite",
            children=dbc.Button(
                "Select File",
                color="secondary",
                className="w-100 mt-2",
            ),
            multiple=False,
            style={"display": "none"},   # 👈 hidden initially
        ),

        # 🔐 STEP 3: password input
        dbc.Input(
            id="overwrite-password",
            type="password",
            placeholder="Enter Admin Password",
            className="mt-2",
            style={"display": "none"},  # 👈 hidden initially
        ),
    ],
    md=4,
),
                        dbc.Col(
                            dbc.Button(
                                "Download Sample Student CSV",
                                id="download-student-sample",
                                color="secondary",
                                outline=True,
                                n_clicks=0,
                                className="w-100",
                            ),
                            md=4,
                        ),
                    ],
                    className="mb-3 g-2",  # spacing fix
                ),
                html.Div(id="student-upload-status"),
                html.Hr(),
                # ============ FEES UPLOAD ============
                html.H6("Fees Ledger Upload", style={"color": "#388E3C"}),
                dbc.Row(
                    [
                        dbc.Col(
                            dcc.Upload(
                                id="upload-fees-file",
                                children=dbc.Button(
                                    "Upload Fees CSV / Excel", color="success"
                                ),
                                multiple=False,
                            ),
                            md=4,
                        ),
                        dbc.Col(
                            dbc.Button(
                                "Download Sample Fees CSV",
                                id="download-fees-sample",
                                color="secondary",
                                outline=True,
                                n_clicks=0,
                            ),
                            md=4,
                        ),
                    ],
                    className="mb-3",
                ),
                html.Div(id="fees-upload-status"),
                html.Hr(),
                # ============ TC UPLOAD ============
                html.H6("TC Ledger Upload", style={"color": "#388E3C"}),
                dbc.Row(
                    [
                        dbc.Col(
                            dcc.Upload(
                                id="upload-tc-file",
                                children=dbc.Button(
                                    "Upload TC CSV / Excel", color="success"
                                ),
                                multiple=False,
                            ),
                            md=4,
                        ),
                        dbc.Col(
                            dbc.Button(
                                "Download Sample TC CSV",
                                id="download-tc-sample",
                                color="secondary",
                                outline=True,
                                n_clicks=0,
                            ),
                            md=4,
                        ),
                    ],
                    className="mb-3",
                ),
                html.Div(id="tc-upload-status"),
                # shared downloader
                dcc.Download(id="download-sample-file"),
                dcc.Download(id="download-tc-sample-file"),
            ]
        ),
        className="shadow-sm",
    )


EXPECTED_COLUMNS = [
    "student_id",
    "account_name",
    "aadhaar",
    "student_name",
    "father_name",
    "mother_name",
    "dob",
    "gender",
    "caste_category",
    "religion",
    "mother_tongue",
    "jan_aadhaar",
    "rural_urban",
    "habitation",
    "admission_date",
    "current_academic_year",
    "admission_no",
    "monthly_fee_concession",
    "bpl",
    "disadvantaged_group",
    "is_RTE",
    "studying_class",
    "previous_class",
    "previous_year_status",
    "previous_year_days",
    "medium",
    "disability_type",
    "cwsn_facility",
    "uniform_sets",
    "textbook_set",
    "transport_facility",
    "bicycle_facility",
    "escort_facility",
    "midday_meal",
    "hostel_facility",
    "special_training",
    "homeless_status",
    "appeared_last_exam",
    "passed_last_exam",
    "last_exam_percentage",
    "stream",
    "trade",
    "iron_tablets",
    "deworming_tablets",
    "vitamin_a",
    "mobile",
    "email",
    "extracurricular_activities",
    "created_at",
]


# ==================================================
# CALLBACKS
# ==================================================
def register_callbacks(app):

    # ==================================================
    # STUDENT UPLOAD
    # ==================================================
    @app.callback(
        Output("student-upload-status", "children"),
        Output("upload-student-file", "contents"),  # reset upload
        Input("upload-student-file", "contents"),
        State("upload-student-file", "filename"),
        State("session", "data"),
        prevent_initial_call=True,
    )
    def upload_student(contents, filename, SessionData):

        if not contents or not filename:
            raise dash.exceptions.PreventUpdate

        try:
            decoded = base64.b64decode(contents.split(",")[1])
            base_path = f"/var/Data/{SessionData['username']}"
            os.makedirs(base_path, exist_ok=True)

            # ------------------------------
            # READ FILE
            # ------------------------------
            if filename.lower().endswith(".csv"):
                df = pd.read_csv(io.StringIO(decoded.decode("utf-8")))
            elif filename.lower().endswith(".xlsx"):
                df = pd.read_excel(io.BytesIO(decoded))

            else:
                return dbc.Alert("❌ Only CSV or Excel allowed", color="danger"), None

            df = df.loc[:, ~df.columns.str.contains("^Unnamed")]

            df.columns = df.columns.str.strip()

            if "student_id" in df.columns:
                df = df[df["student_id"].astype(str).str.lower() != "student_id"]

            if "student_id" in df.columns:
                df = df[
                    df["student_id"].astype(str).str.strip().ne("")
                    & df["student_id"].astype(str).str.strip().ne("0")
                ]

            # ------------------------------
            # 🧹 CLEAN RAW DATA
            # ------------------------------

            if "email" in df.columns:
                df["email"] = df["email"].str.lower()

            # 1️⃣ remove auto columns like Unnamed: 11

            for col in df.columns:
                if df[col].dtype == object:
                    df[col] = df[col].str.strip()

            # 2️⃣ strip column names (extra spaces)

            # 3️⃣ add missing expected columns
            for col in EXPECTED_COLUMNS:
                if col not in df.columns:
                    df[col] = ""

            df = df[EXPECTED_COLUMNS]
            # 4️⃣ drop extra columns (jo system me nahi chahiye)

            #
            # ==================================================

            def normalize_date(val):
                if pd.isna(val) or val == "":
                    return ""
                val = str(val).strip().replace("-", "/")
                try:
                    return pd.to_datetime(val, errors="coerce").strftime("%d/%m/%Y")
                except Exception:
                    return ""

            for col in ["dob", "admission_date", "current_academic_year", "created_at"]:
                if col in df.columns:
                    df[col] = df[col].apply(normalize_date)

            # 🔐 COMMON NORMALIZER (DO NOT TOUCH)
            # ==================================================
            def map_value(val, mapping):
                if pd.isna(val) or val == "":
                    return 0
                try:
                    return int(float(val))  # handles -1, 0, 1, "2"
                except ValueError:
                    key = str(val).strip().lower()
                    return mapping.get(key, 0)

            # ==================================================
            # 🧩 STARTER MAPPINGS
            # ==================================================

            GENDER_MAP = {
                "boy": 1,
                "male": 1,
                "m": 1,
                "girl": 2,
                "female": 2,
                "f": 2,
            }

            RURAL_URBAN_MAP = {
                "rural": 1,
                "urban": 2,
            }

            RELIGION_MAP = {
                "hindu": 0,
                "muslim": 5,
                "christian": 6,
                "sikh": 7,
                "buddhist": 8,
                "jain": 10,
                "other": 11,
            }

            MOTHER_TONGUE_MAP = {
                "hindi": 4,
                "english": 19,
                "rajasthani": 56,
                "urdu": 18,
                "sanskrit": 14,
                "sindhi": 15,
                "punjabi": 13,
                "gujarati": 3,
                "bengali": 2,
                "kannada": 5,
                "kashmiri": 6,
                "konkani": 7,
                "malayalam": 8,
                "manipuri": 9,
                "marathi": 10,
                "nepali": 11,
                "oriya": 12,
                "tamil": 16,
                "telugu": 17,
                "assamese": 1,
                "bodo": 20,
                "dogri": 22,
                "khasi": 23,
                "garo": 24,
                "mizo": 25,
                "maithili": 51,
                "french": 29,
                "german": 46,
                "spanish": 59,
                "other": 99,
            }

            CASTE_MAP = {
                "gen": 1,
                "general": 1,
                "sc": 2,
                "st": 3,
                "obc": 4,
            }

            YES_NO_MAP = {
                "yes": 1,
                "y": 1,
                "no": 2,
                "n": 2,
                "na": 0,
                "n/a": 0,
                "not applicable": 0,
            }

            MEDIUM_MAP = {
                "english": 1,
                "hindi": 2,
                "rajasthani": 3,
                "other": 9,
            }
            TRADE_MAP = {
                "agriculture": 1,
                "automotive": 2,
                "construction": 3,
                "electronics": 4,
                "it": 5,
                "ites": 5,
                "other": 9,
            }

            STREAM_MAP = {
                "science": 1,
                "commerce": 2,
                "arts": 3,
            }

            CWSN_MAP = {
                "none": 0,
                "braille books": 1,
                "braille kit": 2,
                "low vision kit": 3,
                "hearing aid": 4,
                "braces": 5,
                "crutches": 6,
                "wheelchair": 7,
                "tricycle": 8,
                "caliper": 9,
                "others": 10,
            }

            DISABILITY_MAP = {
                "none": 0,
                "blindness": 1,
                "low vision": 2,
                "hearing impairment": 3,
                "speech impairment": 4,
                "locomotor disability": 5,
                "cerebral palsy": 6,
                "autism": 7,
                "multiple disabilities": 8,
                "mental illness": 12,
                "acid attack victim": 13,
                "dwarfism": 14,
                "muscular dystrophy": 15,
                "leprosy cured persons": 16,
                "parkinsons disease": 17,
                "sickle cell disease": 18,
                "thalassemia": 19,
                "chronic neurological conditions": 20,
                "hemophilia": 21,
                "multiple sclerosis": 22,
            }

            PREV_YEAR_STATUS_MAP = {
                "not applicable": 0,
                "same school": 1,
                "other school": 2,
                "not studied": 3,
            }
            CLASS_MAP = load_class_mapping(SessionData["username"])
            if not CLASS_MAP:
                return (
                    dbc.Alert(
                        "❌ Fee structure file not found. Upload it first.",
                        color="danger",
                    ),
                    None,
                )

            # ==================================================
            # 🔗 COLUMN → MAPPING LINK
            # ==================================================
            COLUMN_MAPPINGS = {
                "gender": GENDER_MAP,
                "caste_category": CASTE_MAP,
                "religion": RELIGION_MAP,
                "mother_tongue": MOTHER_TONGUE_MAP,
                "rural_urban": RURAL_URBAN_MAP,
                "bpl": YES_NO_MAP,
                "disadvantaged_group": YES_NO_MAP,
                "is_RTE": YES_NO_MAP,
                "studying_class": CLASS_MAP,
                "previous_class": CLASS_MAP,
                "previous_year_status": PREV_YEAR_STATUS_MAP,
                "medium": MEDIUM_MAP,
                "disability_type": DISABILITY_MAP,
                "cwsn_facility": CWSN_MAP,
                "textbook_set": YES_NO_MAP,
                "transport_facility": YES_NO_MAP,
                "bicycle_facility": YES_NO_MAP,
                "escort_facility": YES_NO_MAP,
                "midday_meal": YES_NO_MAP,
                "hostel_facility": YES_NO_MAP,
                "special_training": YES_NO_MAP,
                "homeless_status": YES_NO_MAP,
                "iron_tablets": YES_NO_MAP,
                "deworming_tablets": YES_NO_MAP,
                "vitamin_a": YES_NO_MAP,
                "appeared_last_exam": YES_NO_MAP,
                "passed_last_exam": YES_NO_MAP,
                "stream": STREAM_MAP,
                "trade": TRADE_MAP,
            }
            # ==================================================
            # 🔄 APPLY MAPPINGS
            # ==================================================
            for col, mapping in COLUMN_MAPPINGS.items():
                if col in df.columns:
                    df[col] = df[col].apply(lambda x: map_value(x, mapping))

            # after APPLY MAPPINGS
            df["previous_year_days"] = df["previous_year_days"].clip(0, 365)
            df.loc[df["studying_class"] < 11, "stream"] = 0
            df.loc[df["studying_class"] < 9, "trade"] = 0

            # ==================================================
            # 💾 SAVE FINAL
            # ==================================================
            target = f"{base_path}/student_log.csv"
            df.to_csv(target, mode="a", header=not os.path.exists(target), index=False)

            msg = dbc.Alert(
                [
                    html.B("✅ Student upload successful"),
                    html.Br(),
                    "All text values converted to system codes",
                    html.Br(),
                    f"📊 Rows uploaded: {len(df)}",
                ],
                color="success",
                dismissable=True,
            )

            return msg, None

        except Exception as e:
            return dbc.Alert(f"❌ Error: {e}", color="danger", dismissable=True), None

    # ==================================================
    # FEES UPLOAD
    # ==================================================
    @app.callback(
        Output("fees-upload-status", "children"),
        Output("upload-fees-file", "contents"),  # 🔑 reset upload
        Input("upload-fees-file", "contents"),
        State("upload-fees-file", "filename"),
        State("session", "data"),
        prevent_initial_call=True,
    )
    def upload_fees(contents, filename, SessionData):

        if not contents or not filename:
            raise dash.exceptions.PreventUpdate

        try:
            decoded = base64.b64decode(contents.split(",")[1])
            base_path = f"/var/Data/{SessionData['username']}"
            os.makedirs(base_path, exist_ok=True)

            # ---- read file
            if filename.lower().endswith(".csv"):
                df = pd.read_csv(io.StringIO(decoded.decode("utf-8")))
            elif filename.lower().endswith(".xlsx"):
                df = pd.read_excel(io.BytesIO(decoded))

            else:
                return (
                    dbc.Alert("❌ Only CSV or Excel allowed", color="danger"),
                    None,
                )

            # ---- save
            target = f"{base_path}/fees_ledger.csv"
            df.to_csv(
                target,
                mode="a",
                header=not os.path.exists(target),
                index=False,
            )

            # ---- success message
            msg = dbc.Alert(
                [
                    html.B("✅ Fees upload successful"),
                    html.Br(),
                    f"📄 File: {filename}",
                    html.Br(),
                    f"📊 Rows uploaded: {len(df)}",
                ],
                color="success",
                dismissable=True,
            )

            return msg, None

        except Exception as e:
            return (
                dbc.Alert(f"❌ Error: {e}", color="danger", dismissable=True),
                None,
            )

    # ==================================================
    # SAMPLE CSV DOWNLOAD
    # ==================================================

    @app.callback(
        Output("tc-upload-status", "children"),
        Output("upload-tc-file", "contents"),
        Input("upload-tc-file", "contents"),
        State("upload-tc-file", "filename"),
        State("session", "data"),
        prevent_initial_call=True,
    )
    def upload_tc(contents, filename, SessionData):

        if not contents or not filename:
            raise dash.exceptions.PreventUpdate

        try:
            decoded = base64.b64decode(contents.split(",")[1])
            base_path = f"/var/Data/{SessionData['username']}"
            os.makedirs(base_path, exist_ok=True)

            # ---------- READ FILE ----------
            if filename.lower().endswith(".csv"):
                df = pd.read_csv(io.StringIO(decoded.decode("utf-8")))
            elif filename.lower().endswith(".xlsx"):
                df = pd.read_excel(io.BytesIO(decoded))
            else:
                return dbc.Alert("❌ Only CSV / Excel allowed", color="danger"), None

            # ---------- CLEAN ----------
            df = df.loc[:, ~df.columns.str.contains("^Unnamed")]
            df.columns = df.columns.str.strip()

            for col in df.columns:
                if df[col].dtype == object:
                    df[col] = df[col].astype(str).str.strip()

            # ---------- ADD MISSING COLUMNS ----------
            for col in TC_EXPECTED_COLUMNS:
                if col not in df.columns:
                    df[col] = ""

            df = df[TC_EXPECTED_COLUMNS]

            def normalize_date(val):
                if pd.isna(val) or val == "":
                    return ""
                d = pd.to_datetime(val, errors="coerce")
                if pd.isna(d):
                    return ""
                return d.strftime("%d/%m/%Y")

            for col in ["dob", "result_date", "issued_at"]:
                df[col] = df[col].apply(normalize_date)

            # ---------- CODE CONVERSION ----------
            df["tc_reason"] = (
                df["tc_reason"]
                .astype(str)
                .str.lower()
                .map(TC_REASON_MAP_REVERSE)
                .fillna(0)
                .astype(int)
            )

            df["student_conduct"] = (
                df["student_conduct"]
                .astype(str)
                .str.lower()
                .map(STUDENT_CONDUCT_MAP_REVERSE)
                .fillna(0)
                .astype(int)
            )

            Class_MAP = load_class_mapping(SessionData["username"])
            df["first_admission_class"] = (
                df["first_admission_class"]
                .astype(str)
                .str.lower()
                .str.strip()
                .map(Class_MAP)
                .fillna(0)
                .astype(int)
            )

            # ---------- SAVE ----------
            target = f"{base_path}/tc_register.csv"
            df.to_csv(target, mode="a", header=not os.path.exists(target), index=False)

            return (
                dbc.Alert(
                    f"✅ TC ledger uploaded & coded successfully | Rows: {len(df)}",
                    color="success",
                    dismissable=True,
                ),
                None,
            )

        except Exception as e:
            return dbc.Alert(f"❌ Error: {e}", color="danger"), None

    @app.callback(
        Output("download-tc-sample-file", "data"),
        Input("download-tc-sample", "n_clicks"),
        prevent_initial_call=True,
    )
    def download_tc_sample(n):

        df = pd.DataFrame(
            [
                {
                    "tc_number": "TC_001",
                    "dob": "01/06/2017",
                    "first_admission_class": "First",
                    "total_working_days": 220,
                    "attendance_days": 198,
                    "test_result": 57,
                    "fail_count": 0,
                    "result_date": "31-03-2025",
                    "tc_reason": "Transfer of parents",
                    "student_conduct": "Very Good",
                    "issued_by": "admin",
                    "issued_at": "12-02-2026",
                },
                {
                    "tc_number": "TC_002",
                    "dob": "15-08-2016",
                    "first_admission_class": "Second",
                    "total_working_days": 210,
                    "attendance_days": 150,
                    "test_result": 56,
                    "fail_count": 1,
                    "result_date": "31-03-2025",
                    "tc_reason": "Due to persistent absence",
                    "student_conduct": "Satisfactory",
                    "issued_by": "admin",
                    "issued_at": "12-02-2026",
                },
                {
                    "tc_number": "TC_003",
                    "dob": "10-01-2015",
                    "first_admission_class": "Third",
                    "total_working_days": 230,
                    "attendance_days": 220,
                    "test_result": 40,
                    "fail_count": 0,
                    "result_date": "31-03-2025",
                    "tc_reason": "Reasons for higher studies",
                    "student_conduct": "Excellent",
                    "issued_by": "admin",
                    "issued_at": "12-02-2026",
                },
            ]
        )

        return dcc.send_data_frame(
            df.to_csv,
            "sample_tc_ledger.csv",
            index=False,
        )

    # ==================================================
    # SAMPLE CSV DOWNLOAD
    @app.callback(
        Output("download-sample-file", "data"),
        Input("download-student-sample", "n_clicks"),
        Input("download-fees-sample", "n_clicks"),
        prevent_initial_call=True,
    )
    def download_sample(student_clicks, fees_clicks):

        student_clicks = student_clicks or 0
        fees_clicks = fees_clicks or 0

        if student_clicks > fees_clicks:
            df = pd.DataFrame(
                [
                    {
                        "student_id": "STU_001",
                        "account_name": "Pooja Kumari",
                        "aadhaar": "500511147888",
                        "student_name": "Pooja Kumari",
                        "father_name": "Sanjay Kumar",
                        "mother_name": "Veena Devi",
                        "dob": "19/03/2009",
                        "gender": "girl",
                        "caste_category": "gen",
                        "religion": "hindu",
                        "mother_tongue": "hindi",
                        "jan_aadhaar": "",
                        "rural_urban": "rural",
                        "habitation": "Jaipur",
                        "admission_date": "01/07/2024",
                        "current_academic_year": "01/04/2024",
                        "admission_no": "ADM001",
                        "monthly_fee_concession": "0",
                        "bpl": "no",
                        "disadvantaged_group": "yes",
                        "is_RTE": "yes",
                        "studying_class": "class 8",
                        "previous_class": "class 7",
                        "previous_year_status": "same school",
                        "previous_year_days": 210,
                        "medium": "english",
                        "disability_type": "none",
                        "cwsn_facility": "none",
                        "uniform_sets": 2,
                        "textbook_set": 1,
                        "transport_facility": "none",
                        "bicycle_facility": "none",
                        "escort_facility": "none",
                        "midday_meal": "yes",
                        "hostel_facility": "no",
                        "special_training": "no",
                        "homeless_status": "no",
                        "appeared_last_exam": "yes",
                        "passed_last_exam": "no",
                        "last_exam_percentage": 78.5,
                        "stream": "science",
                        "trade": "",
                        "iron_tablets": "no",
                        "deworming_tablets": "no",
                        "vitamin_a": "no",
                        "mobile": "9844476654",
                        "email": "pooja@gmail.com",
                        "extracurricular_activities": "cricket",
                        "created_at": "2026-01-01T10:00:00",
                    }
                ]
            )

            return dcc.send_data_frame(
                df.to_csv,
                "sample_student_log.csv",
                index=False,
            )

        if fees_clicks > student_clicks:
            df = pd.DataFrame(
                [
                    {
                        "entry_id": "FEES_001",
                        "form_name": "FEES RECEIPT",
                        "ledger_name": "Student Fees",
                        "account_name": "Pooja Kumari/888721/8TH Std.",
                        "ledger_group": "Student Fees / Income",
                        "cash_amount": 500,
                        "bank1_amount": 0,
                        "bank2_amount": 0,
                        "bank3_amount": 0,
                        "bank4_amount": 0,
                        "bank5_amount": 0,
                        "bank6_amount": 0,
                        "bank7_amount": 0,
                        "bank8_amount": 0,
                        "bank9_amount": 0,
                        "bank10_amount": 0,
                        "total_amount": 500,
                        "breakup_cash": "{}",
                        "breakup_bank1": "{}",
                        "breakup_bank2": "{}",
                        "breakup_bank3": "{}",
                        "breakup_bank4": "{}",
                        "breakup_bank5": "{}",
                        "breakup_bank6": "{}",
                        "breakup_bank7": "{}",
                        "breakup_bank8": "{}",
                        "breakup_bank9": "{}",
                        "breakup_bank10": "{}",
                        "transaction_date": "01-07-2024",
                        "details": "Fee receipt",
                        "created_at": "2024-07-01T10:30:00",
                    }
                ]
            )

            return dcc.send_data_frame(
                df.to_csv,
                "sample_fees_ledger.csv",
                index=False,
            )

        raise dash.exceptions.PreventUpdate

    @app.callback(
    Output("student-upload-status", "children",allow_duplicate=True),
    Output("upload-student-overwrite", "contents"),
    Output("overwrite-password", "value"),
    Output("overwrite-password", "style"),
    Output("upload-student-overwrite", "style"),

    Input("overwrite-btn", "n_clicks"),              # 👈 button click
    Input("upload-student-overwrite", "contents"),   # 👈 file upload

    State("upload-student-overwrite", "filename"),
    State("overwrite-password", "value"),
    State("session", "data"),

    prevent_initial_call=True,
)
    

    def handle_overwrite(btn_click, contents, filename, password, SessionData):

     trigger = ctx.triggered_id

     # STEP 1: show UI
     if trigger == "overwrite-btn":
        return (
            None,
            None,
            "",
            {"display": "block"},
            {"display": "block"},
        )

    # STEP 2: file upload
     if trigger == "upload-student-overwrite":

        if not contents:
            return (
                dbc.Alert("⚠️ Upload file first", color="warning"),
                None,
                "",
                {"display": "block"},
                {"display": "block"},
            )

        if not password:
            return (
                dbc.Alert("⚠️ Enter password", color="warning"),
                None,
                "",
                {"display": "block"},
                {"display": "block"},
            )

        MASTER_ADMIN_PASSWORD = "admin123"

        if password != MASTER_ADMIN_PASSWORD:
            return (
                dbc.Alert("❌ Invalid password", color="danger"),
                None,
                "",
                {"display": "block"},
                {"display": "block"},
            )

        try:
            decoded = base64.b64decode(contents.split(",")[1])
            base_path = f"/var/Data/{SessionData['username']}"
            os.makedirs(base_path, exist_ok=True)

            if filename.lower().endswith(".csv"):
                df = pd.read_csv(io.StringIO(decoded.decode("utf-8")))
            elif filename.lower().endswith(".xlsx"):
                df = pd.read_excel(io.BytesIO(decoded))
            else:
                return (
                    dbc.Alert("❌ Only CSV/Excel allowed", color="danger"),
                    None,
                    "",
                    {"display": "block"},
                    {"display": "block"},
                )

            for col in EXPECTED_COLUMNS:
                if col not in df.columns:
                    df[col] = ""

            df = df[EXPECTED_COLUMNS]

            target = f"{base_path}/student_log.csv"
            df.to_csv(target, mode="w", index=False)

            return (
                dbc.Alert(f"🔥 Overwritten | Rows: {len(df)}", color="warning"),
                None,
                "",
                {"display": "none"},
                {"display": "none"},
            )

        except Exception as e:
            return (
                dbc.Alert(f"❌ Error: {e}", color="danger"),
                None,
                "",
                {"display": "block"},
                {"display": "block"},
            )

     raise dash.exceptions.PreventUpdate
