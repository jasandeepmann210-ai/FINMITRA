import dash
from dash import html, dcc, dash_table
import dash_bootstrap_components as dbc
from dash import Input, Output, State
import pandas as pd
from dash import no_update, ALL
import os
import re
from pandas.tseries.offsets import MonthEnd
from datetime import datetime


# =====================================================
# LEDGER PARSER (AUTHORITATIVE)
# =====================================================


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


# =====================================================
# CALLBACKS
# =====================================================


def register_callbacks(app):

    @app.callback(
        Output("fee-structure-toast", "is_open"),
        Input("submit-fee-structure", "n_clicks"),
        State({"type": "fee-amount", "index": ALL}, "value"),
        State("session", "data"),
        prevent_initial_call=True,
    )
    def save_fee_structure(_, fee_values, SessionData):

        path = f"/var/Data/{SessionData['username']}/fee_structure_static.csv"
        df = pd.read_csv(path)

        df["monthly_fee"] = [v if v is not None else 0 for v in fee_values]

        df.to_csv(path, index=False)

        return True

    # ----------------------------------------------
    # BUILD FEE DUE TABLE (ROLL + CLASS MATCH)
    # ----------------------------------------------
    @app.callback(
        Output("fee-due-table", "data"),
        Input("student-fee-tabs", "active_tab"),
        Input("fee-due-search", "value"),
        State("session", "data"),
    )
    def build_fee_due(active_tab, search, SessionData):
    
        if active_tab != "fee-due":
            return no_update
    
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
        merged["monthly_fee_concession"] = pd.to_numeric(
            merged["monthly_fee_concession"], errors="coerce"
        ).fillna(0)
        
        merged["effective_monthly_fee"] = (
            merged["monthly_fee"] - merged["monthly_fee_concession"]
        ).clip(lower=0)
        
        merged["expected_fee"] = merged["months_elapsed"] * merged["effective_monthly_fee"]
    
        merged["net_balance"] = merged["amount_paid"] - merged["expected_fee"]

        merged["fee_due"] = merged["net_balance"].apply(lambda x: abs(x) if x < 0 else 0)
        merged["over_paid"] = merged["net_balance"].apply(lambda x: x if x > 0 else 0)
    
        due_df = merged.copy()
    
        # ---------------------------
        # SEARCH
        # ---------------------------
        if search:
            s = search.lower()
    
            due_df = due_df[
                due_df.apply(
                    lambda r:
                    s in str(r["student_name"]).lower()
                    or s in str(r["standard"]).lower()
                    or s in str(r["aadhaar"]).lower()
                    or s in str(r["admission_no"]).lower()
                    or s in str(r["mobile"]).lower(),
                    axis=1
                )
            ]
    
        # ---------------------------
        # FORMAT OUTPUT
        # ---------------------------
        due_df["admission_month_end"] = (
            due_df["admission_month_end"]
            .astype("datetime64[ns]")
            .dt.strftime("%d-%m-%Y")
        )
    
        return (
            due_df[
                [
                    "student_name",
                    "admission_no",
                    "standard",
                    "aadhaar",
                    "mobile",
                    "admission_month_end",
                    "months_elapsed",
                    "monthly_fee",
                    "monthly_fee_concession",   
                    "effective_monthly_fee",
                    "amount_paid",
                    "fee_due",
                    "over_paid",
                ]
            ]
            .rename(columns={"amount_paid": "paid"})
            .to_dict("records")
        )

    # ----------------------------------------------
    # DOWNLOAD
    # ----------------------------------------------
    @app.callback(
        Output("download-fee-due-csv", "data"),
        Input("download-fee-due-btn", "n_clicks"),
        State("fee-due-table", "data"),
        prevent_initial_call=True,
    )
    def download_fee_due(_, data):

        df = pd.DataFrame(data)
        return dict(
            content=df.to_csv(index=False),
            filename="monthly_fee_due_students.csv",
        )


# =========================================================
# LOAD / INIT FEE STRUCTURE
# =========================================================
def load_fee_structure(SessionData):

    path = f"/var/Data/{SessionData['username']}/fee_structure_static.csv"

    if not os.path.exists(path):
        df = pd.DataFrame(
            [
                {"standard": f"Std {i}", "studying_class": str(i), "monthly_fee": 0}
                for i in range(1, 13)
            ]
        )
        df.to_csv(path, index=False)
        return df

    return pd.read_csv(path)


def get_fee_structure_layout(SessionData):

    df = load_fee_structure(SessionData)

    rows = []
    for idx, row in df.iterrows():
        rows.append(
            html.Tr(
                [
                    # ---------- STANDARD (READ ONLY) ----------
                    html.Td(row["standard"], className="fw-semibold"),
                    # ---------- CLASS (READ ONLY, OPTIONAL) ----------
                    html.Td(row["studying_class"], className="text-muted"),
                    # ---------- AMOUNT (EDITABLE) ----------
                    html.Td(
                        dbc.Input(
                            id={"type": "fee-amount", "index": idx},
                            type="number",
                            min=0,
                            step=1,
                            value=row["monthly_fee"],
                        )
                    ),
                ]
            )
        )

    return dbc.Container(
        [
            # ================= HEADER =================
            dbc.Row(
                dbc.Col(
                    dbc.Card(
                        dbc.CardBody(
                            [
                                html.H4(
                                    "Monthly Fee Structure",
                                    className="fw-bold text-center mb-1",
                                ),
                                html.P(
                                    "Only the fee amount is editable",
                                    className="text-muted text-center mb-0",
                                ),
                            ]
                        ),
                        className="shadow-sm border-0",
                    ),
                    width=12,
                ),
                className="my-4",
            ),
            # ================= TABLE =================
            dbc.Row(
                dbc.Col(
                    dbc.Card(
                        dbc.CardBody(
                            [
                                dbc.Table(
                                    [
                                        html.Thead(
                                            html.Tr(
                                                [
                                                    html.Th("Standard"),
                                                    html.Th("Class"),
                                                    html.Th("Monthly Fee"),
                                                ]
                                            )
                                        ),
                                        html.Tbody(rows),
                                    ],
                                    bordered=True,
                                    hover=True,
                                    responsive=True,
                                    size="sm",
                                ),
                                dbc.Button(
                                    "Save Fee Structure",
                                    id="submit-fee-structure",
                                    color="success",
                                    className="mt-3",
                                ),
                            ]
                        ),
                        className="shadow-sm border-0",
                    ),
                    md=10,
                    className="mx-auto",
                )
            ),
            # ================= SUCCESS TOAST =================
            dbc.Toast(
                "Fee structure saved successfully",
                id="fee-structure-toast",
                header="Success",
                is_open=False,
                dismissable=True,
                duration=3000,
                icon="success",
                style={
                    "position": "fixed",
                    "top": 20,
                    "right": 20,
                    "width": 350,
                    "zIndex": 2000,
                },
            ),
        ],
        fluid=True,
        className="bg-light min-vh-100 px-4",
    )


def get_fee_due_content(SessionData):
    return dbc.Container(
    [
        html.H4("Monthly Fee Due", className="mb-3"),

        dbc.Input(
            id="fee-due-search",
            type="text",
            placeholder="Search student, phone, aadhaar, class...",
            className="mb-3",
        ),

        dash_table.DataTable(
            id="fee-due-table",
            columns=[
                {"name": "Student Name", "id": "student_name"},
                {"name": "Admission Number", "id": "admission_no"},
                {"name": "Standard", "id": "standard"},
                {"name": "Aadhaar", "id": "aadhaar"},
                {"name": "Phone", "id": "mobile"},
                {"name": "Admission Month End", "id": "admission_month_end"},
                {"name": "Months", "id": "months_elapsed", "type": "numeric"},
                {"name": "Monthly Fee", "id": "monthly_fee", "type": "numeric"},
                {"name": "Concession", "id": "monthly_fee_concession", "type": "numeric"},
                {"name": "Net Fee", "id": "effective_monthly_fee", "type": "numeric"},
                {"name": "Paid", "id": "paid", "type": "numeric"},
                {"name": "Due", "id": "fee_due", "type": "numeric"},
                {"name": "Over Paid", "id": "over_paid", "type": "numeric"},
            ],
            page_size=10,
            style_table={"overflowX": "auto"},
        ),

        dbc.Button(
            "Download Fee Due List",
            id="download-fee-due-btn",
            color="primary",
            className="mt-3",
        ),

        dcc.Download(id="download-fee-due-csv"),
    ],
    fluid=True,
)




