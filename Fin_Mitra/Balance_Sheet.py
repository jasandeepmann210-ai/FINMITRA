import dash
from dash import html, dcc, Input, Output, State
import dash_bootstrap_components as dbc
import pandas as pd
from datetime import date
import os, time
import re
from dash.exceptions import PreventUpdate
from dash.dcc import send_bytes
import io, xlsxwriter
from datetime import datetime, date
from reportlab.platypus import (
    SimpleDocTemplate,
    Table,
    TableStyle,
    Paragraph,
    Spacer,
    LongTable,
)
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4


def get_fy_date_range(selected_fy):
    if not selected_fy:
        return None, None

    fy_year = int(selected_fy.replace("FY", ""))
    end_year = 2000 + fy_year
    start_year = end_year - 1

    start_date = date(start_year, 4, 1)
    end_date = date(end_year, 3, 31)

    return start_date, end_date


# =====================================================
# HARD-CODED BS STRUCTURE (AUTHORITATIVE)
# =====================================================
ASSETS = [
    "Fixed Assets",
    "Investments",
    "Loans and Advances",
    "Cash-in-Hand",
    "Bank Accounts",
    "Current Assets",
    "Sundry debtors",
    "Inventories",
]

LIABILITIES = [
    "Reserve & Surplus",
    "Current Liabilities",
    "Sundry creditors",
    "Non-current liabilities Secured loans",
    "Non-current liabilities Unsecured loans",
    "Provisions (Bad Debts, Warranty)",
    "Deferred Tax",
    "Unearned Revenue",
]


def get_bank_name_map(SessionData):
    path = f"/var/Data/{SessionData['username']}/bank_name_static.csv"
    try:
        df = pd.read_csv(path)
        df["bank_code"] = df["bank_code"].str.strip().str.upper()
        df["bank_label"] = df["bank_label"].str.strip()
        return dict(zip(df["bank_code"], df["bank_label"]))
    except:
        return {}


# =====================================================
# DATE PARSER
# =====================================================
def parse_date(series):
    return pd.to_datetime(series, errors="coerce")


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


# =====================================================
# CASH / BANK — SOURCE OF TRUTH
# =====================================================
def get_cash_closing_balance(as_of_date, SessionData):

    MASTER_LEDGER_PATH = (
        "/var/Data/" + str(SessionData["username"]) + "/master_ledger.csv"
    )

    df = pd.read_csv(MASTER_LEDGER_PATH)
    df["transaction_date"] = (
        df["transaction_date"].apply(normalize_txn_date).dt.normalize()
    )
    df["cash_amount"] = pd.to_numeric(df["cash_amount"], errors="coerce").fillna(0)

    df = df[(df["cash_amount"] != 0) & (df["transaction_date"] <= as_of_date)]

    receipts = df[df["form_name"].isin(["FEES RECEIPT", "OTHER RECEIPT"])][
        "cash_amount"
    ].sum()

    payments = df[
        df["form_name"].isin(["EXPENSES", "SALARY PAYMENT", "OTHER PAYMENT"])
    ]["cash_amount"].sum()

    return receipts - payments


def get_bank_closing_balance(as_of_date, bank_col, SessionData):

    MASTER_LEDGER_PATH = (
        "/var/Data/" + str(SessionData["username"]) + "/master_ledger.csv"
    )

    df = pd.read_csv(MASTER_LEDGER_PATH)
    df["transaction_date"] = (
        df["transaction_date"].apply(normalize_txn_date).dt.normalize()
    )

    col = f"{bank_col}_amount"
    if col not in df.columns:
        return 0.0

    df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0)

    df = df[(df[col] != 0) & (df["transaction_date"] <= as_of_date)]

    receipts = df[df["form_name"].isin(["FEES RECEIPT", "OTHER RECEIPT"])][col].sum()

    payments = df[
        df["form_name"].isin(
            ["EXPENSES", "SALARY PAYMENT", "OTHER PAYMENT", "DECLARE ASSETS"]
        )
    ][col].sum()

    return receipts - payments


def get_layout1():
    return dbc.Container(
        [
            html.H3("BALANCE SHEET", className="text-center my-4"),
            dbc.Row(
                [
                    dbc.Col(
                        dcc.DatePickerSingle(
                            id="bs-date",
                            date=date.today(),
                            display_format="DD-MM-YYYY",
                        ),
                        md=3,
                    ),
                    dbc.Col(
                        dbc.Button(
                            "Run",
                            id="run-bs-btn",
                            color="primary",
                            className="me-2",
                        ),
                        width="auto",
                    ),
                    dbc.Col(
                        dbc.Button(
                            "Download Balance Sheet (Excel)",
                            id="download-bs-btn",
                            color="success",
                        ),
                        width="auto",
                    ),
                    dbc.Col(
                        dbc.Button(
                            "Download Balance Sheet (PDF)",
                            id="download-bs-pdf-btn",
                            color="danger",
                        ),
                        width="auto",
                    ),
                    dcc.Download(id="download-bs-pdf-file"),
                    dcc.Download(id="download-bs-file"),
                ],
                className="mb-4 align-items-end justify-content-center",
            ),
            dbc.Row(
                [
                    dbc.Col(
                        [
                            html.H5("LIABILITIES", className="text-center mb-3"),
                            html.Div(id="bs-liabilities"),
                        ],
                        md=6,
                    ),
                    dbc.Col(
                        [
                            html.H5("ASSETS", className="text-center mb-3"),
                            html.Div(id="bs-assets"),
                        ],
                        md=6,
                    ),
                ]
            ),
        ],
        fluid=True,
    )


# =====================================================
# CALLBACKS
# =====================================================
def register_callbacks(app):

    @app.callback(
        Output("bs-liabilities", "children"),
        Output("bs-assets", "children"),
        Input("run-bs-btn", "n_clicks"),
        State("bs-date", "date"),
        State("session", "data"),
        prevent_initial_call=True,
    )
    def update_balance_sheet(n_clicks, as_of_date, SessionData):

        MELT_DB_PATH = "/var/Data/" + str(SessionData["username"]) + "/melt_db.csv"

        if not n_clicks or not as_of_date:
            return [], []

        as_of = pd.to_datetime(as_of_date)

        # -------------------------------------------------
        # LOAD melt_db
        # -------------------------------------------------
        time.sleep(0.05)

        df = pd.read_csv(MELT_DB_PATH)
        df["transaction_date"].iloc[-1] = df["transaction_date"].iloc[-1] + " 00:00:00"
        df["transaction_date"] = parse_date(df["transaction_date"])
        df["amount"] = pd.to_numeric(df["amount"], errors="coerce").fillna(0)
        df["GROUP"] = df["GROUP"].astype(str).str.strip()

        df = df[(df["FS_GROUP"] == "BS") & (df["transaction_date"] <= as_of)]

        grouped = df.groupby(["GROUP", "LINE_ITEM"], as_index=False)["amount"].sum()

        # -------------------------------------------------
        # OVERRIDE CASH
        # -------------------------------------------------
        grouped = grouped[grouped["GROUP"] != "Cash-in-Hand"]
        grouped = pd.concat(
            [
                grouped,
                pd.DataFrame(
                    [
                        {
                            "GROUP": "Cash-in-Hand",
                            "LINE_ITEM": "Cash Balance",
                            "amount": get_cash_closing_balance(as_of, SessionData),
                        }
                    ]
                ),
            ],
            ignore_index=True,
        )

        # -------------------------------------------------
        # OVERRIDE BANKS (DYNAMIC + ZERO SKIP)
        # -------------------------------------------------
        grouped = grouped[grouped["GROUP"] != "Bank Accounts"]

        bank_map = get_bank_name_map(SessionData)
        banks_data = []

        for i in range(1, 11):

            bank_code = f"BANK{i}"
            bank_col = f"bank{i}"

            balance = get_bank_closing_balance(as_of, bank_col, SessionData)

            if balance == 0:
                continue  # skip zero balance banks

            bank_label = bank_map.get(bank_code, f"Bank-{i}")

            banks_data.append(
                {
                    "GROUP": "Bank Accounts",
                    "LINE_ITEM": bank_label,
                    "amount": balance,
                }
            )

        if banks_data:
            grouped = pd.concat(
                [grouped, pd.DataFrame(banks_data)],
                ignore_index=True,
            )
        # -------------------------------------------------
        # TOTALS
        # -------------------------------------------------
        total_assets = grouped[grouped["GROUP"].isin(ASSETS)]["amount"].sum()
        total_liabilities = grouped[grouped["GROUP"].isin(LIABILITIES)]["amount"].sum()

        # -------------------------------------------------
        # RENDER HELPERS
        # -------------------------------------------------
        def render(groups):
            out = []

            for g in groups:

              gdf = grouped[grouped["GROUP"].str.lower() == g.lower()]

    # agar group me koi data nahi hai to skip karo
              if gdf.empty:
                continue

              total = gdf["amount"].sum()

    # agar total 0 hai to bhi skip karo
              if total == 0:
               continue
              out.append(
                    dbc.Accordion(
                        [
                            dbc.AccordionItem(
                                title=f"{g} — {total:,.2f}",
                                children=[
                                    dbc.Table(
                                        [
                                            html.Tbody(
                                                [
                                                    html.Tr(
                                                        [
                                                            html.Td(r.LINE_ITEM),
                                                            html.Td(
                                                                f"{r.amount:,.2f}",
                                                                className="text-end",
                                                            ),
                                                        ]
                                                    )
                                                    for _, r in gdf.iterrows()
                                                ]
                                            )
                                        ],
                                        bordered=True,
                                        size="sm",
                                    )
                                ],
                            )
                        ],
                        flush=True,
                    )
                )
            return out

        def render_total(label, value):
            return dbc.Card(
                dbc.CardBody(
                    dbc.Row(
                        [
                            dbc.Col(html.B(label), md=6),
                            dbc.Col(
                                html.B(f"{value:,.2f}"),
                                md=6,
                                className="text-end",
                            ),
                        ]
                    )
                ),
                className="mt-3 border-2",
                color="light",
            )

        # -------------------------------------------------
        # FINAL RETURN
        # -------------------------------------------------
        return (
            render(LIABILITIES)
            + [render_total("TOTAL LIABILITIES", total_liabilities)],
            render(ASSETS) + [render_total("TOTAL ASSETS", total_assets)],
        )

    def write_group(ws, row, col, title, gdf, header, th, td, amt):
        total = gdf["amount"].sum() if not gdf.empty else 0

        ws.merge_range(row, col, row, col + 1, f"{title} — {total:,.2f}", header)
        row += 1

        ws.write(row, col, "Particulars", th)
        ws.write(row, col + 1, "Amount", th)
        row += 1

        if gdf.empty:
            ws.write(row, col, "—", td)
            ws.write(row, col + 1, 0, amt)
            row += 1
        else:
            for _, r in gdf.iterrows():
                ws.write(row, col, r.LINE_ITEM, td)
                ws.write(row, col + 1, r.amount, amt)
                row += 1

        return row + 1

    @app.callback(
        Output("download-bs-file", "data"),
        Input("download-bs-btn", "n_clicks"),
        State("bs-date", "date"),
        State("session", "data"),
        prevent_initial_call=True,
    )
    def download_bs(n, as_of_date, SessionData):

        school_name = ""
        address = ""
        pan = ""

        try:
            user = SessionData["username"]

            df_school = pd.read_csv(f"/var/Data/{user}/school_info.csv")

            school_name = df_school.loc[0, "school_name"]
            address = df_school.loc[0, "address"]
            pan = df_school.loc[0, "pan_number"]

        except:
            pass
        if not as_of_date:
            return dash.no_update

        as_of = pd.to_datetime(as_of_date)

        MELT_DB_PATH = f"/var/Data/{SessionData['username']}/melt_db.csv"
        df = pd.read_csv(MELT_DB_PATH)

        df["transaction_date"] = parse_date(df["transaction_date"])
        df["amount"] = pd.to_numeric(df["amount"], errors="coerce").fillna(0)

        df = df[(df["FS_GROUP"] == "BS") & (df["transaction_date"] <= as_of)]

        grouped = df.groupby(["GROUP", "LINE_ITEM"], as_index=False)["amount"].sum()

        # CASH override
        grouped = grouped[grouped["GROUP"] != "Cash-in-Hand"]
        grouped = pd.concat(
            [
                grouped,
                pd.DataFrame(
                    [
                        {
                            "GROUP": "Cash-in-Hand",
                            "LINE_ITEM": "Cash Balance",
                            "amount": get_cash_closing_balance(as_of, SessionData),
                        }
                    ]
                ),
            ],
            ignore_index=True,
        )

        # BANK override
        # -----------------------------------------
        # REMOVE OLD BANKS
        # -----------------------------------------
        grouped = grouped[grouped["GROUP"] != "Bank Accounts"]

        bank_map = get_bank_name_map(SessionData)
        banks = []

        for i in range(1, 11):

            bank_code = f"BANK{i}"
            bank_col = f"bank{i}"

            if bank_code not in bank_map:
                continue

            balance = get_bank_closing_balance(as_of, bank_col, SessionData)

            if balance == 0:
                continue

            bank_label = bank_map[bank_code]

            banks.append(
                {"GROUP": "Bank Accounts", "LINE_ITEM": bank_label, "amount": balance}
            )

        if banks:
            grouped = pd.concat([grouped, pd.DataFrame(banks)], ignore_index=True)
        # ==============================
        # BALANCING FIGURE (Reserve & Surplus)
        # ==============================

        # Assets ka total
        total_assets = grouped[grouped["GROUP"].isin(ASSETS)]["amount"].sum()

        # Reserve & Surplus ke alawa sab liabilities
        other_liabilities = grouped[
            (grouped["GROUP"].isin(LIABILITIES))
            & (grouped["GROUP"] != "Reserve & Surplus")
        ]["amount"].sum()

        reserve_surplus = total_assets - other_liabilities

        # Purana Reserve & Surplus hatao
        grouped = grouped[grouped["GROUP"] != "Reserve & Surplus"]

        

        # ================= EXCEL =================
        output = io.BytesIO()
        wb = xlsxwriter.Workbook(output, {"in_memory": True})
        title = wb.add_format({"bold": True, "align": "center", "font_size": 14})
        ws = wb.add_worksheet("Balance Sheet")
        # SCHOOL HEADER
        ws.merge_range("A1:E1", school_name, title)
        ws.merge_range("A2:B2", f"PAN : {pan}")
        ws.merge_range("C2:E2", address)

        ws.set_column("A:A", 35)
        ws.set_column("B:B", 15)
        ws.set_column("D:D", 35)
        ws.set_column("E:E", 15)

        bold = wb.add_format({"bold": True})
        header = wb.add_format({"bold": True, "bg_color": "#D9E1F2", "border": 1})
        th = wb.add_format({"bold": True, "border": 1})
        td = wb.add_format({"border": 1})
        amt = wb.add_format({"border": 1, "num_format": "#,##0.00"})
        total_fmt = wb.add_format({"bold": True, "top": 1, "num_format": "#,##0.00"})

        ws.merge_range("A3:E3", "BALANCE SHEET", bold)
        ws.merge_range("A4:E4", f"As on {as_of.strftime('%d-%m-%Y')}", bold)

        row = 4
        ws.write(row, 0, "LIABILITIES", bold)
        ws.write(row, 3, "ASSETS", bold)
        row += 1

        liab_row = row
        asset_row = row

        for g in LIABILITIES:

         gdf = grouped[grouped["GROUP"] == g]

         if gdf.empty:
          continue

         if gdf["amount"].sum() == 0:
          continue

         liab_row = write_group(ws, liab_row, 0, g, gdf, header, th, td, amt)

        for g in ASSETS:

         gdf = grouped[grouped["GROUP"] == g]

         if gdf.empty:
          continue

         if gdf["amount"].sum() == 0:
          continue

         asset_row = write_group(ws, asset_row, 3, g, gdf, header, th, td, amt)
        final_row = max(liab_row, asset_row) + 1

        ws.merge_range(
            final_row,
            0,
            final_row,
            1,
            f"TOTAL LIABILITIES — {grouped[grouped['GROUP'].isin(LIABILITIES)]['amount'].sum():,.2f}",
            total_fmt,
        )
        ws.merge_range(
            final_row,
            3,
            final_row,
            4,
            f"TOTAL ASSETS — {grouped[grouped['GROUP'].isin(ASSETS)]['amount'].sum():,.2f}",
            total_fmt,
        )

        wb.close()
        output.seek(0)

        return send_bytes(
            output.getvalue(), f"Balance_Sheet_{as_of.strftime('%d_%m_%Y')}.xlsx"
        )

    @app.callback(
        Output("bs-date", "date"),
        Input("financial-year-dropdown", "value"),
    )
    def auto_set_bs_date(selected_fy):

        if not selected_fy:
            raise PreventUpdate

        _, end_date = get_fy_date_range(selected_fy)

        return end_date.strftime("%Y-%m-%d")

    @app.callback(
        Output("download-bs-pdf-file", "data"),
        Input("download-bs-pdf-btn", "n_clicks"),
        State("bs-date", "date"),
        State("session", "data"),
        prevent_initial_call=True,
    )
    def download_bs_pdf(n, as_of_date, SessionData):

        if not n:
            raise PreventUpdate

        school_name = ""
        address = ""
        pan = ""

        try:
            user = SessionData["username"]

            df_school = pd.read_csv(f"/var/Data/{user}/school_info.csv")

            school_name = df_school.loc[0, "school_name"]
            address = df_school.loc[0, "address"]
            pan = df_school.loc[0, "pan_number"]

        except:
            pass

        as_of = pd.to_datetime(as_of_date)

        MELT_DB_PATH = f"/var/Data/{SessionData['username']}/melt_db.csv"

        df = pd.read_csv(MELT_DB_PATH)

        df["transaction_date"] = parse_date(df["transaction_date"])
        df["amount"] = pd.to_numeric(df["amount"], errors="coerce").fillna(0)
        df["GROUP"] = df["GROUP"].astype(str).str.strip()

        df = df[(df["FS_GROUP"] == "BS") & (df["transaction_date"] <= as_of)]

        grouped = df.groupby(["GROUP", "LINE_ITEM"], as_index=False)["amount"].sum()

        # CASH override
        grouped = grouped[grouped["GROUP"] != "Cash-in-Hand"]

        grouped = pd.concat(
            [
                grouped,
                pd.DataFrame(
                    [
                        {
                            "GROUP": "Cash-in-Hand",
                            "LINE_ITEM": "Cash Balance",
                            "amount": get_cash_closing_balance(as_of, SessionData),
                        }
                    ]
                ),
            ],
            ignore_index=True,
        )

        # BANK override
        grouped = grouped[grouped["GROUP"] != "Bank Accounts"]

        bank_map = get_bank_name_map(SessionData)

        banks = []

        for i in range(1, 11):

            bank_code = f"BANK{i}"
            bank_col = f"bank{i}"

            balance = get_bank_closing_balance(as_of, bank_col, SessionData)

            if balance == 0:
                continue

            bank_label = bank_map.get(bank_code, f"Bank-{i}")

            banks.append(
                {"GROUP": "Bank Accounts", "LINE_ITEM": bank_label, "amount": balance}
            )

        if banks:
            grouped = pd.concat([grouped, pd.DataFrame(banks)], ignore_index=True)

        # -------- LIABILITIES TABLE --------

        liab_table = [["Particulars", "Amount"]]

        for g in LIABILITIES:

            gdf = grouped[grouped["GROUP"] == g]
            if gdf.empty:
                continue    

            total = gdf["amount"].sum()
             
            if total == 0:
             continue

            liab_table.append([f"<b>{g}</b>", f"<b>{total:,.2f}</b>"])

            for _, r in gdf.iterrows():
                liab_table.append(
                    [f"&nbsp;&nbsp;&nbsp;{r.LINE_ITEM}", f"{r.amount:,.2f}"]
                )

        total_liab = grouped[grouped["GROUP"].isin(LIABILITIES)]["amount"].sum()

        liab_table.append(["<b>TOTAL LIABILITIES</b>", f"<b>{total_liab:,.2f}</b>"])

        # -------- ASSETS TABLE --------

        asset_table = [["Particulars", "Amount"]]

        for g in ASSETS:

            gdf = grouped[grouped["GROUP"] == g]
            if gdf.empty:
                continue
            total = gdf["amount"].sum()
            if total == 0:
             continue
            asset_table.append([f"<b>{g}</b>", f"<b>{total:,.2f}</b>"])

            for _, r in gdf.iterrows():
                asset_table.append(
                    [f"&nbsp;&nbsp;&nbsp;{r.LINE_ITEM}", f"{r.amount:,.2f}"]
                )

        total_assets = grouped[grouped["GROUP"].isin(ASSETS)]["amount"].sum()

        asset_table.append(["<b>TOTAL ASSETS</b>", f"<b>{total_assets:,.2f}</b>"])

        # -------- PDF --------

        buffer = io.BytesIO()

        doc = SimpleDocTemplate(buffer, pagesize=A4, leftMargin=40, rightMargin=40)

        styles = getSampleStyleSheet()

        title = styles["Title"]
        title.alignment = 1

        center = styles["Heading3"]
        center.alignment = 1

        subtitle = styles["Heading2"]
        subtitle.alignment = 1

        elements = []

        elements.append(Paragraph(f"<b>{school_name}</b>", title))
        elements.append(Paragraph(address, center))
        elements.append(Paragraph(f"PAN : {pan}", center))

        elements.append(Spacer(1, 20))

        elements.append(Paragraph("Balance Sheet", subtitle))
        elements.append(Paragraph(f"As on {as_of.strftime ('%d-%m-%Y')}", center))

        elements.append(Spacer(1, 20))

        # Convert to Paragraphs
        def convert(data):
            return [[Paragraph(str(c), styles["Normal"]) for c in row] for row in data]

        liab_table = convert(liab_table)
        asset_table = convert(asset_table)

        liab = LongTable(liab_table, colWidths=[200, 70])
        asset = LongTable(asset_table, colWidths=[200, 70])

        liab.setStyle(
            TableStyle(
                [
                    ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
                    ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#dce8d8")),
                    ("ALIGN", (1, 1), (1, -1), "RIGHT"),
                ]
            )
        )

        asset.setStyle(
            TableStyle(
                [
                    ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
                    ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#dce8d8")),
                    ("ALIGN", (1, 1), (1, -1), "RIGHT"),
                ]
            )
        )

        main_table = Table(
            [
                [
                    Paragraph("<b>LIABILITIES</b>", styles["Heading4"]),
                    Paragraph("<b>ASSETS</b>", styles["Heading4"]),
                ],
                [liab, asset],
            ],
            colWidths=[270, 270],
        )
        main_table.setStyle(TableStyle([("VALIGN", (0, 0), (-1, -1), "TOP")]))

        elements.append(main_table)

        doc.build(elements)

        buffer.seek(0)

        return send_bytes(
            buffer.getvalue(), f"Balance_Sheet_{as_of.strftime('%d_%m_%Y')}.pdf"
        )
