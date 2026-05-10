"""
Change Password Page for KPMG Application
Allows users to change their password
"""

from dash import html, dcc, Input, Output, State
import dash

# KPMG Colors
KPMG_BLUE = "#2E8B57"
WHITE = "#FFFFFF"


def get_layout():
    """Return the change password layout"""
    return html.Div(style={
        "backgroundColor": WHITE,
        "padding": "40px 20px",
        "fontFamily": "Segoe UI, Arial, sans-serif",
        "display": "flex",
        "justifyContent": "center",
        "alignItems": "center",
        "minHeight": "80vh"
    }, children=[
        # Change Password Card
        html.Div(className="card-container", style={"maxWidth": "500px", "width": "100%"}, children=[
            html.Div([
                html.Div("🔑 Change Password", style={"color": KPMG_BLUE, "fontSize": "24px", "fontWeight": "700", "marginBottom": "10px", "textAlign": "center"}),
                html.Div("Update your account password securely", style={"color": "#666", "fontSize": "13px", "marginBottom": "30px", "textAlign": "center", "fontWeight": "500"}),
            ]),
            
            # Current Password
            html.Div([
                html.Label("Current Password *", style={"fontSize": "12px", "color": "#333", "fontWeight": "700", "fontFamily": "Arial, Helvetica, sans-serif", "marginBottom": "6px", "display": "block"}),
                dcc.Input(
                    id="current-password",
                    type="password",
                    placeholder="Enter your current password",
                    style={
                        "width": "100%",
                        "padding": "12px 14px",
                        "border": "1.5px solid #d4dce6",
                        "borderRadius": "6px",
                        "fontSize": "14px",
                        "marginBottom": "5px"
                    }
                ),
                html.Div("Required for verification", style={"fontSize": "11px", "color": "#999", "marginBottom": "20px"}),
            ]),
            
            # New Password
            html.Div([
                html.Label("New Password *", style={"fontSize": "12px", "color": "#333", "fontWeight": "700", "fontFamily": "Arial, Helvetica, sans-serif", "marginBottom": "6px", "display": "block"}),
                dcc.Input(
                    id="new-password",
                    type="password",
                    placeholder="Enter new password",
                    style={
                        "width": "100%",
                        "padding": "12px 14px",
                        "border": "1.5px solid #d4dce6",
                        "borderRadius": "6px",
                        "fontSize": "14px",
                        "marginBottom": "5px"
                    }
                ),
                html.Div("Minimum 6 characters, will be encrypted", style={"fontSize": "11px", "color": "#999", "marginBottom": "20px"}),
            ]),
            
            # Confirm New Password
            html.Div([
                html.Label("Confirm New Password *", style={"fontSize": "12px", "color": "#333", "fontWeight": "700", "fontFamily": "Arial, Helvetica, sans-serif", "marginBottom": "6px", "display": "block"}),
                dcc.Input(
                    id="confirm-password",
                    type="password",
                    placeholder="Re-enter new password",
                    style={
                        "width": "100%",
                        "padding": "12px 14px",
                        "border": "1.5px solid #d4dce6",
                        "borderRadius": "6px",
                        "fontSize": "14px",
                        "marginBottom": "5px"
                    }
                ),
                html.Div("Must match new password", style={"fontSize": "11px", "color": "#999", "marginBottom": "25px"}),
            ]),
            
            # Security info
            html.Div(style={
                "backgroundColor": "#f0f7ff",
                "border": "1px solid #88B5E6",
                "borderRadius": "6px",
                "padding": "12px",
                "marginBottom": "25px"
            }, children=[
                html.Div("🔒 Password Security", style={"fontSize": "12px", "fontWeight": "700", "color": KPMG_BLUE, "marginBottom": "8px"}),
                html.Ul([
                    html.Li("Your password will be encrypted using bcrypt", style={"fontSize": "11px", "color": "#666", "marginBottom": "3px"}),
                    html.Li("Recommended: Use at least 8 characters", style={"fontSize": "11px", "color": "#666", "marginBottom": "3px"}),
                    html.Li("Include letters, numbers, and symbols", style={"fontSize": "11px", "color": "#666"}),
                ], style={"margin": "0", "paddingLeft": "20px"}),
            ]),
            
            # Change password button and message
            html.Div([
                html.Div(id="change-password-message", style={"marginBottom": "15px", "fontSize": "13px", "fontWeight": "600", "textAlign": "center"}),
                html.Button(
                    "🔑 Change Password",
                    id="change-password-btn",
                    n_clicks=0,
                    className="custom-button custom-button-upload",
                    style={"width": "100%", "padding": "12px", "fontSize": "15px"}
                ),
            ]),
        ]),
    ])


def register_callbacks(app):
    """Register callbacks for change password"""
    from auth_database import get_auth_db
    
    @app.callback(
        Output("change-password-message", "children"),
        Output("current-password", "value"),
        Output("new-password", "value"),
        Output("confirm-password", "value"),
        Input("change-password-btn", "n_clicks"),
        State("current-password", "value"),
        State("new-password", "value"),
        State("confirm-password", "value"),
        State("session", "data"),
        prevent_initial_call=True
    )
    def change_user_password(n_clicks, current_pwd, new_pwd, confirm_pwd, session_data):
        if n_clicks == 0:
            return "", "", "", ""
        
        # Validation
        if not current_pwd or not new_pwd or not confirm_pwd:
            return html.Div("All fields are required", style={"color": "red"}), current_pwd, new_pwd, confirm_pwd
        
        if new_pwd != confirm_pwd:
            return html.Div("New passwords do not match", style={"color": "red"}), current_pwd, "", ""
        
        if len(new_pwd) < 6:
            return html.Div("New password must be at least 6 characters", style={"color": "red"}), current_pwd, "", ""
        
        if not session_data or not session_data.get("user_id"):
            return html.Div("Session expired. Please login again.", style={"color": "red"}), "", "", ""
        
        # Verify current password
        db = get_auth_db()
        username = session_data.get("username")
        success, user_data, msg = db.authenticate_user(username, current_pwd)
        
        if not success:
            return html.Div("Current password is incorrect", style={"color": "red"}), "", new_pwd, confirm_pwd
        
        # Change password
        user_id = session_data.get("user_id")
        success, message = db.change_password(user_id, new_pwd)
        
        if success:
            return html.Div("✓ Password changed successfully", style={"color": "green"}), "", "", ""
        else:
            return html.Div(message, style={"color": "red"}), current_pwd, "", ""

