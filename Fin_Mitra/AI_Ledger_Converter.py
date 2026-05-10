import os
from flask import Flask
import dash
from dash import html, dcc, Input, Output
import dash_bootstrap_components as dbc
import base64
import os
from openai import OpenAI
from dotenv import load_dotenv

# Load .env file
load_dotenv(override=True)

# Initialize client
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

with open("assets/def create_student_form(SessionData.txt", "r", encoding="utf-8") as f:
    ORIGINAL_FUNCTION = f.read()

# ======================================
# FLASK SERVER
# ======================================
server = Flask(__name__)

ZIP_PATH = "/var/Data/AI_Assist.zip"

# ======================================
# DASH APP
# ======================================
app = dash.Dash(
    __name__,
    server=server,
    external_stylesheets=[dbc.themes.BOOTSTRAP]
)

def get_layout(SessionData):

    tabs = [

        # ======================================
        # TAB 1 — DOWNLOAD
        # ======================================
        dbc.Tab(
            label="Download Application",
            children=[
                html.H2("Download Application", className="mt-4"),

                dbc.Button(
                    "Download ZIP File",
                    id="download-btn",
                    color="success",
                    size="lg",
                    className="mt-3"
                ),

                dcc.Download(id="download-zip"),
            ]
        )
    ]

    # ======================================
    # ONLY RENDER AI TAB IF ADMIN
    # ======================================
    if SessionData.get("username") == "admin":

        tabs.append(
            dbc.Tab(
                label="AI Form Rebuilder",
                children=[
                    html.H3("AI Rebuild Student Form", className="mt-4"),

                    dcc.Upload(
                        id="upload-asp",
                        children=html.Div("Upload ASP HTML File (.txt)"),
                        style={
                            "width": "100%",
                            "height": "60px",
                            "lineHeight": "60px",
                            "borderWidth": "1px",
                            "borderStyle": "dashed",
                            "borderRadius": "5px",
                            "textAlign": "center",
                            "marginBottom": "20px"
                        },
                        multiple=False
                    ),

                    html.Hr(),

                    html.Pre(
                        id="output-code",
                        style={
                            "background": "#f4f4f4",
                            "padding": "15px",
                            "maxHeight": "650px",
                            "overflowY": "scroll"
                        }
                    )
                ]
            )
        )

    return dbc.Container([
        dbc.Tabs(tabs)
    ], fluid=True)
    

# ======================================
# CALLBACK FOR DOWNLOAD
# ======================================
def register_callbacks(app):
    @app.callback(
        Output("download-zip", "data"),
        Input("download-btn", "n_clicks"),
        prevent_initial_call=True
    )
    def trigger_download(n_clicks):
        if not os.path.exists(ZIP_PATH):
            return dash.no_update
    
        return dcc.send_file(
            ZIP_PATH,
            filename="AI_Assist.zip"
        )

    @app.callback(
        Output("output-code", "children"),
        Input("upload-asp", "contents"),
    )
    def rebuild_with_ai(contents):
    
        if not contents:
            return ""
    
        try:
            content_type, content_string = contents.split(",")
            asp_html = base64.b64decode(content_string).decode("utf-8")
        except Exception as e:
            return f"Error reading uploaded file: {e}"
    
        prompt = f"""
    You are a senior Python Dash developer.
    
    Given:
    
    1) The original Dash function:
    
    {ORIGINAL_FUNCTION}
    
    2) The ASP HTML form below:
    
    {asp_html}
    
    Rewrite the full Python function `def create_student_form(SessionData)` so that:
    
    - All labels exactly match the ASP labels
    - All dropdown options match ASP select options
    - Dropdown values match ASP value attributes
    - Preserve Dash layout structure (dbc.Row, dbc.Col, dcc.Dropdown)
    - Maintain clean formatting
    - Return only valid Python code
    - Do NOT add explanation
    - Do NOT add markdown
    - Output pure Python function only
    """
    
        try:
            response = client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {"role": "system", "content": "You are a professional code generator."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.1
            )
    
            return response.choices[0].message.content
    
        except Exception as e:
            return f"OpenAI API Error: {e}"



