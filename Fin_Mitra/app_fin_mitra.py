import dash
from flask import Flask, session
from dash import html, dcc, Input, Output, State
from datetime import datetime, timedelta
import plotly
import os

from dash import Dash, dcc, html, Input, Output
import dash_bootstrap_components as dbc
import hashlib

import importlib
import sys
import ChatBot
from ChatBot import get_chatbot_icon, get_chatbot_popup
from app_context import set_user_context, clear_user_context



# ---=================================================================================================== Import your modules ==============================================================================---

import csv
import os

def load_module_passwords():

    path = "/var/Data/admin/static_pass.csv"
    folder = os.path.dirname(path)

    # Default passwords
    default_passwords = {
        "/Forms": "accounts123",
        "/ctexposure": "admin123",
        "/montecarlo": "admin123",
        "/datarep": "teacher123",
        "/cfproj": "admin123",
        "/db": "accounts123",
        "/ledge": "accounts123",
        "/fs": "admin123",
        "/ailedge": "teacher123",
        "/delmod": "admin123",
        "/bnstatic": "admin123",
    	"/dashboard": "admin123",
    	"/": "admin123",
        "/enquiry_mgmt": "admin123",
    }

    # Ensure folder exists
    os.makedirs(folder, exist_ok=True)

    # If CSV does not exist → create it
    if not os.path.exists(path):

        with open(path, mode="w", newline="", encoding="utf-8") as f:

            writer = csv.writer(f)
            writer.writerow(["module", "password"])

            for module, password in default_passwords.items():
                writer.writerow([module, password])

        print("Created default password file:", path)

    # Load passwords
    passwords = {}

    with open(path, mode="r", newline="", encoding="utf-8") as f:

        reader = csv.DictReader(f)

        for row in reader:
            passwords[row["module"]] = row["password"]

    return passwords


def get_financial_year_dropdown():
    today = datetime.now()
    current_year = today.year

    # Determine current FY start year
    if today >= datetime(current_year, 4, 1):
        current_fy_start = current_year
    else:
        current_fy_start = current_year - 1

    # Generate FY20 to FY30
    all_years = list(range(20, 31))

    options = []
    for y in all_years:
        fy_label = f"FY{y}"
        fy_start_year = 2000 + y  # FY20 → 2020 (start year)

        # Disable if FY is in future
        disabled_flag = fy_start_year > (current_fy_start + 1)

        options.append({
            "label": fy_label,
            "value": fy_label,
            "disabled": disabled_flag
        })

    return html.Div(
        [
            html.Label(
                "Financial Year:",
                style={
                    "marginRight": "10px",
                    "fontWeight": "600",
                    "color": "white",  # fixed invalid "#white"
                    "fontSize": "14px"
                }
            ),
            dcc.Dropdown(
                id="financial-year-dropdown",
                options=options,
                value=f"FY27",
                clearable=False,
                style={
                    "width": "120px",
                    "fontSize": "13px",
                    "backgroundColor": "#2f4b7c",
                    "color": "white",
                    "borderRadius": "6px"
                }
            )
        ],
        style={
            "display": "flex",
            "alignItems": "center",
            "marginRight": "25px"
        }
    )


# import Forms, CT_Exposure_Dashboard, MonteCarlo_Simulator
import Login_Page
# # Try import modules; be tolerant if they don't exist
try:
    Forms = importlib.import_module("Forms")
except Exception as e:
    Forms = None
    print("Warning: could not import Forms:", e, file=sys.stderr)

try:
    CT_Exposure_Dashboard = importlib.import_module("CT_Exposure_Dashboard")
except Exception as e:
    CT_Exposure_Dashboard = None
    print("Warning: could not import CT_Exposure_Dashboard:", e, file=sys.stderr)

try:
    Day_Book = importlib.import_module("Day_Book")
except Exception as e:
    Day_Book = None
    print("Warning: could not import Day_Book:", e, file=sys.stderr)

try:
    View_Ledger = importlib.import_module("View_Ledger")
except Exception as e:
    View_Ledger = None
    print("Warning: could not import View_Ledger:", e, file=sys.stderr)

try:
    Bank_Name_Static = importlib.import_module("Bank_Name_Static")
except Exception as e:
    Bank_Name_Static = None
    print("Warning: could not import Bank_Name_Static:", e, file=sys.stderr)

try:
    Financial_Statement = importlib.import_module("Financial_Statement")
except Exception as e:
    Financial_Statement = None
    print("Warning: could not import Financial_Statement:", e, file=sys.stderr)

try:
    AI_Ledger_Converter = importlib.import_module("AI_Ledger_Converter")
except Exception as e:
    AI_Ledger_Converter = None
    print("Warning: could not import AI_Ledger_Converter:", e, file=sys.stderr)


try:
    Trend_Projection = importlib.import_module("Trend_Projection")
except Exception as e:
    Trend_Projection = None
    print("Warning: could not import Trend_Projection:", e, file=sys.stderr)
 
try:
    MonteCarlo_Simulator = importlib.import_module("MonteCarlo_Simulator")
except Exception as e:
    MonteCarlo_Simulator = None
    print("Warning: could not import MonteCarlo_Simulator:", e, file=sys.stderr)

try:
    Data_Representation = importlib.import_module("Data_Representation")
except Exception as e:
    Data_Representation = None
    print("Warning: could not import Data_Representation:", e, file=sys.stderr)

try:
    User_Management = importlib.import_module("User_Management")
except Exception as e:
    User_Management = None
    print("Warning: could not import User_Management:", e, file=sys.stderr)

try:
    Change_Password = importlib.import_module("Change_Password")
except Exception as e:
    Change_Password = None
    print("Warning: could not import Change_Password:", e, file=sys.stderr)

try:
    Home_Page = importlib.import_module("Home_Page")
except Exception as e:
    Home_Page = None
    print("Warning: could not import Home_Page:", e, file=sys.stderr)

try:
    Entry_Deletion = importlib.import_module("Entry_Deletion")
except Exception as e:
    Entry_Deletion = None
    print("Warning: could not import Entry_Deletion:", e, file=sys.stderr)


# Import authentication database
try:
    from auth_database import get_auth_db
except Exception as e:
    get_auth_db = None
    print("Warning: could not import auth_database:", e, file=sys.stderr)

try:
    Dashboard = importlib.import_module("Dashboard")
except Exception as e:
    Dashboard = None
    print("Warning: could not import Dashboard:", e, file=sys.stderr)

try:
    enquiry_mgmt = importlib.import_module("enquiry_mgmt")
except Exception as e:
    enquiry_mgmt = None
    print("Warning: could not import enquiry_mgmt:", e, file=sys.stderr)
    
        

# ---=================================================================================================== Create Flask server ==============================================================================---

server = Flask(__name__)
server.secret_key = "my_super_secret_key"
server.permanent_session_lifetime = timedelta(minutes=30)

# right after: server = Flask(__name__)
from api_routes import api
server.register_blueprint(api)
    
# ---=================================================================================================== Refresh session on every request (sliding expiration) =============================================================---

@server.before_request
def refresh_session():
    session.permanent = True

# ---=================================================================================================== Initialize app  ==============================================================================---
# Use a neutral bootstrap theme but we'll override visual styling with our inline CSS and custom CSS in index_string
external_stylesheets = [
    dbc.themes.BOOTSTRAP,
    "https://cdn.jsdelivr.net/npm/bootstrap-icons@1.11.1/font/bootstrap-icons.css"
]

app = dash.Dash(__name__, server=server, suppress_callback_exceptions=True, prevent_initial_callbacks=True, external_stylesheets = external_stylesheets)
app.title = "Sheep Fin-Mitra"


# ---================================= Register callbacks from modules ==============================================================================---


# --- Register callbacks from modules (safe) ---
def _safe_register(mod, name):
    if mod is None:
        print(f"Skipping {name}: import failed.")
        return
    if hasattr(mod, "apply_index_string"):
        try:
            mod.apply_index_string(app)
        except Exception as e:
            print(f"Warning: {name}.apply_index_string failed: {e}")
    if hasattr(mod, "register_callbacks"):
        try:
            mod.register_callbacks(app)
        except Exception as e:
            print(f"Warning: {name}.register_callbacks failed: {e}")

_safe_register(Home_Page, "Home_Page")
_safe_register(Forms, "Forms")
_safe_register(View_Ledger, "View_Ledger")
_safe_register(CT_Exposure_Dashboard, "CT_Exposure_Dashboard")
_safe_register(Day_Book, "Day_Book")
_safe_register(Financial_Statement, "Financial_Statement")
_safe_register(AI_Ledger_Converter, "AI_Ledger_Converter")
_safe_register(Trend_Projection, "Trend_Projection")
_safe_register(MonteCarlo_Simulator, "MonteCarlo_Simulator")
_safe_register(Data_Representation, "Data_Representation")
_safe_register(User_Management, "User_Management")
_safe_register(Change_Password, "Change_Password")
_safe_register(Bank_Name_Static, "Bank_Name_Static")
_safe_register(Entry_Deletion, "Entry_Deletion")
_safe_register(enquiry_mgmt, "enquiry_mgmt")


# ---=================================================================================================== Custom index (CSS overrides) ==============================================================================---

app.index_string = """
<!DOCTYPE html>
<html>
    <head>
        {%metas%}
        <title>{%title%}</title>
        {%favicon%}
        {%css%}
        <style>
            body { margin: 0; background-color: #FAFCFE; font-family: 'Segoe UI', Roboto, Arial, sans-serif; color: #243447; }

            
            .sidebar-btn {
                border-radius: 8px;
                font-size: 15px;
                font-weight: 500;
                color: #cfd8dc !important;
                background: transparent !important;
                border: none !important;
                text-align: left !important;
                transition: all 0.2s ease;
            }
            
            .sidebar-btn:hover {
                background-color: rgba(255,255,255,0.1) !important;
                color: #ffffff !important;
            }
            
            .sidebar-btn.active {
                background-color: #4CAF50 !important;
                color: white !important;
            }

            /* Header / top bar */
            .dash-header {
                background: linear-gradient(90deg, #1e2a44, #243b63);
                color: #ffffff !important;
                border-bottom: none;
            }
            
            
            /* Dropdown option hover */
            .dropdown-option:hover { background-color: #F1FFF1; }

            .logout-btn:hover {
                transform: scale(1.03);
                background: linear-gradient(135deg, #81C784, #a5f3fc);
                box-shadow: 0px 6px 12px rgba(56,142,60,0.25);
            }

            /* Make sure footer links are readable */
            .sheep-footer a { color: #ffffff !important; text-decoration: none; }

            /* small adjustments to card headers, tables, etc. */
            .card .card-header { background-color: #F8FFF8; color: #1B5E20; border-bottom: 1px solid #E6F4E6; }
            .table th { background-color: #F1FFF1; color: #1B5E20; }
            
        </style>
    </head>
    <body>
        {%app_entry%}
        <footer>
            {%config%}{%scripts%}{%renderer%}
        </footer>
    </body>
</html>
"""


MODULE_PASSWORDS = load_module_passwords()

MASTER_ADMIN_PASSWORD = "sheepmaster123"

def password_gate(pathname):
    return html.Div(
        style={"textAlign": "center", "marginTop": "120px"},
        children=[
            html.H3("Enter Module Password"),
            dcc.Input(id="module-password-input", type="password"),
            html.Button("Unlock", id="module-password-btn"),
            html.Div(id="module-password-error", style={"color":"red"})
        ]
    )



# ---=================================================================================================== App Layout ==============================================================================---

app.layout = html.Div([
    dcc.Location(id="url", refresh=False, pathname="/"),
    dcc.Store(id="session", storage_type="session"),  # stores login state
    dcc.Store(id="module-password-access", storage_type="session", data={}),
    dcc.Store(id="selected-financial-year", storage_type="session"),
    dcc.Store(id="logo-refresh-trigger"),  # Trigger to refresh logo when changed
    dcc.Interval(id="session-timeout-interval", interval=60000, n_intervals=0),  # Check every 60 seconds
    html.Div(id="page-container")
])

# ---=================================================================================================== Sidebar Helper ==============================================================================---



from flask import send_file

@server.route("/user-logo/<username>")
def serve_user_logo(username):
    logo_path = f"/var/Data/{username}/school_fees_logo.png"
    
    if os.path.exists(logo_path):
        return send_file(logo_path, mimetype="image/png")
    
    return "", 404  



def create_button(label, href, btn_id, default_active=False):
    base_class = "mb-2 w-100 sidebar-btn"
    if default_active:
        base_class += " active"

    return dbc.Button(
        label,
        href=href,
        id=btn_id,
        outline=False,
        size="md",
        className=base_class,
        style={
            "backgroundColor": "#E8F5E9",
            "color": "#1B5E20",
            "border": "1px solid #C8E6C9",
            "textAlign": "left"
        }
    )


# ---=================================================================================================== Sidebar Content ==============================================================================---

def get_sidebar(is_admin=False):
    buttons = [
        create_button("🏡 Home", "/", "btn_home"),
        create_button(
    html.Span([
        html.I(className="bi bi-bar-chart-line-fill me-2"),
        "Dashboard"
    ]),
    "/dashboard",
    "btn_dashboard"
),
        create_button("🏷️ Bank Name Static", "/bnstatic", "btn_boot_10"),
        create_button("🏷️ Enquiry", "/enquiry_mgmt", "btn_boot_13"),
        create_button("📝 Entry Hub", "/Forms", "btn_boot_1"),
        create_button("💵 Cash Book", "/ctexposure", "btn_boot_2"),
        create_button("💳 Bank Book", "/montecarlo", "btn_boot_3"),
        create_button("🎓 Student Log", "/datarep", "btn_boot_4"),
        create_button("🖊️ Teacher Log", "/cfproj", "btn_boot_5"),
        create_button("📆 Day Book", "/db", "btn_boot_6"),
        create_button("📑 View Ledger", "/ledge", "btn_boot_9"),
        create_button("📈 Financial Statement", "/fs", "btn_boot_7"),
        create_button("⚙️ AI Ledger Converter", "/ailedge", "btn_boot_8"),
        create_button("🗑️ Entry Edit & Deletion", "/delmod", "btn_boot_11"),
    ]

    if is_admin:
        buttons.append(
            create_button("👥 User Management", "/usermanagement", "btn_boot_12")
        )

    return html.Div(
        [
            html.Div(buttons)
        ],
        style={
            "width": "320px",
            "position": "fixed",
            "top": "70px",
            "left": "0",
            "bottom": "25px",
            "background": "linear-gradient(180deg, #1e2a44, #16213e)",
            "color": "#ffffff",
            "padding": "20px",
            "overflowY": "auto",
            "borderRight": "1px solid #E3EAF0",
            "boxShadow": "2px 0 8px rgba(76,175,80,0.06)",
        },
    )

# ---=================================================================================================== Header Content ==============================================================================---

def get_header(username="User", role="User", show_user_mgmt=False):
    logo_path = f"/var/Data/{username}/school_fees_logo.png"  # Ensure this path is correct and the image exists
    logo_exists=os.path.exists(logo_path)
    return html.Div(
        [
            html.Div(
                [
                    html.Img(src="/assets/logo.png", style={"height": "50px", "marginRight": "10px"}),
                    html.Span("Sheep.AI Advisory LLP", style={"fontSize": "22px", "fontWeight": "bold", "color": "white"})
                ],
                style={"display": "flex", "alignItems": "center"}
            ),
            # 🔹 CENTER LOGO (User Based)
            html.Div(
                [
                    html.Img(
                        id="school-dynamic-logo",
                        src=f"/user-logo/{username}",
                        style={
                            "height": "55px",
                            "objectFit": "contain"
                        }
                    )
                ] if logo_exists else [],
                style={
                    "position": "absolute",
                    "left": "50%",
                    "transform": "translateX(-50%)"
                } if logo_exists else {"display": "none"}
            ),
            html.Div(
                [
                    html.Div(
                        [
                            html.Span(
                                id="datetime-display",
                                style={
                                    "color": "#a5f3fc",
                                    "fontSize": "14px",
                                    "marginRight": "20px"
                                }
                            ),
                            dcc.Interval(id="datetime-interval", interval=1000, n_intervals=0)
                        ],
                        style={"display": "inline-block"}
                    ),

                    get_financial_year_dropdown(),
                    
                    # User Profile Dropdown
                    html.Div(
                        style={"position": "relative", "display": "inline-block"},
                        children=[
                            # User Profile Button
                            html.Div(
                                [
                                    html.Div([
                                        html.Div("👨🏻‍💻", style={"fontSize": "24px", "marginRight": "8px"}),
                                        html.Div([
                                            html.Div(username, style={"fontSize": "15px", "fontWeight": "600", "color": "white"}),
                                            html.Div(f"Role: {role}", style={"fontSize": "11px", "color": "#cbd5e1"}),
                                        ]),
                                        html.Div("▼", style={"fontSize": "12px", "marginLeft": "8px", "color": "#666"}),
                                    ], style={"display": "flex", "alignItems": "center", "padding": "8px 12px", "cursor": "pointer", "borderRadius": "6px", "transition": "background-color 0.2s"}),
                                ],
                                id="user-profile-btn"
                            ),
                            # Dropdown Menu
                            html.Div(
                                id="user-dropdown-menu",
                                style={
                                    "display": "none",
                                    "position": "absolute",
                                    "top": "50px",
                                    "right": "0",
                                    "backgroundColor": "white",
                                    "border": "1px solid #d9d9d9",
                                    "borderRadius": "8px",
                                    "boxShadow": "0 4px 12px rgba(0,0,0,0.12)",
                                    "minWidth": "220px",
                                    "zIndex": "3000"
                                },
                                children=[
                                    # Change Password
                                    html.Div(
                                        [
                                            html.Span("🔑", style={"marginRight": "10px", "fontSize": "16px"}),
                                            html.Span("Change Password", style={"fontSize": "14px", "color": "#333"})
                                        ],
                                        id="change-password-option",
                                        style={
                                            "padding": "12px 16px",
                                            "cursor": "pointer",
                                            "borderBottom": "1px solid #f0f0f0",
                                            "transition": "background-color 0.2s"
                                        },
                                        className="dropdown-option"
                                    ),
                                    # User Management (Admin only)
                                    html.Div(
                                        [
                                            html.Span("👥", style={"marginRight": "10px", "fontSize": "16px"}),
                                            html.Span("User Management", style={"fontSize": "14px", "color": "#333"})
                                        ],
                                        id="usermgmt-option",
                                        style={
                                            "padding": "12px 16px",
                                            "cursor": "pointer",
                                            "borderBottom": "1px solid #f0f0f0",
                                            "transition": "background-color 0.2s",
                                            "display": "block" if show_user_mgmt else "none"
                                        },
                                        className="dropdown-option"
                                    ),
                                    # Logout
                                    html.Div(
                                        [
                                            html.Span("🚪", style={"marginRight": "10px", "fontSize": "16px"}),
                                            html.Span("Logout", style={"fontSize": "14px", "color": "#e74c3c", "fontWeight": "600"})
                                        ],
                                        id="logout-option",
                                        n_clicks=0,
                                        style={
                                            "padding": "12px 16px",
                                            "cursor": "pointer",
                                            "transition": "background-color 0.2s"
                                        },
                                        className="dropdown-option logout-btn"
                                    ),
                                ]
                            )
                        ]
                    )
                ],
                style={"display": "flex", "alignItems": "center"}
            )
        ],
        className="dash-header",
        style={"width": "100%", "position": "fixed", "top": "0", "left": "0",
               "height": "70px", "backgroundColor": "#FFFFFF", "display": "flex",
               "alignItems": "center", "justifyContent": "space-between",
               "paddingLeft": "20px", "paddingRight": "20px", "borderBottom": "2px solid #4CAF50", "zIndex": "2000"}
    )




# ---=================================================================================================== footer Content ==============================================================================---

def get_footer():
    return html.Div(
        [
            html.Span("© 2025 Sheep.AI Advisory LLP | All Rights Reserved", style={"marginRight": "20px", "color": "#ffffff"}),
            html.A("Privacy Policy", href="#", style={"color": "#ffffff", "marginRight": "15px", "textDecoration": "none"}),
            html.A("Terms of Service", href="#", style={"color": "#ffffff", "textDecoration": "none"})
        ],
        className="sheep-footer",
        style={"width": "100%", "position": "fixed", "bottom": "0", "left": "0",
               "height": "40px", "backgroundColor": "#16213e", "color": "white",
               "display": "flex", "alignItems": "center", "justifyContent": "center",
               "fontSize": "13px", "borderTop": "1px solid #a5f3fc", "zIndex": "2000"}
    )

# ---=================================================================================================== Master Router ==============================================================================---


def get_password_gate():

    return dbc.Card(
        dbc.CardBody(
            [
                html.Div(
                    [
                        html.Div("🔐", style={"fontSize": "48px", "marginBottom": "10px"}),

                        html.H3(
                            "Module Locked",
                            style={
                                "fontWeight": "600",
                                "marginBottom": "5px",
                                "color": "#1e293b"
                            }
                        ),

                        html.P(
                            "Enter the access password to unlock this module.",
                            style={"color": "#64748b", "marginBottom": "25px"}
                        ),

                        dbc.Input(
                            id="module-password-input",
                            type="password",
                            placeholder="Enter module password",
                            style={
                                "maxWidth": "320px",
                                "margin": "auto",
                                "marginBottom": "15px"
                            }
                        ),

                        dbc.Button(
                            "Unlock Module",
                            id="module-password-btn",
                            color="success",
                            size="lg",
                            style={
                                "padding": "8px 25px",
                                "fontWeight": "600"
                            }
                        ),

                        html.Div(
                            id="module-password-error",
                            style={
                                "color": "#ef4444",
                                "marginTop": "10px",
                                "fontSize": "14px"
                            }
                        ),

                        html.Hr(style={"marginTop": "25px", "marginBottom": "15px"}),

                        html.P(
                            "Need access to this module?",
                            style={"color": "#475569"}
                        ),

                        dbc.Button(
                            "Purchase / Get Access",
                            href="https://www.sheepai.info",
                            target="_blank",
                            color="primary",
                            style={
                                "fontWeight": "600",
                                "padding": "8px 22px"
                            }
                        )
                    ],
                    style={"textAlign": "center"}
                )
            ]
        ),
        id="password-gate",
        style={
            "display": "none",
            "maxWidth": "420px",
            "margin": "120px auto",
            "borderRadius": "12px",
            "boxShadow": "0 10px 30px rgba(0,0,0,0.08)"
        }
    )



@app.callback(
    Output("page-container", "children"),
    Input("session", "data"),
    prevent_initial_call=False
)
def render_initial_page(session_data):
    # User not logged in → show login page
    if not session_data or not session_data.get("logged_in"):
        return Login_Page.get_login_layout()

    username = session_data.get("username", "User")
    role = session_data.get("role", "User")
    is_admin = (role == "Admin")

    # Load all module layouts ONCE when user logs in
    home_layout = Home_Page.get_layout(session_data) if Home_Page is not None else html.H3("Home Page module failed to load", style={"textAlign": "center", "marginTop": "50px", "color": "red"})
    enquiry_mgmt_layout = enquiry_mgmt.get_layout(session_data) if enquiry_mgmt is not None else html.H3("enquiry_mgmt module failed to load", style={"textAlign": "center", "marginTop": "50px", "color": "red"})
    Forms_layout = Forms.get_layout(session_data) if Forms is not None else html.H3("Forms module failed to load", style={"textAlign": "center", "marginTop": "50px", "color": "red"})
    ctexposure_layout = CT_Exposure_Dashboard.get_layout() if CT_Exposure_Dashboard is not None else html.H3("CT Exposure Dashboard module failed to load", style={"textAlign": "center", "marginTop": "50px", "color": "red"})
    montecarlo_layout = MonteCarlo_Simulator.get_layout(session_data) if MonteCarlo_Simulator is not None else html.H3("MonteCarlo Simulator module failed to load", style={"textAlign": "center", "marginTop": "50px", "color": "red"})
    cfproj_layout = Trend_Projection.get_layout() if Trend_Projection is not None else html.H3("Trend Projection module failed to load", style={"textAlign": "center", "marginTop": "50px", "color": "red"})
    datarep_layout = Data_Representation.get_layout(session_data) if Data_Representation is not None else html.H3("Data Representation module failed to load", style={"textAlign": "center", "marginTop": "50px", "color": "red"})
    usermgmt_layout = User_Management.get_layout() if (User_Management is not None and is_admin) else html.H3("Access Denied: Admin privileges required", style={"textAlign": "center", "marginTop": "50px", "color": "red"})
    changepwd_layout = Change_Password.get_layout() if Change_Password is not None else html.H3("Change Password module failed to load", style={"textAlign": "center", "marginTop": "50px", "color": "red"})
    Day_Book_layout = Day_Book.get_layout() if Day_Book is not None else html.H3("Day Book module failed to load", style={"textAlign": "center", "marginTop": "50px", "color": "red"})
    Financial_Statement_layout = Financial_Statement.get_layout() if Financial_Statement is not None else html.H3("Financial Statement module failed to load", style={"textAlign": "center", "marginTop": "50px", "color": "red"})
    AI_Ledger_Converter_layout = AI_Ledger_Converter.get_layout(session_data) if AI_Ledger_Converter is not None else html.H3("AI Ledger Converter module failed to load", style={"textAlign": "center", "marginTop": "50px", "color": "red"})
    View_Ledger_layout = View_Ledger.get_layout() if View_Ledger is not None else html.H3("View Ledger module failed to load", style={"textAlign": "center", "marginTop": "50px", "color": "red"})
    Bank_Name_Static_layout = Bank_Name_Static.get_layout(session_data) if Bank_Name_Static is not None else html.H3("Bank Name Static failed to load", style={"textAlign": "center", "marginTop": "50px", "color": "red"})
    Entry_Deletion_layout = Entry_Deletion.get_layout(session_data) if Entry_Deletion is not None else html.H3("Entry Deletion failed to load", style={"textAlign": "center", "marginTop": "50px", "color": "red"})
    current_year = datetime.now().year
    current_fy = f"FY{str(current_year)[-2:]}"
    dashboard_layout = Dashboard.get_layout(session_data, current_fy) if Dashboard is not None else html.H3("Dashboard failed to load", style={"textAlign": "center", "marginTop": "50px", "color": "red"})

   


    return html.Div([
        get_header(username, role, show_user_mgmt=is_admin),
        get_sidebar(is_admin=False),  # Remove User Management from sidebar by default
        # All modules loaded in DOM, visibility controlled by separate callback
        html.Div([
            get_password_gate(),
            html.Div(home_layout, id="home-content"),
            html.Div(dashboard_layout, id="dashboard-content"),
            html.Div(enquiry_mgmt_layout, id="enquiry_mgmt-content"),
            html.Div(Forms_layout, id="Forms-content"),
            html.Div(ctexposure_layout, id="ctexposure-content"),
            html.Div(montecarlo_layout, id="montecarlo-content"),
            html.Div(cfproj_layout, id="cfproj-content"),
            html.Div(datarep_layout, id="datarep-content"),
            html.Div(Day_Book_layout, id="Day_Book_layout-content"),
            html.Div(Financial_Statement_layout, id="Financial_Statement-content"),
            html.Div(View_Ledger_layout, id="View_Ledger-content"),
            html.Div(AI_Ledger_Converter_layout, id="AI_Ledger_Converter-content"),
            html.Div(usermgmt_layout, id="usermgmt-content"),
            html.Div(changepwd_layout, id="changepwd-content"),
            html.Div(Bank_Name_Static_layout, id="Bank_Name_Static-content"),
            html.Div(Entry_Deletion_layout, id="Entry_Deletion-content"),
        ], id="page-content", style={"marginLeft": "320px", "padding": "20px",
                        "background": "linear-gradient(180deg, #f0f4f8, #e2e8f0)",
                        "minHeight": "100vh", "marginTop": "70px", "marginBottom": "40px"}),
        get_footer(),
        get_chatbot_icon(),
        get_chatbot_popup(),
        html.Div(id="chatbot-scroll-dummy",style={"display":"none"})
    ])

# Control visibility of modules based on URL
@app.callback(
    [Output("password-gate","style"),
     Output("home-content", "style"),
     Output("enquiry_mgmt-content", "style"),
     Output("dashboard-content", "style"),
     Output("Forms-content", "style"),
     Output("ctexposure-content", "style"),
     Output("montecarlo-content", "style"),
     Output("cfproj-content", "style"),
     Output("datarep-content", "style"),
     Output("Day_Book_layout-content", "style"),
     Output("Financial_Statement-content", "style"),
     Output("View_Ledger-content", "style"),
     Output("AI_Ledger_Converter-content", "style"),
     Output("usermgmt-content", "style"),
     Output("changepwd-content", "style"),
     Output("Bank_Name_Static-content", "style"),
     Output("Entry_Deletion-content", "style")],
    Input("url", "pathname"),
    State("module-password-access", "data"),
    prevent_initial_call=False
)
def toggle_module_visibility(pathname, access):

    access = access or {}

    base_style = {"width": "100%"}
    hidden_style = {**base_style, "display": "none"}
    visible_style = {**base_style, "display": "block"}

    password_visible = {"display": "block", "textAlign": "center", "marginTop": "120px"}
    password_hidden = {"display": "none"}

    # 🔐 If module is locked show password gate

    if pathname in MODULE_PASSWORDS:
    
        expected = hashlib.sha256(MODULE_PASSWORDS[pathname].encode()).hexdigest()
    
        if access.get(pathname) != expected:

            return (
                password_visible,   # show password gate
                hidden_style, hidden_style, hidden_style, hidden_style,
                hidden_style, hidden_style, hidden_style, hidden_style,
                hidden_style, hidden_style, hidden_style, hidden_style,
                hidden_style, hidden_style, hidden_style, hidden_style
            )

    # Default to Home Page if pathname is None, empty, or "/"
    show_home = not pathname or pathname == "/" or pathname == ""
    show_enquiry_mgmt = pathname == "/enquiry_mgmt"
    show_dashboard = pathname == "/dashboard"
    show_Forms = pathname == "/Forms"
    show_ctexposure = pathname == "/ctexposure"
    show_montecarlo = pathname == "/montecarlo"
    show_cfproj = pathname == "/cfproj"
    show_datarep = pathname and pathname.startswith("/datarep")
    show_db = pathname == "/db"
    show_fs = pathname == "/fs"
    show_ledge = pathname == "/ledge"
    show_ailedge = pathname == "/ailedge"
    show_usermgmt = pathname == "/usermanagement"
    show_changepwd = pathname == "/changepassword"
    show_bnstatic = pathname == "/bnstatic"
    show_delmod = pathname == "/delmod"

    return (
        password_hidden,  # hide password gate
        visible_style if show_home else hidden_style,
        visible_style if show_enquiry_mgmt else hidden_style,
        visible_style if show_dashboard else hidden_style,
        visible_style if show_Forms else hidden_style,
        visible_style if show_ctexposure else hidden_style,
        visible_style if show_montecarlo else hidden_style,
        visible_style if show_cfproj else hidden_style,
        visible_style if show_datarep else hidden_style,
        visible_style if show_db else hidden_style,
        visible_style if show_fs else hidden_style,
        visible_style if show_ledge else hidden_style,
        visible_style if show_ailedge else hidden_style,
        visible_style if show_usermgmt else hidden_style,
        visible_style if show_changepwd else hidden_style,
        visible_style if show_bnstatic else hidden_style,
        visible_style if show_delmod else hidden_style,
    )


MASTER_ADMIN_PASSWORD = "sheepmaster123"


@app.callback(
    Output("module-password-access","data"),
    Output("module-password-error","children"),
    Input("module-password-btn","n_clicks"),
    State("module-password-input","value"),
    State("url","pathname"),
    State("module-password-access","data"),
    State("session","data"),
    prevent_initial_call=True
)
def unlock_module(n, password, pathname, store, session_data):

    import hashlib

    store = store or {}

    role = session_data.get("role") if session_data else None

    # ✅ Master password for Admin
    if role == "Admin" and password == MASTER_ADMIN_PASSWORD:

        for module in load_module_passwords():
            store[module] = hashlib.sha256(
                load_module_passwords()[module].encode()
            ).hexdigest()

        return store, ""

    elif role == "User" and password == MASTER_ADMIN_PASSWORD:
        
        for module in load_module_passwords():
            store[module] = hashlib.sha256(
                load_module_passwords()[module].encode()
            ).hexdigest()

        return store, ""

    MODULE_PASSWORDS = load_module_passwords()

    # ✅ Normal module password
    if pathname in MODULE_PASSWORDS:

        if password == MODULE_PASSWORDS[pathname]:

            store[pathname] = hashlib.sha256(password.encode()).hexdigest()

            return store, ""

    return store, "Incorrect password"


# -------------------- Login logic with database authentication --------------------
@app.callback(
    Output("session", "data"),
    Output("login-message", "children"),
    Output("url", "pathname"),
    Input("login-button", "n_clicks"),
    State("username", "value"),
    State("password", "value"),
    prevent_initial_call=True
)
def login(n_clicks, username, password):
    if not get_auth_db:
        # Fallback to hardcoded authentication if database module failed to load
        if username == "admin" and password == "sheep123":
            return {"logged_in": True, "username": username, "role": "Admin", "user_id": 1}, "", "/"
        return dash.no_update, "Invalid Username or Password", dash.no_update
    
    db = get_auth_db()
    
    # Validate inputs
    if not username or not password:
        return dash.no_update, "Please enter username and password", dash.no_update
    
    # Authenticate user
    success, user_data, message = db.authenticate_user(username, password)


    
    if success:
        try:
            from flask import request
            from app_context import set_user_context   # ✅ ADD THIS IMPORT
    
            user_ip = request.remote_addr if request else "unknown"
            user_agent = request.headers.get("User-Agent", "unknown") if request else "unknown"
    
            # --------------------------------------------------
            # LOG LOGIN
            # --------------------------------------------------
            session_id = db.log_login(
                user_data["user_id"],
                user_data["username"],
                user_ip,
                user_agent
            )
    
            # --------------------------------------------------
            # 🔑 CRITICAL: SET USER DATA CONTEXT
            # --------------------------------------------------
            set_user_context(user_data["username"])
    
            # --------------------------------------------------
            # SESSION PAYLOAD
            # --------------------------------------------------
            user_data["logged_in"] = True
            user_data["session_id"] = session_id
            user_data["login_time"] = datetime.now().isoformat()
    
            return user_data, "", "/"
    
        except Exception as e:
            print(f"Error during login logging: {e}")
    
            # Even on logging failure, still allow login
            from app_context import set_user_context
            set_user_context(user_data["username"])   # ✅ still set context
    
            user_data["logged_in"] = True
            return user_data, "", "/"
    
    else:
        # --------------------------------------------------
        # FAILED LOGIN
        # --------------------------------------------------
        try:
            from flask import request
            user_ip = request.remote_addr if request else "unknown"
            db.log_failed_login(username, user_ip, message)
        except Exception:
            pass
    
        return dash.no_update, message, dash.no_update

@app.callback(
    Output("session", "clear_data"),
    Input("logout-option", "n_clicks"),
    State("session", "data"),
    prevent_initial_call=True
)
def logout(n_clicks, session_data):
    if n_clicks and session_data:
        if get_auth_db and session_data.get("session_id"):
            db = get_auth_db()
            db.log_logout(session_data["session_id"])

        clear_user_context()   # 🔑 REQUIRED
        return True

    return dash.no_update


# -------------------- Session Timeout (30 minutes of inactivity) --------------------
@app.callback(
    Output("session", "clear_data", allow_duplicate=True),
    Input("session-timeout-interval", "n_intervals"),
    State("session", "data"),
    prevent_initial_call=True
)
def check_session_timeout(n_intervals, session_data):
    if not session_data or not session_data.get("logged_in"):
        return dash.no_update
    
    # Check if session has timed out (30 minutes = 1800 seconds)
    if session_data.get("login_time"):
        try:
            login_time = datetime.fromisoformat(session_data["login_time"])
            now = datetime.now()
            elapsed_seconds = (now - login_time).total_seconds()
            
            # Timeout after 30 minutes (1800 seconds)
            if elapsed_seconds > 1800:
                # Log automatic logout
                if get_auth_db and session_data.get("session_id"):
                    db = get_auth_db()
                    db.log_logout(session_data["session_id"])
                
                return True  # Clear session
        except Exception as e:
            print(f"Error checking session timeout: {e}")
    
    return dash.no_update

# -------------------- User Profile Dropdown Toggle --------------------
@app.callback(
    Output("user-dropdown-menu", "style"),
    Input("user-profile-btn", "n_clicks"),
    State("user-dropdown-menu", "style"),
    prevent_initial_call=True
)
def toggle_user_dropdown(n_clicks, current_style):
    # Defensive: if current_style missing keys, initialize
    if not isinstance(current_style, dict):
        current_style = {"display": "none"}
    if current_style.get("display") == "none":
        # Show dropdown
        return {
            **current_style,
            "display": "block"
        }
    else:
        # Hide dropdown
        return {
            **current_style,
            "display": "none"
        }

# -------------------- Dropdown Menu Options --------------------
@app.callback(
    Output("url", "pathname", allow_duplicate=True),
    Output("user-dropdown-menu", "style", allow_duplicate=True),
    Input("change-password-option", "n_clicks"),
    Input("usermgmt-option", "n_clicks"),
    State("user-dropdown-menu", "style"),
    prevent_initial_call=True
)
def handle_dropdown_navigation(change_pwd_clicks, usermgmt_clicks, menu_style):
    ctx = dash.callback_context
    if not ctx.triggered:
        return dash.no_update, dash.no_update
    
    triggered_id = ctx.triggered[0]["prop_id"].split(".")[0]
    
    # Only process if there's an actual click (not initialization)
    if triggered_id == "change-password-option" and change_pwd_clicks and change_pwd_clicks > 0:
        hidden_menu = {**(menu_style or {}), "display": "none"}
        return "/changepassword", hidden_menu
    elif triggered_id == "usermgmt-option" and usermgmt_clicks and usermgmt_clicks > 0:
        hidden_menu = {**(menu_style or {}), "display": "none"}
        return "/usermanagement", hidden_menu
    
    return dash.no_update, dash.no_update

# -------------------- Date & Time --------------------
@app.callback(
    Output("datetime-display", "children"),
    Input("datetime-interval", "n_intervals")
)
def update_datetime(n):
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


# ---=================================================================================================== FULL Sidebar Active Button Mapping ==============================================================================---

@app.callback(
    [
        Output("btn_home", "className"),        # 0
        Output("btn_dashboard", "className"),   # 1
        Output("btn_boot_1", "className"),      # 2
        Output("btn_boot_2", "className"),      # 3
        Output("btn_boot_3", "className"),      # 4
        Output("btn_boot_4", "className"),      # 5
        Output("btn_boot_5", "className"),      # 6
        Output("btn_boot_6", "className"),      # 7
        Output("btn_boot_7", "className"),      # 8
        Output("btn_boot_8", "className"),      # 9
        Output("btn_boot_9", "className"),      # 10
        Output("btn_boot_10", "className"),     # 11
        Output("btn_boot_11", "className"),     # 12
        Output("btn_boot_13", "className"),     # 13
    ],
    Input("url", "pathname"),
)
def update_active(pathname):
    base = "mb-2 w-100 sidebar-btn"
    active = base + " active"

    # 🔥 FIX: length 14 karo
    classes = [base] * 14

    mapping = {
        "/dashboard": 1,
        "/Forms": 2,
        "/ctexposure": 3,
        "/montecarlo": 4,
        "/datarep": 5,
        "/cfproj": 6,
        "/db": 7,
        "/fs": 8,
        "/ailedge": 9,
        "/ledge": 10,
        "/bnstatic": 11,
        "/delmod": 12,
        "/enquiry_mgmt": 13,
    }

    if not pathname or pathname == "/" or pathname == "":
        classes[0] = active
    elif pathname and pathname.startswith("/datarep"):
        classes[5] = active
    elif pathname in mapping:
        classes[mapping[pathname]] = active

    return classes

@app.callback(
    Output("selected-financial-year", "data"),
    Input("financial-year-dropdown", "value"),
    prevent_initial_call=False
)
def update_selected_fy(selected_fy):
    return selected_fy

@app.callback(
    Output("dashboard-content", "children"),
    Input("selected-financial-year", "data"),
    State("session", "data"),
    prevent_initial_call=False
)
def refresh_dashboard(selected_fy, session_data):

    if not session_data or not session_data.get("logged_in"):
        return dash.no_update

    return Dashboard.get_layout(session_data, selected_fy)  

@app.callback(
    Output("financial-overview-graph", "figure"),
    Input("fee-view-type", "value"),
    Input("selected-financial-year", "data"),
    State("session", "data"),
    prevent_initial_call=True
)
def update_financial_chart(view_type, selected_fy, session_data):

    if not session_data or not session_data.get("logged_in"):
        return dash.no_update

    import plotly.graph_objects as go

    username = session_data["username"]

    start_date, end_date = Dashboard.get_fy_date_range(selected_fy)

    months, fees_data = Dashboard.get_monthly_fee_data(
        username,
        start_date,
        end_date,
        view_type
    )

    fig = go.Figure()

    fig.add_trace(go.Bar(
        x=months,
        y=fees_data,
        marker=dict(color="rgba(59,130,246,0.7)"),
        width=0.5
    ))

    fig.add_trace(go.Scatter(
        x=months,
        y=fees_data,
        mode="lines+markers",
        line=dict(color="#10b981", width=3),
        marker=dict(size=6)
    ))

    fig.update_layout(
        margin=dict(l=20, r=20, t=10, b=10),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        xaxis=dict(showgrid=False),
        yaxis=dict(showgrid=True, tickprefix="₹"),
        showlegend=False
    )

    return fig



@app.callback(
    Output("page-container", "children", allow_duplicate=True),
    Input("logo-refresh-trigger", "data"),
    State("session", "data"),
    prevent_initial_call=True
)
def refresh_header_on_logo_upload(_, session_data):

    if not session_data or not session_data.get("logged_in"):
        raise dash.exceptions.PreventUpdate

    username = session_data.get("username", "User")
    role = session_data.get("role", "User")
    is_admin = (role == "Admin")

    # Rebuild entire layout
    return render_initial_page(session_data)






app.clientside_callback(
    """
    function(children) {
        const el = document.getElementById("chatbot-scroll-container");
        if (el) {
            setTimeout(() => {
                el.scrollTop = el.scrollHeight;
            }, 50);
        }
        return "";
    }
    """,
    Output("chatbot-scroll-dummy", "children"),
    Input("chatbot-messages", "children"),
)

# -------------------- Admin button active state (conditional) --------------------
# Note: This callback only fires if btn_boot_6 exists (Admin users only)
# The error is caught by suppress_callback_exceptions=True in app init

# ---=================================================================================================== App hosting Port ==============================================================================---

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=8060, debug=True)
