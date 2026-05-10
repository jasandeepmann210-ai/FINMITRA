import dash
from dash import html, dcc, Input, Output, State
import dash_bootstrap_components as dbc
import pandas as pd
from datetime import date
import re
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
# DATE NORMALIZATION
# =====================================================
def normalize_txn_date(val):
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


# =====================================================
# CASH / BANK ENGINES (UNCHANGED)
# =====================================================
def cash_metrics(from_dt, to_dt, SessionData):

    path = f"/var/Data/{SessionData['username']}/master_ledger.csv"
    df = pd.read_csv(path)

    df["transaction_date"] = df["transaction_date"].apply(normalize_txn_date)
    df["cash_amount"] = pd.to_numeric(df["cash_amount"], errors="coerce").fillna(0)

    before = df[df["transaction_date"] < from_dt]
    period = df[(df["transaction_date"] >= from_dt) & (df["transaction_date"] <= to_dt)]

    ob = (
        before[before["form_name"].isin(["FEES RECEIPT", "OTHER RECEIPT"])]["cash_amount"].sum()
        - before[before["form_name"].isin(["EXPENSES", "SALARY PAYMENT", "OTHER PAYMENT"])]["cash_amount"].sum()
    )

    dr = period[period["form_name"].isin(["FEES RECEIPT", "OTHER RECEIPT"])]["cash_amount"].sum()
    cr = period[period["form_name"].isin(["EXPENSES", "SALARY PAYMENT", "OTHER PAYMENT"])]["cash_amount"].sum()

    cb = ob + dr - cr
    return ob, dr, cr, cb


def bank_metrics(from_dt, to_dt, bank_col, SessionData):

    path = f"/var/Data/{SessionData['username']}/master_ledger.csv"
    df = pd.read_csv(path)

    df["transaction_date"] = df["transaction_date"].apply(normalize_txn_date)
    col = f"{bank_col}_amount"

    if col not in df.columns:
        return 0, 0, 0, 0

    df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0)

    before = df[df["transaction_date"] < from_dt]
    period = df[(df["transaction_date"] >= from_dt) & (df["transaction_date"] <= to_dt)]

    ob = (
        before[before["form_name"].isin(["FEES RECEIPT", "OTHER RECEIPT"])][col].sum()
        - before[before["form_name"].isin(
            ["EXPENSES", "SALARY PAYMENT", "OTHER PAYMENT", "DECLARE ASSETS"]
        )][col].sum()
    )

    dr = period[period["form_name"].isin(["FEES RECEIPT", "OTHER RECEIPT"])][col].sum()
    cr = period[period["form_name"].isin(
        ["EXPENSES", "SALARY PAYMENT", "OTHER PAYMENT", "DECLARE ASSETS"]
    )][col].sum()

    cb = ob + dr - cr
    return ob, dr, cr, cb


# =====================================================
# ACCOUNT GROUPS
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

DISPLAY_ORDER = [
    "Reserve & Surplus",
    "Current Liabilities",
    "Sundry creditors",
    "Non-current liabilities Secured loans",
    "Non-current liabilities Unsecured loans",
    "Provisions (Bad Debts, Warranty)",
    "Deferred Tax",
    "Unearned Revenue",
    "Fixed Assets",
    "Investments",
    "Loans and Advances",
    "Cash-in-Hand",
    "Bank Accounts",
    "Current Assets",
    "Sundry debtors",
    "Inventories",
]

# =====================================================
# DASH APP
# =====================================================
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])


def get_layout1():
    return dbc.Container(
        [
            html.H3("TRIAL BALANCE", className="text-center my-4"),

            # 🔹 ROW 1 → DATE + FILTER (CENTERED)
            dbc.Row(
                [
                    dbc.Col(
                        dcc.DatePickerSingle(
                            id="tb-from-date",
                            date=date.today().replace(day=1),
                            display_format="DD-MM-YYYY",
                        ),
                        md=3,
                    ),

                    dbc.Col(
                        dcc.DatePickerSingle(
                            id="tb-to-date",
                            date=date.today(),
                            display_format="DD-MM-YYYY",
                        ),
                        md=3,
                    ),

                    dbc.Col(
                        dcc.Dropdown(
                            id="tb-group-filter",
                            placeholder="Filter by Group (optional)",
                            clearable=True,
                        ),
                        md=4,
                    ),
                ],
                className="mb-3 justify-content-center",
            ),

            # 🔹 ROW 2 → RUN + DOWNLOAD (SIDE BY SIDE CENTER)
           dbc.Row(
    [
        dbc.Col(
            dbc.Button(
                "Run",
                id="tb-run-btn",
                color="primary",
            ),
            width="auto",
        ),

        dbc.Col(
            [
                dbc.Button(
                    "⬇ Download Excel",
                    id="tb-download-btn",
                    color="success",
                    className="me-2"
                ),
                dbc.Button(
                    "⬇ Download PDF",
                    id="tb-download-pdf-btn",
                    color="danger"
                ),

                dcc.Download(id="tb-download-file"),
                dcc.Download(id="tb-download-pdf-file"),
            ],
            width="auto",
        ),
    ],
    className="mb-4 justify-content-center",
),
            # 🔹 OUTPUT
            dbc.Row(
                dbc.Col(
                    html.Div(id="tb-output"),
                    md=12,
                )
            ),
        ],
        fluid=True,
    )




def build_trial_balance(from_dt, to_dt, selected_group, SessionData):

    path = f"/var/Data/{SessionData['username']}/melt_db.csv"
    df = pd.read_csv(path)

    df["transaction_date"] = df["transaction_date"].apply(normalize_txn_date)
    df["amount"] = pd.to_numeric(df["amount"], errors="coerce").fillna(0)

    df = df[df["FS_GROUP"] == "BS"].copy()
    df["GROUP"] = df["GROUP"].astype(str).str.strip()
    df = df.dropna(subset=["transaction_date", "LINE_ITEM"])

    if selected_group:
        df = df[df["GROUP"] == selected_group]

    GROUP_NATURE = {g.lower(): "ASSET" for g in ASSETS}
    GROUP_NATURE.update({g.lower(): "LIABILITY" for g in LIABILITIES})

    # OPENING
    opening = (
        df[df["transaction_date"] < from_dt]
        .groupby(["GROUP", "LINE_ITEM"], as_index=False)["amount"]
        .sum()
        .rename(columns={"amount": "OPENING"})
    )

    # MOVEMENT
    movement = (
        df[(df["transaction_date"] >= from_dt) & (df["transaction_date"] <= to_dt)]
        .groupby(["GROUP", "LINE_ITEM"], as_index=False)["amount"]
        .sum()
    )

    def split_dr_cr(row):
        amt = row["amount"]
        nature = GROUP_NATURE.get(row["GROUP"].lower())
        if nature == "ASSET":
            return pd.Series({"DR": max(amt, 0), "CR": abs(min(amt, 0))})
        return pd.Series({"DR": abs(min(amt, 0)), "CR": max(amt, 0)})

    movement[["DR", "CR"]] = movement.apply(split_dr_cr, axis=1)

    tb = opening.merge(
        movement[["GROUP", "LINE_ITEM", "DR", "CR"]],
        on=["GROUP", "LINE_ITEM"],
        how="outer",
    ).fillna(0)

    def closing(row):
        if GROUP_NATURE.get(row["GROUP"].lower()) == "ASSET":
            return row["OPENING"] + row["DR"] - row["CR"]
        return row["OPENING"] + row["CR"] - row["DR"]

    tb["CLOSING"] = tb.apply(closing, axis=1)

    # REMOVE CASH/BANK FROM melt
    tb = tb[~tb["GROUP"].isin(["Cash-in-Hand", "Bank Accounts"])]

    # ADD CASH
    ob, dr, cr, cb = cash_metrics(from_dt, to_dt, SessionData)
    tb = pd.concat([tb, pd.DataFrame([{
        "GROUP": "Cash-in-Hand",
        "LINE_ITEM": "Cash",
        "OPENING": ob,
        "DR": dr,
        "CR": cr,
        "CLOSING": cb,
    }])])

    # ADD BANKS

    bank_map= get_bank_name_map(SessionData)

    for i in range(1, 11):
        bank_code = f"BANK{i}"
        bank_col = f"bank{i}"    
        ob, dr, cr, cb = bank_metrics(from_dt, to_dt, bank_col, SessionData)
        if ob == 0 and dr == 0 and cr == 0 and cb == 0:
          continue
        bank_label = bank_map.get(bank_code, f"Bank-{i}")
        tb = pd.concat([tb, pd.DataFrame([{
    "GROUP": "Bank Accounts",
    "LINE_ITEM": bank_label,
    "OPENING": ob,
    "DR": dr,
    "CR": cr,
    "CLOSING": cb,
}])], ignore_index=True)

    # SPLIT OPEN/CLOSE
    def split(val, nature):
        if nature == "ASSET":
            return max(val, 0), abs(min(val, 0))
        return abs(min(val, 0)), max(val, 0)

    tb[["OPEN_DR", "OPEN_CR"]] = tb.apply(
        lambda r: split(r["OPENING"], GROUP_NATURE.get(r["GROUP"].lower())),
        axis=1, result_type="expand"
    )

    tb[["CLOSE_DR", "CLOSE_CR"]] = tb.apply(
        lambda r: split(r["CLOSING"], GROUP_NATURE.get(r["GROUP"].lower())),
        axis=1, result_type="expand"
    )

    return tb



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
# CALLBACK
# =====================================================
def register_callbacks(app):

    @app.callback(
        Output("tb-output", "children"),
        Output("tb-group-filter","options"),
        Input("tb-run-btn", "n_clicks"),
        State("tb-from-date", "date"),
        State("tb-to-date", "date"),
        State("tb-group-filter", "value"),
        State("session", "data"),
        prevent_initial_call=True,
    )
    def generate_tb(n_clicks, from_date, to_date, selected_group, SessionData):

        if not n_clicks or not from_date or not to_date:
            return [], []

        from_dt = pd.to_datetime(from_date)
        to_dt = pd.to_datetime(to_date)

        # -------------------------------------------------
        # LOAD melt_db
        # -------------------------------------------------
        path = f"/var/Data/{SessionData['username']}/melt_db.csv"
        df = pd.read_csv(path)

        df["transaction_date"] = df["transaction_date"].apply(normalize_txn_date)
        df["amount"] = pd.to_numeric(df["amount"], errors="coerce").fillna(0)

        df = df[df["FS_GROUP"] == "BS"].copy()
        df["GROUP"] = df["GROUP"].astype(str).str.strip()
        df = df.dropna(subset=["transaction_date", "LINE_ITEM"])

        # -------------------------------------------------
        # GROUP → NATURE MAP
        # -------------------------------------------------
        GROUP_NATURE = {g.lower(): "ASSET" for g in ASSETS}
        GROUP_NATURE.update({g.lower(): "LIABILITY" for g in LIABILITIES})

        # -------------------------------------------------
        # GROUP FILTER
        # -------------------------------------------------
        groups = sorted(df["GROUP"].dropna().unique())
        group_options = [{"label": g, "value": g} for g in groups]

        if selected_group:
            df = df[df["GROUP"] == selected_group]

        # -------------------------------------------------
        # OPENING
        # -------------------------------------------------
        opening = (
            df[df["transaction_date"] < from_dt]
            .groupby(["GROUP", "LINE_ITEM"], as_index=False)["amount"]
            .sum()
            .rename(columns={"amount": "OPENING"})
        )

        # -------------------------------------------------
        # MOVEMENTS
        # -------------------------------------------------
        movement = (
            df[(df["transaction_date"] >= from_dt) & (df["transaction_date"] <= to_dt)]
            .groupby(["GROUP", "LINE_ITEM"], as_index=False)["amount"]
            .sum()
        )

        def split_dr_cr(row):
            amt = row["amount"]
            nature = GROUP_NATURE.get(row["GROUP"].lower())
            if nature == "ASSET":
                return pd.Series({"DR": max(amt, 0), "CR": abs(min(amt, 0))})
            return pd.Series({"DR": abs(min(amt, 0)), "CR": max(amt, 0)})

        movement[["DR", "CR"]] = movement.apply(split_dr_cr, axis=1)

        # -------------------------------------------------
        # BUILD TB
        # -------------------------------------------------
        tb = opening.merge(
            movement[["GROUP", "LINE_ITEM", "DR", "CR"]],
            on=["GROUP", "LINE_ITEM"],
            how="outer",
        ).fillna(0)

        def closing_balance(row):
            if GROUP_NATURE.get(row["GROUP"].lower()) == "ASSET":
                return row["OPENING"] + row["DR"] - row["CR"]
            return row["OPENING"] + row["CR"] - row["DR"]

        tb["CLOSING"] = tb.apply(closing_balance, axis=1)

        # -------------------------------------------------
        # REMOVE CASH & BANKS FROM melt_db (GROUP-LEVEL, SAFE)
        # -------------------------------------------------
        tb = tb[~tb["GROUP"].isin(["Cash-in-Hand", "Bank Accounts"])]


        # -------------------------------------------------
        # ADD CASH
        # -------------------------------------------------
        ob, dr, cr, cb = cash_metrics(from_dt, to_dt, SessionData)
        tb = pd.concat(
            [tb, pd.DataFrame([{
                "GROUP": "Cash-in-Hand",
                "LINE_ITEM": "Cash",
                "OPENING": ob,
                "DR": dr,
                "CR": cr,
                "CLOSING": cb,
            }])],
            ignore_index=True,
        )

        # -------------------------------------------------
        # ADD BANKS
        # -------------------------------------------------
        bank_map = get_bank_name_map(SessionData)

        for i in range(1, 11):

         bank_code = f"BANK{i}"
         bank_col = f"bank{i}"

         ob, dr, cr, cb = bank_metrics(from_dt, to_dt, bank_col, SessionData)

    # ❌ Skip zero banks
         if ob == 0 and dr == 0 and cr == 0 and cb == 0:
          continue

    # ✅ Get proper bank name
         bank_label = bank_map.get(bank_code, f"Bank-{i}")

         tb = pd.concat(
        [tb, pd.DataFrame([{
            "GROUP": "Bank Accounts",
            "LINE_ITEM": bank_label,  # 🔥 dynamic name
            "OPENING": ob,
            "DR": dr,
            "CR": cr,
            "CLOSING": cb,
        }])],
        ignore_index=True,
    )

        # -------------------------------------------------
        # SPLIT OPEN / CLOSE (EXCEL STYLE)
        # -------------------------------------------------
        def split_balance(val, nature):
            if nature == "ASSET":
                return max(val, 0), abs(min(val, 0))
            return abs(min(val, 0)), max(val, 0)

        tb[["OPEN_DR", "OPEN_CR"]] = tb.apply(
            lambda r: split_balance(r["OPENING"], GROUP_NATURE.get(r["GROUP"].lower())),
            axis=1, result_type="expand"
        )

        tb[["CLOSE_DR", "CLOSE_CR"]] = tb.apply(
            lambda r: split_balance(r["CLOSING"], GROUP_NATURE.get(r["GROUP"].lower())),
            axis=1, result_type="expand"
        )

        # -------------------------------------------------
        # RENDER
        # -------------------------------------------------
        out = []

        for grp in DISPLAY_ORDER:
            if grp not in tb["GROUP"].unique():
             continue
            gdf = tb[tb["GROUP"] == grp]
            nature = GROUP_NATURE.get(grp.lower())

            total = (
                gdf["CLOSE_DR"].sum()
                if nature == "ASSET"
                else gdf["CLOSE_CR"].sum()
            )

            out.append(
                dbc.Accordion(
                    [
                        dbc.AccordionItem(
                            title=f"{grp} — {total:,.2f}",
                            children=[
                                dbc.Table(
                                    [
                                        html.Thead(html.Tr([
                                            html.Th("Ledger"),
                                            html.Th("Opening Dr", className="text-end"),
                                            html.Th("Opening Cr", className="text-end"),
                                            html.Th("Debit", className="text-end"),
                                            html.Th("Credit", className="text-end"),
                                            html.Th("Closing Dr", className="text-end"),
                                            html.Th("Closing Cr", className="text-end"),
                                        ])),
                                        html.Tbody([
                                            html.Tr([
                                                html.Td(r.LINE_ITEM),
                                                html.Td(f"{r.OPEN_DR:,.2f}" if r.OPEN_DR else "", className="text-end"),
                                                html.Td(f"{r.OPEN_CR:,.2f}" if r.OPEN_CR else "", className="text-end"),
                                                html.Td(f"{r.DR:,.2f}" if r.DR else "", className="text-end"),
                                                html.Td(f"{r.CR:,.2f}" if r.CR else "", className="text-end"),
                                                html.Td(f"{r.CLOSE_DR:,.2f}" if r.CLOSE_DR else "", className="text-end"),
                                                html.Td(f"{r.CLOSE_CR:,.2f}" if r.CLOSE_CR else "", className="text-end"),
                                            ])
                                            for r in gdf.itertuples()
                                        ])
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

        # -------------------------------------------------
        # GRAND TOTALS (EXCEL / TALLY STYLE)
        # -------------------------------------------------
        grand_open_dr = tb["OPEN_DR"].sum()
        grand_open_cr = tb["OPEN_CR"].sum()
        grand_dr = tb["DR"].sum()
        grand_cr = tb["CR"].sum()
        grand_close_dr = tb["CLOSE_DR"].sum()
        grand_close_cr = tb["CLOSE_CR"].sum()
        
        out.append(html.Hr())
        
        out.append(
            dbc.Table(
                [
                    html.Thead(
                        html.Tr([
                            html.Th("GRAND TOTAL"),
                            html.Th("Opening Dr", className="text-end"),
                            html.Th("Opening Cr", className="text-end"),
                            html.Th("Debit", className="text-end"),
                            html.Th("Credit", className="text-end"),
                            html.Th("Closing Dr", className="text-end"),
                            html.Th("Closing Cr", className="text-end"),
                        ])
                    ),
                    html.Tbody(
                        [
                            html.Tr([
                                html.Th("ALL GROUPS"),
                                html.Td(f"{grand_open_dr:,.2f}" if grand_open_dr else "", className="text-end"),
                                html.Td(f"{grand_open_cr:,.2f}" if grand_open_cr else "", className="text-end"),
                                html.Td(f"{grand_dr:,.2f}" if grand_dr else "", className="text-end"),
                                html.Td(f"{grand_cr:,.2f}" if grand_cr else "", className="text-end"),
                                html.Td(f"{grand_close_dr:,.2f}" if grand_close_dr else "", className="text-end"),
                                html.Td(f"{grand_close_cr:,.2f}" if grand_close_cr else "", className="text-end"),
                            ])
                        ]
                    ),
                ],
                bordered=True,
                striped=True,
                hover=True,
                size="sm",
                className="mt-3",
            )
        )


        return out, group_options
    

    # ADD THIS
   
    @app.callback(
        Output("tb-download-file", "data"),
        Input("tb-download-btn", "n_clicks"),
        State("tb-from-date", "date"),
        State("tb-to-date", "date"),
        State("tb-group-filter", "value"),
        State("session", "data"),
        prevent_initial_call=True,
     )
    def download_trial_balance(n_clicks, from_date, to_date, selected_group, SessionData):
     

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
        return dash.no_update

     from_dt = pd.to_datetime(from_date)
     to_dt = pd.to_datetime(to_date)

    # 🔁 SAME DATA AS UI
     tb = build_trial_balance(from_dt, to_dt,  selected_group, SessionData)

     output = io.BytesIO()
     workbook = xlsxwriter.Workbook(output)
     sheet = workbook.add_worksheet("Trial Balance")

    # ========= FORMATS =========
     title_fmt = workbook.add_format({
        "bold": True, "font_size": 14, "align": "center"
     })
     header_fmt = workbook.add_format({
        "bold": True, "border": 1, "align": "center"
    })
     group_fmt = workbook.add_format({
        "bold": True, "border": 1
    })
     text_fmt = workbook.add_format({
        "border": 1
    })
     money_fmt = workbook.add_format({
        "border": 1, "num_format": "#,##0.00"
    })
     school_title = workbook.add_format({
    "bold": True,
    "font_size": 14,
    "align": "center"
})

     row = 0

# ===== SCHOOL HEADER =====
     sheet.merge_range(row, 0, row, 6, school_name, school_title)
     row += 1

     sheet.merge_range(row, 0, row, 2, f"PAN : {pan}")
     sheet.merge_range(row, 3, row, 6, address)
     row += 2
    # ========= TITLE =========
     sheet.merge_range(
        row, 0, row, 6,
        f"TRIAL BALANCE FROM {from_dt.strftime('%d-%m-%Y')} TO {to_dt.strftime('%d-%m-%Y')}",
        title_fmt
    )
     row += 2

    # ========= COLUMN HEADERS =========
     headers = [
        "Ledger",
        "Opening Dr", "Opening Cr",
        "Debit", "Credit",
        "Closing Dr", "Closing Cr",
    ]

     sheet.write_row(row, 0, headers, header_fmt)
     row += 1

    # ========= GROUP-WISE (UI LIKE) =========
     for grp in DISPLAY_ORDER:
        if grp not in tb["GROUP"].unique():
          continue
 
        gdf = tb[tb["GROUP"] == grp]

        # group title row
        sheet.merge_range(row, 0, row, 6, grp, group_fmt)
        row += 1

        for _, r in gdf.iterrows():
            sheet.write(row, 0, r["LINE_ITEM"], text_fmt)
            sheet.write(row, 1, r["OPEN_DR"] or "", money_fmt)
            sheet.write(row, 2, r["OPEN_CR"] or "", money_fmt)
            sheet.write(row, 3, r["DR"] or "", money_fmt)
            sheet.write(row, 4, r["CR"] or "", money_fmt)
            sheet.write(row, 5, r["CLOSE_DR"] or "", money_fmt)
            sheet.write(row, 6, r["CLOSE_CR"] or "", money_fmt)
            row += 1

        row += 1  # space after group

    # ========= GRAND TOTAL =========
     sheet.merge_range(row, 0, row, 6, "GRAND TOTAL", group_fmt)
     row += 1

     sheet.write_row(
        row, 0,
        [
            "ALL GROUPS",
            tb["OPEN_DR"].sum(),
            tb["OPEN_CR"].sum(),
            tb["DR"].sum(),
            tb["CR"].sum(),
            tb["CLOSE_DR"].sum(),
            tb["CLOSE_CR"].sum(),
        ],
        money_fmt
    )

    # ========= COLUMN WIDTH =========
     sheet.set_column("A:A", 30)
     sheet.set_column("B:G", 16)

     workbook.close()
     output.seek(0)

    # ========= SYSTEM-FRIENDLY DOWNLOAD =========
     return dcc.send_bytes(
        output.read(),
        filename=f"Trial_Balance_{from_dt.strftime('%d-%m-%Y')}_to_{to_dt.strftime('%d-%m-%Y')}.xlsx",
    )

    @app.callback(
        Output("tb-from-date", "date"),
        Output("tb-to-date", "date"),
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
    Output("tb-download-pdf-file", "data"),
    Input("tb-download-pdf-btn", "n_clicks"),
    State("tb-from-date", "date"),
    State("tb-to-date", "date"),
    State("tb-group-filter", "value"),
    State("session", "data"),
    prevent_initial_call=True,
)
    def download_trial_balance_pdf(n_clicks, from_date, to_date, selected_group, SessionData):

     if not n_clicks:
        return dash.no_update

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

     from_dt = pd.to_datetime(from_date)
     to_dt = pd.to_datetime(to_date)

     tb = build_trial_balance(from_dt, to_dt, selected_group, SessionData)

     buffer = io.BytesIO()

     doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=30,
        leftMargin=30,
        topMargin=30,
        bottomMargin=30,
    )

     styles = getSampleStyleSheet()

    # ===== CENTER STYLES =====
     center_title = styles["Title"]
     center_title.alignment = 1
 
     center_text = styles["Normal"]
     center_text.alignment = 1

     center_heading = styles["Heading3"]
     center_heading.alignment = 1

     group_heading = styles["Heading4"]
     group_heading.alignment = 1

     elements = []

    # ===== SCHOOL HEADER =====
     elements.append(Paragraph(f"<b>{school_name}</b>", center_title))
     elements.append(Paragraph(address, center_text))
     elements.append(Paragraph(f"PAN : {pan}",  center_text))

     elements.append(Spacer(1, 20))

    # ===== REPORT TITLE =====
     elements.append(
        Paragraph(
            f"<b>TRIAL BALANCE FROM {from_dt.strftime('%d-%m-%Y')} TO {to_dt.strftime('%d-%m-%Y')}</b>",
            center_heading,
        )
    )

     elements.append(Spacer(1, 25))

     headers = [
        "Ledger",
        "Opening Dr",
        "Opening Cr",
        "Debit",
        "Credit",
        "Closing Dr",
        "Closing Cr",
    ]

     col_widths = [180, 65, 65, 65, 65, 65, 65]

    # ===== GROUP TABLES =====
     for grp in DISPLAY_ORDER:

        if grp not in tb["GROUP"].unique():
            continue

        gdf = tb[tb["GROUP"] == grp]

        elements.append(Spacer(1, 10))
        elements.append(Paragraph(f"<b>{grp}</b>", group_heading))
        elements.append(Spacer(1, 6))

        table_data = [headers]

        for _, r in gdf.iterrows():

            table_data.append([
                r["LINE_ITEM"],
                f"{r['OPEN_DR']:,.2f}" if r["OPEN_DR"] else "",
                f"{r['OPEN_CR']:,.2f}" if r["OPEN_CR"] else "",
                f"{r['DR']:,.2f}" if r["DR"] else "",
                f"{r['CR']:,.2f}" if r["CR"] else "",
                f"{r['CLOSE_DR']:,.2f}" if r["CLOSE_DR"] else "",
                f"{r['CLOSE_CR']:,.2f}" if r["CLOSE_CR"] else "",
            ])

        table = Table(
            table_data,
            repeatRows=1,
            colWidths=col_widths,
            hAlign="CENTER",
        )

        table.setStyle(
            TableStyle([
                ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
                ("BACKGROUND", (0, 0), (-1, 0), colors.lightgrey),
                ("ALIGN", (1, 1), (-1, -1), "RIGHT"),
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ])
        )

        elements.append(table)

    # ===== GRAND TOTAL =====
     elements.append(Spacer(1, 20))

     totals = [
        [
            "GRAND TOTAL",
            f"{tb['OPEN_DR'].sum():,.2f}",
            f"{tb['OPEN_CR'].sum():,.2f}",
            f"{tb['DR'].sum():,.2f}",
            f"{tb['CR'].sum():,.2f}",
            f"{tb['CLOSE_DR'].sum():,.2f}",
            f"{tb['CLOSE_CR'].sum():,.2f}",
        ]
    ]

     total_table = Table(
        [["Ledger","Opening Dr","Opening Cr","Debit","Credit","Closing Dr","Closing Cr"]] + totals,
        colWidths=col_widths,
        hAlign="CENTER",
    )

     total_table.setStyle(
        TableStyle([
            ("GRID", (0, 0), (-1, -1), 0.7, colors.black),
            ("BACKGROUND", (0, 0), (-1, 0), colors.lightgrey),
            ("BACKGROUND", (0, 1), (-1, 1), colors.whitesmoke),
            ("ALIGN", (1, 1), (-1, -1), "RIGHT"),
            ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ])
    )

     elements.append(total_table)
 
     doc.build(elements)

     buffer.seek(0)

     return dcc.send_bytes(
        buffer.read(),
        filename=f"Trial_Balance_{from_dt.strftime('%d-%m-%Y')}_to_{to_dt.strftime('%d-%m-%Y')}.pdf",
    )