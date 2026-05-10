import dash
from dash import html, dcc, Input, Output, State, dash_table
import pandas as pd
import os
import io
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib import colors

import xlsxwriter

# =====================================================
# MASTER DEPRECIATION RATES
# =====================================================
DEPRECIATION_RATES = {
    "Land & Building": 0.00,
    "Furniture & Fixtures": 10.0 / 100,
    "Laboratory Equipment": 15.0 / 100,
    "Computers & IT Assets": 40.0 / 100,
    "Vehicles": 15.0 / 100,
    "Camera System": 15.0 / 100,
    "Sports Equipment": 15.0 / 100,
    "Electricity Equiment": 15.0 / 100,
    "Solar Powered Equipments": 40 / 100,
}

# 🔒 EXPLICIT DROPDOWN OPTIONS (NO LOOP)
BASE_ASSET_OPTIONS = [
    {"label": "Land & Building", "value": "Land & Building"},
    {"label": "Furniture & Fixtures", "value": "Furniture & Fixtures"},
    {"label": "Laboratory Equipment", "value": "Laboratory Equipment"},
    {"label": "Computers & IT Assets", "value": "Computers & IT Assets"},
    {"label": "Vehicles", "value": "Vehicles"},
    {"label": "Camera System", "value": "Camera System"},
    {"label": "Sports Equipment", "value": "Sports Equipment"},
    {"label": "Electricity Equiment", "value": "Electricity Equiment"},
    {"label": "Solar Powered Equipments", "value": "Solar Powered Equipments"},
]


# =====================================================
# LAYOUT (STATIC)
# =====================================================
def get_layout1():
    return html.Div(
        [
            # ================= HEADER =================
            html.Div(
                [
                    html.H2(
                        "Depreciation Mapper",
                        style={
                            "marginBottom": "4px",
                            "color": "#1b5e20",
                            "fontWeight": "600",
                        },
                    ),
                    html.P(
                        "Map each fixed asset to a depreciation category. "
                        "The rate auto-fills based on your selection - "
                        "Land & Building , Furniture & Fixtures, Laboratory Equipment, "
                        "Computers & IT Assets, Vehicles, Camera System, "
                        "Sports Equipment, Electricity Equiment, Solar Powered Equipments",
                        style={
                            "marginTop": "0px",
                            "color": "#555",
                            "fontSize": "14px",
                        },
                    ),
                ],
                style={"marginBottom": "20px"},
            ),
            # ================= ACTION BAR =================
            html.Div(
                [
                    html.Button(
                        "▶ Run",
                        id="run-btn",
                        n_clicks=0,
                        style={
                            "backgroundColor": "#2e7d32",
                            "color": "white",
                            "border": "none",
                            "padding": "8px 16px",
                            "fontSize": "14px",
                            "borderRadius": "4px",
                            "cursor": "pointer",
                            "marginRight": "10px",
                        },
                    ),
                    html.Span(
                        "Loads fixed assets for mapping",
                        style={
                            "fontSize": "13px",
                            "color": "#666",
                            "verticalAlign": "middle",
                        },
                    ),
                    # 🔽 DOWNLOAD BUTTON
                    html.Button(
                        "⬇ Download Excel",
                        id="download-mapper-btn",
                        disabled=True,
                        style={
                            "backgroundColor": "#2e7d32",
                            "color": "white",
                            "border": "none",
                            "padding": "8px 16px",
                            "fontSize": "14px",
                            "borderRadius": "4px",
                            "cursor": "pointer",
                            "marginLeft": "15px",
                        },
                    ),
                    html.Button(
    "⬇ Download PDF",
    id="download-mapper-pdf-btn",
    disabled=True,
    style={
        "backgroundColor": "#c62828",
        "color": "white",
        "border": "none",
        "padding": "8px 16px",
        "fontSize": "14px",
        "borderRadius": "4px",
        "cursor": "pointer",
        "marginLeft": "10px",
    },
),

dcc.Download(id="download-mapper-pdf-file"),
                    # REQUIRED DOWNLOAD COMPONENT
                    dcc.Download(id="download-mapper-file"),
                ],
                style={"marginBottom": "16px"},
            ),
            # ================= TABLE =================
            dash_table.DataTable(
                id="mapper-table",
                columns=[
                    {"name": "Fixed Asset", "id": "asset_name", "editable": False},
                    {
                        "name": "Depreciation Category",
                        "id": "base_asset",
                        "presentation": "dropdown",
                        "editable": True,
                    },
                    {"name": "Rate (%)", "id": "rate"},
                ],
                # ✅ At least ONE row so dropdown can appear
                data=[
                    {
                        "asset_name": "—",
                        "base_asset": None,
                        "rate": None,
                    }
                ],
                editable=True,
                # ✅ Proper dropdown config
                dropdown={"base_asset": {"options": BASE_ASSET_OPTIONS}},
                style_table={
                    "width": "75%",
                    "border": "1px solid #ddd",
                },
                style_cell={
                    "padding": "10px",
                    "fontFamily": "Segoe UI, Arial",
                    "fontSize": "14px",
                    "borderBottom": "1px solid #eee",
                },
                style_header={
                    "backgroundColor": "#f1f8e9",
                    "fontWeight": "600",
                    "borderBottom": "2px solid #c5e1a5",
                },
                style_data_conditional=[
                    {
                        "if": {"column_id": "asset_name"},
                        "fontWeight": "500",
                        "backgroundColor": "#fafafa",
                    },
                    {
                        "if": {"column_id": "rate"},
                        "textAlign": "right",
                    },
                ],
            ),
            # ================= FOOTER ACTION =================
            html.Div(
                [
                    html.Button(
                        "💾 Save",
                        id="save-btn",
                        style={
                            "backgroundColor": "#1565c0",
                            "color": "white",
                            "border": "none",
                            "padding": "8px 18px",
                            "fontSize": "14px",
                            "borderRadius": "4px",
                            "cursor": "pointer",
                        },
                    ),
                    html.Span(
                        id="save-status",
                        style={
                            "marginLeft": "12px",
                            "fontSize": "13px",
                            "color": "#2e7d32",
                        },
                    ),
                ],
                style={"marginTop": "18px"},
            ),
        ],
        style={
            "padding": "24px",
            "backgroundColor": "#fcfff5",
        },
    )


# =====================================================
# CALLBACKS
# =====================================================
def register_callbacks(app):

    # --------------------------------------------------
    # RUN → LOAD DATA
    # --------------------------------------------------
    @app.callback(
        Output("mapper-table", "data"),
        Input("run-btn", "n_clicks"),
        State("session", "data"),
        prevent_initial_call=True,
    )
    def load_mapper(_, SessionData):

        if not SessionData or "username" not in SessionData:
            return []

        base_path = f"/var/Data/{SessionData['username']}"
        melt_path = f"{base_path}/melt_db.csv"
        mapper_path = f"{base_path}/depreciation_mapper.csv"

        if not os.path.exists(melt_path):
            return []

        melt_df = pd.read_csv(melt_path)

        fixed_assets = (
            melt_df[melt_df["GROUP"] == "Fixed Assets"]["LINE_ITEM"].dropna().unique()
        )

        if os.path.exists(mapper_path):
            mapper_df = pd.read_csv(mapper_path)
        else:
            mapper_df = pd.DataFrame(columns=["asset_name", "base_asset", "rate"])

        rows = []

        for fa in fixed_assets:
            match = mapper_df[mapper_df["asset_name"] == fa]

            if not match.empty:
                rows.append(
                    {
                        "asset_name": fa,
                        "base_asset": match.iloc[0]["base_asset"],
                        "rate": match.iloc[0]["rate"],
                    }
                )
            else:
                rows.append(
                    {
                        "asset_name": fa,
                        "base_asset": "",
                        "rate": "",
                    }
                )

        return rows

    # --------------------------------------------------
    # AUTO-FILL RATE
    # --------------------------------------------------
    @app.callback(
        Output("mapper-table", "data", allow_duplicate=True),
        Input("mapper-table", "data_timestamp"),
        State("mapper-table", "data"),
        prevent_initial_call=True,
    )
    def auto_fill_rate(_, rows):

        for r in rows:
            base = r.get("base_asset")
            if base in DEPRECIATION_RATES:
                r["rate"] = DEPRECIATION_RATES[base]

        return rows

    # --------------------------------------------------
    # SAVE
    # --------------------------------------------------
    @app.callback(
        Output("save-status", "children"),
        Input("save-btn", "n_clicks"),
        State("mapper-table", "data"),
        State("session", "data"),
        prevent_initial_call=True,
    )
    def save_mapper(_, rows, SessionData):

        if not SessionData or "username" not in SessionData:
            return "No session found"

        base_path = f"/var/Data/{SessionData['username']}"
        mapper_path = f"{base_path}/depreciation_mapper.csv"

        df = pd.DataFrame(rows)
        df = df[df["base_asset"] != ""]
        df["rate"] = pd.to_numeric(df["rate"], errors="coerce").fillna(0)

        os.makedirs(base_path, exist_ok=True)
        df.to_csv(mapper_path, index=False)

        return "Saved successfully"

    # ADD THIS
    @app.callback(
        Output("download-mapper-file", "data"),
        Input("download-mapper-btn", "n_clicks"),
        State("mapper-table", "data"),
        State("session", "data"),
        prevent_initial_call=True,
    )
    def download_mapper_excel(n_clicks, rows, SessionData):

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

        if not rows:
            return dash.no_update

        df = pd.DataFrame(rows)

        output = io.BytesIO()
        workbook = xlsxwriter.Workbook(output)
        sheet = workbook.add_worksheet("Depreciation Mapper")

# ===== FORMATS =====
        title_fmt = workbook.add_format({"bold": True, "font_size": 14, "align": "center"})
        header_fmt = workbook.add_format({"bold": True, "border": 1, "align": "center"})
        text_fmt = workbook.add_format({"border": 1})
        rate_fmt = workbook.add_format({"border": 1, "num_format": "0.00%"})

        row = 0

# ===== SCHOOL HEADER =====
        sheet.merge_range(row, 0, row, 2, school_name, title_fmt)
        row += 1
 
        sheet.merge_range(row, 0, row, 1, f"PAN : {pan}")
        sheet.write(row, 2, address)
        row += 2

# ===== TITLE =====
        sheet.merge_range(row, 0, row, 2, "DEPRECIATION MAPPER", header_fmt)
        row += 1

# ===== COLUMN HEADERS =====
        headers = ["Fixed Asset", "Depreciation Category", "Rate (%)"]
        sheet.write_row(row, 0, headers, header_fmt)
        row += 1

# ===== DATA =====
        for _, r in df.iterrows():
         sheet.write(row, 0, r["asset_name"], text_fmt)
         sheet.write(row, 1, r["base_asset"], text_fmt)
         sheet.write(row, 2, r["rate"], rate_fmt)
         row += 1

        sheet.set_column("A:A", 35)
        sheet.set_column("B:B", 30)
        sheet.set_column("C:C", 12)

        workbook.close()
        output.seek(0)
        return dcc.send_bytes(output.read(), "depreciation_mapper.xlsx")

    # ADD THIS
    @app.callback(
        Output("download-mapper-btn", "disabled"),
        Input("run-btn", "n_clicks"),
        prevent_initial_call=True,
    )
    def enable_download_after_run(n_clicks):
        if n_clicks and n_clicks > 0:
            return False  # enable
        return True  # disabled
    


    @app.callback(
    Output("download-mapper-pdf-btn", "disabled"),
    Input("run-btn", "n_clicks"),
    prevent_initial_call=True,
)
    def enable_pdf_download_after_run(n_clicks):
     if n_clicks and n_clicks > 0:
        return False
     return True
    


    @app.callback(
    Output("download-mapper-pdf-file", "data"),
    Input("download-mapper-pdf-btn", "n_clicks"),
    State("mapper-table", "data"),
    State("session", "data"),
    prevent_initial_call=True,
)
    def download_mapper_pdf(n_clicks, rows, SessionData):

     if not rows:
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

     df = pd.DataFrame(rows)

     buffer = io.BytesIO()

     doc = SimpleDocTemplate(buffer, pagesize=A4)

     styles = getSampleStyleSheet()

     title = styles["Title"]
     title.alignment = 1

     normal = styles["Normal"]
     normal.alignment = 1

     elements = []

    # ===== SCHOOL HEADER =====
     elements.append(Paragraph(f"<b>{school_name}</b>", title))
     elements.append(Paragraph(f"PAN : {pan}", normal))
     elements.append(Paragraph(address, normal))
     elements.append(Spacer(1, 20))

     elements.append(Paragraph("<b>DEPRECIATION MAPPER</b>", title))
     elements.append(Spacer(1, 20))

     headers = ["Fixed Asset", "Depreciation Category", "Rate (%)"]

     table_data = [headers]

     for _, r in df.iterrows():
        table_data.append([
            r["asset_name"],
            r["base_asset"],
            f"{float(r['rate'])*100:.2f}%" if r["rate"] else "",
        ])

     table = Table(table_data, hAlign="CENTER", colWidths=[250, 200, 100])

     table.setStyle(
        TableStyle([
            ("GRID", (0,0), (-1,-1), 0.5, colors.grey),
            ("BACKGROUND", (0,0), (-1,0), colors.lightgrey),
            ("ALIGN", (2,1), (-1,-1), "RIGHT"),
            ("FONTNAME", (0,0), (-1,0), "Helvetica-Bold"),
        ])
    )

     elements.append(table)

     doc.build(elements)

     buffer.seek(0)

     return dcc.send_bytes(
        buffer.read(),
        "depreciation_mapper.pdf"
    )










