import dash
from dash import html, dcc, Input, Output, State
import dash_bootstrap_components as dbc
import pandas as pd
import re
import os

# =====================================================
# DATE NORMALIZATION (AUTHORITATIVE – SAME AS CASH BOOK)
# =====================================================


def normalize_txn_date(val):
    """
    Convert raw string dates to datetime WITHOUT pandas guessing.
    Supported:
    - DD-MM-YYYY
    - YYYY-MM-DD
    - YYYY-MM-DD HH:MM:SS
    """
    if pd.isna(val):
        return pd.NaT

    val = str(val).strip()

    if re.fullmatch(r"\d{2}-\d{2}-\d{4}", val):
        return pd.to_datetime(val, format="%d-%m-%Y")

    if re.fullmatch(r"\d{4}-\d{2}-\d{2}", val):
        return pd.to_datetime(val, format="%Y-%m-%d")

    if re.fullmatch(r"\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}", val):
        return pd.to_datetime(val, format="%Y-%m-%d %H:%M:%S")

    return pd.NaT


def parse_picker_date(val):
    """Dash DatePicker always emits YYYY-MM-DD"""
    return pd.to_datetime(val, format="%Y-%m-%d")


# =====================================================
# LAYOUT
# =====================================================


def load_bank_labels(SessionData):

    BANK_LABEL_PATH = (
        "/var/Data/" + str(SessionData["username"]) + "/bank_name_static.csv"
    )

    if not os.path.exists(BANK_LABEL_PATH):
        # fallback if CSV missing
        return {f"BANK{i}": f"Bank {i}" for i in range(1, 11)}

    df = pd.read_csv(BANK_LABEL_PATH)
    return dict(zip(df["bank_code"], df["bank_label"]))


def get_layout(SessionData):

    BANK_LABELS = load_bank_labels(SessionData)

    return dbc.Container(
        [
            html.H3("BANK BOOK", className="text-center my-3"),
            dbc.Row(
                [
                    dbc.Col(html.B("PERIOD SELECT"), md=3),
                    dbc.Col(
                        dcc.DatePickerRange(
                            id="bankbook-period",
                            display_format="YYYY-MM-DD",
                        ),
                        md=5,
                    ),
                    dbc.Col(
                        dcc.Dropdown(
                            id="bank-selector",
                            options=[
                                {
                                    "label": BANK_LABELS.get(f"BANK{i}", f"Bank {i}"),
                                    "value": f"bank{i}",
                                }
                                for i in range(1, 11)
                            ],
                            placeholder="Select Bank",
                        ),
                        md=4,
                    ),
                ],
                className="mb-4",
            ),
            dbc.Row(
                [
                    dbc.Col(
                        html.B("RECEIPTS (BANK IN)"), md=6, className="text-center"
                    ),
                    dbc.Col(
                        html.B("PAYMENTS (BANK OUT)"), md=6, className="text-center"
                    ),
                ],
                className="fw-bold mb-2",
            ),
            # =========================
            # TABLES
            # =========================
            dbc.Row(
                [
                    dbc.Col(
                        dash.dash_table.DataTable(
                            id="bankbook-receipts",
                            columns=[
                                {"name": "Date", "id": "transaction_date"},
                                {"name": "Receipt", "id": "receipt"},
                                {"name": "Amount", "id": "amount"},
                            ],
                            style_table={"height": "320px", "overflowY": "auto"},
                            style_cell={"padding": "6px", "textAlign": "center"},
                            style_cell_conditional=[
                                {"if": {"column_id": "receipt"}, "textAlign": "left"},
                                {"if": {"column_id": "amount"}, "textAlign": "right"},
                            ],
                        ),
                        md=6,
                    ),
                    dbc.Col(
                        dash.dash_table.DataTable(
                            id="bankbook-payments",
                            columns=[
                                {"name": "Date", "id": "transaction_date"},
                                {"name": "Payment", "id": "payment"},
                                {"name": "Amount", "id": "amount"},
                            ],
                            style_table={"height": "320px", "overflowY": "auto"},
                            style_cell={"padding": "6px", "textAlign": "center"},
                            style_cell_conditional=[
                                {"if": {"column_id": "payment"}, "textAlign": "left"},
                                {"if": {"column_id": "amount"}, "textAlign": "right"},
                            ],
                        ),
                        md=6,
                    ),
                ],
                className="mb-4",
            ),
            # =========================
            # TOTALS
            # =========================
            dbc.Row(
                [
                    dbc.Col(html.B("TOTAL RECEIPTS"), md=3),
                    dbc.Col(html.Div(id="bankbook-total-receipts"), md=3),
                    dbc.Col(html.B("TOTAL PAYMENTS"), md=3),
                    dbc.Col(html.Div(id="bankbook-total-payments"), md=3),
                ],
                className="fw-bold my-3",
            ),
            html.Hr(),
            # =========================
            # BALANCES AT END
            # =========================
            dbc.Row(
                [
                    dbc.Col(html.B("OPENING BALANCE"), md=6),
                    dbc.Col(html.Div(id="bankbook-opening-balance"), md=6),
                ],
                className="fw-bold my-2",
            ),
            dbc.Row(
                [
                    dbc.Col(html.H4("CLOSING BALANCE"), md=6),
                    dbc.Col(html.H4(id="bankbook-closing-balance"), md=6),
                ],
                className="fw-bold border-top pt-3",
            ),
        ],
        fluid=True,
    )


# =====================================================
# BANK BOOK ENGINE
# =====================================================


def generate_bank_book(from_date, to_date, bank_col, SessionData):

    df = pd.read_csv("/var/Data/" + str(SessionData["username"]) + "/master_ledger.csv")

    # 🔒 SAFE DATE PARSING (NO GUESSING)
    df["transaction_date"] = df["transaction_date"].apply(normalize_txn_date)
    df["transaction_date"] = df["transaction_date"].dt.normalize()

    bank_amount_col = f"{bank_col}_amount"
    df[bank_amount_col] = pd.to_numeric(df[bank_amount_col], errors="coerce").fillna(0)

    # Picker dates
    from_date = parse_picker_date(from_date).normalize()
    to_date = (
        parse_picker_date(to_date).normalize()
        + pd.Timedelta(days=1)
        - pd.Timedelta(seconds=1)
    )

    # BANK ONLY
    df = df[df[bank_amount_col] != 0]

    # --------------------------------------------------
    # OPENING BALANCE
    # --------------------------------------------------
    prior_df = df[df["transaction_date"] < from_date]

    opening_balance = (
        prior_df[prior_df["form_name"].isin(["FEES RECEIPT", "OTHER RECEIPT"])][
            bank_amount_col
        ].sum()
        - prior_df[
            prior_df["form_name"].isin(
                ["EXPENSES", "SALARY PAYMENT", "OTHER PAYMENT", "DECLARE ASSETS"]
            )
        ][bank_amount_col].sum()
    )

    # --------------------------------------------------
    # CURRENT PERIOD
    # --------------------------------------------------
    period_df = df[
        (df["transaction_date"] >= from_date) & (df["transaction_date"] <= to_date)
    ]

    receipts = period_df[
        period_df["form_name"].isin(["FEES RECEIPT", "OTHER RECEIPT"])
    ][["transaction_date", "form_name", bank_amount_col]]

    receipts = receipts.rename(
        columns={
            "form_name": "receipt",
            bank_amount_col: "amount",
        }
    )

    payments = period_df[
        period_df["form_name"].isin(
            ["EXPENSES", "SALARY PAYMENT", "OTHER PAYMENT", "DECLARE ASSETS"]
        )
    ][["transaction_date", "form_name", bank_amount_col]]

    payments = payments.rename(
        columns={
            "form_name": "payment",
            bank_amount_col: "amount",
        }
    )

    # --------------------------------------------------
    # NEGATIVE PAYMENTS → RECEIPTS (BANK BOOK NORMALIZATION)
    # --------------------------------------------------

    neg_payments = payments[payments["amount"] < 0].copy()

    if not neg_payments.empty:
        # flip sign
        neg_payments["amount"] = neg_payments["amount"].abs()

        # normalize label for receipt side
        neg_payments["receipt"] = "OTHER RECEIPT"

        # align schema with receipts table
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
        Output("bankbook-receipts", "data"),
        Output("bankbook-payments", "data"),
        Output("bankbook-opening-balance", "children"),
        Output("bankbook-total-receipts", "children"),
        Output("bankbook-total-payments", "children"),
        Output("bankbook-closing-balance", "children"),
        Input("bankbook-period", "start_date"),
        Input("bankbook-period", "end_date"),
        Input("bank-selector", "value"),
        State("session", "data"),
    )
    def update_bank_book(from_date, to_date, bank, SessionData):

        if not from_date or not to_date or not bank:
            return [], [], "0.00", "0.00", "0.00", "0.00"

        r, p, ob, tr, tp, cb = generate_bank_book(from_date, to_date, bank, SessionData)

        return (
            r.to_dict("records"),
            p.to_dict("records"),
            f"{ob:,.2f}",
            f"{tr:,.2f}",
            f"{tp:,.2f}",
            f"{cb:,.2f}",
        )
    
    @app.callback(
    Output("bankbook-period", "start_date"),
    Output("bankbook-period", "end_date"),
    Input("selected-financial-year", "data"),
    prevent_initial_call=True
)
    def update_bankbook_dates(selected_fy):

     if not selected_fy:
        raise dash.exceptions.PreventUpdate

     year = int(selected_fy.replace("FY", "")) + 2000

     start_date = f"{year-1}-04-01"
     end_date = f"{year}-03-31"

     return start_date, end_date
