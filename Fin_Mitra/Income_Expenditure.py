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
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer,LongTable
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


def generate_fixed_asset_schedule(from_date, to_date, BASE_PATH):

    MELT_DB_PATH = f"{BASE_PATH}/melt_db.csv"
    MAPPER_PATH = f"{BASE_PATH}/depreciation_mapper.csv"
    melt_path = MELT_DB_PATH

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

    dep_df = pd.DataFrame(rows)

    # --------------------------------------------------
    # LOAD MELT DB
    # --------------------------------------------------
    melt_df = pd.read_csv(melt_path)

    melt_df["transaction_date"] = pd.to_datetime(
        melt_df["transaction_date"], errors="coerce"
    )
    melt_df["amount"] = pd.to_numeric(melt_df["amount"], errors="coerce").fillna(0)

    # Normalize column name
    asset_col = "Asset" if "Asset" in dep_df.columns else "Assets"

    # --------------------------------------------------
    # 1️⃣ UPDATE FIXED ASSET CLOSING BALANCES
    # --------------------------------------------------
    for _, r in dep_df.iterrows():

        asset_name = r[asset_col]
        closing_val = round(r["Closing"], 2)

        asset_mask = (melt_df["LINE_ITEM"] == asset_name) & (
            melt_df["GROUP"] == "Fixed Assets"
        )

        asset_rows = melt_df.loc[asset_mask]

        # --------------------------------------------------
        # SKIP IF ACCOUNT IS CLOSED
        # Condition:
        # 1) Multiple entries exist
        # 2) Net amount < 0
        # --------------------------------------------------
        if len(asset_rows) > 1 and min(asset_rows["amount"]) < 0:
            continue  # account closed → DO NOT MODIFY

        # --------------------------------------------------
        # UPDATE ONLY IF ACTIVE
        # --------------------------------------------------
        if not asset_rows.empty:
            # pick ONE row to carry forward (last occurrence)
            idx = asset_rows.index[-1]
            melt_df.loc[idx, "amount"] = closing_val
            melt_df.loc[idx, "transaction_date"] = to_date + " 00:00:00"
            melt_df.loc[idx, "LINE_ITEM"] = asset_name + "__DEP"

    # --------------------------------------------------
    # 2️⃣ COMPUTE PERIOD DEPRECIATION
    # --------------------------------------------------
    try:
        period_dep = round(dep_df["Depreciation"].sum(), 2)
    except:
        period_dep = 0

    # --------------------------------------------------
    # 3️⃣ REMOVE EXISTING DEPRECIATION (IDEMPOTENCY)
    # --------------------------------------------------
    melt_df = melt_df[
        ~(
            (melt_df["LINE_ITEM"].str.lower() == "depreciation")
            & (melt_df["transaction_date"] == to_date)
            & (melt_df["source"].str.lower() == "journal book")
        )
    ]

    # --------------------------------------------------
    # 4️⃣ POST DEPRECIATION ENTRY
    # --------------------------------------------------
    td = pd.to_datetime(to_date)
    if period_dep > 0:
        dep_row = {
            "entry_id": f"JV_DEP_{td.strftime('%Y%m%d')}",
            "transaction_date": td.strftime("%Y-%m-%d"),
            "LINE_ITEM": "Depreciation",
            "amount": period_dep,
            "GROUP": "Indirect Expenses",
            "FS_GROUP": "I&E",
            "source": "Journal Book",
        }

        melt_df = pd.concat([melt_df, pd.DataFrame([dep_row])], ignore_index=True)

    # --------------------------------------------------
    # 6️⃣ CLEANUP FIXED ASSET DUPLICATES USING __DEP TAG
    # --------------------------------------------------

    def clean_asset_group(g):
        # identify rewritten row
        dep_rows = g[g["LINE_ITEM"].str.endswith("__DEP", na=False)]

        if dep_rows.empty:
            return g  # nothing rewritten → leave untouched

        # keep:
        # 1) rewritten balance row
        # 2) all negative rows (sales)
        keep = pd.concat([dep_rows, g[g["amount"] < 0]])

        # restore original LINE_ITEM name
        keep["LINE_ITEM"] = keep["LINE_ITEM"].str.replace("__DEP", "", regex=False)

        return keep

    melt_df = (
        melt_df.assign(
            _base_li=melt_df["LINE_ITEM"].str.replace("__DEP", "", regex=False)
        )
        .groupby(["GROUP", "_base_li"], group_keys=False)
        .apply(clean_asset_group)
        .drop(columns="_base_li")
        .reset_index(drop=True)
    )

    # --------------------------------------------------
    # 5️⃣ SAVE
    # --------------------------------------------------
    melt_df.to_csv(melt_path, index=False)

    return ""


# =====================================================
# DATA LOADER (NO CACHING)
# =====================================================
def load_ie_data(SessionData):

    time.sleep(0.05)
    os.stat("/var/Data/" + str(SessionData["username"]) + "/melt_db.csv")

    df = pd.read_csv("/var/Data/" + str(SessionData["username"]) + "/melt_db.csv")

    df["transaction_date"] = pd.to_datetime(
        df["transaction_date"], format="mixed", dayfirst=True, errors="coerce"
    )

    df["amount"] = pd.to_numeric(df["amount"], errors="coerce").fillna(0)

    df = df[df["FS_GROUP"] == "I&E"].copy()

    df["source"] = df.get("source", "").astype(str).str.lower()

    def classify_side(group, amount):
        group = str(group).lower()
        if amount == 0:
            return None
        if "income" in group:
            return "CREDIT"
        return "DEBIT"  # ← FIXED

    df["SIDE"] = df.apply(lambda r: classify_side(r["GROUP"], r["amount"]), axis=1)

    return df


# =====================================================
# LAYOUT
# =====================================================
def get_layout1():
    return dbc.Container(
        [
            dcc.Store(id="ie-store", storage_type="session"),
            dbc.Row(
                dbc.Col(
                    html.H3(
                        "Income & Expenditure Account",
                        className="text-center fw-bold my-4",
                    ),
                    width=12,
                )
            ),
            # ---------------- DATE SELECTION ----------------
            dbc.Row(
                [
                    dbc.Col(
                        [
                            html.Label("From Date", className="fw-semibold"),
                            dcc.DatePickerSingle(
                                id="from-date1",
                                display_format="DD-MM-YYYY",
                                className="w-100",
                            ),
                        ],
                        md=3,
                    ),
                    dbc.Col(
                        [
                            html.Label("To Date", className="fw-semibold"),
                            dcc.DatePickerSingle(
                                id="to-date1",
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
                                "Confirm & Generate I&E",
                                id="confirm-btn1",
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
            dcc.Download(id="download-ie-file"),
            dcc.Download(id="download-ie-pdf-file"),
            dbc.Row(
                dbc.Col(
                    dbc.Card(
                        dbc.CardBody(
                            html.Div(id="ie-output", className="table-responsive")
                        ),
                        className="shadow-sm border-0",
                    ),
                    width=12,
                )
            ),
        ],
        fluid=True,
        className="bg-light px-4",
    )


# =====================================================
# CALLBACKS
# =====================================================
def register_callbacks(app):

    @app.callback(
        Output("ie-store", "data"),
        Input("confirm-btn1", "n_clicks"),
        State("from-date1", "date"),
        State("to-date1", "date"),
        State("session", "data"),
        prevent_initial_call=True,
    )
    def generate_ie(_, from_date, to_date, SessionData):

        # -------------------------------------------------
        # 1️⃣ LOAD IE DATA (initial)
        # -------------------------------------------------
        df = load_ie_data(SessionData)

        if df.empty:
            return dbc.Alert("No data available", color="warning")

        if not from_date or not to_date:
            raise PreventUpdate
        fd = pd.to_datetime(from_date, errors="coerce")
        td = pd.to_datetime(to_date, errors="coerce")

        if pd.isna(fd) or pd.isna(td):
            raise PreventUpdate

        #################
        BASE_PATH = "/var/Data/" + str(SessionData["username"])

        generate_fixed_asset_schedule(from_date, to_date, BASE_PATH)
        ##################

        # -------------------------------------------------
        # 3️⃣ RELOAD IE DATA (NOW includes Depreciation)
        # -------------------------------------------------
        df = load_ie_data(SessionData)

        period = df[
            (df["transaction_date"] >= fd) & (df["transaction_date"] <= td)
        ].copy()

        if period.empty:
            return dbc.Alert("No transactions in selected period", color="info")

        # -------------------------------------------------
        # 4️⃣ GROUP DATA (UNCHANGED)
        # -------------------------------------------------
        income_df = (
            period[period["SIDE"] == "CREDIT"]
            .groupby("LINE_ITEM", as_index=False)["amount"]
            .sum()
        )

        exp_df = (
            period[period["SIDE"] == "DEBIT"]
            .groupby("LINE_ITEM", as_index=False)["amount"]
            .sum()
        )

        total_income = income_df["amount"].sum()
        total_exp = exp_df["amount"].sum()
        surplus = round(total_income - total_exp, 2)

        # -------------------------------------------------
        # 5️⃣ AUTO-POST RESERVE & SURPLUS (NEW – ADDED)
        # -------------------------------------------------
        melt_path = "/var/Data/" + str(SessionData["username"]) + "/melt_db.csv"

        if surplus != 0:

            melt_df = pd.read_csv(melt_path)
            melt_df["transaction_date"] = pd.to_datetime(
                melt_df["transaction_date"], errors="coerce"
            )
            melt_df["amount"] = pd.to_numeric(
                melt_df["amount"], errors="coerce"
            ).fillna(0)

            melt_df = melt_df[
                ~(
                    (
                        melt_df["LINE_ITEM"].astype(str).str.lower()
                        == "reserve & surplus"
                    )
                    & (melt_df["transaction_date"] == td)
                    & (melt_df["source"].astype(str).str.lower() == "journal book")
                )
            ]

            rs_row = {
                "entry_id": f"JV_{td.strftime('%Y%m%d')}",
                "transaction_date": td.strftime("%Y-%m-%d"),  # ← FIX
                "LINE_ITEM": "Reserve & Surplus",
                "amount": round(surplus, 2),
                "GROUP": "Reserve & Surplus",
                "FS_GROUP": "BS",
                "source": "Journal Book",
            }

            melt_df = pd.concat([melt_df, pd.DataFrame([rs_row])], ignore_index=True)
            melt_df.to_csv(melt_path, index=False)

        # -------------------------------------------------
        # 6️⃣ BUILD IE TABLE (UNCHANGED)
        # -------------------------------------------------
        rows = []
        max_len = max(len(exp_df), len(income_df))

        for i in range(max_len):
            e = exp_df.iloc[i] if i < len(exp_df) else None
            i_ = income_df.iloc[i] if i < len(income_df) else None

            rows.append(
                html.Tr(
                    [
                        html.Td(f"To {e.LINE_ITEM}" if e is not None else ""),
                        html.Td(f"{e.amount:,.2f}" if e is not None else ""),
                        html.Td(f"By {i_.LINE_ITEM}" if i_ is not None else ""),
                        html.Td(f"{i_.amount:,.2f}" if i_ is not None else ""),
                    ]
                )
            )

        if surplus > 0:
            rows.append(
                html.Tr(
                    [
                        html.Td("To Excess of Income over Expenditure"),
                        html.Td(f"{surplus:,.2f}"),
                        html.Td(""),
                        html.Td(""),
                    ]
                )
            )
            total_exp += surplus
        elif surplus < 0:
            rows.append(
                html.Tr(
                    [
                        html.Td(""),
                        html.Td(""),
                        html.Td("By Excess of Expenditure over Income"),
                        html.Td(f"{abs(surplus):,.2f}"),
                    ]
                )
            )
            total_income += abs(surplus)

        rows.append(
            html.Tr(
                [
                    html.Th("Total"),
                    html.Th(f"{total_exp:,.2f}"),
                    html.Th("Total"),
                    html.Th(f"{total_income:,.2f}"),
                ]
            )
        )

        table = dbc.Table(
            [
                html.Thead(
                    [
                        html.Tr(
                            [
                                html.Th(
                                    "EXPENDITURE", colSpan=2, className="text-center"
                                ),
                                html.Th("INCOME", colSpan=2, className="text-center"),
                            ]
                        ),
                        html.Tr(
                            [
                                html.Th("Particulars"),
                                html.Th("Amount"),
                                html.Th("Particulars"),
                                html.Th("Amount"),
                            ]
                        ),
                    ]
                ),
                html.Tbody(rows),
            ],
            bordered=True,
            className="mt-2",
        )

        return html.Div(
            [
                # 🔽 HEADING + DOWNLOAD (SAME AS R&P STYLE)
                dbc.Row(
                    [
                        dbc.Col(html.H5("Income & Expenditure Account"), md=8),
                        dbc.Col(
    [
        dbc.Button(
            "Download I&E Excel",
            id="download-ie-btn",
            color="success",
            className="me-2",
        ),
        dbc.Button(
            "Download I&E PDF",
            id="download-ie-pdf-btn",
            color="danger",
        ),
    ],
    md=4,
),
                    ],
                    className="align-items-center mb-2",
                ),
                table,
            ]
        )

    @app.callback(
        Output("download-ie-file", "data"),
        Input("download-ie-btn","n_clicks"),
        State("from-date1", "date"),
        State("to-date1", "date"),
        State("session", "data"),
        prevent_initial_call=True,
    )
    def download_ie(ts, from_date, to_date, SessionData):
        if not ts:
          raise PreventUpdate
   
        school_name = ""
        address = ""
        pan = ""

        try:

         user = SessionData["username"]

         df_school = pd.read_csv(
        f"/var/Data/{user}/school_info.csv"
    )

         school_name = df_school.loc[0, "school_name"]
         address = df_school.loc[0, "address"]
         pan = df_school.loc[0, "pan_number"]

        except:
          pass
        if not ts:
            return dash.no_update

        # -------------------------------------------------
        # LOAD DATA (same as UI)
        # -------------------------------------------------
        df = load_ie_data(SessionData)

        if df.empty:
            return dash.no_update
        if not from_date or not to_date:
            return dash.no_update
        fd = pd.to_datetime(from_date, errors="coerce")
        td = pd.to_datetime(to_date, errors="coerce")

        if pd.isna(fd) or pd.isna(td) or td < fd:
            return dash.no_update

        period = df[
            (df["transaction_date"] >= fd) & (df["transaction_date"] <= td)
        ].copy()

        if period.empty:
            return dash.no_update

        income_df = (
            period[period["SIDE"] == "CREDIT"]
            .groupby("LINE_ITEM", as_index=False)["amount"]
            .sum()
        )

        exp_df = (
            period[period["SIDE"] == "DEBIT"]
            .groupby("LINE_ITEM", as_index=False)["amount"]
            .sum()
        )

        total_income = income_df["amount"].sum()
        total_exp = exp_df["amount"].sum()
        surplus = round(total_income - total_exp, 2)

        # -------------------------------------------------
        # BUILD ROWS (UI SAME ORDER)
        # -------------------------------------------------
        rows = []
        max_len = max(len(exp_df), len(income_df))

        for i in range(max_len):
            e = exp_df.iloc[i] if i < len(exp_df) else None
            inc = income_df.iloc[i] if i < len(income_df) else None

            rows.append(
                [
                    f"To {e.LINE_ITEM}" if e is not None else "",
                    e.amount if e is not None else "",
                    f"By {inc.LINE_ITEM}" if inc is not None else "",
                    inc.amount if inc is not None else "",
                ]
            )

        if surplus > 0:
            rows.append(["To Excess of Income over Expenditure", surplus, "", ""])
            total_exp += surplus
        elif surplus < 0:
            rows.append(["", "", "By Excess of Expenditure over Income", abs(surplus)])
            total_income += abs(surplus)

        rows.append(["Total", total_exp, "Total", total_income])

        # -------------------------------------------------
        # CREATE EXCEL
        # -------------------------------------------------
        output = io.BytesIO()
        workbook = xlsxwriter.Workbook(output, {"in_memory": True})
        worksheet = workbook.add_worksheet("Income & Expenditure")
        # SCHOOL HEADER
        title = workbook.add_format({"bold": True, "align": "center", "font_size": 14})
        worksheet.merge_range("A1:D1", school_name, title)
       

        worksheet.merge_range("A2:B2", f"PAN : {pan}")
        worksheet.merge_range("C2:D2", address)

        header = workbook.add_format({"bold": True, "align": "center", "border": 1})
        cell = workbook.add_format({"border": 1})
        money = workbook.add_format({"border": 1, "num_format": "#,##0.00"})

        # Main headers
        worksheet.merge_range("A3:B3", "EXPENDITURE", header)
        worksheet.merge_range("C3:D3", "INCOME", header)
        # Sub headers
        worksheet.write_row(
    "A4", ["Particulars", "Amount", "Particulars", "Amount"], header
)
    

        # Data
        row_no = 4
        for r in rows:
            worksheet.write(row_no, 0, r[0], cell)
            worksheet.write(
                row_no, 1, r[1], money if isinstance(r[1], (int, float)) else cell
            )
            worksheet.write(row_no, 2, r[2], cell)
            worksheet.write(
                row_no, 3, r[3], money if isinstance(r[3], (int, float)) else cell
            )
            row_no += 1

        worksheet.set_column("A:D", 30)

        workbook.close()
        output.seek(0)

        return dcc.send_bytes(
            output.read(),
            f"Income_Expenditure_{fd.strftime('%d-%m-%Y')}_to_{td.strftime('%d-%m-%Y')}.xlsx",
        )

    @app.callback(
        Output("ie-output", "children"),
        Input("ie-store", "data"),
    )
    def show_ie(data):
        if not data:
            raise PreventUpdate
        return data

    @app.callback(
        Output("from-date1", "date"),
        Output("to-date1", "date"),
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
    Output("download-ie-pdf-file","data"),
    Input("download-ie-pdf-btn","n_clicks"),
    State("from-date1","date"),
    State("to-date1","date"),
    State("session","data"),
    prevent_initial_call=True
)
    def download_ie_pdf(n, from_date, to_date, SessionData):

     if not n:
        raise PreventUpdate

    # =========================
    # SCHOOL INFO
    # =========================

     school_name=""
     address=""
     pan=""

     try:

        user=SessionData["username"]

        df_school=pd.read_csv(f"/var/Data/{user}/school_info.csv")

        school_name=df_school.loc[0,"school_name"]
        address=df_school.loc[0,"address"]
        pan=df_school.loc[0,"pan_number"]

     except:
        pass


    # =========================
    # LOAD DATA
    # =========================

     df = load_ie_data(SessionData)

     fd = pd.to_datetime(from_date)
     td = pd.to_datetime(to_date)

     period = df[(df["transaction_date"]>=fd) & (df["transaction_date"]<=td)]

     income_df = period[period["SIDE"]=="CREDIT"].groupby("LINE_ITEM")["amount"].sum()
     exp_df = period[period["SIDE"]=="DEBIT"].groupby("LINE_ITEM")["amount"].sum()

     rows=[]
     max_len=max(len(exp_df),len(income_df))

     exp_list=list(exp_df.items())
     inc_list=list(income_df.items())


     for i in range(max_len):

        e=exp_list[i] if i<len(exp_list) else ("","")
        inc=inc_list[i] if i<len(inc_list) else ("","")

        rows.append([
            f"To {e[0]}" if e[0] else "",
            f"{e[1]:,.2f}" if e[1] else "",
            f"By {inc[0]}" if inc[0] else "",
            f"{inc[1]:,.2f}" if inc[1] else ""
        ])


     # =========================
     # SURPLUS & TOTAL
     # =========================

     total_income = income_df.sum()
     total_exp = exp_df.sum()

     surplus = round(total_income - total_exp,2)

     if surplus > 0:
        rows.append([
            "To Excess of Income over Expenditure",
            f"{surplus:,.2f}",
            "",
            ""
        ])
        total_exp += surplus

     elif surplus < 0:
        rows.append([
            "",
            "",
            "By Excess of Expenditure over Income",
            f"{abs(surplus):,.2f}"
        ])
        total_income += abs(surplus)

     rows.append([
        "Total",
        f"{total_exp:,.2f}",
        "Total",
        f"{total_income:,.2f}"
     ])


    # =========================
    # BUILD PDF
    # =========================

     buffer=io.BytesIO()

     doc=SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=40,
        leftMargin=40,
        topMargin=40,
        bottomMargin=40
    )

     styles=getSampleStyleSheet()

     elements=[]


    # CENTER STYLES
     title=styles["Title"]
     title.alignment=1

     center=styles["Heading3"]
     center.alignment=1

     subtitle=styles["Heading2"]
     subtitle.alignment=1


    # =========================
    # HEADER
    # =========================

     elements.append(Paragraph(f"<b>{school_name}</b>",title))
     elements.append(Paragraph(address,center))
     elements.append(Paragraph(f"PAN : {pan}",center))

     elements.append(Spacer(1,20))

     elements.append(Paragraph("Income & Expenditure Account",subtitle))

     elements.append(Spacer(1,25))


    # =========================
    # TABLE
    # =========================

     table_data = [
    ["EXPENDITURE", "", "INCOME", ""],
    ["Particulars", "Amount", "Particulars", "Amount"]
]

     for r in rows:
      table_data.append([
        Paragraph(r[0], styles["Normal"]),
        Paragraph(r[1], styles["Normal"]),
        Paragraph(r[2], styles["Normal"]),
        Paragraph(r[3], styles["Normal"])
    ])


     table = LongTable(
     table_data,
     colWidths=[200, 60, 200, 60],
     repeatRows=2
)

     table.setStyle(TableStyle([

    ("SPAN",(0,0),(1,0)),
    ("SPAN",(2,0),(3,0)),

    ("BACKGROUND",(0,0),(-1,1),colors.HexColor("#dce8d8")),
    ("TEXTCOLOR",(0,0),(-1,1),colors.HexColor("#2e5e2e")),

    ("GRID",(0,0),(-1,-1),0.5,colors.grey),

    ("ALIGN",(1,2),(1,-1),"RIGHT"),
    ("ALIGN",(3,2),(3,-1),"RIGHT"),

    ("VALIGN",(0,0),(-1,-1),"MIDDLE"),

    ("FONTNAME",(0,0),(-1,1),"Helvetica-Bold"),
    ("FONTSIZE",(0,0),(-1,-1),10),

]))


     elements.append(table)

     doc.build(elements)

     buffer.seek(0)


     return dcc.send_bytes(
        buffer.read(),
        "Income_Expenditure_Report.pdf"
    )