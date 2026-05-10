import dash
from dash import html, dcc, Input, Output, State
import dash_bootstrap_components as dbc
import pandas as pd
import os, time
import io
import xlsxwriter
from dash.exceptions import PreventUpdate
from datetime import datetime, date
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib import colors

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
# DATA LOADER (NO CACHING)
# =====================================================
def load_rs_data(SessionData):

    time.sleep(0.05)
    os.stat("/var/Data/" + str(SessionData["username"]) + "/melt_db.csv")

    df = pd.read_csv("/var/Data/" + str(SessionData["username"]) + "/melt_db.csv")

    df["transaction_date"] = pd.to_datetime(
        df["transaction_date"], format="mixed", dayfirst=True, errors="coerce"
    )

    df["amount"] = pd.to_numeric(abs(df["amount"]), errors="coerce").fillna(0)

    df = df[df["GROUP"] == "Reserve & Surplus"].copy()

    df["LINE_ITEM"] = (
        df.get("LINE_ITEM", "")
        .astype(str)
        .str.lower()
        .str.strip()  # remove leading/trailing spaces
        .str.replace(r"\s+", " ", regex=True)  # collapse double spaces
    )

    def classify_side(line_item, amount):
        line_item = str(line_item).lower()
        if amount == 0:
            return None
        if any(
            word in line_item.lower()
            for word in [
                "withdrawls",
                "withdrawl",
                "withdrawals",
                "drawings",
                "drawing",
                "draw",
            ]
        ):
            return "DEBIT"
        return "CREDIT"  # ← FIXED

    df["SIDE"] = df.apply(lambda r: classify_side(r["LINE_ITEM"], r["amount"]), axis=1)

    return df


# =====================================================
# LAYOUT
# =====================================================
def get_layout1():
    return dbc.Container(
        [
            dcc.Store(id="rs-store", storage_type="session"),
            dbc.Row(
                dbc.Col(
                    html.H2(
                        "Reserve & Surplus Account",
                        className="text-center fw-bold my-4",
                        style={"color": "#1B5E20"},
                    ),
                    width=12,
                )
            ),
            # ---------------- DATE SELECTION ----------------
            dbc.Row(
                [
                    dbc.Col(
                        [
                            html.Label(
                                "From Date", className="fw-semibold text-success"
                            ),
                            dcc.DatePickerSingle(
                                id="from-date7",
                                display_format="DD-MM-YYYY",
                                className="w-100",
                            ),
                        ],
                        md=3,
                    ),
                    dbc.Col(
                        [
                            html.Label("To Date", className="fw-semibold text-success"),
                            dcc.DatePickerSingle(
                                id="to-date7",
                                display_format="DD-MM-YYYY",
                                className="w-100",
                            ),
                        ],
                        md=3,
                    ),
                    dbc.Col(
                        [
                            html.Br(),
                            dbc.Button(
                                "Confirm & Generate R&S",
                                id="confirm-btn7",
                                color="primary",
                                className="mt-2",
                            ),
                        ],
                        md=3,
                    ),
                ],
                className="mb-4 justify-content-center",
            ),
            html.Hr(),
            dbc.Row(
                dbc.Col(
                    dbc.Card(
                        [
                            dbc.CardHeader(
                                dbc.Row(
    [
        dbc.Col(
            html.H5("Reserve & Surplus Account", className="mb-0 fw-semibold"),
            md=8,
        ),
        dbc.Col(
            [
                dbc.Button(
                    "Download R&S PDF",
                    id="download-rs-pdf-btn",
                    color="danger",
                    size="sm",
                    className="me-2",
                ),
                dbc.Button(
                    "Download R&S",
                    id="download-rs-btn",
                    color="success",
                    size="sm",
                ),
            ],
            md=4,
            className="text-end",
        ),
    ]
) ),
                            dbc.CardBody(
                                html.Div(id="rs-output", className="table-responsive")
                            ),
                        ],
                        className="shadow-sm border-0",
                    ),
                    width=12,
                )
            ),
            dcc.Download(id="download-rs-file"),
            dcc.Download(id="download-rs-pdf-file"),
        ],
        fluid=True,
        className="bg-light px-4",
    )


# =====================================================
# CALLBACKS
# =====================================================
def register_callbacks(app):

    @app.callback(
        Output("rs-output", "children"),
        Output("rs-store", "data"),
        Input("confirm-btn7", "n_clicks"),
        State("from-date7", "date"),
        State("to-date7", "date"),
        State("session", "data"),
        prevent_initial_call=True,
    )
    def generate_rs_statement(n_clicks, from_date, to_date, SessionData):

        if not n_clicks or not from_date or not to_date:
            raise PreventUpdate

        df = load_rs_data(SessionData)

        fd = pd.to_datetime(from_date)
        td = pd.to_datetime(to_date)

        # ==============================
        # 1️⃣ OPENING BALANCE
        # ==============================
        opening_df = df[df["transaction_date"] < fd]

        opening_debit = opening_df[opening_df["SIDE"] == "DEBIT"]["amount"].sum()
        opening_credit = opening_df[opening_df["SIDE"] == "CREDIT"]["amount"].sum()

        opening_balance = opening_credit - opening_debit

        # ==============================
        # 2️⃣ PERIOD MOVEMENT
        # ==============================
        period_df = df[
            (df["transaction_date"] >= fd) & (df["transaction_date"] <= td)
        ].copy()

        if period_df.empty and opening_balance == 0:
            return dbc.Alert("No data found.", color="warning"), None

        grouped = (
            period_df.dropna(subset=["SIDE"])
            .groupby(["SIDE", "LINE_ITEM"], as_index=False)
            .agg({"amount": "sum"})
            .sort_values(["SIDE", "LINE_ITEM"])
            .reset_index(drop=True)
        )

        debit_df = grouped[grouped["SIDE"] == "DEBIT"][["LINE_ITEM", "amount"]].copy()
        credit_df = grouped[grouped["SIDE"] == "CREDIT"][["LINE_ITEM", "amount"]].copy()

        debit_total = debit_df["amount"].sum()
        credit_total = credit_df["amount"].sum()

        # ==============================
        # 3️⃣ ADD OPENING BALANCE (b/f)
        # ==============================
        if opening_balance > 0:
            credit_df = pd.concat(
                [
                    pd.DataFrame(
                        [{"LINE_ITEM": "By Balance b/f", "amount": opening_balance}]
                    ),
                    credit_df,
                ],
                ignore_index=True,
            )
            credit_total += opening_balance

        elif opening_balance < 0:
            debit_df = pd.concat(
                [
                    pd.DataFrame(
                        [
                            {
                                "LINE_ITEM": "To Balance b/f",
                                "amount": abs(opening_balance),
                            }
                        ]
                    ),
                    debit_df,
                ],
                ignore_index=True,
            )
            debit_total += abs(opening_balance)

        # ==============================
        # 4️⃣ CLOSING BALANCE (c/d)
        # ==============================
        closing_balance = credit_total - debit_total

        if closing_balance > 0:
            debit_df = pd.concat(
                [
                    debit_df,
                    pd.DataFrame(
                        [{"LINE_ITEM": "To Balance c/d", "amount": closing_balance}]
                    ),
                ],
                ignore_index=True,
            )
            debit_total += closing_balance

        elif closing_balance < 0:
            credit_df = pd.concat(
                [
                    credit_df,
                    pd.DataFrame(
                        [
                            {
                                "LINE_ITEM": "By Balance c/d",
                                "amount": abs(closing_balance),
                            }
                        ]
                    ),
                ],
                ignore_index=True,
            )
            credit_total += abs(closing_balance)

        # =====================================================
        # REBUILD RESERVE & SURPLUS IN melt_db (AUTHORITATIVE)
        # =====================================================

        melt_path = "/var/Data/" + str(SessionData["username"]) + "/melt_db.csv"

        melt_df = pd.read_csv(melt_path)

        melt_df["transaction_date"] = pd.to_datetime(
            melt_df["transaction_date"], errors="coerce"
        )

        melt_df["amount"] = pd.to_numeric(melt_df["amount"], errors="coerce").fillna(0)

        # ---------------------------------------------
        # 🔴 DELETE ALL EXISTING RESERVE & SURPLUS ROWS
        # ---------------------------------------------
        melt_df = melt_df[melt_df["GROUP"] != "Reserve & Surplus"]

        # ---------------------------------------------
        # 🟢 INSERT ONLY FINAL CLOSING BALANCE ROW
        # ---------------------------------------------
        if closing_balance != 0:

            rs_row = {
                "entry_id": f"JV_RS_{td.strftime('%Y%m%d')}",
                "transaction_date": td.strftime("%Y-%m-%d"),
                "LINE_ITEM": "Reserve & Surplus",
                "amount": round(closing_balance, 2),
                "GROUP": "Reserve & Surplus",
                "FS_GROUP": "BS",
                "source": "Journal Book",
            }

            melt_df = pd.concat([melt_df, pd.DataFrame([rs_row])], ignore_index=True)

        melt_df.to_csv(melt_path, index=False)

        # ==============================
        # 5️⃣ ALIGN TABLE
        # ==============================
        max_len = max(len(debit_df), len(credit_df))
        debit_df = debit_df.reindex(range(max_len))
        credit_df = credit_df.reindex(range(max_len))

        rows = []

        for i in range(max_len):
            rows.append(
                html.Tr(
                    [
                        html.Td(
                            debit_df.iloc[i]["LINE_ITEM"]
                            if pd.notna(debit_df.iloc[i]["LINE_ITEM"])
                            else ""
                        ),
                        html.Td(
                            (
                                f'{debit_df.iloc[i]["amount"]:,.2f}'
                                if pd.notna(debit_df.iloc[i]["amount"])
                                else ""
                            ),
                            className="text-end",
                        ),
                        html.Td(
                            credit_df.iloc[i]["LINE_ITEM"]
                            if pd.notna(credit_df.iloc[i]["LINE_ITEM"])
                            else ""
                        ),
                        html.Td(
                            (
                                f'{credit_df.iloc[i]["amount"]:,.2f}'
                                if pd.notna(credit_df.iloc[i]["amount"])
                                else ""
                            ),
                            className="text-end",
                        ),
                    ]
                )
            )

        rows.append(
            html.Tr(
                [
                    html.Th("Total"),
                    html.Th(f"{debit_total:,.2f}", className="text-end"),
                    html.Th("Total"),
                    html.Th(f"{credit_total:,.2f}", className="text-end"),
                ],
                className="table-success fw-bold",
            )
        )

        table = dbc.Table(
            [
                html.Thead(
                    [
                        html.Tr(
                            [
                                html.Th("Debit", colSpan=2, className="text-center"),
                                html.Th("Credit", colSpan=2, className="text-center"),
                            ]
                        ),
                        html.Tr(
                            [
                                html.Th("Particulars"),
                                html.Th("Amount", className="text-end"),
                                html.Th("Particulars"),
                                html.Th("Amount", className="text-end"),
                            ]
                        ),
                    ]
                ),
                html.Tbody(rows),
            ],
            bordered=True,
            hover=True,
            className="align-middle",
        )

        return table, grouped.to_dict("records")

    @app.callback(
        Output("download-rs-file", "data"),
        Input("download-rs-btn", "n_clicks"),
        State("from-date7", "date"),
        State("to-date7", "date"),
        State("session", "data"),
        prevent_initial_call=True,
    )
    def download_rs_excel(n_clicks, from_date, to_date, SessionData):
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

        if not n_clicks or not from_date or not to_date:
            raise PreventUpdate

        df = load_rs_data(SessionData)

        fd = pd.to_datetime(from_date)
        td = pd.to_datetime(to_date)

        # ==============================
        # OPENING BALANCE
        # ==============================
        opening_df = df[df["transaction_date"] < fd]

        opening_debit = opening_df[opening_df["SIDE"] == "DEBIT"]["amount"].sum()
        opening_credit = opening_df[opening_df["SIDE"] == "CREDIT"]["amount"].sum()

        opening_balance = opening_credit - opening_debit

        # ==============================
        # PERIOD MOVEMENT
        # ==============================
        period_df = df[
            (df["transaction_date"] >= fd) & (df["transaction_date"] <= td)
        ].copy()

        grouped = (
            period_df.dropna(subset=["SIDE"])
            .groupby(["SIDE", "LINE_ITEM"], as_index=False)
            .agg({"amount": "sum"})
            .sort_values(["SIDE", "LINE_ITEM"])
            .reset_index(drop=True)
        )

        debit_df = grouped[grouped["SIDE"] == "DEBIT"][["LINE_ITEM", "amount"]].copy()
        credit_df = grouped[grouped["SIDE"] == "CREDIT"][["LINE_ITEM", "amount"]].copy()

        debit_total = debit_df["amount"].sum()
        credit_total = credit_df["amount"].sum()

        # ==============================
        # ADD OPENING (b/f)
        # ==============================
        if opening_balance > 0:
            credit_df = pd.concat(
                [
                    pd.DataFrame(
                        [{"LINE_ITEM": "By Balance b/f", "amount": opening_balance}]
                    ),
                    credit_df,
                ],
                ignore_index=True,
            )
            credit_total += opening_balance

        elif opening_balance < 0:
            debit_df = pd.concat(
                [
                    pd.DataFrame(
                        [
                            {
                                "LINE_ITEM": "To Balance b/f",
                                "amount": abs(opening_balance),
                            }
                        ]
                    ),
                    debit_df,
                ],
                ignore_index=True,
            )
            debit_total += abs(opening_balance)

        # ==============================
        # CLOSING (c/d)
        # ==============================
        closing_balance = credit_total - debit_total

        if closing_balance > 0:
            debit_df = pd.concat(
                [
                    debit_df,
                    pd.DataFrame(
                        [{"LINE_ITEM": "To Balance c/d", "amount": closing_balance}]
                    ),
                ],
                ignore_index=True,
            )
            debit_total += closing_balance

        elif closing_balance < 0:
            credit_df = pd.concat(
                [
                    credit_df,
                    pd.DataFrame(
                        [
                            {
                                "LINE_ITEM": "By Balance c/d",
                                "amount": abs(closing_balance),
                            }
                        ]
                    ),
                ],
                ignore_index=True,
            )
            credit_total += abs(closing_balance)

        max_len = max(len(debit_df), len(credit_df))

        # ==============================
        # EXCEL CREATION
        # ==============================
        output = io.BytesIO()
        workbook = xlsxwriter.Workbook(output, {"in_memory": True})
        worksheet = workbook.add_worksheet("Reserve & Surplus")

        worksheet.set_column("A:A", 35)
        worksheet.set_column("B:B", 18)
        worksheet.set_column("D:D", 35)
        worksheet.set_column("E:E", 18)

        bold = workbook.add_format({"bold": True, "align": "center"})
        header = workbook.add_format({"bold": True, "border": 1})
        cell = workbook.add_format({"border": 1})
        money = workbook.add_format({"border": 1, "num_format": "#,##0.00"})
        total_fmt = workbook.add_format(
            {"bold": True, "top": 1, "num_format": "#,##0.00"}
        )

        worksheet.merge_range("A1:E1", school_name, bold)

        worksheet.merge_range("A2:B2", f"PAN : {pan}")
        worksheet.merge_range("C2:E2", address)

        worksheet.merge_range("A3:E3", "RESERVE & SURPLUS ACCOUNT", bold)

        worksheet.merge_range(
    "A4:E4",
    f"For the period {fd.strftime('%d-%m-%Y')} to {td.strftime('%d-%m-%Y')}",
    bold,
)

        row = 6
        worksheet.merge_range(row, 0, row, 1, "Debit", header)
        worksheet.merge_range(row, 3, row, 4, "Credit", header)
        row += 1

        worksheet.write(row, 0, "Particulars", header)
        worksheet.write(row, 1, "Amount", header)
        worksheet.write(row, 3, "Particulars", header)
        worksheet.write(row, 4, "Amount", header)

        row += 1

        for i in range(max_len):

            d_item = debit_df.iloc[i]["LINE_ITEM"] if i < len(debit_df) else ""
            d_amt = debit_df.iloc[i]["amount"] if i < len(debit_df) else ""

            c_item = credit_df.iloc[i]["LINE_ITEM"] if i < len(credit_df) else ""
            c_amt = credit_df.iloc[i]["amount"] if i < len(credit_df) else ""

            worksheet.write(row, 0, d_item, cell)
            worksheet.write(row, 1, d_amt, money)

            worksheet.write(row, 3, c_item, cell)
            worksheet.write(row, 4, c_amt, money)

            row += 1

        worksheet.write(row, 0, "Total", header)
        worksheet.write(row, 1, debit_total, total_fmt)

        worksheet.write(row, 3, "Total", header)
        worksheet.write(row, 4, credit_total, total_fmt)

        workbook.close()
        output.seek(0)

        return dcc.send_bytes(
            output.read(),
            f"Reserve_Surplus_{fd.strftime('%d_%m_%Y')}_to_{td.strftime('%d_%m_%Y')}.xlsx",
        )

    @app.callback(
        Output("from-date7", "date"),
        Output("to-date7", "date"),
        Input("financial-year-dropdown", "value"),
    )
    def auto_set_rp_dates(selected_fy):

        if not selected_fy:
            raise dash.exceptions.PreventUpdate

        start_date, end_date = get_fy_date_range(selected_fy)

        return (
            start_date.strftime("%Y-%m-%d"),
            end_date.strftime("%Y-%m-%d"),
        )
    


    @app.callback(
    Output("download-rs-pdf-file", "data"),
    Input("download-rs-pdf-btn", "n_clicks"),
    State("from-date7", "date"),
    State("to-date7", "date"),
    State("session", "data"),
    prevent_initial_call=True,
)
    def download_rs_pdf(n_clicks, from_date, to_date, SessionData):

     if not n_clicks or not from_date or not to_date:
        raise PreventUpdate

     user = SessionData["username"]

     school_name = ""
     address = ""
     pan = ""

     try:
        df_school = pd.read_csv(f"/var/Data/{user}/school_info.csv")
        school_name = df_school.loc[0, "school_name"]
        address = df_school.loc[0, "address"]
        pan = df_school.loc[0, "pan_number"]
     except:
        pass

     df = load_rs_data(SessionData)
 
     fd = pd.to_datetime(from_date)
     td = pd.to_datetime(to_date)

     opening_df = df[df["transaction_date"] < fd]
 
     opening_debit = opening_df[opening_df["SIDE"] == "DEBIT"]["amount"].sum()
     opening_credit = opening_df[opening_df["SIDE"] == "CREDIT"]["amount"].sum()

     opening_balance = opening_credit - opening_debit
 
     period_df = df[
        (df["transaction_date"] >= fd) & (df["transaction_date"] <= td)
    ].copy()

     grouped = (
        period_df.dropna(subset=["SIDE"])
        .groupby(["SIDE", "LINE_ITEM"], as_index=False)
        .agg({"amount": "sum"})
    )

     debit_df = grouped[grouped["SIDE"] == "DEBIT"][["LINE_ITEM", "amount"]].copy()
     credit_df = grouped[grouped["SIDE"] == "CREDIT"][["LINE_ITEM", "amount"]].copy()

     rows = []

     max_len = max(len(debit_df), len(credit_df))

     for i in range(max_len):

        d_item = debit_df.iloc[i]["LINE_ITEM"] if i < len(debit_df) else ""
        d_amt = debit_df.iloc[i]["amount"] if i < len(debit_df) else ""

        c_item = credit_df.iloc[i]["LINE_ITEM"] if i < len(credit_df) else ""
        c_amt = credit_df.iloc[i]["amount"] if i < len(credit_df) else ""

        rows.append([
            d_item,
            f"{d_amt:,.2f}" if d_amt else "",
            c_item,
            f"{c_amt:,.2f}" if c_amt else "",
        ])

     buffer = io.BytesIO()

     doc = SimpleDocTemplate(buffer, pagesize=A4)

     styles = getSampleStyleSheet()

     title = styles["Title"]
     title.alignment = 1

     normal = styles["Normal"]
     normal.alignment = 1

     elements = []

     elements.append(Paragraph(f"<b>{school_name}</b>", title))
     elements.append(Paragraph(f"PAN : {pan}", normal))
     elements.append(Paragraph(address, normal))
     elements.append(Spacer(1, 20))

     elements.append(Paragraph("<b>RESERVE & SURPLUS  ACCOUNT</b>", title))
     elements.append(Spacer(1, 20))

     headers = ["Debit Particulars", "Amount", "Credit Particulars", "Amount"]

     table_data = [headers] + rows

     table = Table(table_data, hAlign="CENTER", colWidths=[200,100,200,100])

     table.setStyle(
        TableStyle([
            ("GRID",(0,0),(-1,-1),0.5,colors.grey),
            ("BACKGROUND",(0,0),(-1,0),colors.lightgrey),
            ("ALIGN",(1,1),(-1,-1),"RIGHT"),
            ("ALIGN",(3,1),(-1,-1),"RIGHT"),
            ("FONTNAME",(0,0),(-1,0),"Helvetica-Bold"),
        ])
    )

     elements.append(table)

     doc.build(elements)

     buffer.seek(0)

     return dcc.send_bytes(
        buffer.read(),
        f"Reserve_Surplus_{fd.strftime('%d_%m_%Y')}_to_{td.strftime('%d_%m_%Y')}.pdf",
    )
