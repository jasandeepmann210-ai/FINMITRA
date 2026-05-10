import dash
from dash import html, dcc, Input, Output, State
import dash_bootstrap_components as dbc
import pandas as pd
import ast


MASTER_LEDGER_PATH = "data/master_ledger.csv"

df = pd.read_csv(MASTER_LEDGER_PATH)
df.fillna("", inplace=True)


# =========================================================
# BUILD VOUCHER LEDGER (TALLY-LIKE)
# =========================================================
def reload_data(SessionData):
    global df, postings_df, voucher_df

    MASTER_LEDGER_PATH = (
        "/var/Data/" + str(SessionData["username"]) + "/master_ledger.csv"
    )

    df = pd.read_csv(MASTER_LEDGER_PATH)
    df.fillna("", inplace=True)

    postings_df = build_postings(df)
    voucher_df = build_ledger_vouchers(df)

    accounts = sorted(postings_df["account"].dropna().unique())

    # REMOVE CASH & BANK
    accounts = [acc for acc in accounts if acc not in BLOCKED_ACCOUNTS]

    return accounts

def build_ledger_vouchers(df):
    rows = []

    for _, r in df.iterrows():
        date = r.get("transaction_date", "")
        form = r.get("form_name", "")
        vch_no = r.get("entry_id", "")

        # ---------- OPENING BALANCE ----------
        total_amt = float(r.get("total_amount", 0) or 0)
        cash = float(r.get("cash_amount", 0) or 0)
        bank1 = float(r.get("bank1_amount", 0) or 0)
        bank2 = float(r.get("bank2_amount", 0) or 0)
        bank3 = float(r.get("bank3_amount", 0) or 0)
        bank4 = float(r.get("bank4_amount", 0) or 0)
        bank5 = float(r.get("bank5_amount", 0) or 0)
        bank6 = float(r.get("bank6_amount", 0) or 0)
        bank7 = float(r.get("bank7_amount", 0) or 0)
        bank8 = float(r.get("bank8_amount", 0) or 0)
        bank9 = float(r.get("bank9_amount", 0) or 0)
        bank10 = float(r.get("bank10_amount", 0) or 0)

        if (
            total_amt > 0
            and cash == 0
            and bank1 == 0
            and bank2 == 0
            and bank3 == 0
            and bank4 == 0
            and bank5 == 0
            and bank6 == 0
            and bank7 == 0
            and bank8 == 0
            and bank9 == 0
            and bank10 == 0
        ):
            acc = r.get("account_name") or r.get("ledger_name")
            if not acc:
                continue

            form = (r.get("form_name") or "").upper()

            debit = total_amt
            credit = 0.0
            if "RECEIPT" in form:
                debit = 0.0
                credit = total_amt

            rows.append(
                {
                    "date": date,
                    "particulars": acc,
                    "vch_type": "Opening Balance",
                    "vch_no": vch_no,
                    "debit": debit,
                    "credit": credit,
                }
            )
            continue

        # ---------- EXPENSES ----------
        elif vch_no.startswith("EXP_"):
            for col in [
                "breakup_cash",
                "breakup_bank1",
                "breakup_bank2",
                "breakup_bank3",
                "breakup_bank4",
                "breakup_bank5",
                "breakup_bank6",
                "breakup_bank7",
                "breakup_bank8",
                "breakup_bank9",
                "breakup_bank10",
            ]:
                if not r[col]:
                    continue
                breakup = ast.literal_eval(r[col])
                for head, amt in breakup.items():
                    rows.append(
                        {
                            "date": date,
                            "particulars": head,
                            "vch_type": form,
                            "vch_no": vch_no,
                            "debit": float(amt),
                            "credit": 0.0,
                        }
                    )

        # ---------- OTHER RECEIPT ----------
        elif vch_no.startswith("OR_"):
            for col in [
                "breakup_cash",
                "breakup_bank1",
                "breakup_bank2",
                "breakup_bank3",
                "breakup_bank4",
                "breakup_bank5",
                "breakup_bank6",
                "breakup_bank7",
                "breakup_bank8",
                "breakup_bank9",
                "breakup_bank10",
            ]:
                if not r[col]:
                    continue
                breakup = ast.literal_eval(r[col])
                for _, obj in breakup.items():
                    rows.append(
                        {
                            "date": date,
                            "particulars": obj.get("account", ""),
                            "vch_type": form,
                            "vch_no": vch_no,
                            "debit": 0.0,
                            "credit": float(obj.get("amount", 0)),
                        }
                    )

        # ---------- OTHER PAYMENT ----------
        elif vch_no.startswith("OP_"):
            for col in [
                "breakup_cash",
                "breakup_bank1",
                "breakup_bank2",
                "breakup_bank3",
                "breakup_bank4",
                "breakup_bank5",
                "breakup_bank6",
                "breakup_bank7",
                "breakup_bank8",
                "breakup_bank9",
                "breakup_bank10",
            ]:
                if not r[col]:
                    continue
                breakup = ast.literal_eval(r[col])
                for _, obj in breakup.items():
                    rows.append(
                        {
                            "date": date,
                            "particulars": obj.get("account", ""),
                            "vch_type": form,
                            "vch_no": vch_no,
                            "debit": float(obj.get("amount", 0)),
                            "credit": 0.0,
                        }
                    )

        # ---------- FEES ----------
        elif vch_no.startswith("FEES_"):
            acc = r.get("account_name") or r.get("ledger_name")
            if not acc:
                continue

            amt = (
                float(r.get("cash_amount", 0) or 0)
                + float(r.get("bank1_amount", 0) or 0)
                + float(r.get("bank2_amount", 0) or 0)
                + float(r.get("bank3_amount", 0) or 0)
                + float(r.get("bank4_amount", 0) or 0)
                + float(r.get("bank5_amount", 0) or 0)
                + float(r.get("bank6_amount", 0) or 0)
                + float(r.get("bank7_amount", 0) or 0)
                + float(r.get("bank8_amount", 0) or 0)
                + float(r.get("bank9_amount", 0) or 0)
                + float(r.get("bank10_amount", 0) or 0)
            )

            if amt > 0:
                rows.append(
                    {
                        "date": date,
                        "particulars": acc,
                        "vch_type": form,
                        "vch_no": vch_no,
                        "debit": 0.0,
                        "credit": amt,
                    }
                )

    return pd.DataFrame(rows)


voucher_df = build_ledger_vouchers(df)


# =========================================================
# BUILD POSTINGS (T-ACCOUNT)
# =========================================================
def build_postings(df):
    postings = []

    for _, r in df.iterrows():
        date = r.get("transaction_date", "")
        entry_id = r.get("entry_id", "")

        # ---------- OPENING BALANCE ----------
        total_amt = float(r.get("total_amount", 0) or 0)
        cash = float(r.get("cash_amount", 0) or 0)
        bank1 = float(r.get("bank1_amount", 0) or 0)
        bank2 = float(r.get("bank2_amount", 0) or 0)
        bank3 = float(r.get("bank3_amount", 0) or 0)
        bank4 = float(r.get("bank4_amount", 0) or 0)
        bank5 = float(r.get("bank5_amount", 0) or 0)
        bank6 = float(r.get("bank6_amount", 0) or 0)
        bank7 = float(r.get("bank7_amount", 0) or 0)
        bank8 = float(r.get("bank8_amount", 0) or 0)
        bank9 = float(r.get("bank9_amount", 0) or 0)
        bank10 = float(r.get("bank10_amount", 0) or 0)

        if (
            total_amt > 0
            and cash == 0
            and bank1 == 0
            and bank2 == 0
            and bank3 == 0
            and bank4 == 0
            and bank5 == 0
            and bank6 == 0
            and bank7 == 0
            and bank8 == 0
            and bank9 == 0
            and bank10 == 0
        ):
            acc = r.get("account_name") or r.get("ledger_name")
            if not acc:
                continue

            form = (r.get("form_name") or "").upper()

            side = "DR"
            if "RECEIPT" in form:
                side = "CR"

            postings.append(
                {
                    "date": date,
                    "account": acc,
                    "side": side,
                    "contra": "Opening Balance",
                    "amount": total_amt,
                }
            )

            continue

        # ---------- FEES RECEIPT ----------
        if entry_id.startswith("FEES_"):
            acc = r.get("account_name") or r.get("ledger_name")
            if not acc:
                continue

            for col, contra in [
                ("cash_amount", "Cash A/C"),
                ("bank1_amount", "Bank 1 A/C"),
                ("bank2_amount", "Bank 2 A/C"),
                ("bank3_amount", "Bank 3 A/C"),
                ("bank4_amount", "Bank 4 A/C"),
                ("bank5_amount", "Bank 5 A/C"),
                ("bank6_amount", "Bank 6 A/C"),
                ("bank7_amount", "Bank 7 A/C"),
                ("bank8_amount", "Bank 8 A/C"),
                ("bank9_amount", "Bank 9 A/C"),
                ("bank10_amount", "Bank 10 A/C"),
            ]:
                amt = float(r.get(col, 0) or 0)
                if amt <= 0:
                    continue

                postings.append(
                    {
                        "date": date,
                        "account": acc,
                        "side": "CR",
                        "contra": contra,
                        "amount": amt,
                    }
                )

                postings.append(
                    {
                        "date": date,
                        "account": contra,
                        "side": "DR",
                        "contra": acc,
                        "amount": amt,
                    }
                )

        elif entry_id.startswith("SAL_"):
            acc = r.get("account_name") or r.get("ledger_name")
            if not acc:
                continue

            for col, contra in [
                ("cash_amount", "Cash A/C"),
                ("bank1_amount", "Bank 1 A/C"),
                ("bank2_amount", "Bank 2 A/C"),
                ("bank3_amount", "Bank 3 A/C"),
                ("bank4_amount", "Bank 4 A/C"),
                ("bank5_amount", "Bank 5 A/C"),
                ("bank6_amount", "Bank 6 A/C"),
                ("bank7_amount", "Bank 7 A/C"),
                ("bank8_amount", "Bank 8 A/C"),
                ("bank9_amount", "Bank 9 A/C"),
                ("bank10_amount", "Bank 10 A/C"),
            ]:
                amt = float(r.get(col, 0) or 0)
                if amt <= 0:
                    continue

                postings.append(
                    {
                        "date": date,
                        "account": acc,
                        "side": "DR",
                        "contra": contra,
                        "amount": amt,
                    }
                )

                postings.append(
                    {
                        "date": date,
                        "account": contra,
                        "side": "CR",
                        "contra": acc,
                        "amount": amt,
                    }
                )

        # ---------- SALARY / ASSETS ----------
        elif entry_id.startswith(("FEE_", "SAL_", "MAN_")):
            acc = r.get("account_name") or r.get("ledger_name")
            if not acc:
                continue

            form = (r.get("form_name") or "").upper()

            side = "DR"
            if "RECEIPT" in form:
                side = "CR"

            for col, contra in [
                ("cash_amount", "Cash A/C"),
                ("bank1_amount", "Bank 1 A/C"),
                ("bank2_amount", "Bank 2 A/C"),
                ("bank3_amount", "Bank 3 A/C"),
                ("bank4_amount", "Bank 4 A/C"),
                ("bank5_amount", "Bank 5 A/C"),
                ("bank6_amount", "Bank 6 A/C"),
                ("bank7_amount", "Bank 7 A/C"),
                ("bank8_amount", "Bank 8 A/C"),
                ("bank9_amount", "Bank 9 A/C"),
                ("bank10_amount", "Bank 10 A/C"),
            ]:
                amt = float(r.get(col, 0) or 0)
                if amt > 0:
                    postings.append(
                        {
                            "date": date,
                            "account": acc,
                            "side": side,
                            "contra": contra,
                            "amount": amt,
                        }
                    )

        # ---------- EXPENSES ----------
        elif entry_id.startswith("EXP_"):
            for col, contra in [
                ("breakup_cash", "Cash A/C"),
                ("breakup_bank1", "Bank 1 A/C"),
                ("breakup_bank2", "Bank 2 A/C"),
                ("breakup_bank3", "Bank 3 A/C"),
                ("breakup_bank4", "Bank 4 A/C"),
                ("breakup_bank5", "Bank 5 A/C"),
                ("breakup_bank6", "Bank 6 A/C"),
                ("breakup_bank7", "Bank 7 A/C"),
                ("breakup_bank8", "Bank 8 A/C"),
                ("breakup_bank9", "Bank 9 A/C"),
                ("breakup_bank10", "Bank 10 A/C"),
            ]:
                if not r[col]:
                    continue
                breakup = ast.literal_eval(r[col])
                for acc, amt in breakup.items():
                    postings.append(
                        {
                            "date": date,
                            "account": acc,
                            "side": "DR",
                            "contra": contra,
                            "amount": float(amt),
                        }
                    )

        # ---------- OTHER RECEIPT ----------
        elif entry_id.startswith("OR_"):
            for col, contra in [
                ("breakup_cash", "Cash A/C"),
                ("breakup_bank1", "Bank 1 A/C"),
                ("breakup_bank2", "Bank 2 A/C"),
                ("breakup_bank3", "Bank 3 A/C"),
                ("breakup_bank4", "Bank 4 A/C"),
                ("breakup_bank5", "Bank 5 A/C"),
                ("breakup_bank6", "Bank 6 A/C"),
                ("breakup_bank7", "Bank 7 A/C"),
                ("breakup_bank8", "Bank 8 A/C"),
                ("breakup_bank9", "Bank 9 A/C"),
                ("breakup_bank10", "Bank 10 A/C"),
            ]:
                if not r[col]:
                    continue
                breakup = ast.literal_eval(r[col])
                for _, obj in breakup.items():
                    postings.append(
                        {
                            "date": date,
                            "account": obj.get("account"),
                            "side": "CR",
                            "contra": contra,
                            "amount": float(obj.get("amount", 0)),
                        }
                    )

        # ---------- OTHER PAYMENT ----------
        elif entry_id.startswith("OP_"):
            for col, contra in [
                ("breakup_cash", "Cash A/C"),
                ("breakup_bank1", "Bank 1 A/C"),
                ("breakup_bank2", "Bank 2 A/C"),
                ("breakup_bank3", "Bank 3 A/C"),
                ("breakup_bank4", "Bank 4 A/C"),
                ("breakup_bank5", "Bank 5 A/C"),
                ("breakup_bank6", "Bank 6 A/C"),
                ("breakup_bank7", "Bank 7 A/C"),
                ("breakup_bank8", "Bank 8 A/C"),
                ("breakup_bank9", "Bank 9 A/C"),
                ("breakup_bank10", "Bank 10 A/C"),
            ]:
                if not r[col]:
                    continue
                breakup = ast.literal_eval(r[col])
                for _, obj in breakup.items():
                    postings.append(
                        {
                            "date": date,
                            "account": obj.get("account"),
                            "side": "DR",
                            "contra": contra,
                            "amount": float(obj.get("amount", 0)),
                        }
                    )

        # ---------- JOURNAL ----------
        else:
            if not r.get("journal_entries"):
                continue
            entries = ast.literal_eval(r["journal_entries"])
            for e in entries:
                if e.get("debit", 0) > 0:
                    postings.append(
                        {
                            "date": date,
                            "account": e["account"],
                            "side": "DR",
                            "contra": "Journal",
                            "amount": float(e["debit"]),
                        }
                    )
                if e.get("credit", 0) > 0:
                    postings.append(
                        {
                            "date": date,
                            "account": e["account"],
                            "side": "CR",
                            "contra": "Journal",
                            "amount": float(e["credit"]),
                        }
                    )

    return pd.DataFrame(postings)


postings_df = build_postings(df)
ACCOUNT_LIST = sorted(postings_df["account"].dropna().unique())

BLOCKED_ACCOUNTS = {
    "Bank 1 A/C",
    "Bank 2 A/C",
    "Bank 3 A/C",
    "Bank 4 A/C",
    "Bank 5 A/C",
    "Bank 6 A/C",
    "Bank 7 A/C",
    "Cash A/C",
    "Bank 8 A/C",
    "Bank 9 A/C",
    "Bank 10 A/C",
}

ACCOUNT_LIST = [acc for acc in ACCOUNT_LIST if acc not in BLOCKED_ACCOUNTS]

# =========================================================
# DASH APP
# =========================================================
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])


def ledger_table(df, side):
    label = "To" if side == "DR" else "By"

    return dbc.Table(
        [
            html.Thead(
                html.Tr([html.Th("Date"), html.Th("Particulars"), html.Th("Amount")])
            ),
            html.Tbody(
                [
                    html.Tr(
                        [
                            html.Td(r.date),
                            html.Td(f"{label} {r.contra}"),
                            html.Td(f"{r.amount:,.2f}", className="text-end"),
                        ]
                    )
                    for r in df.itertuples()
                ]
            ),
            html.Tfoot(
                html.Tr(
                    [
                        html.Th(""),
                        html.Th("Total"),
                        html.Th(f"{df['amount'].sum():,.2f}", className="text-end"),
                    ]
                )
            ),
        ],
        bordered=True,
        size="sm",
    )


def get_layout():
    return dbc.Container(
        [
            # ================= HEADER =================
            dbc.Row(
                dbc.Col(
                    dbc.Card(
                        dbc.CardBody(
                            [
                                html.H3(
                                    "Ledger Statement Viewer",
                                    className="fw-bold mb-1 text-center",
                                ),
                                html.P(
                                    "Account-wise T-Account and Voucher Ledger",
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
            # ================= ACCOUNT SELECT =================
            dbc.Row(
                dbc.Col(
                    dbc.Card(
                        dbc.CardBody(
                            [
                                html.Label(
                                    "Select Ledger Account",
                                    className="fw-semibold mb-2",
                                ),
                                dbc.Button(
                                    "🔄 Refresh Accounts",
                                    id="refresh-accounts",
                                    size="sm",
                                    color="secondary",
                                    className="mb-2",
                                ),
                                dcc.Dropdown(
                                    id="ledger-account",
                                    options=[
                                        {"label": a, "value": a} for a in ACCOUNT_LIST
                                    ],
                                    placeholder="🔍 Type or select an account name...",
                                    searchable=True,
                                    clearable=True,
                                    className="ledger-dropdown",
                                ),
                                html.Small(
                                    "Start typing to quickly filter accounts",
                                    className="text-muted mt-1 d-block",
                                ),
                            ]
                        ),
                        className="shadow-sm border-0",
                    ),
                    md=8,
                    className="mx-auto mb-4",
                )
            ),
            # ================= LEDGER OUTPUT =================
            dbc.Row(
                dbc.Col(
                    dbc.Card(
                        dbc.CardBody(
                            html.Div(
                                id="ledger-output",
                                className="ledger-output",
                            )
                        ),
                        className="shadow-sm border-0",
                    ),
                    width=12,
                )
            ),
        ],
        fluid=True,
        className="bg-light min-vh-100 px-4",
    )


def register_callbacks(app):
    @app.callback(
        Output("ledger-output", "children"),
        Input("ledger-account", "value"),
    )
    def render_ledger(account):

        if not account:
            return ""

        acc_df = postings_df[postings_df["account"] == account]
        dr = acc_df[acc_df["side"] == "DR"].copy()
        cr = acc_df[acc_df["side"] == "CR"].copy()

        bal = dr["amount"].sum() - cr["amount"].sum()

        if bal > 0:
            cr = pd.concat(
                [
                    cr,
                    pd.DataFrame(
                        [{"date": "", "contra": "Balance C/d", "amount": bal}]
                    ),
                ]
            )
        elif bal < 0:
            dr = pd.concat(
                [
                    dr,
                    pd.DataFrame(
                        [{"date": "", "contra": "Balance C/d", "amount": abs(bal)}]
                    ),
                ]
            )

        vdf = voucher_df[voucher_df["particulars"] == account]

        voucher_table = dbc.Table(
            [
                html.Thead(
                    html.Tr(
                        [
                            html.Th("Date"),
                            html.Th("Particulars"),
                            html.Th("Vch Type"),
                            html.Th("Vch No"),
                            html.Th("Debit"),
                            html.Th("Credit"),
                        ]
                    )
                ),
                html.Tbody(
                    [
                        html.Tr(
                            [
                                html.Td(r.date),
                                html.Td(r.particulars),
                                html.Td(r.vch_type),
                                html.Td(r.vch_no),
                                html.Td(f"{r.debit:,.2f}" if r.debit else ""),
                                html.Td(f"{r.credit:,.2f}" if r.credit else ""),
                            ]
                        )
                        for r in vdf.itertuples()
                    ]
                ),
            ],
            bordered=True,
            striped=True,
            hover=True,
            size="sm",
        )

        return dbc.Container(
            [
                html.H4(account, className="text-center my-3"),
                dbc.Row(
                    [
                        dbc.Col(ledger_table(dr, "DR"), md=6),
                        dbc.Col(ledger_table(cr, "CR"), md=6),
                    ]
                ),
                html.Hr(),
                html.H5("Ledger Vouchers"),
                voucher_table,
            ]
        )

    @app.callback(
        Output("ledger-account", "options"),
        Output("ledger-account", "value"),
        Input("refresh-accounts", "n_clicks"),
        State("session", "data"),
        prevent_initial_call=True,
    )
    def refresh_account_list(_, SessionData):

        accounts = reload_data(SessionData)

        return (
            [{"label": a, "value": a} for a in accounts],
            None,  # clear selection after refresh
        )
