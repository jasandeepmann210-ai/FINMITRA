import dash
from dash import html, dcc, Input, Output, State, ALL
import dash_bootstrap_components as dbc
import pandas as pd
import csv
import os
import json
from datetime import datetime
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader
import io
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from dash import dcc
from datetime import datetime, date


# --------------------------------------------------
# App setup
# --------------------------------------------------
external_stylesheets = [
    dbc.themes.BOOTSTRAP,
    "https://cdn.jsdelivr.net/npm/bootstrap-icons@1.11.1/font/bootstrap-icons.css",
]

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
app.title = "Institution Forms Portal"


# --------------------------------------------------
# Book / Form Definitions
# --------------------------------------------------
FORMS = [
    ("ENTRY HUB", "bi-collection"),
    ("FEES RECEIPT", "bi-cash-coin"),
    ("OTHER RECEIPT", "bi-journal-plus"),
    ("EXPENSES", "bi-cash-stack"),
    ("SALARY PAYMENT", "bi-person-lines-fill"),
    ("OTHER PAYMENT", "bi-credit-card"),
    ("JOURNAL BOOK", "bi-journal-text"),
    ("CONTRA ENTRY", "bi-arrow-left-right"),
]

GROUP = [
    "Direct Income",
    "Indirect Income",
    "Indirect Expenses",
    "Fixed Assets",
    "Investments",
    "Loans and Advances",
    "Cash-in-Hand",
    "Bank Accounts",
    "Current Assets",
    "Current Liabilities",
    "Accrued Income",
    "Outstanding Expense",
    "Prepaid Expense",
    "Unearned Revenue",
    "Provisions (Bad Debts, Warranty)",
    "Depreciation",
    "Deferred Tax",
    "Non-current liabilities Secured loans",
    "Non-current liabilities Unsecured loans",
    "Sundry debtors",
    "Sundry creditors",
    "Inventories",
    "Reserve & Surplus",
]

FS_GROUPS = [
    "BS",
    "I&E",
]

FORM_NORMALIZER = {
    "FEE": "OTHER_RECEIPT",
    "OTHER_RECEIPT": "OTHER_RECEIPT",
    "EXPENSE_HEADS": "OTHER_PAYMENT",
    "SALARY": "OTHER_PAYMENT",
    "OTHER_PAYMENT": "OTHER_PAYMENT",
    "JOURNAL BOOK": "JOURNAL BOOK",
    "DECLARE ASSETS": "OTHER_PAYMENT",
    "DECLARE OTHER BS ITEMS": "OTHER_PAYMENT",
}


GROUP_FORM_RULES = {
    # -------- I&E --------
    "Direct Income": {
        "fs": "I&E",
        "forms": ["OTHER_PAYMENT", "OTHER_RECEIPT"],
    },
    "Indirect Income": {
        "fs": "I&E",
        "forms": ["OTHER_PAYMENT", "OTHER_RECEIPT"],
    },
    "Indirect Expenses": {
        "fs": "I&E",
        "forms": ["OTHER_PAYMENT", "OTHER_RECEIPT"],
    },
    "Depreciation": {
        "fs": "I&E",
        "forms": ["OTHER_PAYMENT", "OTHER_RECEIPT"],
    },
    # -------- BS --------
    "Fixed Assets": {
        "fs": "BS",
        "forms": ["OTHER_PAYMENT", "OTHER_RECEIPT"],
    },
    "Investments": {
        "fs": "BS",
        "forms": ["OTHER_PAYMENT", "OTHER_RECEIPT"],
    },
    "Loans and Advances": {
        "fs": "BS",
        "forms": ["OTHER_PAYMENT", "OTHER_RECEIPT"],
    },
    "Cash-in-Hand": {
        "fs": "BS",
        "forms": ["OTHER_PAYMENT", "OTHER_RECEIPT"],
    },
    "Bank Accounts": {
        "fs": "BS",
        "forms": ["OTHER_RECEIPT", "OTHER_PAYMENT"],
    },
    "Current Assets": {
        "fs": "BS",
        "forms": ["OTHER_PAYMENT", "OTHER_RECEIPT"],
    },
    "Current Liabilities": {
        "fs": "BS",
        "forms": ["OTHER_PAYMENT", "OTHER_RECEIPT"],
    },
    "Accrued Income": {
        "fs": "BS",
        "forms": ["OTHER_PAYMENT", "OTHER_RECEIPT"],
    },
    "Outstanding Expense": {
        "fs": "BS",
        "forms": ["OTHER_PAYMENT", "OTHER_RECEIPT"],
    },
    "Prepaid Expense": {
        "fs": "BS",
        "forms": ["OTHER_PAYMENT", "OTHER_RECEIPT"],
    },
    "Unearned Revenue": {
        "fs": "BS",
        "forms": ["OTHER_PAYMENT", "OTHER_RECEIPT"],
    },
    "Provisions (Bad Debts, Warranty)": {
        "fs": "BS",
        "forms": ["OTHER_PAYMENT", "OTHER_RECEIPT"],
    },
    "Deferred Tax": {
        "fs": "BS",
        "forms": ["OTHER_PAYMENT", "OTHER_RECEIPT"],
    },
    "Non-current liabilities Secured loans": {
        "fs": "BS",
        "forms": ["OTHER_PAYMENT", "OTHER_RECEIPT"],
    },
    "Non-current liabilities Unsecured loans": {
        "fs": "BS",
        "forms": ["OTHER_PAYMENT", "OTHER_RECEIPT"],
    },
    "Sundry debtors": {
        "fs": "BS",
        "forms": ["OTHER_PAYMENT", "OTHER_RECEIPT"],
    },
    "Sundry creditors": {
        "fs": "BS",
        "forms": ["OTHER_PAYMENT", "OTHER_RECEIPT"],
    },
    "Inventories": {
        "fs": "BS",
        "forms": ["OTHER_PAYMENT", "OTHER_RECEIPT"],
    },
    "Reserve & Surplus": {
        "fs": "BS",
        "forms": ["OTHER_PAYMENT", "OTHER_RECEIPT"],
    },
}


FORM = [
    "OTHER_RECEIPT",
    "OTHER_PAYMENT",
]

FORM_LEDGER_MAP = {
    "FEE": "FEES RECEIPT",
    "EXPENSE_HEADS": "EXPENSES",
    "OTHER_RECEIPT": "OTHER RECEIPT",
    "OTHER_PAYMENT": "OTHER PAYMENT",
    "SALARY": "SALARY PAYMENT",
    "JOURNAL BOOK": "JOURNAL BOOK",
}


def get_default_fy():
    today = datetime.now()
    current_year = today.year

    fy_cutoff = datetime(current_year, 3, 31)

    if today <= fy_cutoff:
        return f"FY{str(current_year)[-2:]}"
    else:
        return f"FY{str(current_year + 1)[-2:]}"


def get_fy_date_range(selected_fy):

    if not selected_fy:
        return None, None

    fy_year = int(selected_fy.replace("FY", ""))  # 26
    end_year = 2000 + fy_year  # 2026
    start_year = end_year - 1  # 2025

    start_date = date(start_year, 4, 1)
    end_date = date(end_year, 3, 31)

    return start_date, end_date


def load_bank_labels(SessionData):

    BANK_LABEL_PATH = (
        "/var/Data/" + str(SessionData["username"]) + "/bank_name_static.csv"
    )

    if not os.path.exists(BANK_LABEL_PATH):
        # fallback if CSV missing
        return {f"BANK{i}": f"Bank {i}" for i in range(1, 11)}

    df = pd.read_csv(BANK_LABEL_PATH)
    return dict(zip(df["bank_code"], df["bank_label"]))


def resolve_allowed_form_from_group(group, user_selected_form=None):

    if not group or group not in GROUP_FORM_RULES:
        return user_selected_form

    allowed_forms = GROUP_FORM_RULES[group]["forms"]

    if user_selected_form:
        user_clean = user_selected_form.strip().upper()

        allowed_clean = [f.strip().upper() for f in allowed_forms]

        if user_clean in allowed_clean:
            return allowed_forms[allowed_clean.index(user_clean)]

    if allowed_forms:
        return allowed_forms[0]

    return user_selected_form


def append_to_mapper(line_item, group, fs_group, form, SessionData):
    """
    Appends a new account mapping into data/mapper.xlsx
    Schema EXACTLY matches mapper.xlsx
    """

    mapper_path = "/var/Data/" + str(SessionData["username"]) + "/Mapper.xlsx"
    os.makedirs("/var/Data/" + str(SessionData["username"]), exist_ok=True)

    new_row = {
        "LINE_ITEM": line_item.strip(),
        "GROUP": group.strip(),
        "FS_GROUP": fs_group.strip(),
        "FORM": form.strip(),
    }

    if os.path.exists(mapper_path):
        df = pd.read_excel(mapper_path)

        # ✅ DUPLICATE GUARD (correct column)
        if (
            df["LINE_ITEM"]
            .astype(str)
            .str.lower()
            .str.strip()
            .eq(line_item.lower().strip())
            .any()
        ):
            print("⚠️ LINE_ITEM already exists in mapper.xlsx")
            return
    else:
        df = pd.DataFrame(columns=new_row.keys())

    df.loc[len(df)] = new_row
    df.to_excel(mapper_path, index=False)

    print("✅ mapper.xlsx updated →", line_item)


# --------------------------------------------------
# Icon Card Component (3 rows × 2 columns)
# --------------------------------------------------
def icon_card(idx, title, icon):
    return dbc.Col(
        html.Div(
            dbc.Card(
                dbc.CardBody(
                    [
                        html.I(
                            className=f"bi {icon}",
                            style={"fontSize": "52px", "color": "#0d6efd"},
                        ),
                        html.H5(title, className="fw-semibold text-center mt-2"),
                    ],
                    className="d-flex flex-column justify-content-center align-items-center",
                ),
                className="shadow-sm border-0",
                style={"borderRadius": "14px", "minHeight": "180px"},
            ),
            id={"type": "open-form", "index": idx},
            n_clicks=0,
            style={"cursor": "pointer"},
        ),
        md=6,
        sm=6,
        xs=12,
        className="mb-4",
    )


def create_account_post_entry_form(SessionData):

    default_fy = get_default_fy()
    start_date, end_date = get_fy_date_range(default_fy)

    BANK_LABELS = load_bank_labels(SessionData)

    PAYMENT_OPTIONS = [{"label": "Cash", "value": "CASH"}] + [
        {
            "label": BANK_LABELS.get(f"BANK{i}", f"Bank {i}"),
            "value": f"BANK{i}",
        }
        for i in range(1, 11)
    ]

    return dbc.Container(
        [
            html.H4("Entry Hub", className="mb-4"),
            # ==================================================
            # ACCOUNT METADATA
            # ==================================================
            dbc.Row(
                [
                    dbc.Col(
                        [
                            dbc.Label("Account / Item Name"),
                            html.Div(
                                [
                                    dbc.Input(
                                        id="ca-account-name",
                                        list="account-name-list",
                                        placeholder="Type new account or select existing",
                                    ),
                                    html.Datalist(id="account-name-list"),
                                ]
                            ),
                        ],
                        md=6,
                    ),
                    dbc.Col(
                        [
                            dbc.Label("Account Group"),
                            dcc.Dropdown(
                                options=[{"label": g, "value": g} for g in GROUP],
                                id="ca-account-group",
                            ),
                        ],
                        md=6,
                    ),
                ],
                className="mb-3",
            ),
            dbc.Row(
                [
                    dbc.Col(
                        [
                            dbc.Label("FS Group"),
                            dcc.Dropdown(
                                options=[{"label": g, "value": g} for g in FS_GROUPS],
                                id="ca-fs-group",
                            ),
                        ],
                        md=6,
                    ),
                    dbc.Col(
                        [
                            dbc.Label("Allowed Form"),
                            dcc.Dropdown(
                                options=[{"label": f, "value": f} for f in FORM],
                                id="ca-allowed-form",
                            ),
                        ],
                        md=6,
                    ),
                ],
                className="mb-4",
            ),
            html.Hr(),
            # ==================================================
            # OPENING / TRANSACTION ENTRY
            # ==================================================
            html.H5("Opening / Transaction Entry"),
            # ---------- OPENING BALANCE TOGGLE ----------
            dbc.Row(
                [
                    dbc.Col(
                        dbc.Checkbox(
                            id="ca-opening-balance-flag",
                            label="This is an Opening Balance (BS only)",
                            value=False,
                        ),
                        md=6,
                    )
                ],
                className="mb-3",
            ),
            # ---------- OPENING BALANCE INPUT ----------
            html.Div(
                id="ca-opening-balance-block",
                children=[
                    dbc.Row(
                        [
                            dbc.Col(
                                [
                                    dbc.Label("Opening Balance Amount"),
                                    dbc.Input(
                                        id="ca-opening-balance",
                                        type="number",
                                        min=0,
                                    ),
                                ],
                                md=4,
                            )
                        ],
                        className="mb-3",
                    )
                ],
                style={"display": "none"},
            ),
            # ---------- DATE ----------
            dbc.Row(
                [
                    dbc.Col(
                        [
                            dbc.Label("Transaction Date"),
                            dcc.DatePickerSingle(
                                id="ca-date",
                                display_format="DD-MM-YYYY",
                                min_date_allowed=start_date,
                                max_date_allowed=end_date,
                            ),
                        ],
                        md=4,
                    ),
                ],
                className="mb-3",
            ),
            # ==================================================
            # PAYMENT MODE (HIDDEN FOR JOURNAL BOOK)
            # ==================================================
            html.Div(
                id="ca-channel-block",
                children=[
                    dbc.Row(
                        [
                            dbc.Col(
                                [
                                    dbc.Label("Payment Mode"),
                                    dcc.Dropdown(
                                        id="ca-payment-mode",
                                        options=PAYMENT_OPTIONS,
                                        value="CASH",
                                        clearable=False,
                                    ),
                                ],
                                md=4,
                            ),
                            dbc.Col(
                                [
                                    dbc.Label("Amount"),
                                    dbc.Input(
                                        id="ca-payment-amount",
                                        type="number",
                                        min=0,
                                    ),
                                ],
                                md=4,
                            ),
                        ],
                        className="mb-3",
                    )
                ],
            ),
            dbc.Button(
                "Create Account & Post Entry",
                id="submit-create-account",
                color="primary",
                className="mt-3",
            ),

            dbc.Button(
                "Sell Asset",
                id="sell-asset-btn",
                color="danger",
                className="mt-3 ms-2",
            ),
        ],
        fluid=True,
    )


def contra_entry_form(SessionData):

    BANK_LABELS = load_bank_labels(SessionData)

    default_fy = get_default_fy()
    start_date, end_date = get_fy_date_range(default_fy)

    CHANNELS = [{"label": "Cash", "value": "CASH"}] + [
        {
            "label": BANK_LABELS.get(f"BANK{i}", f"Bank {i}"),
            "value": f"BANK{i}",
        }
        for i in range(1, 11)
    ]

    return dbc.Container(
        [
            html.H4("Contra Entry"),
            dbc.Row(
                [
                    dbc.Col(
                        [
                            dbc.Label("Debit Account"),
                            dcc.Dropdown(id="contra-debit", options=CHANNELS),
                        ],
                        md=4,
                    ),
                    dbc.Col(
                        [
                            dbc.Label("Credit Account"),
                            dcc.Dropdown(id="contra-credit", options=CHANNELS),
                        ],
                        md=4,
                    ),
                    dbc.Col(
                        [
                            dbc.Label("Amount"),
                            dbc.Input(id="contra-amount", type="number", min=0),
                        ],
                        md=4,
                    ),
                ],
                className="mb-3",
            ),
            dbc.Row(
                [
                    dbc.Col(
                        [
                            dbc.Label("Date"),
                            dcc.DatePickerSingle(
                                id="contra-date",
                                display_format="DD-MM-YYYY",
                                min_date_allowed=start_date,
                                max_date_allowed=end_date,
                            ),
                        ],
                        md=4,
                    ),
                ]
            ),
            dbc.Button("Submit Contra Entry", id="submit-contra", color="warning"),
        ],
        fluid=True,
    )


# --------------------------------------------------
# Receipt Number Generator
# --------------------------------------------------
def generate_receipt_no():
    if os.path.exists("master_database.csv"):
        df = pd.read_csv("master_database.csv")
        last_seq = len(df)
    else:
        last_seq = 0
    return f"RCPT-{datetime.now().year}-{last_seq+1:06d}"


# --------------------------------------------------
# Student Fee Heads
# --------------------------------------------------
FEE_HEADS = [
    "Admission Fees",
    "Tuition Fees",
    "Registration Fees",
    "Examination Fees",
    "Library Fees",
    "Laboratory Fees",
    "Sports / Games Fees",
    "Transportation Fees",
    "Uniform Fees",
    "Activity / Co-curricular Fees",
    "Development Fees",
    "Computer / Technology Fees",
]


# --------------------------------------------------
# Student Fee Receipt Form
# --------------------------------------------------
def student_fee_receipt_form(ledger_group, SessionData):

    default_fy = get_default_fy()
    start_date, end_date = get_fy_date_range(default_fy)

    receipt_no = generate_receipt_no()
    BANK_LABELS = load_bank_labels(SessionData)

    PAYMENT_OPTIONS = [{"label": "Cash", "value": "CASH"}] + [
        {
            "label": BANK_LABELS.get(f"BANK{i}", f"Bank {i}"),
            "value": f"BANK{i}",
        }
        for i in range(1, 11)
    ]

    return dbc.Container(
        [
            # ---------------- HEADER ----------------
            dbc.Row(
                [
                    dbc.Col(
                        [
                            dbc.Label("RECEIPT NO."),
                            dbc.Input(
                                id="fee-receipt-no", value=receipt_no, disabled=True
                            ),
                        ],
                        md=4,
                    ),
                    dbc.Col(
                        [
                            dbc.Label("STUDENT NAME / Roll / Class"),
                            dcc.Dropdown(
                                id="student-name",
                                options=[],  # loaded dynamically
                                placeholder="Search Student",
                                searchable=True,
                            ),
                        ],
                        md=4,
                    ),
                    dbc.Col(
                        [
                            dbc.Label("DATE"),
                            dcc.DatePickerSingle(
                                id="fee-receipt-date",
                                display_format="DD-MM-YYYY",
                                min_date_allowed=start_date,
                                max_date_allowed=end_date,
                            ),
                        ],
                        md=4,
                    ),
                ],
                className="mb-3",
            ),
            dbc.Alert(f"Ledger Group: {ledger_group}", color="info", className="mb-3"),
            # ---------------- GLOBAL PAYMENT MODE ----------------
            dbc.Row(
                [
                    dbc.Col(
                        [
                            dbc.Label("PAYMENT MODE"),
                            dcc.Dropdown(
                                id="fee-payment-mode",
                                options=PAYMENT_OPTIONS,
                                value="CASH",
                                clearable=False,
                            ),
                        ],
                        md=4,
                    ),
                ],
                className="mb-4",
            ),
            # ---------------- TABLE HEADER ----------------
            dbc.Row(
                [
                    dbc.Col(html.B("FEE HEAD"), md=6),
                    dbc.Col(html.B("AMOUNT"), md=3),
                ],
                className="border-bottom pb-2 mb-2",
            ),
            # ---------------- FEE ROWS ----------------
            *[
                dbc.Row(
                    [
                        dbc.Col(head, md=6),
                        dbc.Col(
                            dbc.Input(
                                id=f"fee-amount-{i}",
                                type="number",
                                min=0,
                            ),
                            md=3,
                        ),
                    ],
                    className="mb-2",
                )
                for i, head in enumerate(FEE_HEADS)
            ],
            # ---------------- ACTION BUTTONS ----------------
            dbc.Row(
                [
                    dbc.Col(
                        dbc.Button(
                            "Submit Receipt",
                            id="submit-fee-receipt",
                            color="success",
                            className="me-2",
                        ),
                        width="auto",
                    ),
                    dbc.Col(
                        dbc.Button(
                            "Print Receipt (PDF)",
                            id="print-fee-receipt",
                            color="secondary",
                            outline=True,
                        ),
                        width="auto",
                    ),
                ],
                className="mt-3",
            ),
        ],
        fluid=True,
    )


# --------------------------------------------------
# Expense Form
# --------------------------------------------------
EXPENSE_HEADS = [
    "Salaries & Wages",
    "Non-Teaching Staff Salaries",
    "Staff Welfare Expenses",
    "Recruitment & Training Expenses",
    "Electricity Expenses",
    "Water Charges",
    "Internet & Telephone Expenses",
    "Fuel & Generator Expenses",
    "Building Rent / Lease Charges",
    "Repairs & Maintenance",
]


def expense_day_voucher_form(SessionData):

    default_fy = get_default_fy()
    start_date, end_date = get_fy_date_range(default_fy)

    BANK_LABELS = load_bank_labels(SessionData)

    PAYMENT_OPTIONS = [{"label": "Cash", "value": "CASH"}] + [
        {
            "label": BANK_LABELS.get(f"BANK{i}", f"Bank {i}"),
            "value": f"BANK{i}",
        }
        for i in range(1, 11)
    ]

    return dbc.Container(
        [
            # Header
            dbc.Row(
                [
                    dbc.Col(
                        [
                            dbc.Label("DAY VOUCHER"),
                            dbc.Input(
                                value=f"EXP-{datetime.now().strftime('%Y%m%d')}",
                                disabled=True,
                                className="fw-bold",
                            ),
                        ],
                        md=6,
                    ),
                    dbc.Col(
                        [
                            dbc.Label("DATE"),
                            dcc.DatePickerSingle(
                                id="expense-date",
                                display_format="DD-MM-YYYY",
                                min_date_allowed=start_date,
                                max_date_allowed=end_date,
                            ),
                        ],
                        md=6,
                    ),
                ],
                className="mb-3",
            ),
            dbc.Alert(
                "Ledger Group: Expenses",
                color="info",
                className="mb-3",
            ),
            # ---------------- Table Header ----------------
            dbc.Row(
                [
                    dbc.Col(html.B("EXPENSES"), md=5),
                    dbc.Col(html.B("PAYMENT MODE"), md=3),
                    dbc.Col(html.B("AMOUNT"), md=2),
                ],
                className="border-bottom pb-2 mb-2",
            ),
            # ---------------- Expense Rows ----------------
            *[
                dbc.Row(
                    [
                        # Expense Head
                        dbc.Col(head, md=5),
                        # Payment Mode (Cash default)
                        dbc.Col(
                            dcc.Dropdown(
                                id=f"exp-mode-{i}",
                                options=PAYMENT_OPTIONS,
                                value="CASH",
                                clearable=False,
                            ),
                            md=3,
                        ),
                        # Amount
                        dbc.Col(
                            dbc.Input(
                                id=f"exp-amount-{i}",
                                type="number",
                                min=0,
                            ),
                            md=2,
                        ),
                    ],
                    className="mb-2",
                )
                for i, head in enumerate(EXPENSE_HEADS)
            ],
            dbc.Button(
                "Submit Expense Voucher",
                id="submit-expense-voucher",
                color="danger",
                className="mt-3",
            ),
        ],
        fluid=True,
    )


# --------------------------------------------------
# Salary Form
# --------------------------------------------------


def load_statutory_config(SessionData):

    path = f"/var/Data/{SessionData['username']}/statutory_config.json"

    default_config = {
        "PF_RATE": 0.1275,
        "ESI_RATE": 0.0375,
        "TDS_RATE": 0.10,
        "PF_ENABLED": True,
        "ESI_ENABLED": True,
        "TDS_ENABLED": True,
    }

    if not os.path.exists(path):
        return default_config

    with open(path, "r") as f:
        return json.load(f)


SALARY_COMPONENTS = [
    "Basic Pay",
    "D.A.",
    "Other Allowances",
    "HRA",
]

PF_RATE = 0.1275
ESI_RATE = 0.0375
TDS_RATE = 0.10


def salary_payment_form(SessionData):

    default_fy = get_default_fy()
    start_date, end_date = get_fy_date_range(default_fy)

    BANK_LABELS = load_bank_labels(SessionData)

    PAYMENT_OPTIONS = [{"label": "Cash", "value": "CASH"}] + [
        {
            "label": BANK_LABELS.get(f"BANK{i}", f"Bank {i}"),
            "value": f"BANK{i}",
        }
        for i in range(1, 11)
    ]

    return dbc.Container(
        [
            # Header
            dbc.Row(
                [
                    dbc.Col(
                        [
                            dbc.Label("SALARY ACCOUNT"),
                            dbc.Input(
                                value=f"SAL-{datetime.now().strftime('%Y%m%d')}",
                                disabled=True,
                                className="fw-bold",
                            ),
                        ],
                        md=4,
                    ),
                    dbc.Col(
                        [
                            dbc.Label("DATE"),
                            dcc.DatePickerSingle(
                                id="salary-date",
                                display_format="DD-MM-YYYY",
                                min_date_allowed=start_date,
                                max_date_allowed=end_date,
                            ),
                        ],
                        md=4,
                    ),
                    dbc.Col(
                        [
                            dbc.Label("MONTH OF PAYMENT"),
                            dbc.Input(
                                type="month",
                                value=datetime.today().strftime("%Y-%m"),
                            ),
                        ],
                        md=4,
                    ),
                ],
                className="mb-3",
            ),
            dbc.Row(
                [
                    dbc.Col(
    [
        dbc.Label("A/C NAME"),
        dcc.Dropdown(
            id="employee-name",
            options=[],   # dynamic load hoga
            placeholder="Search Teacher",
            searchable=True,
            clearable=False,
        ),
    ],
    md=6,
)
                ],
                className="mb-3",
            ),
            dbc.Alert(
                "Ledger Group: Salary & Wages Expense",
                color="info",
                className="mb-3",
            ),
            # Salary components
            *[
                dbc.Row(
                    [
                        dbc.Col(comp, md=6),
                        dbc.Col(
                            dbc.Input(
                                type="number",
                                min=0,
                                id=f"salary-comp-{i}",
                            ),
                            md=3,
                        ),
                    ],
                    className="mb-2",
                )
                for i, comp in enumerate(SALARY_COMPONENTS)
            ],
            html.Hr(),
            dbc.Button(
                "Edit Statutory %", id="toggle-statutory-edit", size="sm", color="link"
            ),
            html.Div(
                id="statutory-edit-block",
                style={"display": "none"},
                children=[
                    dbc.Row(
                        [
                            dbc.Col(
                                dbc.Input(
                                    id="edit-pf-rate",
                                    type="number",
                                    step=0.0001,
                                    placeholder="Enter PF Rate",
                                ),
                                md=4,
                            ),
                            dbc.Col(
                                dbc.Input(
                                    id="edit-esi-rate",
                                    type="number",
                                    step=0.0001,
                                    placeholder="Enter ESI Rate",
                                ),
                                md=4,
                            ),
                            dbc.Col(
                                dbc.Input(
                                    id="edit-tds-rate",
                                    type="number",
                                    step=0.0001,
                                    placeholder="Enter TDS Rate",
                                ),
                                md=4,
                            ),
                        ],
                        className="mb-2",
                    ),
                    dbc.Button(
                        "Save", id="save-inline-statutory", size="sm", color="primary"
                    ),
                ],
            ),
            # Deductions (calculated)
            dbc.Row(
                [
                    dbc.Col(html.Span(id="pf-label"), md=6),
                    dbc.Col(dbc.Input(id="pf-amount", disabled=True), md=3),
                ],
                className="mb-2",
            ),
            dbc.Row(
                [
                    dbc.Col(html.Span(id="esi-label"), md=6),
                    dbc.Col(dbc.Input(id="esi-amount", disabled=True), md=3),
                ],
                className="mb-2",
            ),
            dbc.Row(
                [
                    dbc.Col(html.Span(id="tds-label"), md=6),
                    dbc.Col(dbc.Input(id="tds-amount", disabled=True), md=3),
                ],
                className="mb-2",
            ),
            html.Hr(),
            # Net Pay + Source
            dbc.Row(
                [
                    dbc.Col("NET PAY", md=6),
                    dbc.Col(dbc.Input(id="net-pay", disabled=True), md=3),
                ],
                className="mb-3",
            ),
            dbc.Row(
                [
                    dbc.Col(
                        [
                            dbc.Label("SOURCE OF PAYMENT"),
                            dcc.Dropdown(
                                id="salary-payment-mode",
                                options=PAYMENT_OPTIONS,
                                value="CASH",  # ✅ sensible default
                                clearable=False,
                            ),
                        ],
                        md=6,
                    )
                ],
                className="mb-3",
            ),
            dbc.Row(
            [
                dbc.Col(
                    dbc.Button(
                        "Submit Salary Voucher",
                        id="submit-salary-voucher",
                        color="warning",
                        className="w-100"
                    ),
                    md=4,
                ),
                dbc.Col(
                    dbc.Button(
                        "Download Salary Slip (PDF)",
                        id="print-salary-slip",
                        color="secondary",
                        outline=True,
                        className="w-100"
                    ),
                    md=4,
                ),
            ],
            className="mt-3",
        )
        ],
        fluid=True,
    )


# --------------------------------------------------
# Other Receipt Form
# --------------------------------------------------
OTHER_RECEIPT_HEADS = [
    "Interest Income",
    "Donations",
]


def other_receipt_form(SessionData):

    default_fy = get_default_fy()
    start_date, end_date = get_fy_date_range(default_fy)

    BANK_LABELS = load_bank_labels(SessionData)

    PAYMENT_OPTIONS = [{"label": "Cash", "value": "CASH"}] + [
        {
            "label": BANK_LABELS.get(f"BANK{i}", f"Bank {i}"),
            "value": f"BANK{i}",
        }
        for i in range(1, 11)
    ]

    return dbc.Container(
        [
            # Header
            dbc.Row(
                [
                    dbc.Col(
                        [
                            dbc.Label("OTHER RECEIPT"),
                            dbc.Input(
                                value=f"OR-{datetime.now().strftime('%Y%m%d')}",
                                disabled=True,
                                className="fw-bold",
                            ),
                        ],
                        md=4,
                    ),
                    dbc.Col(
                        [
                            dbc.Label("CREATE"),
                            dbc.Input(value="AUTO", disabled=True),
                        ],
                        md=4,
                    ),
                    dbc.Col(
                        [
                            dbc.Label("DATE"),
                            dcc.DatePickerSingle(
                                id="other-receipt-date",
                                display_format="DD-MM-YYYY",
                                min_date_allowed=start_date,
                                max_date_allowed=end_date,
                            ),
                        ],
                        md=4,
                    ),
                ],
                className="mb-3",
            ),
            dbc.Alert(
                "Ledger Group: Other Income / Receipts",
                color="info",
                className="mb-3",
            ),
            # -------- TABLE HEADER --------
            dbc.Row(
                [
                    dbc.Col(html.B("RECEIPT"), md=4),
                    dbc.Col(html.B("ACCOUNT NAME"), md=3),
                    dbc.Col(html.B("PAYMENT MODE"), md=3),
                    dbc.Col(html.B("AMOUNT"), md=2),
                ],
                className="border-bottom pb-2 mb-2",
            ),
            # -------- RECEIPT ROWS --------
            *[
                dbc.Row(
                    [
                        # Receipt Head
                        dbc.Col(head, md=4),
                        # Account / Party Name
                        dbc.Col(
                            dbc.Input(
                                type="text",
                                placeholder="Account / Party Name",
                                id=f"or-account-{i}",
                            ),
                            md=3,
                        ),
                        # Payment Mode (Cash default)
                        dbc.Col(
                            dcc.Dropdown(
                                id=f"or-mode-{i}",
                                options=PAYMENT_OPTIONS,
                                value="CASH",
                                clearable=False,
                            ),
                            md=3,
                        ),
                        # Amount
                        dbc.Col(
                            dbc.Input(
                                id=f"or-amount-{i}",
                                type="number",
                                min=0,
                            ),
                            md=2,
                        ),
                    ],
                    className="mb-2",
                )
                for i, head in enumerate(OTHER_RECEIPT_HEADS)
            ],
            dbc.Button(
                "Submit Other Receipt",
                id="submit-other-receipt",
                color="success",
                className="mt-3",
            ),
        ],
        fluid=True,
    )


# --------------------------------------------------
# Other Payment Form
# --------------------------------------------------
OTHER_PAYMENT_HEADS = [
    "Interest on Loan Paid",
]


def other_payment_form(SessionData):

    default_fy = get_default_fy()
    start_date, end_date = get_fy_date_range(default_fy)

    BANK_LABELS = load_bank_labels(SessionData)

    PAYMENT_OPTIONS = [{"label": "Cash", "value": "CASH"}] + [
        {
            "label": BANK_LABELS.get(f"BANK{i}", f"Bank {i}"),
            "value": f"BANK{i}",
        }
        for i in range(1, 11)
    ]

    return dbc.Container(
        [
            # Header
            dbc.Row(
                [
                    dbc.Col(
                        [
                            dbc.Label("OTHER PAYMENTS"),
                            dbc.Input(
                                value=f"OP-{datetime.now().strftime('%Y%m%d')}",
                                disabled=True,
                                className="fw-bold",
                            ),
                        ],
                        md=4,
                    ),
                    dbc.Col(
                        [
                            dbc.Label("CREATE"),
                            dbc.Input(value="AUTO", disabled=True),
                        ],
                        md=4,
                    ),
                    dbc.Col(
                        [
                            dbc.Label("DATE"),
                            dcc.DatePickerSingle(
                                id="other-payment-date",
                                display_format="DD-MM-YYYY",
                                min_date_allowed=start_date,
                                max_date_allowed=end_date,
                            ),
                        ],
                        md=4,
                    ),
                ],
                className="mb-3",
            ),
            dbc.Alert(
                "Ledger Group: Other Payments / Outgoings",
                color="info",
                className="mb-3",
            ),
            # -------- TABLE HEADER --------
            dbc.Row(
                [
                    dbc.Col(html.B("PAYMENT"), md=4),
                    dbc.Col(html.B("ACCOUNT NAME"), md=3),
                    dbc.Col(html.B("PAYMENT MODE"), md=3),
                    dbc.Col(html.B("AMOUNT"), md=2),
                ],
                className="border-bottom pb-2 mb-2",
            ),
            # -------- PAYMENT ROWS --------
            *[
                dbc.Row(
                    [
                        # Payment Head
                        dbc.Col(head, md=4),
                        # Account / Party Name
                        dbc.Col(
                            dbc.Input(
                                type="text",
                                placeholder="Account / Party Name",
                                id=f"op-account-{i}",
                            ),
                            md=3,
                        ),
                        # Payment Mode (Cash default)
                        dbc.Col(
                            dcc.Dropdown(
                                id=f"op-mode-{i}",
                                options=PAYMENT_OPTIONS,
                                value="CASH",
                                clearable=False,
                            ),
                            md=3,
                        ),
                        # Amount
                        dbc.Col(
                            dbc.Input(
                                id=f"op-amount-{i}",
                                type="number",
                                min=0,
                            ),
                            md=2,
                        ),
                    ],
                    className="mb-2",
                )
                for i, head in enumerate(OTHER_PAYMENT_HEADS)
            ],
            dbc.Button(
                "Submit Other Payment",
                id="submit-other-payment",
                color="danger",
                className="mt-3",
            ),
        ],
        fluid=True,
    )


# --------------------------------------------------
# Journal Book Form
# --------------------------------------------------

JOURNAL_ROWS = 2  # can be increased later


def journal_book_form(SessionData):

    default_fy = get_default_fy()
    start_date, end_date = get_fy_date_range(default_fy)

    return dbc.Container(
        [
            # Header
            dbc.Row(
                [
                    dbc.Col(
                        [
                            dbc.Label("JOURNAL BOOK"),
                            dbc.Input(
                                value=f"JV-{datetime.now().strftime('%Y%m%d')}",
                                disabled=True,
                                className="fw-bold",
                            ),
                        ],
                        md=4,
                    ),
                    dbc.Col(
                        [
                            dbc.Label("CREATE"),
                            dbc.Input(value="AUTO", disabled=True),
                        ],
                        md=4,
                    ),
                    dbc.Col(
                        [
                            dbc.Label("DATE"),
                            dcc.DatePickerSingle(
                                id="journal-date",
                                display_format="DD-MM-YYYY",
                                min_date_allowed=start_date,
                                max_date_allowed=end_date,
                            ),
                        ],
                        md=4,
                    ),
                ],
                className="mb-3",
            ),
            dbc.Alert(
                "Ledger Group: Journal Book",
                color="info",
                className="mb-3",
            ),
            # Table header
            dbc.Row(
                [
                    dbc.Col(html.B("ACCOUNT"), md=6),
                    dbc.Col(html.B("DEBIT"), md=3),
                    dbc.Col(html.B("CREDIT"), md=3),
                ],
                className="border-bottom pb-2 mb-2",
            ),
            # Journal rows
            *[
                dbc.Row(
                    [
                        dbc.Col(
                            dcc.Dropdown(
                                options=[
                                    {"label": acc, "value": acc}
                                    for acc in pd.read_excel(
                                        "/var/Data/"
                                        + str(SessionData["username"])
                                        + "/Mapper.xlsx"
                                    )["LINE_ITEM"]
                                    .dropna()
                                    .unique()
                                ],
                                placeholder="Select Account",
                                id=f"jr-account-{i}",
                            ),
                            md=6,
                        ),
                        dbc.Col(
                            dbc.Input(type="number", min=0, id=f"jr-debit-{i}"),
                            md=3,
                        ),
                        dbc.Col(
                            dbc.Input(type="number", min=0, id=f"jr-credit-{i}"),
                            md=3,
                        ),
                    ],
                    className="mb-2",
                )
                for i in range(JOURNAL_ROWS)
            ],
            html.Hr(),
            dbc.Row(
                [
                    dbc.Col("TOTAL AMOUNT", md=6),
                    dbc.Col(dbc.Input(id="jr-total-debit", disabled=True), md=3),
                    dbc.Col(dbc.Input(id="jr-total-credit", disabled=True), md=3),
                ],
                className="mb-3",
            ),
            dbc.Button(
                "Submit Journal Entry",
                id="submit-journal-book",
                color="secondary",
                className="mt-2",
            ),
        ],
        fluid=True,
    )


# --------------------------------------------------
# Generic Ledger Voucher Form
# --------------------------------------------------
def generic_ledger_form():

    return dbc.Form(
        [
            dbc.Label("Ledger / Account Name"),
            dcc.Dropdown(id="ledger-dropdown", className="mb-3"),
            dbc.Alert(
                id="ledger-group-output", color="info", is_open=False, className="mb-3"
            ),
            dbc.Label("Amount"),
            dbc.Input(id="amount-input", type="number", className="mb-3"),
            dbc.Label("Transaction Date"),
            dbc.Input(id="date-input", type="date", className="mb-3"),
            dbc.Label("Remarks"),
            dbc.Textarea(id="remarks-input", rows=3),
            dbc.Button("Submit", id="submit-form", color="primary", className="mt-3"),
        ]
    )


# --------------------------------------------------
# Layout
# --------------------------------------------------
def get_layout(SessionData):
    
    BANK_LABELS = load_bank_labels(SessionData)

    default_fy = get_default_fy()
    start_date, end_date = get_fy_date_range(default_fy)

    CHANNELS = [{"label": "Cash", "value": "CASH"}] + [
        {
            "label": BANK_LABELS.get(f"BANK{i}", f"Bank {i}"),
            "value": f"BANK{i}",
        }
        for i in range(1, 11)
    ]
    
    return dbc.Container(
        [
            html.H3("Institution Forms Portal", className="text-center my-4"),
            dcc.Store(id="selected-form-name"),
            dbc.Row([icon_card(i, f[0], f[1]) for i, f in enumerate(FORMS)]),
            # Required for submit callbacks
            html.Div(id="callback-sink", style={"display": "none"}),
            dcc.Download(id="download-fee-receipt-pdf"),
            dcc.Download(id="download-salary-slip-pdf"),
            dbc.Modal(
                [
                    dbc.ModalHeader(dbc.ModalTitle(id="modal-title")),
                    dbc.ModalBody(
                        [
                            html.Div(
                                student_fee_receipt_form(
                                    "Student Fees / Income", SessionData
                                ),
                                id="form-fees",
                                style={"display": "none"},
                            ),
                            html.Div(
                                expense_day_voucher_form(SessionData),
                                id="form-expense",
                                style={"display": "none"},
                            ),
                            html.Div(
                                salary_payment_form(SessionData),
                                id="form-salary",
                                style={"display": "none"},
                            ),
                            html.Div(
                                other_receipt_form(SessionData),
                                id="form-other-receipt",
                                style={"display": "none"},
                            ),
                            html.Div(
                                other_payment_form(SessionData),
                                id="form-other-payment",
                                style={"display": "none"},
                            ),
                            html.Div(
                                journal_book_form(SessionData),
                                id="form-journal",
                                style={"display": "none"},
                            ),
                            html.Div(
                                create_account_post_entry_form(SessionData),
                                id="form-create-account",
                                style={"display": "none"},
                            ),
                            html.Div(
                                contra_entry_form(SessionData),
                                id="form-contra",
                                style={"display": "none"},
                            ),
                        ]
                    ),
                    dbc.ModalFooter(dbc.Button("Close", id="close-modal")),
                ],
                id="main-modal",
                size="xl",
                is_open=False,
                style={"marginTop": "8vh"},
            ),

            dbc.Modal(
                [
                    dbc.ModalHeader("Sell Fixed Asset"),
                
                    dbc.ModalBody(
                        dbc.Container(
                            [
                                dbc.Row(
                                    [
                                        dbc.Col(
                                            [
                                                dbc.Label("Gain on Sale"),
                                                dbc.Input(
                                                    id="asset-sale-gain",
                                                    type="number",
                                                    placeholder="Enter Gain",
                                                ),
                                            ],
                                            md=6,
                                        ),

                                        dbc.Col(
                                            [
                                                dbc.Label("Transaction Date"),
                                                dcc.DatePickerSingle(
                                                    id="asset-sale-date",
                                                    display_format="DD-MM-YYYY",
                                                )
                                            ],
                                            md=6,
                                        ),
                
                                        dbc.Col(
                                            [
                                                dbc.Label("Received In"),
                                                dcc.Dropdown(
                                                    id="asset-sale-mode",
                                                    options=CHANNELS,
                                                    value="CASH",
                                                    clearable=False
                                                )
                                            ],
                                            md=6,
                                        ),
                                    ],
                                    justify="center",   # ⭐ centers fields
                                )
                            ],
                            fluid=True,
                        )
                    ),
                
                    dbc.ModalFooter(
                        dbc.Button("Submit Sale", id="submit-asset-sale", color="danger")
                    ),
                ],
                id="asset-sale-modal",
                centered=True,   # ⭐ centers modal
                is_open=False,
                size="lg"
                ),
            
            dbc.Toast(
                "Form submitted!!",
                id="submit-toast",
                header="Success",
                icon="success",
                is_open=False,
                dismissable=True,
                duration=3000,  # auto close after 3 seconds
                style={
                    "position": "fixed",
                    "top": 20,
                    "right": 20,
                    "width": 300,
                    "zIndex": 2000,
                },
            ),
            dbc.Toast(
                "",
                id="error-toast",
                header="Entry blocked",
                icon="danger",
                is_open=False,
                dismissable=True,
                duration=5000,
                style={
                    "position": "fixed",
                    "top": 20,
                    "right": 340,
                    "width": 420,
                    "zIndex": 2000,
                },
            ),
        ],
        fluid=True,
    )


# --------------------------------------------------
# Historization Controller (Form Router)
# --------------------------------------------------
def path_creator(SessionData):

    LEDGER_PATHS = {
        "FEES RECEIPT": "/var/Data/" + str(SessionData["username"]) + "/fees_ledger.csv",
        "EXPENSES": "/var/Data/" + str(SessionData["username"]) + "/expenses_ledger.csv",
        "SALARY PAYMENT": "/var/Data/"
        + str(SessionData["username"])
        + "/salary_ledger.csv",
        "OTHER RECEIPT": "/var/Data/"
        + str(SessionData["username"])
        + "/other_receipt_ledger.csv",
        "OTHER PAYMENT": "/var/Data/"
        + str(SessionData["username"])
        + "/other_payment_ledger.csv",
        "JOURNAL BOOK": "/var/Data/"
        + str(SessionData["username"])
        + "/journal_ledger.csv",
        "MASTER": "/var/Data/" + str(SessionData["username"]) + "/master_ledger.csv",
    }

    return LEDGER_PATHS


def append_entry(form_name, unique_id, payload, SessionData):

    os.makedirs("/var/Data/" + str(SessionData["username"]), exist_ok=True)

    # ---------------- STANDARD LEDGER SCHEMA ----------------
    STANDARD_COLUMNS = [
        "entry_id",
        "form_name",
        "ledger_name",
        "account_name",
        "ledger_group",
        "cash_amount",
        # ---- BANKS 1 → 10 ----
        *[f"bank{i}_amount" for i in range(1, 11)],
        "total_amount",
        "breakup_cash",
        *[f"breakup_bank{i}" for i in range(1, 11)],
        "transaction_date",
        "details",
        "created_at",
    ]

    # ---------------- ROW BUILD ----------------
    row = {
        "entry_id": unique_id,
        "form_name": form_name,
        "ledger_name": payload.get("ledger_name", ""),
        "account_name": payload.get("account_name", ""),
        "ledger_group": payload.get("ledger_group", ""),
        "cash_amount": float(payload.get("cash_amount", 0.0)),
        "total_amount": float(payload.get("total_amount", 0.0)),
        "breakup_cash": payload.get("breakup_cash", ""),
        "transaction_date": payload.get("transaction_date"),
        "details": payload.get("details", ""),
        "created_at": datetime.now().isoformat(),
    }

    # ---- NORMALISE BANK AMOUNTS ----
    for i in range(1, 11):
        row[f"bank{i}_amount"] = float(payload.get(f"bank{i}_amount", 0.0))
        row[f"breakup_bank{i}"] = payload.get(f"breakup_bank{i}", "")

    # ---------------- WRITE TO LEDGERS ----------------

    LEDGER_PATHS = path_creator(SessionData)

    for ledger_key in [form_name, "MASTER"]:

        path = LEDGER_PATHS.get(ledger_key)
        if not path:
            continue
    
        if os.path.exists(path):
            df = pd.read_csv(path)
        else:
            df = pd.DataFrame()
    
        # ---------------- BASE COLUMNS ----------------
        for col in STANDARD_COLUMNS:
            if col not in df.columns:
                df[col] = ""
    
        # ---------------- SALARY EXTRA COLUMNS ----------------
        if form_name == "SALARY PAYMENT" and ledger_key == "SALARY PAYMENT":
            for col in ["pf_amount", "esi_amount", "tds_amount"]:
                if col not in df.columns:
                    df[col] = ""
    
        # ---------------- BUILD ROW ----------------
        row_to_write = row.copy()
    
        # ✅ Add statutory fields ONLY for salary ledger
        if form_name == "SALARY PAYMENT" and ledger_key == "SALARY PAYMENT":
            row_to_write["pf_amount"] = float(payload.get("pf_amount", 0))
            row_to_write["esi_amount"] = float(payload.get("esi_amount", 0))
            row_to_write["tds_amount"] = float(payload.get("tds_amount", 0))
    
        # ❌ DO NOT add these fields to MASTER
        df.loc[len(df)] = row_to_write

        if form_name == "SALARY PAYMENT" and ledger_key == "SALARY PAYMENT":
            ordered_cols = STANDARD_COLUMNS + ["pf_amount", "esi_amount", "tds_amount"]
        
            for col in ordered_cols:
                if col not in df.columns:
                    df[col] = ""
        
            df = df[ordered_cols]
        else:
            df = df[STANDARD_COLUMNS]            
        df.to_csv(path, index=False)
    print(f"✅ Stored {form_name} → {unique_id}")


def append_journal_entry(unique_id, journal_rows, transaction_date, SessionData):

    print("📘 Writing Journal Entry:", unique_id)

    os.makedirs("data", exist_ok=True)

    # ---------- BASE ROW ----------
    row = {
        "entry_id": unique_id,
        "form_name": "JOURNAL BOOK",
        "ledger_group": "Journal Book",
        # journal has NO payment channels
        "cash_amount": 0.0,
        "total_amount": (
            sum(r.get("debit", 0) for r in journal_rows)
            - sum(r.get("credit", 0) for r in journal_rows)
        ),
        "journal_entries": str(journal_rows),
        "transaction_date": transaction_date,
        "created_at": datetime.now().isoformat(),
    }

    # ---------- NORMALISE BANK COLUMNS (1 → 10) ----------
    for i in range(1, 11):
        row[f"bank{i}_amount"] = 0.0
        row[f"breakup_bank{i}"] = ""

    # journal never has breakup_cash either
    row["breakup_cash"] = ""

    journal_path = "/var/Data/" + str(SessionData["username"]) + "/journal_ledger.csv"

    # ---------- LOAD OR INIT ----------
    if os.path.exists(journal_path):
        df = pd.read_csv(journal_path)
    else:
        df = pd.DataFrame()

    # ---------- ENSURE SCHEMA ----------
    for col in row.keys():
        if col not in df.columns:
            df[col] = ""

    # ---------- APPEND ----------
    df.loc[len(df)] = row
    df.to_csv(journal_path, index=False)

    print("✅ Journal ledger updated")


# --------------------------------------------------------


def register_callbacks(app):

    @app.callback(
        Output("selected-form-name", "data"),
        Output("main-modal", "is_open"),
        Output("modal-title", "children"),
        Output("form-fees", "style"),
        Output("form-expense", "style"),
        Output("form-salary", "style"),
        Output("form-other-receipt", "style"),
        Output("form-other-payment", "style"),
        Output("form-journal", "style"),
        Output("form-create-account", "style"),
        Output("form-contra", "style"),  # ✅ ADDED
        Input({"type": "open-form", "index": ALL}, "n_clicks"),
        Input("close-modal", "n_clicks"),
        prevent_initial_call=True,
    )
    def open_form(n_clicks, close):

        hidden = {"display": "none"}
        shown = {"display": "block"}

        ctx = dash.callback_context
        trigger = ctx.triggered_id

        # ---------------- CLOSE MODAL ----------------
        if trigger == "close-modal":
            return (
                None,
                False,
                "",
                hidden,
                hidden,
                hidden,
                hidden,
                hidden,
                hidden,
                hidden,
                hidden,
            )

        # ---------------- OPEN FORM ----------------
        if not isinstance(trigger, dict) or "index" not in trigger:
            raise dash.exceptions.PreventUpdate

        idx = trigger["index"]
        form_name = FORMS[idx][0]

        return (
            form_name,
            True,
            form_name,
            shown if form_name == "FEES RECEIPT" else hidden,
            shown if form_name == "EXPENSES" else hidden,
            shown if form_name == "SALARY PAYMENT" else hidden,
            shown if form_name == "OTHER RECEIPT" else hidden,
            shown if form_name == "OTHER PAYMENT" else hidden,
            shown if form_name == "JOURNAL BOOK" else hidden,
            shown if form_name == "ENTRY HUB" else hidden,
            shown if form_name == "CONTRA ENTRY" else hidden,
        )

    @app.callback(
        Output("pf-label", "children"),
        Output("esi-label", "children"),
        Output("tds-label", "children"),
        Input("selected-form-name", "data"),  # ✅ TRIGGER
        Input("save-inline-statutory", "n_clicks"),  # ✅ refresh after save
        State("session", "data"),
        prevent_initial_call=True,
    )
    def load_statutory_labels(selected_form, _, SessionData):

        if selected_form != "SALARY PAYMENT" or not SessionData:
            raise dash.exceptions.PreventUpdate

        config = load_statutory_config(SessionData)

        return (
            f"PF ({config['PF_RATE']*100:.2f}%)",
            f"ESI ({config['ESI_RATE']*100:.2f}%)",
            f"TDS ({config['TDS_RATE']*100:.2f}%)",
        )

    @app.callback(
        Output("statutory-edit-block", "style"),
        Input("toggle-statutory-edit", "n_clicks"),
        prevent_initial_call=True,
    )
    def toggle_edit(n):
        return {"display": "block"}

    @app.callback(
        Output("callback-sink", "children", allow_duplicate=True),
        Input("save-inline-statutory", "n_clicks"),
        State("edit-pf-rate", "value"),
        State("edit-esi-rate", "value"),
        State("edit-tds-rate", "value"),
        State("session", "data"),
        prevent_initial_call=True,
    )
    def save_inline_config(n, pf, esi, tds, SessionData):

        if not n:
            return ""

        config = load_statutory_config(SessionData)

        config["PF_RATE"] = float(pf or config["PF_RATE"])
        config["ESI_RATE"] = float(esi or config["ESI_RATE"])
        config["TDS_RATE"] = float(tds or config["TDS_RATE"])

        path = f"/var/Data/{SessionData['username']}/statutory_config.json"

        with open(path, "w") as f:
            json.dump(config, f, indent=4)

        return ""

    @app.callback(
        Output("pf-amount", "value"),
        Output("esi-amount", "value"),
        Output("tds-amount", "value"),
        Output("net-pay", "value"),
        [Input(f"salary-comp-{i}", "value") for i in range(len(SALARY_COMPONENTS))],
        State("session", "data"),
        prevent_initial_call=True,
    )
    def calculate_salary(*components_and_session):
    
        components = components_and_session[:-1]
        SessionData = components_and_session[-1]
    
        if not SessionData:
            return 0, 0, 0, 0
    
        config = load_statutory_config(SessionData)
    
        # ---------------- COMPONENT EXTRACTION ----------------
        c1 = float(components[0] or 0)  # Basic
        c2 = float(components[1] or 0)  # DA
        c3 = float(components[2] or 0)  # Other Allowances
        c4 = float(components[3] or 0)  # HRA
    
        # ---------------- GROSS ----------------
        gross = c1 + c2 + c3 + c4
    
        # ---------------- CORRECT BASE ----------------
        pf_base = c1 + c2
        esi_base = c1 + c2
    
        # ---------------- CALCULATIONS ----------------
        pf = round(pf_base * config["PF_RATE"], 2) if config["PF_ENABLED"] else 0
        esi = round(esi_base * config["ESI_RATE"], 2) if config["ESI_ENABLED"] else 0
    
        # TDS on gross (your current simplified assumption)
        tds = round(gross * config["TDS_RATE"], 2) if config["TDS_ENABLED"] else 0
    
        net = round(gross - pf - esi - tds, 2)
    
        return pf, esi, tds, net
        
    @app.callback(
        Output("callback-sink", "children", allow_duplicate=True),
        Output("jr-total-debit", "value"),
        Output("jr-total-credit", "value"),
        [Input(f"jr-debit-{i}", "value") for i in range(JOURNAL_ROWS)]
        + [Input(f"jr-credit-{i}", "value") for i in range(JOURNAL_ROWS)],
        prevent_initial_call=True,
    )
    def calculate_journal_totals(*values):

        n = JOURNAL_ROWS
        debits = values[:n]
        credits = values[n:]

        total_debit = sum(v or 0 for v in debits)
        total_credit = sum(v or 0 for v in credits)

        return "", total_debit, total_credit

    # --------------------------------------------------
    # Ledger Dropdown → Ledger Group Mapping
    # --------------------------------------------------
    @app.callback(
        Output("ledger-group-output", "children"),
        Output("ledger-group-output", "is_open"),
        Input("ledger-dropdown", "value"),
        State("session", "data"),
        prevent_initial_call=True,
    )
    def show_ledger_group(ledger, SessionData):
        if not ledger:
            return "", False

        df = pd.read_excel("/var/Data/" + str(SessionData["username"]) + "/Mapper.xlsx")

        row = df.loc[df["LINE_ITEM"] == ledger]
        if row.empty:
            return "", False

        group = row.iloc[0]["GROUP"]
        return f"Ledger Group: {group}", True

    # --------------------------------------------------
    # HIstorization Block
    # --------------------------------------------------

    @app.callback(
        Output("callback-sink", "children", allow_duplicate=True),
        Input("submit-form", "n_clicks"),
        State("selected-form-name", "data"),
        State("ledger-dropdown", "value"),
        State("ledger-group-output", "children"),
        State("amount-input", "value"),
        State("date-input", "date"),
        State("remarks-input", "value"),
        State("session", "data"),
        prevent_initial_call=True,
    )
    def submit_generic(n, form, ledger, group_txt, amt, date, remarks, SessionData):

        # ---------------- HARD GUARDS ----------------
        if not all([n, form, ledger, group_txt, amt, date]):
            return ""

        try:
            amt = float(amt)
        except Exception:
            return ""

        ledger_group = group_txt.replace("Ledger Group:", "").strip()

        # ---------------- CHANNEL ALLOCATION ----------------
        # Default rule: generic form = CASH
        cash_amt = amt
        bank1_amt = 0.0
        bank2_amt = 0.0

        # ---------------- PAYLOAD (NEW STANDARD SCHEMA) ----------------
        payload = {
            "ledger_name": ledger,
            "ledger_group": ledger_group,
            # channel-wise amounts
            "cash_amount": cash_amt,
            "bank1_amount": bank1_amt,
            "bank2_amount": bank2_amt,
            "total_amount": cash_amt + bank1_amt + bank2_amt,
            # channel-wise breakup (not applicable here)
            "breakup_cash": "",
            "breakup_bank1": "",
            "breakup_bank2": "",
            "transaction_date": date,
            "details": remarks or "",
        }

        uid = f"{form}_{datetime.now().strftime('%Y%m%d%H%M%S%f')}"
        append_entry(form, uid, payload, SessionData)

        return None

    @app.callback(
    Output("callback-sink", "children", allow_duplicate=True),
    Output("error-toast", "is_open", allow_duplicate=True),

    Output("student-name", "value", allow_duplicate=True),
    Output("fee-receipt-date", "date", allow_duplicate=True),
    Output("fee-payment-mode", "value", allow_duplicate=True),

    *[Output(f"fee-amount-{i}", "value", allow_duplicate=True) for i in range(len(FEE_HEADS))],

    Input("submit-fee-receipt", "n_clicks"),
    State("student-name", "value"),
    State("fee-receipt-date", "date"),
    State("fee-payment-mode", "value"),
    *[State(f"fee-amount-{i}", "value") for i in range(len(FEE_HEADS))],
    State("session", "data"),
    prevent_initial_call=True,
)
    def submit_fees(n, student, receipt_date, payment_mode, *vals):

        import re

        # ---------------- HARD GUARD ----------------
        if not n:
            return "", False

        # -------- DATE VALIDATION --------
        if not receipt_date:
         return "", True

# -------- STUDENT VALIDATION --------
        if not student:
         return "", True

# -------- PAYMENT MODE VALIDATION --------
        if not payment_mode:
         return "", True

        # ---------------- CLEAN INPUT ----------------
        student = str(student).strip()

        # Normalize multiple spaces
        student = re.sub(r"\s+", " ", student)

        # Remove spaces around slashes → "A / B / C" → "A/B/C"
        student = re.sub(r"\s*/\s*", "/", student)

        # Remove trailing slash if user typed accidentally
        student = student.rstrip("/")

        # ---------------- STRICT STRUCTURE CHECK ----------------
        parts = student.split("/")

        # Must be exactly 3 parts
        if len(parts) != 3:
            return "", True

        name, roll, student_class = parts

        # Remove extra spaces again for safety
        name = name.strip()
        roll = roll.strip()
        student_class = student_class.strip()

        # All three must be non-empty
        if not name or not roll or not student_class:
            return "", True

        # Optional strict numeric roll enforcement
        # Uncomment if required:
        # if not roll.isdigit():
        #     return "", True

        # ---------------- PROCESS AMOUNTS ----------------
        fee_amounts = vals[:-1]
        SessionData = vals[-1]

        cash_total = 0.0
        bank_totals = {f"bank{i}_amount": 0.0 for i in range(1, 11)}
        breakup_cash = {}
        breakup_banks = {f"breakup_bank{i}": {} for i in range(1, 11)}

        for head, amt in zip(FEE_HEADS, fee_amounts):
            amt = float(amt or 0)

            if amt <= 0:
                continue

            if payment_mode == "CASH":
                cash_total += amt
                breakup_cash[head] = amt
            else:
                idx = payment_mode.replace("BANK", "")
                bank_totals[f"bank{idx}_amount"] += amt
                breakup_banks[f"breakup_bank{idx}"][head] = amt

        total_amount = cash_total + sum(bank_totals.values())

        # Must enter at least one fee
        if total_amount <= 0:
            return "", True

        # ---------------- BUILD PAYLOAD ----------------
        payload = {
            "ledger_name": "Student Fees",
            "account_name": f"{name}/{roll}/{student_class}",
            "ledger_group": "Student Fees / Income",
            "cash_amount": cash_total,
            "total_amount": total_amount,
            "breakup_cash": str(breakup_cash),
            "transaction_date": receipt_date,
            "details": f"Fee receipt from {name}",
        }

        payload.update(bank_totals)

        for i in range(1, 11):
            payload[f"breakup_bank{i}"] = str(breakup_banks[f"breakup_bank{i}"])

        uid = f"FEES_{datetime.now().strftime('%Y%m%d%H%M%S%f')}"

        append_entry("FEES RECEIPT", uid, payload, SessionData)

        return (
    "saved", False,
    None,          # student reset
    None,          # date reset
    "CASH",        # payment mode reset
    *([None] * len(FEE_HEADS))  # all fee fields reset
)



    @app.callback(
        Output("download-fee-receipt-pdf", "data"),
        Input("print-fee-receipt", "n_clicks"),
        State("fee-receipt-no", "value"),
        State("student-name", "value"),
        State("fee-receipt-date", "date"),
        State("fee-payment-mode", "value"),
        State("session", "data"),
        *[State(f"fee-amount-{i}", "value") for i in range(len(FEE_HEADS))],
        prevent_initial_call=True,
    )
    def download_fee_receipt(n, receipt_no, student, date, mode, SessionData, *amounts):

        if not n:
            return dash.no_update

        BANK_LABELS = load_bank_labels(SessionData)

        # ===============================
        # LOAD SCHOOL INFO
        # ===============================
        school_name = ""
        school_address = ""

        info_path = f"/var/Data/{SessionData['username']}/school_info.csv"

        if os.path.exists(info_path):
            df_info = pd.read_csv(info_path)

            if not df_info.empty:
                school_name = df_info.loc[0, "school_name"]
                school_address = df_info.loc[0, "address"]

        if mode == "CASH":
            payment_label = "Cash"
        elif mode.startswith("BANK"):
            payment_label = BANK_LABELS.get(mode, mode)
        else:
            payment_label = mode

        buffer = io.BytesIO()
        c = canvas.Canvas(buffer, pagesize=A4)
        width, height = A4

        y = height - 60

        # =====================================================
        # CENTER SCHOOL LOGO (ONLY LOGO, NO TEXT)
        # =====================================================
        school_logo_path = (
            "/var/Data/" + SessionData["username"] + "/school_fees_logo.png"
        )

        if os.path.exists(school_logo_path):
            logo = ImageReader(school_logo_path)
            logo_width = 150
            logo_height = 90
            c.drawImage(
                logo,
                (width - logo_width) / 2,
                y - 80,
                width=logo_width,
                height=logo_height,
                preserveAspectRatio=True,
                mask="auto",
            )
            y -= 100

        # Divider
        # =====================================================
        # SCHOOL HEADER
        # =====================================================
        c.setFont("Helvetica-Bold", 16)
        c.drawCentredString(width / 2, y, school_name)
        y -= 18

        c.setFont("Helvetica", 11)
        c.drawCentredString(width / 2, y, school_address)
        y -= 16

        # Divider
        c.line(50, y, width - 50, y)
        y -= 30

        # =====================================================
        # RECEIPT TITLE
        # =====================================================
        c.setFont("Helvetica-Bold", 16)
        c.drawCentredString(width / 2, y, "STUDENT FEE RECEIPT")
        y -= 30

        # =====================================================
        # DETAILS
        # =====================================================
        c.setFont("Helvetica", 11)

        c.drawString(60, y, f"Receipt No: {receipt_no}")
        c.drawRightString(width - 60, y, f"Date: {date}")
        y -= 18

        # Split student input (format: name/roll/class)
        name = ""
        roll = ""
        student_class = ""

        if student and "/" in student:
            parts = student.split("/")
            name = parts[0] if len(parts) > 0 else ""
            roll = parts[1] if len(parts) > 1 else ""
            student_class = parts[2] if len(parts) > 2 else ""
        else:
            name = student

        c.drawString(60, y, f"Student Name: {name}")
        y -= 18

        if roll:
            c.drawString(60, y, f"Roll No: {roll}")
            y -= 18

        if student_class:
            c.drawString(60, y, f"Class: {student_class}")
            y -= 18

        c.drawString(60, y, f"Payment Mode: {payment_label}")
        y -= 25

        # Divider
        c.line(50, y, width - 50, y)
        y -= 20

        # =====================================================
        # TABLE HEADER
        # =====================================================
        c.setFont("Helvetica-Bold", 12)
        c.drawString(60, y, "Particulars")
        c.drawRightString(width - 60, y, "Amount")
        y -= 10
        c.line(50, y, width - 50, y)
        y -= 18

        # =====================================================
        # TABLE ROWS
        # =====================================================
        c.setFont("Helvetica", 11)
        total = 0

        for head, amt in zip(FEE_HEADS, amounts):
            amt = float(amt or 0)
            if amt > 0:
                c.drawString(60, y, head)
                c.drawRightString(width - 60, y, f"₹ {amt:,.2f}")
                y -= 18
                total += amt

        y -= 10
        c.line(50, y, width - 50, y)
        y -= 20

        c.setFont("Helvetica-Bold", 13)
        c.drawString(60, y, "TOTAL")
        c.drawRightString(width - 60, y, f"₹ {total:,.2f}")

        # =====================================================
        # FOOTER SECTION
        # =====================================================
        y = 140

        # Top dashed style separator
        c.line(50, y + 30, width - 50, y + 30)

        # Signature lines
        c.setFont("Helvetica", 10)
        c.drawString(60, y, "Received By:")
        c.line(150, y - 3, 300, y - 3)

        c.drawRightString(width - 150, y, "Date")
        c.line(width - 140, y - 3, width - 60, y - 3)

        # =====================================================
        # TRULEDGR LOGO BOTTOM LEFT
        # =====================================================
        truledgr_logo = "assets/logo.png"

        if os.path.exists(truledgr_logo):
            logo = ImageReader(truledgr_logo)
            c.drawImage(
                logo,
                30,
                35,
                width=150,
                height=60,
                preserveAspectRatio=True,
                mask="auto",
            )

        c.showPage()
        c.save()
        buffer.seek(0)

        return dcc.send_bytes(buffer.getvalue(), filename=f"{receipt_no}.pdf")

  
  
    @app.callback(
    Output("callback-sink", "children", allow_duplicate=True),
    Output("error-toast", "children", allow_duplicate=True),
    Output("error-toast", "is_open", allow_duplicate=True),

    Output("expense-date", "date", allow_duplicate=True),

    *[Output(f"exp-mode-{i}", "value", allow_duplicate=True) for i in range(len(EXPENSE_HEADS))],
    *[Output(f"exp-amount-{i}", "value", allow_duplicate=True) for i in range(len(EXPENSE_HEADS))],

    Input("submit-expense-voucher", "n_clicks"),
    State("expense-date", "date"),
    *[State(f"exp-mode-{i}", "value") for i in range(len(EXPENSE_HEADS))],
    *[State(f"exp-amount-{i}", "value") for i in range(len(EXPENSE_HEADS))],
    State("session", "data"),
    prevent_initial_call=True,
)
    def submit_expense(n, expense_date, *vals):
    
        NUM_EXP = len(EXPENSE_HEADS)
    
        exp_modes = vals[:NUM_EXP]
        exp_amounts = vals[NUM_EXP:2*NUM_EXP]
        SessionData = vals[-1]
    
        if not n:
            return "", "", False
    
        # ---------------- DATE VALIDATION ----------------
        if not expense_date:
            print("❌ Transaction date missing")
            return "", "Transaction date is mandatory", True
    
        # ---------- INITIALISE TOTALS ----------
        cash_total = 0.0
        bank_totals = {f"bank{i}_amount": 0.0 for i in range(1, 11)}
    
        breakup_cash = {}
        breakup_banks = {f"breakup_bank{i}": {} for i in range(1, 11)}
    
        # ---------- PROCESS EACH EXPENSE HEAD ----------
        for head, mode, amt in zip(EXPENSE_HEADS, exp_modes, exp_amounts):
    
            amt = float(amt or 0)
    
            if amt <= 0 or not mode:
                continue
    
            if mode == "CASH":
                cash_total += amt
                breakup_cash[head] = amt
    
            elif mode.startswith("BANK"):
                idx = mode.replace("BANK", "")
                bank_totals[f"bank{idx}_amount"] += amt
                breakup_banks[f"breakup_bank{idx}"][head] = amt
    
        total_amount = cash_total + sum(bank_totals.values())
    
        if total_amount == 0:
            return "", "No expense amount entered", True
    
        # ---------- PAYLOAD ----------
        payload = {
            "ledger_group": "Expenses",
            "cash_amount": cash_total,
            "total_amount": total_amount,
            "breakup_cash": str(breakup_cash),
            "transaction_date": expense_date,
            "details": "Expense Day Voucher",
        }
    
        payload.update(bank_totals)
    
        for i in range(1, 11):
            payload[f"breakup_bank{i}"] = str(breakup_banks[f"breakup_bank{i}"])
    
        uid = f"EXP_{datetime.now().strftime('%Y%m%d%H%M%S%f')}"
    
        append_entry("EXPENSES", uid, payload, SessionData)
    
        return (
    "saved", "", False,
    None,                                # date reset
    *(["CASH"] * NUM_EXP),               # modes reset to CASH
    *([None] * NUM_EXP)                  # amounts clear
)
    





    @app.callback(
    Output("callback-sink", "children", allow_duplicate=True),
    Output("error-toast", "is_open", allow_duplicate=True),

    Output("employee-name", "value", allow_duplicate=True),
    Output("salary-date", "date", allow_duplicate=True),
    Output("salary-payment-mode", "value", allow_duplicate=True),

    Output("salary-comp-0", "value", allow_duplicate=True),
    Output("salary-comp-1", "value", allow_duplicate=True),
    Output("salary-comp-2", "value", allow_duplicate=True),
    Output("salary-comp-3", "value", allow_duplicate=True),

    Output("pf-amount", "value", allow_duplicate=True),
    Output("esi-amount", "value", allow_duplicate=True),
    Output("tds-amount", "value", allow_duplicate=True),
    Output("net-pay", "value", allow_duplicate=True),

    Input("submit-salary-voucher", "n_clicks"),
        State("employee-name", "value"),
        State("salary-comp-0", "value"),
        State("salary-comp-1", "value"),
        State("salary-comp-2", "value"),
        State("salary-comp-3", "value"),
        # State("pf-amount", "value"),
        # State("esi-amount", "value"),
        # State("tds-amount", "value"),
        # State("net-pay", "value"),
        State("salary-payment-mode", "value"),
        State("salary-date", "date"),
        State("session", "data"),
        prevent_initial_call=True,
    )
    def submit_salary(
        n, emp, c1, c2, c3, c4, mode, salary_date, SessionData
    ):
        
        ERROR_RETURN = (
    "", True,
    dash.no_update,
    dash.no_update,
    dash.no_update,
    dash.no_update,
    dash.no_update,
    dash.no_update,
    dash.no_update,
)
        # ---------------- HARD VALIDATION ----------------
        # ---------------- BUTTON GUARD ----------------
        if not n:
            return ERROR_RETURN

# ---------------- EMPLOYEE VALIDATION ---------------- 
        if not emp:
         return ERROR_RETURN

# ---------------- DATE VALIDATION ----------------
        if not salary_date:
          return ERROR_RETURN

# ---------------- PAYMENT MODE VALIDATION ----------------
        if not mode:
          return ERROR_RETURN
        
        config = load_statutory_config(SessionData)
        
        c1 = float(c1 or 0)  # Basic
        c2 = float(c2 or 0)  # DA
        c3 = float(c3 or 0)  # Other
        c4 = float(c4 or 0)  # HRA
        
        gross = c1 + c2 + c3 + c4
        
        # ✅ PF & ESI base excludes HRA
        pf_base = c1 + c2
        esi_base = c1 + c2
        
        pf = round(pf_base * config["PF_RATE"], 2) if config["PF_ENABLED"] else 0
        esi = round(esi_base * config["ESI_RATE"], 2) if config["ESI_ENABLED"] else 0
        tds = round(gross * config["TDS_RATE"], 2) if config["TDS_ENABLED"] else 0
        
        net = round(gross - pf - esi - tds, 2)        
        try:
            c1 = float(c1 or 0)
            c2 = float(c2 or 0)
            c3 = float(c3 or 0)
            c4 = float(c4 or 0)

            pf = float(pf or 0)
            esi = float(esi or 0)
            tds = float(tds or 0)
            net = float(net or 0)

        except Exception:
          return ERROR_RETURN

        gross = c1 + c2 + c3 + c4
        total_deduction = pf + esi + tds

        # ---------------- 1️⃣ POST NET SALARY (SALARY PAYMENT) ----------------

        cash_amt = 0.0
        bank_amts = {f"bank{i}_amount": 0.0 for i in range(1, 11)}

        if mode == "CASH":
            cash_amt = net
        elif mode.startswith("BANK"):
            idx = mode.replace("BANK", "")
            bank_amts[f"bank{idx}_amount"] = net
        else:
            return ERROR_RETURN


        payload_salary = {
            "ledger_name": "Salary Expense",
            "account_name": emp,
            "ledger_group": "Salary & Wages Expense",
            "cash_amount": cash_amt,
            "total_amount": net,
            "breakup_cash": "",
            "transaction_date": salary_date,
            "details": f"Salary payment to {emp}",
             "pf_amount": pf,
            "esi_amount": esi,
            "tds_amount": tds,
        }

        payload_salary.update(bank_amts)

        for i in range(1, 11):
            payload_salary.setdefault(f"breakup_bank{i}", "")

        uid1 = f"SAL_{datetime.now().strftime('%Y%m%d%H%M%S%f')}"

        append_entry("SALARY PAYMENT", uid1, payload_salary, SessionData)
        reset_outputs = (
    "saved", False,
    None,
    None,
    "CASH",
    None, None, None, None,
    None,
    None,
    None,
    None
)

        # ---------------- 2️⃣ POST DEDUCTION (ENTRY HUB STYLE) ----------------

        if total_deduction > 0:

            ledger_name = "OTHER PAYABLES"
            ledger_group = "Current Liabilities"

            resolved_form = resolve_allowed_form_from_group(
                ledger_group, "OTHER_PAYMENT"
            )

            cash_liab = 0.0
            bank_liab = {f"bank{i}_amount": 0.0 for i in range(1, 11)}

            if mode == "CASH":
                cash_liab = total_deduction
            elif mode.startswith("BANK"):
                idx = mode.replace("BANK", "")
                bank_liab[f"bank{idx}_amount"] = total_deduction

            payload_liability = {
                "ledger_name": ledger_name,
                "account_name": ledger_name,
                "ledger_group": ledger_group,
                "cash_amount": cash_liab,
                "total_amount": total_deduction,
                "breakup_cash": "",
                "transaction_date": salary_date,
                "details": f"Salary deductions payable for {emp}",
            }

            payload_liability.update(bank_liab)

            for i in range(1, 11):
                payload_liability.setdefault(f"breakup_bank{i}", "")

            uid2 = f"MAN_{datetime.now().strftime('%Y%m%d%H%M%S%f')}"

            append_entry("OTHER RECEIPT", uid2, payload_liability, SessionData)
            

        return reset_outputs
    


    

    @app.callback(
    Output("callback-sink", "children", allow_duplicate=True),
    Output("error-toast", "children", allow_duplicate=True),
    Output("error-toast", "is_open", allow_duplicate=True),

    Output("other-receipt-date", "date", allow_duplicate=True),

    *[Output(f"or-account-{i}", "value", allow_duplicate=True) for i in range(len(OTHER_RECEIPT_HEADS))],
    *[Output(f"or-mode-{i}", "value", allow_duplicate=True) for i in range(len(OTHER_RECEIPT_HEADS))],
    *[Output(f"or-amount-{i}", "value", allow_duplicate=True) for i in range(len(OTHER_RECEIPT_HEADS))],

    Input("submit-other-receipt", "n_clicks"),
        State("other-receipt-date", "date"),
        *[State(f"or-account-{i}", "value") for i in range(len(OTHER_RECEIPT_HEADS))],
        *[State(f"or-mode-{i}", "value") for i in range(len(OTHER_RECEIPT_HEADS))],
        *[State(f"or-amount-{i}", "value") for i in range(len(OTHER_RECEIPT_HEADS))],
        State("session", "data"),
        prevent_initial_call=True,
    )
    def submit_other_receipt(n, receipt_date, *vals):
    
        NUM_OR = len(OTHER_RECEIPT_HEADS)
    
        or_accounts = vals[:NUM_OR]
        or_modes = vals[NUM_OR:2 * NUM_OR]
        or_amounts = vals[2 * NUM_OR:3 * NUM_OR]
        SessionData = vals[-1]
    
        if not n:
            return "", "", False
    
        # ---------------- DATE VALIDATION ----------------
        if not receipt_date:
            print("❌ Transaction date missing")
            return "", "Transaction date is mandatory", True
    
        # ---------- INITIALISE TOTALS ----------
        cash_total = 0.0
        bank_totals = {f"bank{i}_amount": 0.0 for i in range(1, 11)}
    
        breakup_cash = {}
        breakup_banks = {f"breakup_bank{i}": {} for i in range(1, 11)}
    
        # ---------- PROCESS EACH RECEIPT HEAD ----------
        for head, account, mode, amt in zip(
            OTHER_RECEIPT_HEADS, or_accounts, or_modes, or_amounts
        ):
    
            account = (account or "").strip()
            amt = float(amt or 0)
    
            if amt > 0 and not account:
                return "", "Account name required for receipt", True
    
            if amt <= 0 or not mode:
                continue
    
            if mode == "CASH":
                cash_total += amt
                breakup_cash[head] = {
                    "account": account,
                    "amount": amt,
                }
    
            elif mode.startswith("BANK"):
                idx = mode.replace("BANK", "")
                bank_totals[f"bank{idx}_amount"] += amt
                breakup_banks[f"breakup_bank{idx}"][head] = {
                    "account": account,
                    "amount": amt,
                }
    
        total_amount = cash_total + sum(bank_totals.values())
    
        if total_amount == 0:
            return "", "No receipt amount entered", True
    
        # ---------- VOUCHER ACCOUNT NAME ----------
        accounts_used = {a.strip() for a in or_accounts if a and a.strip()}
    
        if len(accounts_used) == 1:
            voucher_account = list(accounts_used)[0]
        elif len(accounts_used) > 1:
            voucher_account = "MULTIPLE"
        else:
            voucher_account = ""
    
        # ---------- PAYLOAD ----------
        payload = {
            "ledger_group": "Other Income / Receipts",
            "ledger_name": "",
            "account_name": voucher_account,
            "cash_amount": cash_total,
            "total_amount": total_amount,
            "breakup_cash": str(breakup_cash),
            "transaction_date": receipt_date,
            "details": "Other Receipt",
        }
    
        payload.update(bank_totals)
    
        for i in range(1, 11):
            payload[f"breakup_bank{i}"] = str(breakup_banks[f"breakup_bank{i}"])
    
        uid = f"OR_{datetime.now().strftime('%Y%m%d%H%M%S%f')}"
    
        append_entry("OTHER RECEIPT", uid, payload, SessionData)
    
        return (
    "saved", "", False,
    None,
    *([None] * NUM_OR),
    *(["CASH"] * NUM_OR),
    *([None] * NUM_OR),
)



    @app.callback(
    Output("callback-sink", "children", allow_duplicate=True),
    Output("error-toast", "children", allow_duplicate=True),
    Output("error-toast", "is_open", allow_duplicate=True),

    Output("other-payment-date", "date", allow_duplicate=True),

    *[Output(f"op-account-{i}", "value", allow_duplicate=True) for i in range(len(OTHER_PAYMENT_HEADS))],
    *[Output(f"op-mode-{i}", "value", allow_duplicate=True) for i in range(len(OTHER_PAYMENT_HEADS))],
    *[Output(f"op-amount-{i}", "value", allow_duplicate=True) for i in range(len(OTHER_PAYMENT_HEADS))],
    
        Input("submit-other-payment", "n_clicks"),
        State("other-payment-date", "date"),
        *[State(f"op-account-{i}", "value") for i in range(len(OTHER_PAYMENT_HEADS))],
        *[State(f"op-mode-{i}", "value") for i in range(len(OTHER_PAYMENT_HEADS))],
        *[State(f"op-amount-{i}", "value") for i in range(len(OTHER_PAYMENT_HEADS))],
        State("session", "data"),
        prevent_initial_call=True,
    )
    def submit_other_payment(n, payment_date, *vals):
    
        NUM_OP = len(OTHER_PAYMENT_HEADS)
    
        op_accounts = vals[:NUM_OP]
        op_modes = vals[NUM_OP:2 * NUM_OP]
        op_amounts = vals[2 * NUM_OP:3 * NUM_OP]
        SessionData = vals[-1]
    
        if not n:
            return "", "", False
    
        # ---------------- DATE VALIDATION ----------------
        if not payment_date:
            print("❌ Transaction date missing")
            return "", "Transaction date is mandatory", True
    
        # ---------- INITIALISE TOTALS ----------
        cash_total = 0.0
        bank_totals = {f"bank{i}_amount": 0.0 for i in range(1, 11)}
    
        breakup_cash = {}
        breakup_banks = {f"breakup_bank{i}": {} for i in range(1, 11)}
    
        # ---------- PROCESS EACH PAYMENT HEAD ----------
        for head, account, mode, amt in zip(
            OTHER_PAYMENT_HEADS, op_accounts, op_modes, op_amounts
        ):
    
            account = (account or "").strip()
            amt = float(amt or 0)
    
            if amt > 0 and not mode:
                return "", "Payment mode required when amount entered", True
    
            if amt <= 0 or not mode:
                continue
    
            if mode == "CASH":
                cash_total += amt
                breakup_cash[head] = {
                    "account": account,
                    "amount": amt,
                }
    
            elif mode.startswith("BANK"):
                idx = mode.replace("BANK", "")
                bank_totals[f"bank{idx}_amount"] += amt
                breakup_banks[f"breakup_bank{idx}"][head] = {
                    "account": account,
                    "amount": amt,
                }
    
        total_amount = cash_total + sum(bank_totals.values())
    
        if total_amount == 0:
            return "", "No payment amount entered", True
    
        # ---------- VOUCHER ACCOUNT NAME ----------
        accounts_used = {a.strip() for a in op_accounts if a and a.strip()}
    
        if len(accounts_used) == 1:
            voucher_account = list(accounts_used)[0]
        elif len(accounts_used) > 1:
            voucher_account = "MULTIPLE"
        else:
            voucher_account = ""
    
        # ---------- PAYLOAD ----------
        payload = {
            "ledger_group": "Other Payments / Outgoings",
            "ledger_name": "",
            "account_name": voucher_account,
            "cash_amount": cash_total,
            "total_amount": total_amount,
            "breakup_cash": str(breakup_cash),
            "transaction_date": payment_date,
            "details": "Other Payment",
        }
    
        payload.update(bank_totals)
    
        for i in range(1, 11):
            payload[f"breakup_bank{i}"] = str(breakup_banks[f"breakup_bank{i}"])
    
        uid = f"OP_{datetime.now().strftime('%Y%m%d%H%M%S%f')}"
    
        append_entry("OTHER PAYMENT", uid, payload, SessionData)
    
        return (
    "saved", "", False,
    None,
    *([None] * NUM_OP),
    *(["CASH"] * NUM_OP),
    *([None] * NUM_OP),
)
    
    @app.callback(
    Output("callback-sink", "children", allow_duplicate=True),
    Output("error-toast", "children", allow_duplicate=True),
    Output("error-toast", "is_open", allow_duplicate=True),

    Output("journal-date", "date", allow_duplicate=True),

    *[Output(f"jr-account-{i}", "value", allow_duplicate=True) for i in range(JOURNAL_ROWS)],
    *[Output(f"jr-debit-{i}", "value", allow_duplicate=True) for i in range(JOURNAL_ROWS)],
    *[Output(f"jr-credit-{i}", "value", allow_duplicate=True) for i in range(JOURNAL_ROWS)],
    
        Input("submit-journal-book", "n_clicks"),
    
        State("journal-date", "date"),
        *[State(f"jr-account-{i}", "value") for i in range(JOURNAL_ROWS)],
        *[State(f"jr-debit-{i}", "value") for i in range(JOURNAL_ROWS)],
        *[State(f"jr-credit-{i}", "value") for i in range(JOURNAL_ROWS)],
        State("session", "data"),
    
        prevent_initial_call=True,
    )
    def submit_journal(n, journal_date, *vals):
        ERROR_RETURN = (
    "",
    "Validation error",
    True,
    dash.no_update,
    *([dash.no_update] * JOURNAL_ROWS),
    *([dash.no_update] * JOURNAL_ROWS),
    *([dash.no_update] * JOURNAL_ROWS),
)
    
        print("🟡 submit_journal called")
    
        if not n:
            return ERROR_RETURN
    
        # ---------------- DATE VALIDATION ----------------
        if not journal_date:
         return (
        "",
        "Transaction date is mandatory",
        True,
        dash.no_update,
        *([dash.no_update] * JOURNAL_ROWS),
        *([dash.no_update] * JOURNAL_ROWS),
        *([dash.no_update] * JOURNAL_ROWS),
    )
    
        n_r = JOURNAL_ROWS
    
        accounts = vals[:n_r]
        debits = vals[n_r:2*n_r]
        credits = vals[2*n_r:3*n_r]
        SessionData = vals[-1]
    
        journal_rows = []
        total_d = 0.0
        total_c = 0.0
    
        # ---------------- PROCESS ROWS ----------------
        for acc, d, c in zip(accounts, debits, credits):
    
            d = float(d or 0)
            c = float(c or 0)
    
            if acc and (d > 0 or c > 0):
    
                journal_rows.append({
                    "account": acc,
                    "debit": d,
                    "credit": c,
                })
    
                total_d += d
                total_c += c
    
        # ---------------- EMPTY JOURNAL BLOCK ----------------
        if total_d == 0 and total_c == 0:
            print("❌ Empty journal")
            return (
        "",
        "Enter debit or credit amount",
        True,
        dash.no_update,
        *([dash.no_update] * JOURNAL_ROWS),
        *([dash.no_update] * JOURNAL_ROWS),
        *([dash.no_update] * JOURNAL_ROWS),
    )
    
        # ---------------- BALANCE CHECK ----------------
        if round(total_d, 2) != round(total_c, 2):
    
            print("❌ Unbalanced journal entry")
            return (
        "",
        "Debit and Credit must be equal",
        True,
        dash.no_update,
        *([dash.no_update] * JOURNAL_ROWS),
        *([dash.no_update] * JOURNAL_ROWS),
        *([dash.no_update] * JOURNAL_ROWS),
    )
    
        # ---------------- SAVE ENTRY ----------------
        uid = f"JV_{datetime.now().strftime('%Y%m%d%H%M%S%f')}"
    
        append_journal_entry(
            unique_id=uid,
            journal_rows=journal_rows,
            transaction_date=journal_date,
            SessionData=SessionData,
        )
    
        print("✅ Journal entry stored")
    
        return (
    "saved", "", False,
    None,
    *([None] * JOURNAL_ROWS),
    *([None] * JOURNAL_ROWS),
    *([None] * JOURNAL_ROWS),
)

  
  
    #############################

    @app.callback(
        Output("ca-account-name", "options"),
        Input("ca-account-name", "search_value"),
        State("session", "data"),
    )
    def load_account_suggestions(search, SessionData):

        df = pd.read_excel("/var/Data/" + str(SessionData["username"]) + "/Mapper.xlsx")
        accounts = sorted(df["LINE_ITEM"].dropna().unique())

        if not search:
            return [{"label": a, "value": a} for a in accounts[:50]]

        search_l = search.lower()

        matches = [a for a in accounts if search_l in a.lower()][:20]

        return [{"label": a, "value": a} for a in matches]

    @app.callback(
        Output("account-name-list", "children"),
        Input("ca-account-name", "value"),
        State("session", "data"),
    )
    def populate_account_name_datalist(_, SessionData):

        try:
            df = pd.read_excel(
                "/var/Data/" + str(SessionData["username"]) + "/Mapper.xlsx"
            )
        except Exception:
            return []

        accounts = sorted(df["LINE_ITEM"].dropna().astype(str).unique())

        return [html.Option(value=acc) for acc in accounts]

        ########################################

    @app.callback(
    Output("callback-sink", "children", allow_duplicate=True),
    Output("error-toast", "children", allow_duplicate=True),
    Output("error-toast", "is_open", allow_duplicate=True),

    Output("ca-account-name", "value", allow_duplicate=True),
    Output("ca-account-group", "value", allow_duplicate=True),
    Output("ca-fs-group", "value", allow_duplicate=True),
    Output("ca-allowed-form", "value", allow_duplicate=True),
    Output("ca-date", "date", allow_duplicate=True),
    Output("ca-payment-mode", "value", allow_duplicate=True),
    Output("ca-payment-amount", "value", allow_duplicate=True),
    Output("ca-opening-balance-flag", "value", allow_duplicate=True),
    Output("ca-opening-balance", "value", allow_duplicate=True),

    Input("submit-create-account", "n_clicks"),
    State("ca-account-name", "value"),
    State("ca-account-group", "value"),
    State("ca-fs-group", "value"),
    State("ca-allowed-form", "value"),
    State("ca-date", "date"),
    State("ca-payment-mode", "value"),
    State("ca-payment-amount", "value"),
    State("ca-opening-balance-flag", "value"),
    State("ca-opening-balance", "value"),
    State("session", "data"),
    prevent_initial_call=True,
)
    def submit_create_account(
        n,
        name,
        group,
        fs_group,
        allowed_form,
        date,
        payment_mode,
        amount,
        opening_flag,
        opening_balance,
        SessionData,
    ):
        ERROR_RETURN = (
    "",
    "Validation error",
    True,
    dash.no_update,
    dash.no_update,
    dash.no_update,
    dash.no_update,
    dash.no_update,
    dash.no_update,
    dash.no_update,
    dash.no_update,
    dash.no_update,
)
    
        # ---------- HARD VALIDATION ----------
        if not n:
            return "", "", False
    
       
       
        if not date:
         return (
        "",
        "Transaction date is mandatory",
        True,
        dash.no_update,
        dash.no_update,
        dash.no_update,
        dash.no_update,
        dash.no_update,
        dash.no_update,
        dash.no_update,
        dash.no_update,
        dash.no_update,
    )
    
        if not name or not group or not fs_group or not allowed_form:
         return (
        "",
        "Account information incomplete",
        True,
        dash.no_update,
        dash.no_update,
        dash.no_update,
        dash.no_update,
        dash.no_update,
        dash.no_update,
        dash.no_update,
        dash.no_update,
        dash.no_update,
    )
    
        # ---------- NORMALIZE ----------
        amount = float(amount or 0)
    
        cash = 0.0
        banks = {f"bank{i}_amount": 0.0 for i in range(1, 11)}
    
        # ---------- OPENING BALANCE ----------
        if opening_flag and fs_group == "BS":
    
            opening_balance = float(opening_balance or 0)
    
            if opening_balance <= 0:
              return (
        "",
        "Opening balance must be greater than zero",
        True,
        dash.no_update,
        dash.no_update,
        dash.no_update,
        dash.no_update,
        dash.no_update,
        dash.no_update,
        dash.no_update,
        dash.no_update,
        dash.no_update,
    )
    
            if name == "Cash":
                cash = opening_balance
    
            elif name and name.upper().replace(" ", "") in {
                f"BANK{i}" for i in range(1, 11)
            }:
                idx = name.upper().replace(" ", "").replace("BANK", "")
                banks[f"bank{idx}_amount"] = opening_balance
    
            total = opening_balance
    
        else:
    
            if amount <= 0:
                return "", "Amount must be greater than zero", True
    
            if payment_mode == "CASH":
                cash = amount
    
            elif payment_mode and payment_mode.startswith("BANK"):
                idx = payment_mode.replace("BANK", "")
                banks[f"bank{idx}_amount"] = amount
    
            else:
                return "", "Payment mode required", True
    
            total = cash + sum(banks.values())
    
        # ---------- APPEND TO MAPPER ----------
        final_form = resolve_allowed_form_from_group(group, allowed_form)
    
        append_to_mapper(
            line_item=name,
            group=group,
            fs_group=GROUP_FORM_RULES.get(group, {}).get("fs", fs_group),
            form=final_form,
            SessionData=SessionData,
        )
    
        # ---------- APPEND TO MASTER LEDGER ----------
        if total > 0:
    
            payload = {
                "ledger_name": name,
                "ledger_group": group,
                "cash_amount": cash,
                "total_amount": total,
                "transaction_date": date,
                "details": "Manual Account Creation Entry",
                "breakup_cash": "",
            }
    
            payload.update(banks)
    
            for i in range(1, 11):
                payload.setdefault(f"breakup_bank{i}", "")
    
            uid = f"MAN_{datetime.now().strftime('%Y%m%d%H%M%S%f')}"
            ledger_form = FORM_LEDGER_MAP.get(final_form)
    
            if ledger_form:
                append_entry(ledger_form, uid, payload, SessionData)
    
        return (
    "saved", "", False,
    None, None, None, None, None,
    "CASH", None, False, None
)

 
 
 
 
 
    @app.callback(
    Output("submit-toast", "is_open"),
    Input("callback-sink", "children"),
    State("error-toast", "is_open"),
    prevent_initial_call=True
)
    def show_submit_toast(_, error_open):

      if error_open:
        return False

      if _ is None or _ == "":
        return False

      return True

    @app.callback(
        Output("ca-channel-block", "style"),
        Output("ca-opening-balance-block", "style"),
        Output("ca-payment-mode", "value"),
        Output("ca-payment-amount", "value"),
        Input("ca-allowed-form", "value"),
        Input("ca-opening-balance-flag", "value"),
        Input("ca-fs-group", "value"),
    )
    def toggle_entryhub_amount_fields(allowed_form, opening_flag, fs_group):

        show = {"display": "block"}
        hide = {"display": "none"}

        # 1️⃣ JOURNAL BOOK → hide everything
        if allowed_form == "JOURNAL BOOK":
            return hide, hide, "CASH", None

        # 2️⃣ OPENING BALANCE (BS ONLY)
        if opening_flag and fs_group == "BS":
            return hide, show, "CASH", None

        # 3️⃣ DEFAULT → normal payment
        return show, hide, dash.no_update, dash.no_update

    @app.callback(
        Output("ca-account-group", "value"),
        Output("ca-fs-group", "value"),
        Output("ca-fs-group", "options"),
        Output("ca-allowed-form", "value"),
        Output("ca-account-group", "disabled"),
        Input("ca-account-name", "value"),
        Input("ca-account-group", "value"),
        State("session", "data"),
        prevent_initial_call=True,
    )
    def smart_entryhub_autofill(account_name, account_group, SessionData):

        ctx = dash.callback_context
        trigger = ctx.triggered_id

        default_fs_opts = [{"label": g, "value": g} for g in FS_GROUPS]

        # --------------------------------------------------
        # 1️⃣ Account selected → read Mapper.xlsx (AUTHORITATIVE)
        # --------------------------------------------------
        if trigger == "ca-account-name" and account_name:
            try:
                df = pd.read_excel(
                    "/var/Data/" + str(SessionData["username"]) + "/Mapper.xlsx"
                )
            except Exception:
                raise dash.exceptions.PreventUpdate

            row = df.loc[
                df["LINE_ITEM"].astype(str).str.strip().str.lower()
                == account_name.strip().lower()
            ]

            if not row.empty:
                r = row.iloc[0]
                fs = r["FS_GROUP"]

                return (
                    r["GROUP"],  # Account Group
                    fs,  # FS Group
                    [{"label": fs, "value": fs}],  # Lock FS options
                    FORM_NORMALIZER.get(r["FORM"]),
                    True,
                )

            # New account → reset
            return None, None, default_fs_opts, None, False

        # --------------------------------------------------
        # 2️⃣ Group selected manually → derive FS + Allowed Form
        # --------------------------------------------------
        if trigger == "ca-account-group" and account_group:

            rule = GROUP_FORM_RULES.get(account_group)

            fs = rule["fs"] if rule else None
            auto_form = rule["forms"][0] if rule and rule["forms"] else None

            if fs:
                return (
                    dash.no_update,  # keep account name
                    fs,  # auto FS
                    [{"label": fs, "value": fs}],  # lock FS dropdown
                    auto_form,
                    False,
                )

        raise dash.exceptions.PreventUpdate

    @app.callback(
    Output("callback-sink", "children", allow_duplicate=True),
    Output("error-toast", "children", allow_duplicate=True),
    Output("error-toast", "is_open", allow_duplicate=True),

    Output("contra-debit", "value", allow_duplicate=True),
    Output("contra-credit", "value", allow_duplicate=True),
    Output("contra-amount", "value", allow_duplicate=True),
    Output("contra-date", "date", allow_duplicate=True),

    Input("submit-contra", "n_clicks"),
    State("contra-debit", "value"),
    State("contra-credit", "value"),
    State("contra-amount", "value"),
    State("contra-date", "date"),
    State("session", "data"),
    prevent_initial_call=True,
)
    def submit_contra(n, debit, credit, amount, date, SessionData):

    
        if not n:
            return "", "", False
    
        # ---------------- DATE VALIDATION ----------------
        if not date:
            return "", "Transaction date is mandatory", True
    
        # ---------------- ACCOUNT VALIDATION ----------------
        if not debit or not credit:
            return "", "Debit and Credit accounts are required", True
    
        if debit == credit:
            return "", "Debit and Credit accounts cannot be the same", True
    
        # ---------------- AMOUNT VALIDATION ----------------
        amount = float(amount or 0)
    
        if amount <= 0:
            return "", "Amount must be greater than zero", True
    
        amount = -amount
    
        # ---------------- INITIALISE CHANNELS ----------------
        payload = {
            "ledger_name": "Contra Entry",
            "ledger_group": "Cash-in-Hand",
            "cash_amount": 0.0,
            "total_amount": 0.0,   # contra net = 0
            "transaction_date": date,
            "details": f"Contra: {debit} → {credit}",
            "breakup_cash": "",
        }
    
        for i in range(1, 11):
            payload[f"bank{i}_amount"] = 0.0
            payload[f"breakup_bank{i}"] = ""
    
        # ---------------- CREDIT LEG ----------------
        if credit == "CASH":
            payload["cash_amount"] += amount
        else:
            idx = credit.replace("BANK", "")
            payload[f"bank{idx}_amount"] += amount
    
        # ---------------- DEBIT LEG ----------------
        if debit == "CASH":
            payload["cash_amount"] -= amount
        else:
            idx = debit.replace("BANK", "")
            payload[f"bank{idx}_amount"] -= amount
    
        uid = f"CONTRA_{datetime.now().strftime('%Y%m%d%H%M%S%f')}"
    
        append_entry("OTHER PAYMENT", uid, payload, SessionData)
    
        return (
    "saved", "", False,
    None,
    None,
    None,
    None
)



    @app.callback(
        Output("ca-date", "min_date_allowed"),
        Output("ca-date", "max_date_allowed"),
        Output("expense-date", "min_date_allowed"),
        Output("expense-date", "max_date_allowed"),
        Output("salary-date", "min_date_allowed"),
        Output("salary-date", "max_date_allowed"),
        Output("other-receipt-date", "min_date_allowed"),
        Output("other-receipt-date", "max_date_allowed"),
        Output("other-payment-date", "min_date_allowed"),
        Output("other-payment-date", "max_date_allowed"),
        Output("journal-date", "min_date_allowed"),
        Output("journal-date", "max_date_allowed"),
        Output("fee-receipt-date", "min_date_allowed"),
        Output("fee-receipt-date", "max_date_allowed"),
        Output("contra-date", "min_date_allowed"),
        Output("contra-date", "max_date_allowed"),
        Input("financial-year-dropdown", "value"),
        State("selected-form-name", "data"),
    )
    def restrict_dates(selected_fy, selected_form):

        if not selected_fy or not selected_form:
            raise dash.exceptions.PreventUpdate

        start_date, end_date = get_fy_date_range(selected_fy)

        start = start_date.strftime("%Y-%m-%d")
        end = end_date.strftime("%Y-%m-%d")
        print("FY Restriction Triggered:", selected_fy)

        return (
            start,
            end,
            start,
            end,
            start,
            end,
            start,
            end,
            start,
            end,
            start,
            end,
            start,
            end,
            start,
            end,
        )

    @app.callback(
        Output("error-toast", "children"),
        Output("error-toast", "is_open"),
        Output("submit-toast", "is_open", allow_duplicate=True),  # ✅ FIX
        [
            Input("submit-fee-receipt", "n_clicks"),
            Input("submit-other-receipt", "n_clicks"),
        ],
        State("student-name", "value"),
        *[State(f"or-account-{i}", "value") for i in range(len(OTHER_RECEIPT_HEADS))],
        *[State(f"or-amount-{i}", "value") for i in range(len(OTHER_RECEIPT_HEADS))],
        State("session", "data"),
        prevent_initial_call=True,
    )
    def validation_guard(fee_click, other_receipt_click, student_name, *vals):
        ctx = dash.callback_context
        trigger = ctx.triggered_id

        *or_vals, SessionData = vals

        # ---------------- FEES RECEIPT ----------------
        if trigger == "submit-fee-receipt":
            if not student_name or not str(student_name).strip():
                return (
                    "Student Name / Roll No. / Class is mandatory for Fees Receipt.",
                    True,
                    False,
                )

        # ---------------- OTHER RECEIPT ----------------
        if trigger == "submit-other-receipt":
            n = len(OTHER_RECEIPT_HEADS)
            accounts = or_vals[:n]
            amounts = or_vals[n : 2 * n]

            for acc, amt in zip(accounts, amounts):
                if float(amt or 0) > 0 and not (acc or "").strip():
                    return (
                        "Account / Party Name is required when amount is entered in Other Receipt.",
                        True,
                        False,
                    )

        # ✅ All validations passed → allow success toast
        return "", False, dash.no_update

    @app.callback(
        Output("ca-date", "date"),
        Output("ca-date", "disabled"),
        Input("ca-opening-balance-flag", "value"),
        Input("financial-year-dropdown", "value"),
        prevent_initial_call=True,
    )
    def handle_opening_balance(flag, selected_fy):

        if not selected_fy:
            raise dash.exceptions.PreventUpdate

        start_date, end_date = get_fy_date_range(selected_fy)

        if flag:
            # Opening balance date = previous FY end
            opening_date = start_date.replace(day=31, month=3)
            return opening_date.strftime("%Y-%m-%d"), True

        return start_date.strftime("%Y-%m-%d"), False

    @app.callback(
        Output("student-name", "options"),
        Input("selected-form-name", "data"),
        State("session", "data"),
        prevent_initial_call=True,
    )
    def load_students_dropdown(selected_form, SessionData):

        if selected_form != "FEES RECEIPT":
            raise dash.exceptions.PreventUpdate

        base = f"/var/Data/{SessionData['username']}"

        student_path = f"{base}/student_log.csv"
        fee_map_path = f"{base}/fee_structure_static.csv"

        if not os.path.exists(student_path):
            return []

        df_students = pd.read_csv(student_path)

        # ---------------- Load class mapping ----------------
        if os.path.exists(fee_map_path):
            df_map = pd.read_csv(fee_map_path)

            class_map = dict(zip(df_map["studying_class"], df_map["standard"]))
        else:
            class_map = {}

        options = []

        for _, row in df_students.iterrows():

            class_code = row["studying_class"]

            class_name = class_map.get(class_code, class_code)

            label = f"{row['student_name']} / {row['admission_no']} / {class_name}"
            value = f"{row['student_name']}/{row['admission_no']}/{class_name}"

            options.append({"label": label, "value": value})

        return options
    

    @app.callback(
    Output("employee-name", "options"),
    Input("selected-form-name", "data"),
    State("session", "data"),
    prevent_initial_call=True,
)
    def load_teacher_dropdown(selected_form, SessionData):
     if not selected_form:
        raise dash.exceptions.PreventUpdate

     if selected_form != "SALARY PAYMENT":
        raise dash.exceptions.PreventUpdate

     if not SessionData:
        return []
     if selected_form != "SALARY PAYMENT":
        return []

     base = f"/var/Data/{SessionData['username']}"
     teacher_path = f"{base}/teacher_log.csv"

     if not os.path.exists(teacher_path):
        return []

     try:
        df = pd.read_csv(teacher_path)
     except Exception:
        return []

     if df.empty:
        return []

     options = []

     for _, row in df.iterrows():

        teacher_id = row.get("teacher_id", "")
        name = row.get("full_name", "")

        if not name:
            continue

        options.append({
            "label": f"{name} / {teacher_id}",
            "value": name
        })

     return options

    @app.callback(
    Output("asset-sale-modal","is_open"),
    Input("sell-asset-btn","n_clicks"),
    State("ca-account-group","value"),
    prevent_initial_call=True
    )
    def open_sale_modal(n, group):
    
        if group == "Fixed Assets":
            return True
    
        return False

    @app.callback(
        Output("callback-sink", "children", allow_duplicate=True),
        Output("submit-toast", "is_open", allow_duplicate=True),
        Input("submit-asset-sale", "n_clicks"),
        State("ca-account-name", "value"),
        State("asset-sale-gain", "value"),
        State("asset-sale-mode", "value"),
        State("asset-sale-date", "date"),
        State("session", "data"),
        prevent_initial_call=True,
    )
    def submit_asset_sale(n, asset_name, gain, mode, sale_date, SessionData):
    
        if not n or not asset_name or not gain or not sale_date:
            return "", False
    
        gain = float(gain)
    
        # ---------------- CHANNEL ALLOCATION ----------------
        cash_amt = 0.0
        bank_totals = {f"bank{i}_amount": 0.0 for i in range(1, 11)}
    
        breakup_cash = ""
        breakup_banks = {f"breakup_bank{i}": "" for i in range(1, 11)}
    
        if mode == "CASH":
            cash_amt = gain
        elif mode.startswith("BANK"):
            idx = mode.replace("BANK", "")
            bank_totals[f"bank{idx}_amount"] = gain

        user = SessionData["username"]

        master_path = f"/var/Data/{user}/master_ledger.csv"
        journal_path = f"/var/Data/{user}/journal_ledger.csv"
        
        # ---------------- DELETE ASSET ENTRY ----------------
        
        if os.path.exists(master_path):
            df = pd.read_csv(master_path)
        
            df = df[df["ledger_name"] != asset_name]
        
            df.to_csv(master_path, index=False)
        
        
        if os.path.exists(journal_path):
            df = pd.read_csv(journal_path)
        
            df = df[df["ledger_name"] != asset_name]
        
            df.to_csv(journal_path, index=False)
    
        # ---------------- BUILD PAYLOAD ----------------
        payload = {
            "ledger_name": "Reserve and Surplus",
            "account_name": asset_name,
            "ledger_group": "Reserve & Surplus",
            "cash_amount": cash_amt,
            "total_amount": gain,
            "breakup_cash": breakup_cash,
            "transaction_date": sale_date,
            "details": f"Gain on sale of asset {asset_name}",
        }
    
        payload.update(bank_totals)
    
        for i in range(1, 11):
            payload[f"breakup_bank{i}"] = breakup_banks[f"breakup_bank{i}"]
    
        uid = f"MAN_{datetime.now().strftime('%Y%m%d%H%M%S%f')}"
    
        append_entry("OTHER RECEIPT", uid, payload, SessionData)
    
        return "", True


    @app.callback(
        Output("download-salary-slip-pdf", "data"),
        Input("print-salary-slip", "n_clicks"),
        State("employee-name", "value"),
        State("salary-date", "date"),
        State("salary-comp-0", "value"),
        State("salary-comp-1", "value"),
        State("salary-comp-2", "value"),
        State("salary-comp-3", "value"),
        State("session", "data"),
        prevent_initial_call=True,
    )
    def generate_salary_slip(n, emp, date, c1, c2, c3, c4, SessionData):
    
        if not n:
            return dash.no_update
    
        # ---------------- SAFE NUMERIC ----------------
        c1 = float(c1 or 0)
        c2 = float(c2 or 0)
        c3 = float(c3 or 0)
        c4 = float(c4 or 0)
    
        # ---------------- LOAD CONFIG ----------------
        config = load_statutory_config(SessionData)
    
        gross = c1 + c2 + c3 + c4
    
        pf_base = c1 + c2
        esi_base = c1 + c2
    
        pf = round(pf_base * config["PF_RATE"], 2) if config["PF_ENABLED"] else 0
        esi = round(esi_base * config["ESI_RATE"], 2) if config["ESI_ENABLED"] else 0
        tds = round(gross * config["TDS_RATE"], 2) if config["TDS_ENABLED"] else 0
    
        net = round(gross - pf - esi - tds, 2)
    
        # ---------------- LOAD SCHOOL INFO ----------------
        school_name = "Your Organization"
        school_pan = "N/A"
    
        info_path = f"/var/Data/{SessionData['username']}/school_info.csv"
    
        if os.path.exists(info_path):
            df_info = pd.read_csv(info_path)
            if not df_info.empty:
                school_name = df_info.loc[0].get("school_name", school_name)
                school_pan = df_info.loc[0].get("pan_number", school_pan)
    
        # ---------------- LOAD TEACHER PAN + UAN ----------------
        teacher_pan = "-"
        teacher_uan = "-"
    
        teacher_path = f"/var/Data/{SessionData['username']}/teacher_log.csv"
    
        if os.path.exists(teacher_path):
            df_teacher = pd.read_csv(teacher_path)
    
            t = df_teacher[df_teacher["full_name"] == emp]
    
            if not t.empty:
                teacher_pan = t.iloc[0].get("pan_number", "-")
                teacher_uan = t.iloc[0].get("uan", "-")
    
                # handle NaN
                if pd.isna(teacher_pan):
                    teacher_pan = "-"
                if pd.isna(teacher_uan):
                    teacher_uan = "-"
    
        # ---------------- PDF SETUP ----------------
        buffer = io.BytesIO()
        c = canvas.Canvas(buffer, pagesize=A4)
        width, height = A4
    
        y = height - 50
    
        # ---------------- LOGO ----------------
        logo_path = f"/var/Data/{SessionData['username']}/school_fees_logo.png"
    
        if os.path.exists(logo_path):
            logo = ImageReader(logo_path)
            c.drawImage(
                logo,
                (width - 120) / 2,
                y - 60,
                width=120,
                height=60,
                preserveAspectRatio=True,
                mask="auto",
            )
            y -= 80
    
        # ---------------- HEADER ----------------
        c.setFont("Helvetica-Bold", 14)
        c.drawCentredString(width / 2, y, school_name)
        y -= 15
    
        c.setFont("Helvetica", 9)
        c.drawCentredString(width / 2, y, f"PAN: {school_pan}")
        y -= 25
    
        c.setFont("Helvetica-Bold", 14)
        c.drawCentredString(width / 2, y, "SALARY SLIP")
        y -= 25
    
        # ---------------- EMPLOYEE DETAILS ----------------
        c.setFont("Helvetica", 10)
    
        c.drawString(50, y, f"Employee Name: {emp}")
        c.drawRightString(width - 50, y, f"Date: {date}")
        y -= 18
    
        # ✅ NEW LINES ADDED
        c.drawString(50, y, f"Employee PAN: {teacher_pan}")
        c.drawRightString(width - 50, y, f"UAN: {teacher_uan}")
        y -= 25
    
        # ---------------- TABLE HEADER ----------------
        c.setFont("Helvetica-Bold", 11)
    
        c.drawString(50, y, "Earnings")
        c.drawRightString(width / 2, y, "Amount")
    
        c.drawString(width / 2 + 20, y, "Deductions")
        c.drawRightString(width - 50, y, "Amount")
    
        y -= 10
        c.line(50, y, width - 50, y)
        y -= 15
    
        # ---------------- DATA ----------------
        c.setFont("Helvetica", 10)
    
        earnings = [
            ("Basic Salary", c1),
            ("D.A.", c2),
            ("Other Allowances", c3),
            ("HRA", c4),
        ]
    
        deductions = [
            ("Provident Fund", pf),
            ("ESI", esi),
            ("TDS", tds),
        ]
    
        max_rows = max(len(earnings), len(deductions))
    
        for i in range(max_rows):
            if i < len(earnings):
                name, val = earnings[i]
                c.drawString(50, y, name)
                c.drawRightString(width / 2, y, f"{val:,.2f}")
    
            if i < len(deductions):
                name, val = deductions[i]
                c.drawString(width / 2 + 20, y, name)
                c.drawRightString(width - 50, y, f"{val:,.2f}")
    
            y -= 18
    
        # ---------------- TOTALS ----------------
        total_ded = pf + esi + tds
    
        y -= 10
        c.line(50, y, width - 50, y)
        y -= 20
    
        c.setFont("Helvetica-Bold", 11)
    
        c.drawString(50, y, "Gross Earnings")
        c.drawRightString(width / 2, y, f"{gross:,.2f}")
    
        c.drawString(width / 2 + 20, y, "Total Deductions")
        c.drawRightString(width - 50, y, f"{total_ded:,.2f}")
    
        y -= 25
    
        # ---------------- NET PAY ----------------
        c.setFont("Helvetica-Bold", 12)
        c.drawString(50, y, f"Net Pay: ₹ {net:,.2f}")
        y -= 18
    
        # ---------------- NET IN WORDS ----------------
        try:
            from num2words import num2words
            words = num2words(net, to='cardinal', lang='en_IN')
        except:
            words = str(net)
    
        c.setFont("Helvetica", 10)
        c.drawString(50, y, f"Net Pay (in words): {words}")
        y -= 30
    
        # ---------------- FOOTER ----------------
        c.setFont("Helvetica", 8)
    
        compliance = [
            "1. Issued under EPF Act, 1952.",
            "2. TDS deducted as per Income Tax Act.",
            "3. ESI as per applicable laws.",
            "4. This is a computer-generated document.",
        ]
    
        for line in compliance:
            c.drawString(50, y, line)
            y -= 12
    
        # ---------------- SAVE ----------------
        c.showPage()
        c.save()
        buffer.seek(0)
    
        return dcc.send_bytes(buffer.getvalue(), filename=f"{emp}_salary_slip.pdf")

