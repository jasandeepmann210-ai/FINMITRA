import dash
from dash import html, dcc, Input, Output, State
import dash_bootstrap_components as dbc
import pandas as pd
import os
import re

# =====================================================
# DATE NORMALIZATION (AUTHORITATIVE)
# =====================================================


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


def parse_picker_date(val):
    """
    Safe parser for Dash DatePicker values (YYYY-MM-DD).
    """
    return pd.to_datetime(val, format="%Y-%m-%d")


# =====================================================
# LAYOUT
# =====================================================


def get_layout():

    COL_WIDTHS = {
        "date": "25%",
        "desc": "45%",
        "amt": "30%",
    }

    return dbc.Container(
        [
            html.H3("CASH BOOK", className="text-center my-3"),
            dbc.Row(
                [
                    dbc.Col(html.B("PERIOD SELECT"), md=3),
                    dbc.Col(
                        dcc.DatePickerRange(
                            id="cashbook-period",
                            display_format="YYYY-MM-DD",
                        ),
                        md=6,
                    ),
                ],
                className="mb-4",
            ),
            dbc.Row(
                [
                    dbc.Col(
                        html.B("RECEIPTS (CASH IN)"), md=6, className="text-center"
                    ),
                    dbc.Col(
                        html.B("PAYMENTS (CASH OUT)"), md=6, className="text-center"
                    ),
                ],
                className="fw-bold mb-2",
            ),
            # ================================
            # TABLES
            # ================================
            dbc.Row(
                [
                    dbc.Col(
                        [
                            dash.dash_table.DataTable(
                                id="cashbook-receipts",
                                columns=[
                                    {"name": "Date", "id": "transaction_date"},
                                    {"name": "Receipt", "id": "receipt"},
                                    {"name": "Amount", "id": "amount"},
                                ],
                                style_table={"height": "320px", "overflowY": "auto"},
                                style_cell={"padding": "6px", "textAlign": "center"},
                                style_cell_conditional=[
                                    {
                                        "if": {"column_id": "receipt"},
                                        "textAlign": "left",
                                    },
                                    {
                                        "if": {"column_id": "amount"},
                                        "textAlign": "right",
                                    },
                                ],
                            ),
                        ],
                        md=6,
                    ),
                    dbc.Col(
                        [
                            dash.dash_table.DataTable(
                                id="cashbook-payments",
                                columns=[
                                    {"name": "Date", "id": "transaction_date"},
                                    {"name": "Payment", "id": "payment"},
                                    {"name": "Amount", "id": "amount"},
                                ],
                                style_table={"height": "320px", "overflowY": "auto"},
                                style_cell={"padding": "6px", "textAlign": "center"},
                                style_cell_conditional=[
                                    {
                                        "if": {"column_id": "payment"},
                                        "textAlign": "left",
                                    },
                                    {
                                        "if": {"column_id": "amount"},
                                        "textAlign": "right",
                                    },
                                ],
                            ),
                        ],
                        md=6,
                    ),
                ],
                className="mb-4",
            ),
            # ================================
            # TOTALS
            # ================================
            dbc.Row(
                [
                    dbc.Col(html.B("TOTAL RECEIPTS"), md=3),
                    dbc.Col(html.Div(id="cashbook-total-receipts"), md=3),
                    dbc.Col(html.B("TOTAL PAYMENTS"), md=3),
                    dbc.Col(html.Div(id="cashbook-total-payments"), md=3),
                ],
                className="fw-bold my-3",
            ),
            html.Hr(),
            # ================================
            # BALANCES AT END
            # ================================
            dbc.Row(
                [
                    dbc.Col(html.B("OPENING BALANCE"), md=6),
                    dbc.Col(html.Div(id="cashbook-opening-balance"), md=6),
                ],
                className="fw-bold my-2",
            ),
            dbc.Row(
                [
                    dbc.Col(html.H4("CLOSING BALANCE"), md=6),
                    dbc.Col(html.H4(id="cashbook-closing-balance"), md=6),
                ],
                className="fw-bold border-top pt-3",
            ),
        ],
        fluid=True,
    )


# =====================================================
# CASH BOOK ENGINE
# =====================================================


def generate_cash_book(from_date, to_date, SessionData):

    ledger_path = "/var/Data/" + str(SessionData["username"]) + "/master_ledger.csv"
    df = pd.read_csv(ledger_path)
    print("📊 CashBook rows loaded:", SessionData["username"])

    # 🔒 SAFE DATE PARSING (NO GUESSING)
    df["transaction_date"] = df["transaction_date"].apply(normalize_txn_date)

    # normalize ledger dates
    df["transaction_date"] = df["transaction_date"].dt.normalize()

    df["cash_amount"] = pd.to_numeric(df["cash_amount"], errors="coerce").fillna(0)

    # picker dates
    from_date = parse_picker_date(from_date).normalize()
    to_date = (
        parse_picker_date(to_date).normalize()
        + pd.Timedelta(days=1)
        - pd.Timedelta(seconds=1)
    )

    df = df[df["cash_amount"] != 0]

    # --------------------------------------------------
    # OPENING BALANCE
    # --------------------------------------------------
    prior_df = df[df["transaction_date"] < from_date]

    opening_balance = (
        prior_df[prior_df["form_name"].isin(["FEES RECEIPT", "OTHER RECEIPT"])][
            "cash_amount"
        ].sum()
        - prior_df[
            prior_df["form_name"].isin(["EXPENSES", "SALARY PAYMENT", "OTHER PAYMENT"])
        ]["cash_amount"].sum()
    )

    # --------------------------------------------------
    # CURRENT PERIOD
    # --------------------------------------------------
    period_df = df[
        (df["transaction_date"] >= from_date) & (df["transaction_date"] <= to_date)
    ]

    receipts = period_df[
        period_df["form_name"].isin(["FEES RECEIPT", "OTHER RECEIPT"])
    ][["transaction_date", "form_name", "cash_amount"]]

    receipts = receipts.rename(
        columns={"form_name": "receipt", "cash_amount": "amount"}
    )

    payments = period_df[
        period_df["form_name"].isin(["EXPENSES", "SALARY PAYMENT", "OTHER PAYMENT"])
    ][["transaction_date", "form_name", "cash_amount"]]

    payments = payments.rename(
        columns={"form_name": "payment", "cash_amount": "amount"}
    )

    # --------------------------------------------------
    # NEGATIVE PAYMENTS → RECEIPTS (GENERIC CASH RULE)
    # --------------------------------------------------

    neg_payments = payments[payments["amount"] < 0].copy()

    if not neg_payments.empty:
        # flip sign
        neg_payments["amount"] = neg_payments["amount"].abs()

        # 🔑 NORMALISE LABEL
        neg_payments["receipt"] = "OTHER RECEIPT"

        # drop old column and align schema
        neg_payments = neg_payments[["transaction_date", "receipt", "amount"]]

        # append to receipts
        receipts = pd.concat([receipts, neg_payments], ignore_index=True)

        # keep only positive payments
        payments = payments[payments["amount"] >= 0]

    total_receipts = receipts["amount"].sum()
    total_payments = payments["amount"].sum()

    closing_balance = opening_balance + total_receipts - total_payments

    return (
        receipts,
        payments,
        opening_balance,
        total_receipts,
        total_payments,
        closing_balance,
    )


# =====================================================
# CALLBACKS
# =====================================================


def register_callbacks(app):



    @app.callback(
    Output("cashbook-period", "start_date"),
    Output("cashbook-period", "end_date"),
    Input("selected-financial-year", "data"),
)
    def update_cashbook_dates(selected_fy):

     if not selected_fy:
        raise dash.exceptions.PreventUpdate

     year = int(selected_fy.replace("FY", "")) + 2000

     start_date = f"{year-1}-04-01"
     end_date = f"{year}-03-31"

     return start_date, end_date

    @app.callback(
        Output("cashbook-receipts", "data"),
        Output("cashbook-payments", "data"),
        Output("cashbook-opening-balance", "children"),
        Output("cashbook-total-receipts", "children"),
        Output("cashbook-total-payments", "children"),
        Output("cashbook-closing-balance", "children"),
        Input("cashbook-period", "start_date"),
        Input("cashbook-period", "end_date"),
        State("session", "data"),
    )
    def update_cash_book(from_date, to_date, session_data):

        if not from_date or not to_date:
            return [], [], "0.00", "0.00", "0.00", "0.00"

        r, p, ob, tr, tp, cb = generate_cash_book(from_date, to_date, session_data)

        return (
            r.to_dict("records"),
            p.to_dict("records"),
            f"{ob:,.2f}",
            f"{tr:,.2f}",
            f"{tp:,.2f}",
            f"{cb:,.2f}",
        )
