import dash
from dash import html, dcc, Input, Output, State
import dash_bootstrap_components as dbc
import pandas as pd
import os
import io
import xlsxwriter
from datetime import date
from reportlab.lib.pagesizes import landscape, A4
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib import colors
# IMPORT YOUR EXISTING ENGINES
from CT_Exposure_Dashboard import generate_cash_book
from MonteCarlo_Simulator import generate_bank_book


# =====================================================
# FINANCIAL YEAR
# =====================================================

def get_fy_date_range(selected_fy):

    fy_year = int(selected_fy.replace("FY", ""))
    end_year = 2000 + fy_year
    start_year = end_year - 1

    start_date = date(start_year, 4, 1)
    end_date = date(end_year, 3, 31)

    return start_date, end_date


# =====================================================
# LAYOUT
# =====================================================

def get_layout1():

    return dbc.Container([

        html.H3(
            "Receipt & Payment Account",
            className="text-center my-4 fw-bold"
        ),

        dbc.Row([

            dbc.Col(dcc.DatePickerSingle(id="from-date"), md=3),
            dbc.Col(dcc.DatePickerSingle(id="to-date"), md=3),

        ], className="mb-3 justify-content-center"),

        dbc.Row([

            dbc.Col(
                dbc.Input(
                    id="ob-cash",
                    type="number",
                    placeholder="Opening Cash"
                ),
                md=3
            ),

            dbc.Col(
                dbc.Input(
                    id="ob-bank",
                    type="number",
                    placeholder="Opening Bank"
                ),
                md=3
            ),

        ], className="mb-3 justify-content-center"),

        dbc.Row([

            dbc.Col(
                dbc.Button(
                    "Confirm & Generate R&P",
                    id="confirm-btn",
                    color="primary"
                ),
                width="auto"
            ),

            dbc.Col(
                dbc.Button(
                    "Download R&P",
                    id="download-rp-btn",
                    color="success",
                    style={"display":"none"}
                ),
                width="auto"
            ),
            dbc.Col(
    dbc.Button(
        "Download PDF",
        id="download-rp-pdf-btn",
        color="danger",
        style={"display":"none"}
    ),
    width="auto"
),

        ], className="mb-3 justify-content-center"),

        dcc.Download(id="download-rp-file"),
        dcc.Store(id="rp-data"),
        dcc.Download(id="download-rp-pdf-file"),

        html.Hr(),

        dbc.Row([
            dbc.Col(html.Div(id="rp-output"), md=10)
        ], className="justify-content-center")

    ], fluid=True)



def write_number_safe(ws,row,col,value,fmt):

    if value == "" or value is None:
        ws.write(row,col,"",fmt)
    else:
        ws.write_number(row,col,float(value),fmt)

# =====================================================
# CALLBACKS
# =====================================================

def register_callbacks(app):


    # -------------------------------------------------
    # FY AUTO DATE
    # -------------------------------------------------

    @app.callback(
        Output("from-date","date"),
        Output("to-date","date"),
        Input("financial-year-dropdown","value")
    )
    def auto_set_dates(selected_fy):

        if not selected_fy:
            raise dash.exceptions.PreventUpdate

        start,end = get_fy_date_range(selected_fy)

        return (
            start.strftime("%Y-%m-%d"),
            end.strftime("%Y-%m-%d")
        )


    # -------------------------------------------------
    # OPENING BALANCE
    # -------------------------------------------------

    @app.callback(
        Output("ob-cash","value"),
        Output("ob-bank","value"),
        Input("from-date","date"),
        State("session","data")
    )
    def compute_opening_balance(from_date, SessionData):

        if not from_date:
            return 0,0

        cash_r, cash_p, ob_cash, *_ = generate_cash_book(
            "1900-01-01", from_date, SessionData
        )

        bank_r, bank_p, ob_bank, *_ = generate_bank_book(
            "1900-01-01", from_date, "bank1", SessionData
        )

        return ob_cash, ob_bank


    # -------------------------------------------------
    # GENERATE RECEIPT & PAYMENT
    # -------------------------------------------------

    @app.callback(
        Output("rp-output","children"),
        Output("download-rp-btn","style"),
        Output("download-rp-pdf-btn","style"),
        Output("rp-data","data"),
        Input("confirm-btn","n_clicks"),
        State("from-date","date"),
        State("to-date","date"),
        State("session","data"),
        prevent_initial_call=True
    )

    def generate_rp(_, from_date, to_date, SessionData):

        receipts = {}
        payments = {}
    
        # -------------------------------------------------
        # GET CASH BOOK DATA
        # -------------------------------------------------
    
        cash_r, cash_p, ob_cash, *_ = generate_cash_book(
            from_date, to_date, SessionData
        )
    
        for _, row in cash_r.iterrows():
    
            name = row["receipt"]
    
            receipts.setdefault(name, {"cash":0,"bank":0})
            receipts[name]["cash"] += row["amount"]
    
        for _, row in cash_p.iterrows():
    
            name = row["payment"]
    
            payments.setdefault(name, {"cash":0,"bank":0})
            payments[name]["cash"] += row["amount"]
    
    
        # -------------------------------------------------
        # ADD ALL BANK BOOKS
        # -------------------------------------------------
    
        ob_bank = 0
    
        for i in range(1,11):
    
            bank_col = f"bank{i}"
    
            try:
    
                bank_r, bank_p, ob_b, *_ = generate_bank_book(
                    from_date, to_date, bank_col, SessionData
                )
    
                ob_bank += ob_b
    
            except:
                continue
    
            for _, row in bank_r.iterrows():
    
                name = row["receipt"]
    
                receipts.setdefault(name, {"cash":0,"bank":0})
                receipts[name]["bank"] += row["amount"]
    
            for _, row in bank_p.iterrows():
    
                name = row["payment"]
    
                payments.setdefault(name, {"cash":0,"bank":0})
                payments[name]["bank"] += row["amount"]
    
    
        # -------------------------------------------------
        # PREPARE ROWS
        # -------------------------------------------------
    
        rc_rows = list(receipts.items())
        pm_rows = list(payments.items())
    
        max_rows = max(len(rc_rows), len(pm_rows))
    
        rows = []
    
        rc_cash = ob_cash
        rc_bank = ob_bank
        pm_cash = 0
        pm_bank = 0
    
    
        # -------------------------------------------------
        # OPENING BALANCE
        # -------------------------------------------------
    
        rows.append(html.Tr([
    
            html.Td("Opening Balance"),
            html.Td(f"{ob_cash:,.2f}"),
            html.Td(f"{ob_bank:,.2f}"),
    
            html.Td(""),
            html.Td(""),
            html.Td("")
    
        ]))
    
    
        # -------------------------------------------------
        # TRANSACTION ROWS
        # -------------------------------------------------
    
        for i in range(max_rows):
    
            r = rc_rows[i] if i < len(rc_rows) else ("",{"cash":0,"bank":0})
            p = pm_rows[i] if i < len(pm_rows) else ("",{"cash":0,"bank":0})
    
            rc_cash += r[1]["cash"]
            rc_bank += r[1]["bank"]
    
            pm_cash += p[1]["cash"]
            pm_bank += p[1]["bank"]
    
            rows.append(html.Tr([
    
                html.Td(r[0]),
                html.Td(f"{r[1]['cash']:,.2f}"),
                html.Td(f"{r[1]['bank']:,.2f}"),
    
                html.Td(p[0]),
                html.Td(f"{p[1]['cash']:,.2f}"),
                html.Td(f"{p[1]['bank']:,.2f}")
    
            ]))
    
    
        # -------------------------------------------------
        # CLOSING BALANCE
        # -------------------------------------------------
    
        close_cash = rc_cash - pm_cash
        close_bank = rc_bank - pm_bank
    
        rows.append(html.Tr([
    
            html.Td(""),
            html.Td(""),
            html.Td(""),
    
            html.Td("Closing Balance"),
            html.Td(f"{close_cash:,.2f}"),
            html.Td(f"{close_bank:,.2f}")
    
        ]))
    
    
        # -------------------------------------------------
        # TOTAL ROW
        # -------------------------------------------------
    
        rows.append(html.Tr([
    
            html.Th("Total"),
            html.Th(f"{rc_cash:,.2f}"),
            html.Th(f"{rc_bank:,.2f}"),
    
            html.Th("Total"),
            html.Th(f"{pm_cash + close_cash:,.2f}"),
            html.Th(f"{pm_bank + close_bank:,.2f}")
    
        ]))
    
    
        # -------------------------------------------------
        # BUILD TABLE
        # -------------------------------------------------
    
        table = dbc.Table(
    
            [
    
                html.Thead([
    
                    html.Tr([
                        html.Th("Receipts", colSpan=3),
                        html.Th("Payments", colSpan=3)
                    ]),
    
                    html.Tr([
                        html.Th("Particulars"),
                        html.Th("Cash"),
                        html.Th("Bank"),
                        html.Th("Particulars"),
                        html.Th("Cash"),
                        html.Th("Bank"),
                    ])
    
                ]),
    
                html.Tbody(rows)
    
            ],
    
            bordered=True,
            striped=True,
            hover=True
    
        )

        excel_rows = []

        excel_rows.append([
    "Opening Balance", ob_cash, ob_bank, "", "", ""
])

        for i in range(max_rows):

         r = rc_rows[i] if i < len(rc_rows) else ("",{"cash":0,"bank":0})
         p = pm_rows[i] if i < len(pm_rows) else ("",{"cash":0,"bank":0})

         excel_rows.append([
        r[0],
        r[1]["cash"],
        r[1]["bank"],
        p[0],
        p[1]["cash"],
        p[1]["bank"]
    ])

        excel_rows.append([
    "", "", "", "Closing Balance", close_cash, close_bank
])

        excel_rows.append([
    "Total",
    rc_cash,
    rc_bank,
    "Total",
    pm_cash + close_cash,
    pm_bank + close_bank
])
    
        return table, {"display":"inline-block"}, {"display":"inline-block"}, excel_rows


    # -------------------------------------------------
    # DOWNLOAD EXCEL
    # -------------------------------------------------

    @app.callback(
    Output("download-rp-file","data"),
    Input("download-rp-btn","n_clicks"),
    State("rp-data","data"),
    State("session","data"),
    prevent_initial_call=True
)
    def download_excel(n, data, SessionData):
     
     school_name = ""
     address = ""
     pan = ""

     try:
      user = SessionData["username"]

      df_school = pd.read_csv(f"/var/Data/{user}/school_info.csv")
      school_name = df_school.loc[0,"school_name"]
      address = df_school.loc[0,"address"]
      pan = df_school.loc[0,"pan_number"]
     except:
       pass
     output = io.BytesIO()

     workbook = xlsxwriter.Workbook(output, {'in_memory':  True})
     worksheet = workbook.add_worksheet("Receipt & Payment")

     header = workbook.add_format({'bold': True, 'align': 'center', 'border':1})
     bold = workbook.add_format({'bold': True, 'border':1})
     border = workbook.add_format({'border':1})
     money = workbook.add_format({'border':1, 'num_format': '#,##0.00'})

    # column width
     worksheet.set_column("A:A",30)
     worksheet.set_column("B:C",18)
     worksheet.set_column("D:D",30)
     worksheet.set_column("E:F",18)
     

    # SCHOOL NAME (CENTER)
     worksheet.merge_range("A1:F1", school_name, header)

    # PAN LEFT
     worksheet.merge_range("A2:C2", f"PAN : {pan}")

    # ADDRESS RIGHT
     worksheet.merge_range("D2:F2", address)
    # HEADER
     worksheet.merge_range("A3:C3","Receipts",header)
     worksheet.merge_range("D3:F3","Payments",header)

     worksheet.write_row("A4",["Particulars","Cash","Bank"],header)
     worksheet.write_row("D4",["Particulars","Cash","Bank"],header)

     row = 4

     for r in data:

      worksheet.write(row,0,r[0],border)
      write_number_safe(worksheet,row,1,r[1],money)
      write_number_safe(worksheet,row,2,r[2],money)

      worksheet.write(row,3,r[3],border)
      write_number_safe(worksheet,row,4,r[4],money)
      write_number_safe(worksheet,row,5,r[5],money)

      row += 1

     workbook.close()
     output.seek(0)

     return dcc.send_bytes(
        output.read(),
        "Receipt_Payment.xlsx"
    )

    @app.callback(
    Output("download-rp-pdf-file","data"),
    Input("download-rp-pdf-btn","n_clicks"),
    State("rp-data","data"),
    State("session","data"),
    State("from-date","date"),
    State("to-date","date"),
    prevent_initial_call=True
)
    def download_pdf(n, data, SessionData, from_date, to_date):

     school_name = ""
     address = ""
     pan = ""

     try:
        user = SessionData["username"]

        df_school = pd.read_csv(f"/var/Data/{user}/school_info.csv")

        school_name = df_school.loc[0,"school_name"]
        address = df_school.loc[0,"address"]
        pan = df_school.loc[0,"pan_number"]

     except:
        pass

     buffer = io.BytesIO()

     doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=40,
        leftMargin=40,
        topMargin=40,
        bottomMargin=40
    )

     styles = getSampleStyleSheet()

     elements = []

    # =============================
    # CENTER STYLES
    # =============================

     title_style = styles["Title"]
     title_style.alignment = 1

     center_style = styles["Heading3"]
     center_style.alignment = 1

     subtitle = styles["Heading2"]
     subtitle.alignment = 1

    # =============================
    # HEADER
    # =============================

     elements.append(Paragraph(f"<b>{school_name}</b>", title_style))
     elements.append(Paragraph(address, center_style))
     elements.append(Paragraph(f"PAN : {pan}", center_style))

     elements.append(Spacer(1,15))

     elements.append(
        Paragraph(
            f"<b>Receipt & Payment Account ({from_date} to {to_date})</b>",
            subtitle
        )
    )

     elements.append(Spacer(1,25))

    # =============================
    # TABLE DATA
    # =============================

     table_data = [

        ["Receipts","","","Payments","",""],

        ["Particulars","Cash","Bank","Particulars","Cash","Bank"]

    ]

     for r in data:

        table_data.append([

            r[0],
            f"{r[1]:,.2f}" if r[1] else "",
            f"{r[2]:,.2f}" if r[2] else "",

            r[3],
            f"{r[4]:,.2f}" if r[4] else "",
            f"{r[5]:,.2f}" if r[5] else ""

        ])

     table = Table(
        table_data,
        colWidths=[150,70,70,150,70,70]
    )

     table.setStyle(TableStyle([

        ("GRID",(0,0),(-1,-1),1,colors.black),

        ("SPAN",(0,0),(2,0)),
        ("SPAN",(3,0),(5,0)),

        ("BACKGROUND",(0,0),(-1,1),colors.lightgreen),

        ("ALIGN",(1,2),(-1,-1),"RIGHT"),

        ("FONTNAME",(0,0),(-1,1),"Helvetica-Bold"),

        ("FONTSIZE",(0,0),(-1,-1),10)

    ]))

     elements.append(table)

     doc.build(elements)

     buffer.seek(0)

     return dcc.send_bytes(
        buffer.read(),
        "Receipt_Payment_Report.pdf"
    )
