import dash
from dash import html, dcc, Input, Output, State
import dash_bootstrap_components as dbc
import pandas as pd
import os
from datetime import datetime
from pandas.tseries.offsets import MonthEnd

# -----------------------------------
# Layout
# -----------------------------------

def format_date(date_val):
    if date_val is None or str(date_val).strip() == "":
        return None

    try:
        # Handles DatePicker format directly
        return datetime.strptime(str(date_val)[:10], "%Y-%m-%d").strftime("%d/%m/%Y")
    except:
        pass

    for fmt in ("%d-%m-%Y", "%d/%m/%Y"):
        try:
            return datetime.strptime(str(date_val)[:10], fmt).strftime("%d/%m/%Y")
        except:
            continue

    return None
    
def month_end(date_val):
    """Convert date to nearest month end"""
    if pd.isna(date_val):
        return None
    dt = pd.to_datetime(date_val, errors="coerce")
    if pd.isna(dt):
        return None
    return dt + MonthEnd(0)


def months_between(start, end):
    """Floor months between two dates"""
    if not start or not end:
        return 0
    if end < start:
        return 0
    return (end.year - start.year) * 12 + (end.month - start.month)


def parse_account_name(val):
    """
    Input:
        Viru/1235/9TH Std.
    Output:
        admission_no = 1235
        studying_class = 9
    """
    if pd.isna(val):
        return None, None

    parts = str(val).split("/")

    admission_no = parts[1].strip() if len(parts) > 1 else None

    studying_class = None
    if len(parts) > 2:
        match = re.search(r"\d+", parts[2])
        if match:
            studying_class = match.group()

    return admission_no, studying_class


def build_fee_due(SessionData):

    base = f"/var/Data/{SessionData['username']}"

    # ---------------------------
    # LOAD DATA
    # ---------------------------
    students = pd.read_csv(f"{base}/student_log.csv")
    ledger = pd.read_csv(f"{base}/fees_ledger.csv")
    fee_struct = pd.read_csv(f"{base}/fee_structure_static.csv")

    # ---------------------------
    # EXTRACT ADMISSION NUMBER (LEDGER)
    # ---------------------------
    ledger["admission_no"] = (
        ledger["account_name"].astype(str).str.split("/").str[1]
    )

    # ---------------------------
    # NORMALIZE TYPES
    # ---------------------------
    ledger["admission_no"] = ledger["admission_no"].astype(str)
    students["admission_no"] = students["admission_no"].astype(str)
    students["studying_class"] = students["studying_class"].astype(str)

    fee_struct["studying_class"] = fee_struct["studying_class"].astype(str)
    fee_struct["monthly_fee"] = pd.to_numeric(
        fee_struct["monthly_fee"], errors="coerce"
    ).fillna(0)

    ledger["total_amount"] = pd.to_numeric(
        ledger["total_amount"], errors="coerce"
    ).fillna(0)

    # ---------------------------
    # AGGREGATE PAID AMOUNT
    # ---------------------------
    paid_df = (
        ledger.groupby(["admission_no"], as_index=False)
        .agg({"total_amount": "sum"})
        .rename(columns={"total_amount": "amount_paid"})
    )

    # ---------------------------
    # MERGE
    # ---------------------------
    merged = students.merge(fee_struct, on="studying_class", how="left").merge(
        paid_df, on="admission_no", how="left"
    )

    merged["amount_paid"] = merged["amount_paid"].fillna(0)

    # ---------------------------
    # TIME LOGIC
    # ---------------------------
    today = pd.Timestamp.today().normalize()

    # Ensure column exists
    if "current_academic_year" not in merged.columns:
        merged["current_academic_year"] = pd.NaT

    # Parse dates
    merged["current_academic_year"] = pd.to_datetime(
        merged["current_academic_year"]
        .astype(str)
        .str.replace("-", "/", regex=False),
        format="%d/%m/%Y",
        errors="coerce"
    )

    merged["admission_date"] = pd.to_datetime(
        merged["admission_date"]
        .astype(str)
        .str.replace("-", "/", regex=False),
        format="%d/%m/%Y",
        errors="coerce"
    )

    # ---------------------------
    # PICK DATE CLOSER TO TODAY
    # ---------------------------
    def pick_closer_date(row):
        d1 = row["current_academic_year"]
        d2 = row["admission_date"]

        if pd.isna(d1):
            return d2
        if pd.isna(d2):
            return d1

        return d1 if abs((today - d1).days) < abs((today - d2).days) else d2

    merged["effective_date"] = merged.apply(pick_closer_date, axis=1)

    # ---------------------------
    # MONTH CALCULATION
    # ---------------------------
    merged["admission_month_end"] = merged["effective_date"].apply(month_end)

    merged["months_elapsed"] = (
        merged["admission_month_end"]
        .apply(lambda d: months_between(d, today))
        .clip(lower=0)
    )

    # ---------------------------
    # FEE CALCULATION
    # ---------------------------
    # merged["expected_fee"] = merged["months_elapsed"] * merged["monthly_fee"]
    if "monthly_fee_concession" not in merged.columns:
        merged["monthly_fee_concession"] = 0
    
    merged["monthly_fee_concession"] = pd.to_numeric(
        merged["monthly_fee_concession"], errors="coerce"
    ).fillna(0)
    
    # Prevent concession > fee
    merged["monthly_fee_concession"] = merged[
        ["monthly_fee_concession", "monthly_fee"]
    ].min(axis=1)
    
    # Apply concession
    merged["effective_monthly_fee"] = (
        merged["monthly_fee"] - merged["monthly_fee_concession"]
    ).clip(lower=0)
    
    # Final expected fee
    merged["expected_fee"] = merged["months_elapsed"] * merged["effective_monthly_fee"]
    
    merged["net_balance"] = merged["amount_paid"] - merged["expected_fee"]

    merged["fee_due"] = merged["net_balance"].apply(lambda x: abs(x) if x < 0 else 0)
    merged["over_paid"] = merged["net_balance"].apply(lambda x: x if x > 0 else 0)

    # due_df = merged[merged["fee_due"] > 0].copy()
    due_df = merged.copy()
    return due_df


def get_promote_layout(SessionData):

    base_path = f"/var/Data/{SessionData['username']}/"
    fee_file = base_path + "fee_structure_static.csv"

    options = []

    if os.path.exists(fee_file):
        df_fee = pd.read_csv(fee_file)

        options = [
            {
                "label": f"{row['standard']}",
                "value": str(row["studying_class"]),
            }
            for _, row in df_fee.iterrows()
        ]

    return dbc.Container(
        [
            html.H4(
                "🚀 Promote Students",
                className="mb-4",
                style={"color": "#1B5E20", "fontWeight": "600"},
            ),

            dbc.Card(
                dbc.CardBody(
                    [
                        dbc.Row(
                            [
                                # FROM CLASS
                                dbc.Col(
                                    [
                                        dbc.Label("Select Current Class"),
                                        dcc.Dropdown(
                                            id="promote-from-class",
                                            options=options,
                                            placeholder="Select class",
                                        ),
                                    ],
                                    md=4,
                                ),

                                # TO CLASS (optional - keep or remove later)
                                dbc.Col(
                                    [
                                        dbc.Label("Promote To Class"),
                                        dcc.Dropdown(
                                            id="promote-to-class",
                                            options=options,
                                            placeholder="Auto or select next class",
                                        ),
                                    ],
                                    md=4,
                                ),

                                # ACADEMIC YEAR
                                dbc.Col(
                                    [
                                        dbc.Label("New Academic Year"),
                                        dcc.DatePickerSingle(
                                            id="promote-academic-year",
                                            display_format="DD/MM/YYYY",
                                            date=pd.Timestamp.today().date(), 
                                            style={"width": "100%"}
                                        )
                                    ],
                                    md=4,
                                ),
                            ],
                            className="mb-3",
                        ),
                        html.Div(id="student-preview-table", className="mt-3"),

                        dbc.Row(
    [
        dbc.Col(
            dbc.Button("👀 Preview", id="preview-btn", color="info", className="w-100"),
            md=4,
        ),
        dbc.Col(
            dbc.Button("🚀 Confirm Promote", id="confirm-btn-promote", color="success", className="w-100"),
            md=4,
        ),
    ]
),

html.Div(id="confirm-box", className="mt-3"),

                        html.Div(id="promote-msg", className="mt-4"),
                    ]
                ),
                className="shadow-sm",
                style={"borderRadius": "10px"},
            ),
        ],
        fluid=True,
    )



# -----------------------------------
# Callbacks
# -----------------------------------

def register_callbacks(app):

    @app.callback(
        Output("promote-msg", "children"),
        Input("confirm-btn-promote", "n_clicks"),
        State("promote-from-class", "value"),
        State("promote-to-class", "value"),
        State("promote-academic-year", "date"),
        State("session", "data"),
        prevent_initial_call=True,
    )
    def promote_students(n, from_class, to_class, new_year, SessionData):
    
        if not n:
            raise dash.exceptions.PreventUpdate
    
        if not from_class or not new_year:
            return dbc.Alert("⚠️ Fill required fields", color="danger")
    
        if not to_class:
            to_class = str(int(from_class) + 1)
    
        base_path = f"/var/Data/{SessionData['username']}/"
    
        student_file = base_path + "student_log.csv"
        history_file = base_path + "student_log_history.csv"
        ledger_file = base_path + "fees_ledger.csv"
        attendance_file = base_path + "student_attendance.csv"
        marks_file = base_path + f"marks/{from_class}.csv"
    
        try:
            df = pd.read_csv(student_file)
            df_att = pd.read_csv(attendance_file) if os.path.exists(attendance_file) else pd.DataFrame()
    
            # -----------------------
            # FILTER CLASS
            # -----------------------
            mask = df["studying_class"].astype(str) == str(from_class)
            promote_df = df[mask].copy()
    
            if promote_df.empty:
                return dbc.Alert("⚠️ No students found", color="warning")
    
            # -----------------------
            # 🔥 GET CORRECT FEE DUE
            # -----------------------
            due_df = build_fee_due(SessionData)
    
            promote_df["admission_no"] = promote_df["admission_no"].astype(str).str.strip()
            due_df["admission_no"] = due_df["admission_no"].astype(str).str.strip()
    
            promote_df = promote_df.merge(
                due_df[["admission_no", "fee_due"]],
                on="admission_no",
                how="left"
            )
    
            promote_df["fee_due"] = pd.to_numeric(promote_df["fee_due"], errors="coerce").fillna(0)
            promote_df["fees_pending"] = promote_df["fee_due"] > 0
    
            # -----------------------
            # 🔥 FILTER ELIGIBLE ONLY
            # -----------------------
            promote_df = promote_df[promote_df["fees_pending"] == False]
    
            if promote_df.empty:
                return dbc.Alert("❌ No eligible students (fees pending)", color="danger")
    
            pass_ids = promote_df["student_id"].tolist()
    
            # -----------------------
            # BACKUP
            # -----------------------
            backup_df = df[df["student_id"].isin(pass_ids)].copy()
            backup_df["backup_date"] = datetime.now().isoformat()
            backup_df["backup_reason"] = "PROMOTION"
    
            backup_df.to_csv(
                history_file,
                mode="a",
                index=False,
                header=not os.path.exists(history_file),
            )
    
            # -----------------------
            # ATTENDANCE UPDATE
            # -----------------------
            for _, row in backup_df.iterrows():
                admission_no = str(row["admission_no"]).strip().lower()
    
                if not df_att.empty:
                    stu_att = df_att[
                        df_att["admission_no"].astype(str).str.strip().str.lower() == admission_no
                    ]
    
                    present_days = stu_att[
                        stu_att["status"].astype(str).str.lower() == "present"
                    ].shape[0]
    
                    df.loc[
                        df["admission_no"].astype(str).str.strip().str.lower() == admission_no,
                        "previous_year_days"
                    ] = present_days
    
            # -----------------------
            # UPDATE STUDENT
            # -----------------------
            df.loc[df["student_id"].isin(pass_ids), "previous_class"] = df["studying_class"]
            df.loc[df["student_id"].isin(pass_ids), "studying_class"] = int(to_class)
            formatted_date = format_date(new_year)
            df.loc[df["student_id"].isin(pass_ids), "current_academic_year"] = formatted_date
    
            df.to_csv(student_file, index=False)
    
            return dbc.Alert(
                f"✅ {len(pass_ids)} students promoted (fees cleared)",
                color="success",
            )
    
        except Exception as e:
            return dbc.Alert(f"❌ Error: {str(e)}", color="danger")
    
    
    
    @app.callback(
        Output("student-preview-table", "children"),
        Output("confirm-btn-promote", "disabled"),
        Input("preview-btn", "n_clicks"),
        State("promote-from-class", "value"),
        State("promote-to-class", "value"),
        State("promote-academic-year", "date"),
        State("session", "data"),
        prevent_initial_call=True
    )
    def preview_students(n, from_class, to_class, new_year, SessionData):
    
        if not from_class or not new_year:
            return dbc.Alert("⚠️ Fill required fields", color="danger"), True
    
        if not to_class:
            to_class = str(int(from_class) + 1)
    
        base_path = f"/var/Data/{SessionData['username']}/"
        student_file = base_path + "student_log.csv"
    
        df = pd.read_csv(student_file)
    
        df = df[df["studying_class"].astype(str) == str(from_class)].copy()
    
        if df.empty:
            return dbc.Alert("⚠️ No students found", color="warning"), True
    
        # -----------------------
        # 🔥 GET CORRECT FEE
        # -----------------------
        due_df = build_fee_due(SessionData)
    
        df["admission_no"] = df["admission_no"].astype(str).str.strip()
        due_df["admission_no"] = due_df["admission_no"].astype(str).str.strip()
    
        df = df.merge(
            due_df[["admission_no", "fee_due"]],
            on="admission_no",
            how="left"
        )
    
        df["fee_due"] = pd.to_numeric(df["fee_due"], errors="coerce").fillna(0)
        df["fees_pending"] = df["fee_due"] > 0
    
        df_pass = df[df["fees_pending"] == False]
        df_blocked = df[df["fees_pending"] == True]
    
        return html.Div([
            dbc.Table.from_dataframe(df_pass, striped=True, bordered=True, hover=True, size="sm"),
            html.Hr(),
            html.H5("❌ Not Eligible (Fees Pending)"),
            dbc.Table.from_dataframe(df_blocked, striped=True, bordered=True, hover=True, size="sm"),
        ]), False
