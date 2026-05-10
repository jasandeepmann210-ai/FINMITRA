import dash
from dash import dash_table, html, dcc, Input, Output, State
import pandas as pd
import os
import base64
import io

# ---------------------------
# Columns
# ---------------------------
columns = [
    "Delete",   
    "S.No",
    "Enquiry Date",
    "Follow-up Date",
    "Next-Follow up date",
    "Class Seeking Admission",
    "Enquiry Stage",
    "Phone Number",
    "Guardian Name",
    "Student Name",
    "Calendar Remarks",
]


# ---------------------------
# Load Data
# ---------------------------
def load_data(username):
    path = f"/var/Data/{username}/enquiries.csv"
    if os.path.exists(path):
        return pd.read_csv(path)
    return pd.DataFrame(columns=columns)


# ---------------------------
# Layout
# ---------------------------
def get_layout(session_data):
    if not session_data or "username" not in session_data:
        return html.Div("⚠️ Session expired", style={"textAlign": "center", "marginTop": "50px"})

    df = load_data(session_data["username"])
    df["Delete"] = "🗑️"  # Delete icon column

    return html.Div([
        # External Resources (Icons & Fonts)
        html.Link(rel="stylesheet", href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css"),
        html.Link(rel="stylesheet", href="https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;600&display=swap"),

        html.Div(style={
            "backgroundColor": "#f0f2f5", 
            "minHeight": "100vh", 
            "padding": "30px", 
            "fontFamily": "'Poppins', sans-serif"
        }, children=[
            
            # --- TOP HEADER ---
            html.Div(style={
                "display": "flex", 
                "justifyContent": "space-between", 
                "alignItems": "center", 
                "backgroundColor": "white", 
                "padding": "20px 30px", 
                "borderRadius": "15px", 
                "boxShadow": "0 4px 6px rgba(0,0,0,0.05)",
                "marginBottom": "25px"
            }, children=[
                html.H2([
                    html.I(className="fas fa-address-book", style={"marginRight": "15px", "color": "#4e73df"}),
                    "Enquiry Management"
                ], style={"margin": "0", "fontSize": "24px", "fontWeight": "600"}),
                
                html.Div([
                    html.Button([html.I(className="fas fa-save"), " Save"], id="save-btn-enq", 
                                style={"backgroundColor": "#4e73df", "color": "white", "border": "none", "padding": "10px 25px", "borderRadius": "8px", "cursor": "pointer", "marginRight": "10px", "fontWeight": "500"}),
                    html.Button([html.I(className="fas fa-file-excel"), " Export"], id="export-btn", 
                                style={"backgroundColor": "#1cc88a", "color": "white", "border": "none", "padding": "10px 25px", "borderRadius": "8px", "cursor": "pointer", "fontWeight": "500"}),
                ])
            ]),

            # --- INPUT FORM (Full Width) ---
            html.Div(style={
                "backgroundColor": "white", 
                "padding": "30px", 
                "borderRadius": "15px", 
                "boxShadow": "0 10px 25px rgba(0,0,0,0.05)",
                "marginBottom": "30px"
            }, children=[
                html.H4([html.I(className="fas fa-plus", style={"marginRight": "10px"}), "Add New Entry"], 
                        style={"marginTop": "0", "marginBottom": "20px", "color": "#333"}),
                
                html.Div(style={
                    "display": "grid", 
                    "gridTemplateColumns": "repeat(auto-fit, minmax(220px, 1fr))", 
                    "gap": "20px"
                }, children=[
                    # Inputs with consistent styling
                    dcc.Input(id="student-input", placeholder="Student Name", type="text", style={"padding": "12px", "borderRadius": "8px", "border": "1px solid #ddd"}),
                    dcc.Input(id="guardian-input", placeholder="Guardian Name", type="text", style={"padding": "12px", "borderRadius": "8px", "border": "1px solid #ddd"}),
                    dcc.Input(id="phone-input", placeholder="Phone Number", type="tel", style={"padding": "12px", "borderRadius": "8px", "border": "1px solid #ddd"}),
                    dcc.Input(id="class-input", placeholder="Class Admission", type="text", style={"padding": "12px", "borderRadius": "8px", "border": "1px solid #ddd"}),
                    
                    dcc.DatePickerSingle(id="enq-date", placeholder="Enquiry Date", style={"width": "100%"}),
                    dcc.DatePickerSingle(id="follow-date", placeholder="Follow-up Date"),
                    dcc.DatePickerSingle(id="next-follow-date", placeholder="Next Follow-up"),
                    
                    dcc.Dropdown(
                        id="stage-dropdown",
                        options=[
                            {"label": "✅ Admission Done", "value": "admission successful!"},
                            {"label": "⏳ Follow Up Pending", "value": "Follow Up Pending"},
                            {"label": "❌ Not Interested", "value": "Not Interested"},
                        ],
                        placeholder="Select Stage",
                        style={"height": "45px"}
                    ),
                ]),

                html.Button(
                    [html.I(className="fas fa-check-circle"), " Add Entry to Table"], 
                    id="add-form-btn", n_clicks=0,
                    style={
                        "marginTop": "25px", "width": "100%", "padding": "15px", 
                        "backgroundColor": "#36b9cc", "color": "white", "border": "none", 
                        "borderRadius": "8px", "fontWeight": "600", "fontSize": "16px", "cursor": "pointer"
                    }
                )
            ]),

            # --- DATA TABLE AREA ---
            html.Div(style={
                "backgroundColor": "white", "padding": "20px", "borderRadius": "15px", "boxShadow": "0 10px 25px rgba(0,0,0,0.05)"
            }, children=[
                html.Div(style={"display": "flex", "justifyContent": "space-between", "marginBottom": "15px", "alignItems": "center"}, children=[
                    html.H4("Enquiry Database", style={"margin": "0"}),
                    dcc.Upload(id="upload-data", children=html.Div([
                        html.I(className="fas fa-cloud-upload-alt", style={"marginRight": "8px"}),
                        "Bulk Upload Excel"
                    ], style={"color": "#4e73df", "fontWeight": "600", "cursor": "pointer"}))
                ]),
                
                html.Div(id="save-status-enq", style={"color": "#28a745", "fontWeight": "bold", "marginBottom": "10px"}),

                dash_table.DataTable(
    id="table-enq",
    active_cell=None,
    columns=[{"name": col, "id": col} for col in columns],
    data=df.to_dict("records"),
    editable=True,
    row_deletable=False,
    filter_action="native",
    sort_action="native",
    page_size=10,
    
    # --- FIXED COLUMN SETTINGS ---
    fixed_columns={'headers': True, 'data': 2}, # Sirf S.No fix rahega
    
    style_table={
        "minWidth": "100%",
        "overflowX": "auto", 
    },
    
    # Default cell style
    style_cell={
        "minWidth": "150px", 
        "padding": "10px",
        "fontFamily": "'Poppins', sans-serif",
        "fontSize": "13px",
    },

    # --- SPECIFIC WIDTH FOR S.No ---
    style_cell_conditional=[
        {
            'if': {'column_id': 'S.No'},
            'width': '50px',      # S.No ki width kam kar di
            'minWidth': '50px',
            'maxWidth': '50px',
            'textAlign': 'center'
        },
        {
    'if': {'column_id': 'Delete'},
    'width': '75px',
    'minWidth': '75px',
    'maxWidth': '75px',
    'textAlign': 'center'
},
    ],
    
    style_header={
        "backgroundColor": "#2c3e50",
        "color": "white",
        "fontWeight": "bold",
        "textAlign": "center"
    },
    style_data_conditional=[
        {"if": {"row_index": "odd"}, "backgroundColor": "#f8f9fc"},
    ],
)
, dcc.Download(id="download-excel"),
dcc.Store(id="delete-row-index"),
html.Div(
    id="delete-modal",
    style={
        "display": "none",
        "position": "fixed",
        "top": "0",
        "left": "0",
        "width": "100%",
        "height": "100%",
        "backgroundColor": "rgba(0,0,0,0.5)",
        "justifyContent": "center",
        "alignItems": "center",
        "zIndex": "1000"
    },
    children=[
        html.Div(
            style={
                "backgroundColor": "white",
                "padding": "30px",
                "borderRadius": "12px",
                "width": "400px",
                "textAlign": "center",
                "boxShadow": "0 10px 30px rgba(0,0,0,0.2)"
            },
            children=[
                html.H3("Confirm Delete", style={"marginBottom": "15px"}),
                html.P("Are you sure you want to permanently delete this entry?"),
                
                html.Div([
                    html.Button("Cancel", id="cancel-delete", n_clicks=0,
                        style={
                            "marginRight": "10px",
                            "padding": "10px 20px",
                            "borderRadius": "8px",
                            "border": "none",
                            "backgroundColor": "#6c757d",
                            "color": "white",
                            "cursor": "pointer"
                        }),
                    
                    html.Button("Delete", id="confirm-delete-btn", n_clicks=0,
                        style={
                            "padding": "10px 20px",
                            "borderRadius": "8px",
                            "border": "none",
                            "backgroundColor": "#e74a3b",
                            "color": "white",
                            "cursor": "pointer"
                        })
                ])
            ]
        )
    ]
),

            ]
            )
        ])
    ])







# ---------------------------
# Callbacks
# ---------------------------
def  register_callbacks(app):

    # ---------------------------
    # Add from FORM
    # ---------------------------
    # ---------------------------
    # Add from FORM + Clear Inputs (Fixed Error)
    # ---------------------------
    @app.callback(
        [Output("table-enq", "data", allow_duplicate=True), # Pehle se update ho raha tha isliye
         Output("student-input", "value"),
         Output("guardian-input", "value"),
         Output("phone-input", "value"),
         Output("class-input", "value"),
         Output("enq-date", "date"),
         Output("follow-date", "date"),
         Output("next-follow-date", "date"),
         Output("stage-dropdown", "value"),
         Output("save-status-enq", "children", allow_duplicate=True)], # ERROR YAHAN THI
        Input("add-form-btn", "n_clicks"),
        State("table-enq", "data"),
        State("enq-date", "date"),
        State("follow-date", "date"),
        State("next-follow-date", "date"),
        State("class-input", "value"),
        State("stage-dropdown", "value"),
        State("phone-input", "value"),
        State("guardian-input", "value"),
        State("student-input", "value"),
        prevent_initial_call=True, # Ye hona zaroori hai allow_duplicate ke liye
    )
    def add_and_reset(n, rows, enq, follow, nextf, cls, stage, phone, guardian, student):
        if not n:
            return dash.no_update

        rows = rows or []
        rows.append({
            "S.No": len(rows) + 1,
            "Enquiry Date": enq,
            "Follow-up Date": follow,
            "Next-Follow up date": nextf,
            "Class Seeking Admission": cls,
            "Enquiry Stage": stage,
            "Phone Number": phone,
            "Guardian Name": guardian,
            "Student Name": student,
            "Calendar Remarks": "",
        })

        # Sab clear aur message update
        return rows, "", "", "", "", None, None, None, None, "✨ Entry Added to Table!"

    # ---------------------------
    # SAVE + EVENTS
    # ---------------------------
    @app.callback(
        Output("save-status-enq", "children"),
        Input("save-btn-enq", "n_clicks"),
        State("table-enq", "data"),
        State("session", "data"),
        prevent_initial_call=True,
    )
    def save_data(n, rows, session_data):

        if not session_data:
            return "Session expired"

        username = session_data["username"]

        df = pd.DataFrame(rows)
        df.to_csv(f"/var/Data/{username}/enquiries.csv", index=False)

        events = []

        for _, r in df.iterrows():
            remarks = f"{r.get('Student Name','')} parents/guardian {r.get('Guardian Name','')} is seeking admission to {r.get('Class Seeking Admission','')} connect on {r.get('Phone Number','')}. The discussion Stage is {r.get('Enquiry Stage','')}"

            if r.get("Follow-up Date"):
                events.append({"event": remarks, "date": r["Follow-up Date"]})

            if r.get("Next-Follow up date"):
                events.append({"event": remarks, "date": r["Next-Follow up date"]})

        events_df = pd.DataFrame(events)
        path = f"/var/Data/{username}/events.csv"

        if os.path.exists(path):
            existing = pd.read_csv(path)
            events_df = pd.concat([existing, events_df])
            events_df.drop_duplicates(inplace=True)

        events_df.to_csv(path, index=False)

        return "✅ Saved successfully"

    # ---------------------------
    # EXPORT
    # ---------------------------
    @app.callback(
        Output("download-excel", "data"),
        Input("export-btn", "n_clicks"),
        State("table-enq", "data"),
        prevent_initial_call=True,
    )
    def export_excel(n, rows):
        df = pd.DataFrame(rows)
        return dcc.send_data_frame(df.to_excel, "enquiry.xlsx", index=False)

    # ---------------------------
    # UPLOAD
    # ---------------------------
   
    @app.callback(
    Output("table-enq", "data", allow_duplicate=True),
    Input("upload-data", "contents"),
    State("upload-data", "filename"),  # Filename mangwana zaroori hai
    State("session", "data"),
    prevent_initial_call=True,
)
    def upload_excel(contents, filename, session_data):
     if not contents or not filename:
        return dash.no_update

     content_type, content_string = contents.split(",")
     decoded = base64.b64decode(content_string)
    
    # Check extension to decide engine
     try:
        if filename.endswith('.xlsx'):
            df = pd.read_excel(io.BytesIO(decoded), engine='openpyxl')
        elif filename.endswith('.xls'):
            df = pd.read_excel(io.BytesIO(decoded), engine='xlrd')
        elif filename.endswith('.csv'):
            df = pd.read_csv(io.BytesIO(decoded))
        else:
            return dash.no_update # Format support nahi karta
            
        df = df.reindex(columns=columns)
        path = f"/var/Data/{session_data['username']}/enquiries.csv"
        df.to_csv(path, index=False)

        return df.to_dict("records")
        
     except Exception as e:
        print(f"Error reading file: {e}")
        return dash.no_update
     

    @app.callback(
    Output("delete-modal", "style"),
    Output("delete-row-index", "data"),
    Output("table-enq", "data"),
    Input("table-enq", "active_cell"),
    Input("cancel-delete", "n_clicks"),
    Input("confirm-delete-btn", "n_clicks"),
    State("delete-row-index", "data"),
    State("table-enq", "data"),
    prevent_initial_call=True
)
    def handle_delete(active_cell, cancel_click, confirm_click, row_index, rows):
     ctx = dash.callback_context

     if not ctx.triggered:
        return dash.no_update, dash.no_update, dash.no_update

     trigger = ctx.triggered[0]["prop_id"].split(".")[0]

    # 🟢 OPEN MODAL
     if trigger == "table-enq" and active_cell and active_cell.get("column_id") == "Delete":
        return {
            "display": "flex",
            "position": "fixed",
            "top": "0",
            "left": "0",
            "width": "100%",
            "height": "100%",
            "backgroundColor": "rgba(0,0,0,0.5)",
            "justifyContent": "center",
            "alignItems": "center",
            "zIndex": "1000"
        }, active_cell["row"], dash.no_update

    # 🔴 CANCEL
     if trigger == "cancel-delete":
        return {"display": "none"}, dash.no_update, dash.no_update

    # 🔥 DELETE
     if trigger == "confirm-delete-btn" and row_index is not None:
        rows.pop(row_index)

        # reset S.No
        for i, r in enumerate(rows):
            r["S.No"] = i + 1

        return {"display": "none"}, None, rows

     return dash.no_update, dash.no_update, dash.no_update 