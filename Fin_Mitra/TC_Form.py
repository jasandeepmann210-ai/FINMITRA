from dash import html
import dash_bootstrap_components as dbc
from dash import Input, Output, State, callback, no_update
from datetime import datetime
import pandas as pd
import os
import dash_core_components as dcc


TC_FIELD_MAP = {
    "tc_number": "ctl00_ContentPlaceHolder1_txtTCNumber",  # (portal hidden / auto)
    "dob": "ctl00_ContentPlaceHolder1_txtDOB_Edit",
    "first_admission_class": "ctl00_ContentPlaceHolder1_ddlentryclass_edit",
    "total_working_days": "ctl00_ContentPlaceHolder1_txtMaxAttendance",
    "attendance_days": "ctl00_ContentPlaceHolder1_txtMinAttendance",
    "test_result": "ctl00_ContentPlaceHolder1_ddlResultFinal",
    "fail_count": "ctl00_ContentPlaceHolder1_txtFail",
    "result_date": "ctl00_ContentPlaceHolder1_txtResultDate",
    "tc_reason": "ctl00_ContentPlaceHolder1_ddlTcReason",
    "student_conduct": "ctl00_ContentPlaceHolder1_ddlCharacter",
    "issued_by": "ctl00_ContentPlaceHolder1_txtIssuedBy",  # backend / session
    "issued_at": "ctl00_ContentPlaceHolder1_txtIssuedDate",  # backend
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

# ---- PORTAL EXACT VALUE MAPS ----



STUDENT_CONDUCT_MAP = {
    "Excellent": "1",
    "Very Good": "2",
    "Good": "3",
    "Satisfactory": "4",
    "Not Good": "5",
}

def load_class_options(username):
    file_path = f"/var/Data/{username}/fee_structure_static.csv"

    if not os.path.exists(file_path):
        return []

    df = pd.read_csv(file_path)

    # dropdown ke liye format
    return [
        {"label": row["standard"], "value": str(row["studying_class"])}
        for _, row in df.iterrows()
    ]


def get_tc_form_content(SessionData):
    return dbc.Card(
        [
            dbc.CardHeader(
                "Information required for issuing student's TC",
                style={
                    "backgroundColor": "#086A87",
                    "color": "white",
                    "fontWeight": "600",
                },
            ),
            dbc.CardBody(
                [
                    # DOB + First Admission Class
                    dbc.Row(
                        [
                            dbc.Col(
                                [
                                    dbc.Label("Date of Birth * (Editable)"),
                                    dbc.Input(id="tc-dob", type="date"),
                                ],
                                md=6,
                            ),
                            dbc.Col(
                                [
                                    dbc.Label("First Admission Class in School *"),
                                    dbc.Select(
                                        id="tc-first-class",
                                        options=load_class_options(SessionData["username"]),
                                    ),
                                ],
                                md=6,
                            ),
                        ],
                        className="mb-3",
                    ),
                    # Attendance
                    dbc.Row(
                        [
                            dbc.Col(
                                [
                                    dbc.Label("Total working days (2025-26) *"),
                                    dbc.Input(
                                        id="tc-total-days",
                                        type="number",
                                        min=0,
                                        max=366,
                                    ),
                                ],
                                md=6,
                            ),
                            dbc.Col(
                                [
                                    dbc.Label(
                                        "Student attendance working days (2025-26) *"
                                    ),
                                    dbc.Input(
                                        id="tc-attended-days",
                                        type="number",
                                        min=0,
                                        max=366,
                                    ),
                                ],
                                md=6,
                            ),
                        ],
                        className="mb-3",
                    ),
                    # Result + Fail count
                    dbc.Row(
                        [
                            dbc.Col(
                                [
                                    dbc.Label("Test result *"),
                                    dbc.Input(id="tc-result", type="text"),
                                ],
                                md=6,
                            ),
                            dbc.Col(
                                [
                                    dbc.Label(
                                        "Failed in examination (number of times) *"
                                    ),
                                    dbc.Input(
                                        id="tc-fail-count",
                                        type="number",
                                        min=0,
                                        max=9,
                                        step=1,
                                    ),
                                ],
                                md=6,
                            ),
                        ],
                        className="mb-3",
                    ),
                    # Result Date
                    dbc.Row(
                        [
                            dbc.Col(
                                [
                                    dbc.Label(
                                        "Date of Examination Result / School Leaving *"
                                    ),
                                    dbc.Input(id="tc-result-date", type="date"),
                                ],
                                md=6,
                            ),
                        ],
                        className="mb-3",
                    ),
                    # Reason + Conduct (✅ PORTAL NUMERIC CODES)
                    dbc.Row(
                        [
                            dbc.Col(
                                [
                                    dbc.Label("Reason for issuing TC *"),
                                    dbc.Select(
                                        id="tc-reason",
                                        options=[
                                            {"label": k, "value": v}
                                            for k, v in TC_REASON_MAP.items()
                                        ],
                                    ),
                                ],
                                md=6,
                            ),
                            dbc.Col(
                                [
                                    dbc.Label("Student Conduct *"),
                                    dbc.Select(
                                        id="tc-conduct",
                                        options=[
                                            {"label": k, "value": v}
                                            for k, v in STUDENT_CONDUCT_MAP.items()
                                        ],
                                    ),
                                ],
                                md=6,
                            ),
                        ],
                        className="mb-4",
                    ),
                    # Buttons
                    dbc.Row(
                        [
                            dbc.Col(
                                dbc.Button(
                                    "Issue TC",
                                    id="issue-tc-btn",
                                    color="primary",
                                    className="me-2",
                                ),
                                width="auto",
                            ),
                            dbc.Col(
                                dbc.Button(
                                    "Download TC Ledger",
                                    id="download-tc-btn",
                                    color="secondary",
                                    outline=True,
                                ),
                                width="auto",
                            ),
                            dbc.Col(dcc.Download(id="download-tc-ledger")),
                            dbc.Col(html.Div(id="tc-msg"), md=True),
                        ],
                        justify="center",
                    ),
                ]
            ),
        ],
        className="mt-3",
    )


def register_callbacks(app):

    @app.callback(
        Output("tc-msg", "children"),
        Input("issue-tc-btn", "n_clicks"),
        State("tc-dob", "value"),
        State("tc-first-class", "value"),
        State("tc-total-days", "value"),
        State("tc-attended-days", "value"),
        State("tc-result", "value"),
        State("tc-fail-count", "value"),
        State("tc-result-date", "value"),
        State("tc-reason", "value"),
        State("tc-conduct", "value"),
        State("session", "data"),  # 🔑 IMPORTANT
        prevent_initial_call=True,
    )
    def issue_tc(
        n,
        dob,
        first_class,
        total_days,
        attended_days,
        result,
        fail_count,
        result_date,
        reason,
        conduct,
        SessionData,
    ):
        # -------------------------
        # BASIC VALIDATION
        # -------------------------
        required_fields = [
            dob,
            first_class,
            total_days,
            attended_days,
            result,
            fail_count,
            result_date,
            reason,
            conduct,
        ]

        if any(v in (None, "", []) for v in required_fields):
            return dbc.Alert("❌ Please fill all required fields", color="danger")

        if attended_days > total_days:
            return dbc.Alert(
                "❌ Attendance days cannot be greater than total working days",
                color="danger",
            )

        if not SessionData or "username" not in SessionData:
            return dbc.Alert("❌ Session expired. Please login again.", color="danger")

        # -------------------------
        # DATE FORMAT (same style as student_log)
        # -------------------------
        def fmt_date(d):
            if not d:
                return ""

            try:
                # Dash date input always gives YYYY-MM-DD
                return datetime.strptime(d, "%Y-%m-%d").strftime("%d/%m/%Y")
            except ValueError:
                return ""

        # -------------------------
        # TC ROW (CSV STYLE)
        # -------------------------
        tc_row = {
            "tc_number": f"TC_{datetime.now().strftime('%Y%m%d%H%M%S%f')}",
            "dob": fmt_date(dob),  # ✅ DD/MM/YYYY
            "first_admission_class": first_class,
            "total_working_days": total_days,
            "attendance_days": attended_days,
            "test_result": result,
            "fail_count": fail_count,
            "result_date": fmt_date(result_date),  # ✅ DD/MM/YYYY
            "tc_reason": reason,
            "student_conduct": conduct,
            "issued_by": SessionData["username"],
            "issued_at": datetime.now().strftime("%d/%m/%Y"),  # ✅ SAME FORMAT
        }

        # -------------------------
        # FILE PATH (SAME FAMILY)
        # -------------------------
        base_path = f"/var/Data/{SessionData['username']}"
        os.makedirs(base_path, exist_ok=True)

        tc_path = os.path.join(base_path, "tc_register.csv")

        try:
            pd.DataFrame([tc_row]).to_csv(
                tc_path,
                mode="a",
                index=False,
                header=not os.path.exists(tc_path),
            )

            return dbc.Alert(
                "✅ TC issued & saved successfully",
                color="success",
                dismissable=True,
            )

        except Exception as e:
            return dbc.Alert(
                f"❌ Error saving TC: {str(e)}",
                color="danger",
                dismissable=True,
            )

    @callback(
        Output("download-tc-ledger", "data"),
        Input("download-tc-btn", "n_clicks"),
        State("session", "data"),
        prevent_initial_call=True,
    )
    def download_tc_ledger(n, SessionData):
        if not SessionData or "username" not in SessionData:
            return no_update

        tc_path = f"/var/Data/{SessionData['username']}/tc_register.csv"

        if not os.path.exists(tc_path):
            return no_update

        return dcc.send_file(tc_path)
