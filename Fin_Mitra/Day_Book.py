import dash
from dash import html, dcc, Input, Output, State
import dash_bootstrap_components as dbc
import pandas as pd
import os
import io
from datetime import datetime
import re


def normalize_txn_date(val):
    """
    Convert raw string dates to datetime WITHOUT pandas guessing.
    """
    if pd.isna(val):
        return pd.NaT

    val = str(val).strip()

    # DD-MM-YYYY
    if re.fullmatch(r"\d{2}-\d{2}-\d{4}", val):
        return pd.to_datetime(val, format="%d-%m-%Y")

    # YYYY-MM-DD
    if re.fullmatch(r"\d{4}-\d{2}-\d{2}", val):
        return pd.to_datetime(val, format="%Y-%m-%d")

    # YYYY-MM-DD HH:MM:SS
    if re.fullmatch(r"\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}", val):
        return pd.to_datetime(val, format="%Y-%m-%d %H:%M:%S")

    return pd.NaT


def get_layout():
    return dbc.Container(
        [
            html.H3("DAY BOOK", className="text-center my-3"),
            dbc.Row(
                [
                    dbc.Col(
                        [
                            dbc.Label("From Date"),
                            dbc.Input(type="date", id="daybook-from"),
                        ],
                        md=3,
                    ),
                    dbc.Col(
                        [
                            dbc.Label("To Date"),
                            dbc.Input(type="date", id="daybook-to"),
                        ],
                        md=3,
                    ),
                    dbc.Col(
                        dbc.Button(
                            "Load Day Book",
                            id="load-daybook",
                            color="primary",
                            className="mt-4",
                        ),
                        md=3,
                    ),
                ],
                className="mb-4",
            ),
            dash.dash_table.DataTable(
                id="daybook-table",
                style_table={"overflowX": "auto"},
                style_cell={
                    "fontFamily": "Times New Roman",
                    "fontSize": "14px",
                    "padding": "6px",
                },
                style_header={
                    "fontWeight": "bold",
                    "borderBottom": "2px solid black",
                },
                page_size=20,
            ),
        ],
        fluid=True,
    )


def register_callbacks(app):
    @app.callback(
        Output("daybook-table", "data"),
        Output("daybook-table", "columns"),
        Input("load-daybook", "n_clicks"),
        State("daybook-from", "value"),
        State("daybook-to", "value"),
        State("session", "data"),
        prevent_initial_call=True,
    )
    def load_day_book(n, from_date, to_date, SessionData):

        if not n or not from_date or not to_date:
            return [], []

        path = "/var/Data/" + str(SessionData["username"]) + "/master_ledger.csv"
        if not os.path.exists(path):
            return [], []

        df = pd.read_csv(path)

        # --------------------------------------------------
        # Ensure numeric & handle missing columns safely
        # --------------------------------------------------
        for col in ["cash_amount", "bank1_amount", "bank2_amount"]:
            if col not in df.columns:
                df[col] = 0
            df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0)

        # --------------------------------------------------
        # Calculate TOTAL AMOUNT
        # --------------------------------------------------
        df["total_amount"] = (
            df["cash_amount"]
            + df["bank1_amount"]
            + df["bank2_amount"]
            + df["bank3_amount"]
            + df["bank4_amount"]
            + df["bank5_amount"]
            + df["bank6_amount"]
            + df["bank7_amount"]
            + df["bank8_amount"]
            + df["bank9_amount"]
            + df["bank10_amount"]
        )

        # --------------------------------------------------
        # Date filtering
        # --------------------------------------------------
        df["transaction_date"] = pd.to_datetime(
            df["transaction_date"].apply(normalize_txn_date)
        )
        from_dt = pd.to_datetime(from_date)
        to_dt = pd.to_datetime(to_date)

        df = df[(df["transaction_date"] >= from_dt) & (df["transaction_date"] <= to_dt)]

        if df.empty:
            return [], []

        # --------------------------------------------------
        # Debit / Credit classification
        # --------------------------------------------------
        RECEIPT_FORMS = [
            "FEES RECEIPT",
            "OTHER RECEIPT",
        ]

        PAYMENT_FORMS = [
            "EXPENSES",
            "SALARY PAYMENT",
            "OTHER PAYMENT",
        ]

        df["Debit Amount"] = df.apply(
            lambda r: r["total_amount"] if r["form_name"] in PAYMENT_FORMS else "",
            axis=1,
        )

        df["Credit Amount"] = df.apply(
            lambda r: r["total_amount"] if r["form_name"] in RECEIPT_FORMS else "",
            axis=1,
        )

        # --------------------------------------------------
        # Final Day Book format
        # --------------------------------------------------
        daybook = pd.DataFrame(
            {
                "Date": df["transaction_date"].dt.strftime("%d-%b-%y"),
                "Particulars": df["ledger_group"],
                "Vch Type": df["form_name"],
                "Vch No.": df["entry_id"],
                "Debit Amount": df["Debit Amount"],
                "Credit Amount": df["Credit Amount"],
            }
        )

        daybook = daybook.sort_values(by=["Date", "Vch No."])

        columns = [{"name": c, "id": c} for c in daybook.columns]

        return daybook.to_dict("records"), columns
    


    @app.callback(
    Output("daybook-from", "value"),
    Output("daybook-to", "value"),
    Input("selected-financial-year", "data"),
    prevent_initial_call=True
)
    def update_daybook_dates(selected_fy):

     if not selected_fy:
        raise dash.exceptions.PreventUpdate

     year = int(selected_fy.replace("FY", "")) + 2000

     start_date = f"{year-1}-04-01"
     end_date = f"{year}-03-31"

     return start_date, end_date
