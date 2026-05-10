import dash
from dash import html, dcc, Input, Output, State
import dash_bootstrap_components as dbc
import pandas as pd
from datetime import date
import os
import io
import xlsxwriter
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
# MASTER DEPRECIATION RATES (BASE DEFINITIONS)
# =====================================================
DEPRECIATION_RATES = {
    "Land & Building": 0.00,
    "Furniture & Fixtures": 0.10,
    "Laboratory Equipment": 0.15,
    "Computers & IT Assets": 0.40,
    "Vehicles": 0.15,
    "Camera System": 0.15,
    "Sports Equipment": 0.15,
    "Electricity Equiment": 0.15,
    "Solar Powered Equipments": 0.4,
}


# =====================================================
# HELPERS
# =====================================================
def calculate_depreciation(amount, rate, txn_date, to_date):
    if amount <= 0 or rate == 0 or pd.isna(txn_date):
        return 0.0, amount

    days = (to_date - txn_date).days

    if days < 180:
        asset_value = amount * (1 - rate / 2)
    elif days < 365:
        asset_value = amount * (1 - rate)
    else:
        years = days // 365
        asset_value = amount * ((1 - rate) ** (years + 1))

    depreciation = amount - asset_value
    return round(depreciation, 2), round(asset_value, 2)


def load_or_build_depreciation_map(df, base_rates, mapper_path):
    """
    Loads existing depreciation mapper,
    auto-discovers NEW assets every run,
    appends them safely, and persists.
    """

    # ---------------- Load existing mapper ----------------
    if os.path.exists(mapper_path):
        mapper_df = pd.read_csv(mapper_path)
        active_map = dict(zip(mapper_df["asset_name"], mapper_df["rate"]))
        existing_assets = set(active_map.keys())
    else:
        active_map = {}
        existing_assets = set()
        mapper_df = pd.DataFrame(columns=["asset_name", "rate", "base_asset"])

    new_rows = []

    # ---------------- Discover new assets ----------------
    for li in df["LINE_ITEM"].dropna().unique():
        if li in existing_assets:
            continue

        li_lower = li.lower()

        for base_asset, rate in base_rates.items():
            if base_asset.lower() in li_lower:
                active_map[li] = rate
                new_rows.append(
                    {"asset_name": li, "rate": rate, "base_asset": base_asset}
                )
                break

    # ---------------- Persist only new discoveries ----------------
    if new_rows:
        os.makedirs(os.path.dirname(mapper_path), exist_ok=True)
        mapper_df = pd.concat([mapper_df, pd.DataFrame(new_rows)], ignore_index=True)
        mapper_df.to_csv(mapper_path, index=False)

    return active_map


# =====================================================
# APP INIT
# =====================================================
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])
app.title = "Fixed Asset Schedule"


# =====================================================
# LAYOUT (UNCHANGED)
def get_layout1():
    return dbc.Container(
        [
            html.H3("Fixed Asset Schedule", className="text-center my-4 fw-bold"),
            dbc.Row(
                [
                    dbc.Col(
                        dcc.DatePickerSingle(
                            id="fa-from-date",
                            display_format="DD-MM-YYYY",
                            placeholder="From Date",
                        ),
                        md=3,
                    ),
                    dbc.Col(
                        dcc.DatePickerSingle(
                            id="fa-to-date",
                            display_format="DD-MM-YYYY",
                            date=date.today(),
                        ),
                        md=3,
                    ),
                    dbc.Col(
                        dbc.Button(
                            "Generate",
                            id="fa-generate",
                            color="primary",
                            className="mt-1 me-2",
                        ),
                        width="auto",  # 👈 change here
                    ),
                    dbc.Col(
    [
        dbc.Button(
            "⬇ Download Excel",
            id="fa-download-btn",
            color="success",
            className="mt-1 me-2",
            style={"display": "none"},
        ),

        dbc.Button(
            "⬇ Download PDF",
            id="fa-download-pdf-btn",
            color="danger",
            className="mt-1",
            style={"display": "none"},
        ),
    ],
    width="auto",
)
                ],
                className="mb-4 justify-content-center align-items-end",
            ),
            dcc.Download(id="fa-download-file"),
            dcc.Download(id="fa-download-pdf-file"),
            dbc.Card(
                dbc.CardBody(html.Div(id="fa-output")),
                className="shadow-sm",
            ),
        ],
        fluid=True,
    )


# =====================================================
# CALLBACK (SINGLE SOURCE OF TRUTH)
# =====================================================
def register_callbacks(app):
    @app.callback(
        Output("fa-output", "children"),
        Input("fa-generate", "n_clicks"),
        State("fa-from-date", "date"),
        State("fa-to-date", "date"),
        State("session", "data"),
        prevent_initial_call=True,
    )
    def generate_fixed_asset_schedule(_, from_date, to_date, SessionData):

        BASE_PATH = f"/var/Data/{SessionData['username']}"
        MELT_DB_PATH = f"{BASE_PATH}/melt_db.csv"
        MAPPER_PATH = f"{BASE_PATH}/depreciation_mapper.csv"

        df = pd.read_csv(MELT_DB_PATH)

        df["transaction_date"] = pd.to_datetime(df["transaction_date"], errors="coerce")
        df["amount"] = pd.to_numeric(df["amount"], errors="coerce").fillna(0)

        fd = pd.to_datetime(from_date)
        td = pd.to_datetime(to_date)

        ACTIVE_MAP = load_or_build_depreciation_map(df, DEPRECIATION_RATES, MAPPER_PATH)

        asset_df = df[
            (df["GROUP"] == "Fixed Assets") & (df["LINE_ITEM"].isin(ACTIVE_MAP))
        ].copy()

        rows = []

        for asset, rate in ACTIVE_MAP.items():

            a = asset_df[asset_df["LINE_ITEM"] == asset]
            if a.empty:
                continue

            opening = a[a["transaction_date"] < fd]["amount"].sum()

            eligible_for_dep = a[(a["transaction_date"] <= td) & (a["amount"] > 0)]

            add_lt_6 = 0.0
            add_ge_6 = 0.0
            sale = 0.0
            depreciation = 0.0

            # --------------------------------------------------
            # 1️⃣ SALES (ONLY DURING PERIOD)
            # --------------------------------------------------
            sale = a[
                (a["transaction_date"] >= fd)
                & (a["transaction_date"] <= td)
                & (a["amount"] < 0)
            ]["amount"].sum()

            # --------------------------------------------------
            # 2️⃣ ADDITIONS SPLIT (ONLY DURING PERIOD)
            # --------------------------------------------------
            add_lt_6 = 0.0
            add_ge_6 = 0.0

            period_additions = a[
                (a["transaction_date"] >= fd)
                & (a["transaction_date"] <= td)
                & (a["amount"] > 0)
            ]

            for _, r in period_additions.iterrows():
                days = (td - r["transaction_date"]).days
                if days < 180:
                    add_lt_6 += r["amount"]
                else:
                    add_ge_6 += r["amount"]

            additions = add_lt_6 + add_ge_6

            # --------------------------------------------------
            # 3️⃣ DEPRECIATION (ALL POSITIVE ASSETS UP TO TO-DATE)
            # --------------------------------------------------
            depreciation = 0.0

            eligible_for_dep = a[(a["transaction_date"] <= td) & (min(a["amount"]) > 0)]

            for _, r in eligible_for_dep.iterrows():
                dep, _ = calculate_depreciation(
                    r["amount"], rate, r["transaction_date"], td
                )
                depreciation += dep

            # --------------------------------------------------
            # 4️⃣ TOTALS & SAFETY GUARDS
            # --------------------------------------------------
            total = opening + additions + sale

            if total <= 0:
                depreciation = 0.0

            closing = total - depreciation

            # --------------------------------------------------
            # 5️⃣ FINAL ROW
            # --------------------------------------------------
            rows.append(
                {
                    "Asset": asset,
                    "Opening": opening,
                    "<6M Additions": add_lt_6,
                    "≥6M Additions": add_ge_6,
                    "Sale": sale,
                    "Total": total,
                    "Dep %": rate * 100,
                    "Depreciation": round(depreciation, 2),
                    "Closing": round(closing, 2),
                }
            )

        fa = pd.DataFrame(rows)

        if fa.empty:
            return dbc.Alert("No Fixed Assets found", color="warning")

        return dbc.Table(
            [
                html.Thead(
                    html.Tr(
                        [
                            html.Th("Asset"),
                            html.Th("Opening"),
                            html.Th("< 6M Additions"),
                            html.Th("≥ 6M Additions"),
                            html.Th("Sale"),
                            html.Th("Total"),
                            html.Th("Dep %"),
                            html.Th("Dep Amount"),
                            html.Th("Closing Balance"),
                        ]
                    )
                ),
                html.Tbody(
                    [
                        html.Tr(
                            [
                                html.Td(r.Asset),
                                html.Td(f"{r.Opening:,.2f}", className="text-end"),
                                html.Td(
                                    f"{r['<6M Additions']:,.2f}", className="text-end"
                                ),
                                html.Td(
                                    f"{r['≥6M Additions']:,.2f}", className="text-end"
                                ),
                                html.Td(
                                    f"{r.Sale:,.2f}", className="text-end text-warning"
                                ),
                                html.Td(
                                    f"{r.Total:,.2f}", className="text-end fw-bold"
                                ),
                                html.Td(f"{r['Dep %']:.0f}%"),
                                html.Td(
                                    f"{r.Depreciation:,.2f}",
                                    className="text-end text-danger",
                                ),
                                html.Td(
                                    f"{r.Closing:,.2f}", className="text-end fw-bold"
                                ),
                            ]
                        )
                        for _, r in fa.iterrows()
                    ]
                ),
            ],
            bordered=True,
            hover=True,
            responsive=True,
            className="mt-3",
        )

    # ADD THIS
    @app.callback(
        Output("fa-download-btn", "style"),
        Input("fa-output", "children"),
    )
    def show_fa_download(output):
        if output:
            return {"display": "inline-block"}
        return {"display": "none"}

    # ADD THIS
    @app.callback(
        Output("fa-download-file", "data"),
        Input("fa-download-btn", "n_clicks"),
        State("fa-from-date", "date"),
        State("fa-to-date", "date"),
        State("session", "data"),
        prevent_initial_call=True,
    )
    def download_fixed_asset_schedule(_, from_date, to_date, SessionData):

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

        if not from_date or not to_date:
            return dash.no_update

        BASE_PATH = f"/var/Data/{SessionData['username']}"
        MELT_DB_PATH = f"{BASE_PATH}/melt_db.csv"
        MAPPER_PATH = f"{BASE_PATH}/depreciation_mapper.csv"

        df = pd.read_csv(MELT_DB_PATH)
        df["transaction_date"] = pd.to_datetime(df["transaction_date"], errors="coerce")
        df["amount"] = pd.to_numeric(df["amount"], errors="coerce").fillna(0)

        fd = pd.to_datetime(from_date)
        td = pd.to_datetime(to_date)

        ACTIVE_MAP = load_or_build_depreciation_map(df, DEPRECIATION_RATES, MAPPER_PATH)

        asset_df = df[
            (df["GROUP"] == "Fixed Assets") & (df["LINE_ITEM"].isin(ACTIVE_MAP))
        ].copy()

        rows = []

        for asset, rate in ACTIVE_MAP.items():
            a = asset_df[asset_df["LINE_ITEM"] == asset]
            if a.empty:
                continue

            opening = a[a["transaction_date"] < fd]["amount"].sum()

            add_lt_6 = 0.0
            add_ge_6 = 0.0

            period_additions = a[
                (a["transaction_date"] >= fd)
                & (a["transaction_date"] <= td)
                & (a["amount"] > 0)
            ]

            for _, r in period_additions.iterrows():
                days = (td - r["transaction_date"]).days
                if days < 180:
                    add_lt_6 += r["amount"]
                else:
                    add_ge_6 += r["amount"]

            sale = a[
                (a["transaction_date"] >= fd)
                & (a["transaction_date"] <= td)
                & (a["amount"] < 0)
            ]["amount"].sum()

            depreciation = 0.0
            eligible = a[(a["transaction_date"] <= td) & (a["amount"] > 0)]

            for _, r in eligible.iterrows():
                dep, _ = calculate_depreciation(
                    r["amount"], rate, r["transaction_date"], td
                )
                depreciation += dep

            total = opening + add_lt_6 + add_ge_6 + sale
            if total <= 0:
                depreciation = 0.0

            closing = total - depreciation

            rows.append(
                {
                    "Asset": asset,
                    "Opening": opening,
                    "<6M Additions": add_lt_6,
                    "≥6M Additions": add_ge_6,
                    "Sale": sale,
                    "Total": total,
                    "Dep %": rate * 100,
                    "Depreciation": round(depreciation, 2),
                    "Closing": round(closing, 2),
                }
            )

        fa = pd.DataFrame(rows)

        output = io.BytesIO()
      
        workbook = xlsxwriter.Workbook(output)
        sheet = workbook.add_worksheet("Fixed Asset Schedule")

# ===== FORMATS =====
        title_fmt = workbook.add_format({"bold": True, "font_size": 14, "align": "center"})
        header_fmt = workbook.add_format({"bold": True, "border": 1, "align": "center"})
        text_fmt = workbook.add_format({"border": 1})
        money_fmt = workbook.add_format({"border": 1, "num_format": "#,##0.00"})

        row = 0

# ===== SCHOOL HEADER =====
        sheet.merge_range(row, 0, row, 8, school_name, title_fmt)
        row += 1

        sheet.merge_range(row, 0, row, 3, f"PAN : {pan}")
        sheet.merge_range(row, 4, row, 8, address)
        row += 2

# ===== TITLE =====
        sheet.merge_range(row, 0, row, 8, "FIXED ASSET SCHEDULE", header_fmt)
        row += 1

# ===== COLUMN HEADERS =====
        headers = [
    "Asset", "Opening", "<6M Additions", "≥6M Additions",
    "Sale", "Total", "Dep %", "Dep Amount", "Closing Balance"
]

        sheet.write_row(row, 0, headers, header_fmt)
        row += 1

# ===== DATA =====
        for _, r in fa.iterrows():
         sheet.write(row, 0, r["Asset"], text_fmt)
         sheet.write(row, 1, r["Opening"], money_fmt)
         sheet.write(row, 2, r["<6M Additions"],  money_fmt)
         sheet.write(row, 3, r["≥6M Additions"],  money_fmt)
         sheet.write(row, 4, r["Sale"], money_fmt)
         sheet.write(row, 5, r["Total"], money_fmt)
         sheet.write(row, 6, r["Dep %"])
         sheet.write(row, 7, r["Depreciation"], money_fmt)
         sheet.write(row, 8, r["Closing"], money_fmt)
         row += 1

# ===== COLUMN WIDTH =====
        sheet.set_column("A:A", 30)
        sheet.set_column("B:I", 16)

        workbook.close()
        output.seek(0)

        return dcc.send_bytes(
            output.read(),
            f"Fixed_Asset_Schedule_{td.date()}.xlsx",
        )

    @app.callback(
        Output("fa-from-date", "date"),
        Output("fa-to-date", "date"),
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
    Output("fa-download-pdf-btn", "style"),
    Input("fa-output", "children"),
)
    def show_fa_pdf_download(output):
     if output:
        return {"display": "inline-block"}
     return {"display": "none"}


    @app.callback(
    Output("fa-download-pdf-file", "data"),
    Input("fa-download-pdf-btn", "n_clicks"),
    State("fa-from-date", "date"),
    State("fa-to-date", "date"),
    State("session", "data"),
    prevent_initial_call=True,
)
    def download_fixed_asset_schedule_pdf(_, from_date, to_date, SessionData):

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

     BASE_PATH = f"/var/Data/{user}"
     MELT_DB_PATH = f"{BASE_PATH}/melt_db.csv"
     MAPPER_PATH = f"{BASE_PATH}/depreciation_mapper.csv"

     df = pd.read_csv(MELT_DB_PATH)

     df["transaction_date"] = pd.to_datetime(df["transaction_date"], errors="coerce")
     df["amount"] = pd.to_numeric(df["amount"], errors="coerce").fillna(0)

     fd = pd.to_datetime(from_date)
     td = pd.to_datetime(to_date)

     ACTIVE_MAP = load_or_build_depreciation_map(df, DEPRECIATION_RATES, MAPPER_PATH)

     asset_df = df[
        (df["GROUP"] == "Fixed Assets") & (df["LINE_ITEM"].isin(ACTIVE_MAP))
    ].copy()

     rows = []

     for asset, rate in ACTIVE_MAP.items():

        a = asset_df[asset_df["LINE_ITEM"] == asset]
        if a.empty:
            continue

        opening = a[a["transaction_date"] < fd]["amount"].sum()

        add_lt_6 = 0
        add_ge_6 = 0

        period_additions = a[
            (a["transaction_date"] >= fd)
            & (a["transaction_date"] <= td)
            & (a["amount"] > 0)
        ]

        for _, r in period_additions.iterrows():
            days = (td - r["transaction_date"]).days
            if days < 180:
                add_lt_6 += r["amount"]
            else:
                add_ge_6 += r["amount"]

        sale = a[
            (a["transaction_date"] >= fd)
            & (a["transaction_date"] <= td)
            & (a["amount"] < 0)
        ]["amount"].sum()

        depreciation = 0
        eligible = a[(a["transaction_date"] <= td) & (a["amount"] > 0)]

        for _, r in eligible.iterrows():
            dep, _ = calculate_depreciation(
                r["amount"], rate, r["transaction_date"], td
            )
            depreciation += dep

        total = opening + add_lt_6 + add_ge_6 + sale
        if total <= 0:
            depreciation = 0

        closing = total - depreciation

        rows.append([
            asset,
            f"{opening:,.2f}",
            f"{add_lt_6:,.2f}",
            f"{add_ge_6:,.2f}",
            f"{sale:,.2f}",
            f"{total:,.2f}",
            f"{rate*100:.0f}%",
            f"{depreciation:,.2f}",
            f"{closing:,.2f}",
        ])

     buffer = io.BytesIO()

     doc = SimpleDocTemplate(buffer, pagesize=A4)

     styles = getSampleStyleSheet()

     center = styles["Title"]
     center.alignment = 1

     elements = []

     elements.append(Paragraph(f"<b>{school_name}</b>", center))
     elements.append(Paragraph(address, styles["Normal"]))
     elements.append(Paragraph(f"PAN : {pan}", styles ["Normal"]))
     elements.append(Spacer(1,20))

     elements.append(Paragraph("<b>FIXED ASSET SCHEDULE</b>", center))
     elements.append(Spacer(1,20))

     headers = [
        "Asset",
        "Opening",
        "<6M Additions",
        "≥6M Additions",
        "Sale",
        "Total",
        "Dep %",
        "Dep Amount",
        "Closing Balance",
    ]

     table_data = [headers] + rows

     table = Table(table_data, hAlign="CENTER")

     table.setStyle(
        TableStyle([
            ("GRID",(0,0),(-1,-1),0.5,colors.grey),
            ("BACKGROUND",(0,0),(-1,0),colors.lightgrey),
            ("ALIGN",(1,1),(-1,-1),"RIGHT"),
            ("FONTNAME",(0,0),(-1,0),"Helvetica-Bold")
        ])
    )

     elements.append(table)

     doc.build(elements)

     buffer.seek(0)

     return dcc.send_bytes(
        buffer.read(),
        f"Fixed_Asset_Schedule_{td.date()}.pdf"
    )


