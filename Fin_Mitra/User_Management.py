"""
User Management Page for KPMG Application
Admin-only page for creating and managing users
"""

from dash import html, dcc, dash_table, Input, Output, State
import dash
import pandas as pd

# KPMG Colors
KPMG_BLUE = "#2E8B57"
KPMG_LIGHT_BLUE = "#A9DFBF"
WHITE = "#FFFFFF"
CARD_BORDER = "#D5F5E3"


def get_layout():
    """Return the user management layout"""
    return html.Div(style={
        "backgroundColor": WHITE,
        "padding": "20px",
        "fontFamily": "Segoe UI, Arial, sans-serif"
    }, children=[
        # Header
        html.Div([
            html.H2("User Management", style={"color": KPMG_BLUE, "margin": "0", "textAlign": "center", "fontWeight": "700"}),
            html.Div("Create and manage user accounts for the FinMitra platform", style={"color": "#555", "textAlign": "center"}),
        ], style={"marginBottom": "35px"}),
        
        html.Div(style={"display": "flex", "gap": "20px", "maxWidth": "1400px", "margin": "0 auto"}, children=[
            # Left Column: Create User Card
            html.Div(className="card-container", style={"flex": "1", "maxWidth": "500px"}, children=[
                html.Div([
                    html.Div("➕ Create New User", style={"color": KPMG_BLUE, "fontSize": "20px", "fontWeight": "700", "marginBottom": "25px"}),
                    html.Div("Add a new user account to the system", style={"color": "#666", "fontSize": "13px", "marginBottom": "20px", "fontWeight": "500"}),
                ]),
            
                # Username
                html.Div([
                    html.Label("Username *", style={"fontSize": "12px", "color": "#333", "fontWeight": "700", "fontFamily": "Arial, Helvetica, sans-serif", "marginBottom": "6px", "display": "block"}),
                    dcc.Input(
                        id="create-username",
                        type="text",
                        placeholder="e.g., john.doe",
                        style={
                            "width": "100%",
                            "padding": "12px 14px",
                            "border": "1.5px solid #d4dce6",
                            "borderRadius": "6px",
                            "fontSize": "14px",
                            "marginBottom": "5px"
                        }
                    ),
                    html.Div("Must be unique", style={"fontSize": "11px", "color": "#999", "marginBottom": "15px"}),
                ]),
                
                # Email
                html.Div([
                    html.Label("Email Address *", style={"fontSize": "12px", "color": "#333", "fontWeight": "700", "fontFamily": "Arial, Helvetica, sans-serif", "marginBottom": "6px", "display": "block"}),
                    dcc.Input(
                        id="create-email",
                        type="email",
                        placeholder="e.g., john.doe@sheepai.info",
                        style={
                            "width": "100%",
                            "padding": "12px 14px",
                            "border": "1.5px solid #d4dce6",
                            "borderRadius": "6px",
                            "fontSize": "14px",
                            "marginBottom": "5px"
                        }
                    ),
                    html.Div("Must be unique and valid", style={"fontSize": "11px", "color": "#999", "marginBottom": "15px"}),
                ]),
                
                # Password
                html.Div([
                    html.Label("Password *", style={"fontSize": "12px", "color": "#333", "fontWeight": "700", "fontFamily": "Arial, Helvetica, sans-serif", "marginBottom": "6px", "display": "block"}),
                    dcc.Input(
                        id="create-password",
                        type="password",
                        placeholder="Enter secure password",
                        style={
                            "width": "100%",
                            "padding": "12px 14px",
                            "border": "1.5px solid #d4dce6",
                            "borderRadius": "6px",
                            "fontSize": "14px",
                            "marginBottom": "5px"
                        }
                    ),
                    html.Div("Minimum 6 characters, will be encrypted", style={"fontSize": "11px", "color": "#999", "marginBottom": "15px"}),
                ]),
                
                # Re-enter Password
                html.Div([
                    html.Label("Re-enter Password *", style={"fontSize": "12px", "color": "#333", "fontWeight": "700", "fontFamily": "Arial, Helvetica, sans-serif", "marginBottom": "6px", "display": "block"}),
                    dcc.Input(
                        id="create-password-confirm",
                        type="password",
                        placeholder="Re-enter the same password",
                        style={
                            "width": "100%",
                            "padding": "12px 14px",
                            "border": "1.5px solid #d4dce6",
                            "borderRadius": "6px",
                            "fontSize": "14px",
                            "marginBottom": "5px"
                        }
                    ),
                    html.Div("Must match the password above", style={"fontSize": "11px", "color": "#999", "marginBottom": "15px"}),
                ]),
                
                # Role
                html.Div([
                    html.Label("User Role *", style={"fontSize": "12px", "color": "#333", "fontWeight": "700", "fontFamily": "Arial, Helvetica, sans-serif", "marginBottom": "6px", "display": "block"}),
                    dcc.Dropdown(
                        id="create-role",
                        options=[
                            {"label": "👤 User - Dashboard Access Only", "value": "User"},
                            {"label": "🧩 Sub-Admin - Assigned Users + Consolidation", "value": "SubAdmin"},
                            {"label": "👑 Admin - Full Access + User Management", "value": "Admin"}
                        ],
                        value="User",
                        style={"marginBottom": "5px"}
                    ),
                    html.Div("Admin can create/manage users", style={"fontSize": "11px", "color": "#999", "marginBottom": "20px"}),
                ]),
            
                # Security info
                html.Div(style={
                    "backgroundColor": "#f0f7ff",
                    "border": f"1px solid {KPMG_LIGHT_BLUE}",
                    "borderRadius": "6px",
                    "padding": "12px",
                    "marginBottom": "20px"
                }, children=[
                    html.Div("🔒 Security Information", style={"fontSize": "12px", "fontWeight": "700", "color": KPMG_BLUE, "marginBottom": "8px"}),
                    html.Ul([
                        html.Li("Passwords are encrypted using bcrypt", style={"fontSize": "11px", "color": "#666", "marginBottom": "3px"}),
                        html.Li("Each password has a unique salt", style={"fontSize": "11px", "color": "#666", "marginBottom": "3px"}),
                        html.Li("Plain text passwords are never stored", style={"fontSize": "11px", "color": "#666"}),
                    ], style={"margin": "0", "paddingLeft": "20px"}),
                ]),
            
                # Create button and message
                html.Div([
                    html.Button(
                        "➕ Create User",
                        id="create-user-btn",
                        n_clicks=0,
                        className="custom-button custom-button-upload",
                        style={"width": "100%", "marginTop": "10px", "padding": "12px", "fontSize": "15px"}
                    ),
                    html.Div(id="create-user-message", style={"marginTop": "15px", "fontSize": "13px", "fontWeight": "600", "textAlign": "center"}),
                ]),
            ]),
            
            # Right Column: Users List Card
            html.Div(className="card-container", style={"flex": "2"}, children=[
                html.Div(style={"display": "flex", "justifyContent": "space-between", "alignItems": "center", "marginBottom": "15px"}, children=[
                    html.Div([
                        html.Div("👥 Users", style={"color": KPMG_BLUE, "fontSize": "20px", "fontWeight": "700"}),
                        html.Div(id="user-count", style={"fontSize": "12px", "color": "#666", "marginTop": "4px"}),
                    ]),
                    html.Div([
                        html.Button(
                            "▼ Show Users",
                            id="toggle-users-btn",
                            n_clicks=0,
                            className="custom-button custom-button-reload",
                            style={"marginRight": "10px"}
                        ),
                        html.Button(
                            "🔄 Refresh",
                            id="refresh-users-btn",
                            n_clicks=0,
                            className="custom-button custom-button-reload"
                        ),
                    ], style={"display": "flex"}),
                ]),
            
            html.Div(id="users-table-container", style={"display": "none"}, children=[
                dash_table.DataTable(
                id="users-table",
                columns=[
                    {"name": "User ID", "id": "user_id", "editable": False},
                    {"name": "Username", "id": "Username", "editable": False},
                    {"name": "Email", "id": "Email", "editable": False},
                    {"name": "Role", "id": "Role", "editable": False},
                    {"name": "Created At", "id": "Created_At", "editable": False},
                    {"name": "Status", "id": "Is_Active", "editable": False},
                    {"name": "Actions", "id": "Actions", "presentation": "markdown"},
                ],
                data=[],
                page_size=15,
                style_table={"overflowX": "auto", "backgroundColor": WHITE, "border": f"1px solid {CARD_BORDER}"},
                style_header={
                    "backgroundColor": "#1e49e2",
                    "color": "white",
                    "fontWeight": "700",
                    "borderBottom": "2px solid #1e49e2",
                    "textAlign": "left",
                    "fontSize": "15px",
                    "padding": "10px",
                },
                style_cell={
                    "backgroundColor": WHITE,
                    "color": "#666",
                    "fontWeight": "600",
                    "textAlign": "left",
                    "fontSize": "13px",
                    "padding": "8px 10px",
                    "border": f"1px solid {CARD_BORDER}",
                },
                style_data_conditional=[
                    {
                        "if": {"column_id": "Is_Active", "filter_query": "{Is_Active} contains 'Active'"},
                        "color": "#28a745",
                        "fontWeight": "700"
                    },
                    {
                        "if": {"column_id": "Is_Active", "filter_query": "{Is_Active} contains 'Inactive'"},
                        "color": "#dc3545",
                        "fontWeight": "700"
                    },
                ],
            ),
            html.Div(id="user-action-message", style={"marginTop": "15px", "fontSize": "13px", "fontWeight": "600"}),
            
            # Save Changes Button (shown when user makes changes)
            html.Div(id="save-button-container", style={"marginTop": "20px", "display": "none"}, children=[
                html.Button(
                    "💾 Save Changes",
                    id="save-user-changes-btn",
                    className="custom-button",
                    style={
                        "backgroundColor": "#28a745",
                        "color": "white",
                        "padding": "12px 24px",
                        "fontSize": "14px",
                        "fontWeight": "600",
                        "border": "none",
                        "borderRadius": "6px",
                        "cursor": "pointer",
                        "boxShadow": "0 2px 4px rgba(0,0,0,0.1)"
                    }
                ),
                html.Span(id="pending-changes-count", style={"marginLeft": "15px", "fontSize": "13px", "color": "#666"}),
            ]),
            
            # Hidden storage for pending changes
            dcc.Store(id="pending-user-changes", data=[]),
            ]),
        ]),
        ]),

        #############
        # --------------------------------------------------
        # SUB-ADMIN USER MAPPING (ADMIN ONLY)
        # --------------------------------------------------
        html.Div(className="card-container", style={
            "maxWidth": "1400px",
            "margin": "30px auto 0"
        }, children=[
        
            html.Div("🔗 Sub-Admin User Mapping", style={
                "color": KPMG_BLUE,
                "fontSize": "20px",
                "fontWeight": "700",
                "marginBottom": "15px"
            }),
        
            html.Div(style={"display": "flex", "gap": "20px"}, children=[
        
                # SubAdmin dropdown
                html.Div(style={"flex": "1"}, children=[
                    html.Label("Select Sub-Admin"),
                    dcc.Dropdown(
                        id="map-subadmin",
                        placeholder="Choose Sub-Admin"
                    )
                ]),
        
                # Users dropdown
                html.Div(style={"flex": "2"}, children=[
                    html.Label("Select Users"),
                    dcc.Dropdown(
                        id="map-users",
                        multi=True,
                        placeholder="Choose Users"
                    )
                ]),
        
                # Action button
                html.Div(style={"flex": "0.5", "marginTop": "22px"}, children=[
                    html.Button(
                        "Attach Users",
                        id="map-users-btn",
                        className="custom-button",
                        style={"width": "100%"}
                    )
                ])
            ]),
        
            html.Div(id="mapping-message", style={
                "marginTop": "15px",
                "fontWeight": "600"
            })
        ]),

        #############
        
        # Access Logs Card - Full Width
        html.Div(className="card-container", style={"maxWidth": "1400px", "margin": "30px auto 0"}, children=[
            html.Div(style={"display": "flex", "justifyContent": "space-between", "alignItems": "center", "marginBottom": "15px"}, children=[
                html.Div([
                    html.Div("📊 Recent Access Logs", style={"color": KPMG_BLUE, "fontSize": "20px", "fontWeight": "700"}),
                    html.Div("Last 50 login sessions", style={"fontSize": "12px", "color": "#666", "marginTop": "4px"}),
                ]),
                html.Div([
                    html.Button(
                        "▼ Show Access Logs",
                        id="toggle-logs-btn",
                        n_clicks=0,
                        className="custom-button custom-button-reload",
                        style={"marginRight": "10px"}
                    ),
                    html.Button(
                        "🔄 Refresh",
                        id="refresh-logs-btn",
                        n_clicks=0,
                        className="custom-button custom-button-reload"
                    ),
                ], style={"display": "flex"}),
            ]),
            
            html.Div(id="logs-table-container", style={"display": "none"}, children=[
                dash_table.DataTable(
                id="access-logs-table",
                columns=[
                    {"name": "Session ID", "id": "Session_ID"},
                    {"name": "Username", "id": "Username"},
                    {"name": "IP Address", "id": "User_IP"},
                    {"name": "Login Time", "id": "Login_Timestamp"},
                    {"name": "Logout Time", "id": "Logout_Timestamp"},
                    {"name": "Duration (sec)", "id": "Access_Duration"},
                ],
                data=[],
                page_size=15,
                style_table={"overflowX": "auto", "backgroundColor": WHITE, "border": f"1px solid {CARD_BORDER}"},
                style_header={
                    "backgroundColor": "#1e49e2",
                    "color": "white",
                    "fontWeight": "700",
                    "borderBottom": "2px solid #1e49e2",
                    "textAlign": "left",
                    "fontSize": "15px",
                    "padding": "10px",
                },
                style_cell={
                    "backgroundColor": WHITE,
                    "color": "#666",
                    "fontWeight": "600",
                    "textAlign": "left",
                    "fontSize": "13px",
                    "padding": "8px 10px",
                    "border": f"1px solid {CARD_BORDER}",
                },
            ),
            ]),
        ]),
    ])


def register_callbacks(app):
    from auth_database import get_auth_db
    from flask import session
    import pandas as pd
    import dash

    # =====================================================
    # TOGGLE USERS TABLE
    # =====================================================
    @app.callback(
        Output("users-table-container", "style"),
        Output("toggle-users-btn", "children"),
        Input("toggle-users-btn", "n_clicks"),
        prevent_initial_call=False
    )
    def toggle_users_table(n_clicks):
        if not n_clicks or n_clicks % 2 == 0:
            return {"display": "none"}, "▼ Show Users"
        return {"display": "block"}, "▲ Hide Users"

    # =====================================================
    # TOGGLE ACCESS LOGS
    # =====================================================
    @app.callback(
        Output("logs-table-container", "style"),
        Output("toggle-logs-btn", "children"),
        Input("toggle-logs-btn", "n_clicks"),
        prevent_initial_call=False
    )
    def toggle_logs_table(n_clicks):
        if not n_clicks or n_clicks % 2 == 0:
            return {"display": "none"}, "▼ Show Access Logs"
        return {"display": "block"}, "▲ Hide Access Logs"

    # =====================================================
    # CREATE NEW USER
    # =====================================================
    @app.callback(
        Output("create-user-message", "children"),
        Output("create-username", "value"),
        Output("create-email", "value"),
        Output("create-password", "value"),
        Output("create-password-confirm", "value"),
        Output("create-role", "value"),
        Input("create-user-btn", "n_clicks"),
        State("create-username", "value"),
        State("create-email", "value"),
        State("create-password", "value"),
        State("create-password-confirm", "value"),
        State("create-role", "value"),
        prevent_initial_call=True
    )
    def create_new_user(n, username, email, password, confirm, role):

        if not username or not email or not password or not confirm:
            return html.Div("❌ All fields are required", style={"color": "red"}), username, email, "", "", role

        if password != confirm:
            return html.Div("❌ Passwords do not match", style={"color": "red"}), username, email, "", "", role

        if len(password) < 6:
            return html.Div("❌ Password too short", style={"color": "red"}), username, email, "", "", role

        db = get_auth_db()
        success, msg = db.create_user(username, password, email, role)

        if success:
            admin_id = session.get("user_id", 0)
            admin_name = session.get("username", "system")

            new_user = db.get_user_by_username(username)
            if new_user:
                db.log_audit_trail(
                    target_user_id=new_user["user_id"],
                    target_username=username,
                    action="CREATED",
                    performed_by_user_id=admin_id,
                    performed_by_username=admin_name,
                    new_value=f"Role={role}, Email={email}"
                )

            return html.Div(f"✓ {msg}", style={"color": "green"}), "", "", "", "", "User"

        return html.Div(f"❌ {msg}", style={"color": "red"}), username, email, "", "", role

    # =====================================================
    # REFRESH USERS TABLE
    # =====================================================
    @app.callback(
        Output("users-table", "data"),
        Output("user-count", "children"),
        Input("refresh-users-btn", "n_clicks"),
        Input("create-user-btn", "n_clicks"),
        Input("users-table", "active_cell"),
        prevent_initial_call=False
    )
    def refresh_users_table(refresh_clicks, create_clicks, active_cell):
    
        # ✅ ALWAYS INITIALIZE DB
        db = get_auth_db()
    
        users = db.get_all_users()
    
        # ✅ Normalize primary key for UI
        for u in users:
            u["user_id"] = u["User_ID"]
    
        active_count = sum(1 for u in users if u["Is_Active"])
        total_count = len(users)
    
        count_text = f"{active_count} active user{'s' if active_count != 1 else ''} • {total_count} total"
    
        # ✅ FORMAT FOR DISPLAY
        for u in users:
            is_active = u["Is_Active"]
    
            u["Is_Active"] = "✓ Active" if is_active else "✗ Inactive"
    
            if is_active:
                u["Actions"] = f'[Deactivate User #{u["user_id"]}]'
            else:
                u["Actions"] = f'[Activate User #{u["user_id"]}]'
    
            if u.get("Created_At"):
                try:
                    u["Created_At"] = pd.to_datetime(
                        u["Created_At"]
                    ).strftime("%Y-%m-%d %H:%M")
                except Exception:
                    pass
    
        # ✅ ALWAYS RETURN BOTH OUTPUTS
        return users, count_text

    
    # =====================================================
    # HANDLE ACTION CLICK (PENDING CHANGES)
    # =====================================================
    @app.callback(
        Output("pending-user-changes", "data"),
        Output("save-button-container", "style"),
        Output("pending-changes-count", "children"),
        Output("users-table", "data", allow_duplicate=True),
        Input("users-table", "active_cell"),
        State("users-table", "data"),
        State("pending-user-changes", "data"),
        prevent_initial_call=True
    )
    def handle_user_action(cell, rows, pending):

        if not cell or cell.get("column_id") != "Actions":
            return dash.no_update, dash.no_update, dash.no_update, dash.no_update

        idx = cell["row"]
        row = rows[idx]
        user_id = row["user_id"]

        is_active = row["Is_Active"].startswith("✓")
        new_value = 0 if is_active else 1

        row["Is_Active"] = "✓ Active" if new_value else "✗ Inactive"
        row["Actions"] = (
            f'[Deactivate User #{user_id}]'
            if new_value else
            f'[Activate User #{user_id}]'
        )

        pending = pending or []
        existing = next((p for p in pending if p["user_id"] == user_id), None)

        if existing:
            existing["new_status"] = new_value
        else:
            pending.append({
                "user_id": user_id,
                "username": row["Username"],
                "new_status": new_value
            })

        return pending, {"display": "block"}, f"({len(pending)} pending)", rows

    ###################
    @app.callback(
        Output("map-users", "value"),
        Input("map-subadmin", "value"),
        prevent_initial_call=True
    )
    def preload_attached_users(subadmin):
        if not subadmin:
            return []
    
        db = get_auth_db()
    
        # fetch already-mapped users
        users = db.get_users_for_subadmin(subadmin)
    
        return users

    @app.callback(
        Output("map-subadmin", "options"),
        Output("map-users", "options"),
        Input("refresh-users-btn", "n_clicks"),
        Input("toggle-users-btn", "n_clicks"),
        Input("create-user-btn", "n_clicks"),
        prevent_initial_call=False
    )
    def load_subadmin_user_options(_, __, ___):
        db = get_auth_db()
    
        subadmins = db.get_users_by_role("SubAdmin")
        users = db.get_users_by_role("User")
    
        return (
            [{"label": u, "value": u} for u in subadmins],
            [{"label": u, "value": u} for u in users],
        )

    ###################

    @app.callback(
        Output("mapping-message", "children"),
        Input("map-users-btn", "n_clicks"),
        State("map-subadmin", "value"),
        State("map-users", "value"),
        prevent_initial_call=True
    )
    def attach_users_to_subadmin(_, subadmin, users):

        if not subadmin or not users:
            return html.Div(
                "❌ Select a Sub-Admin and at least one User",
                style={"color": "red"}
            )
    
        db = get_auth_db()
        messages = []
    
        # 1️⃣ Attach mappings
        for u in users:
            ok, msg = db.attach_user_to_subadmin(subadmin, u)
            messages.append(msg)
    
        # 2️⃣ 🔑 AUTO-GENERATE CONSOLIDATED FILES
        ok, merge_msg = db.consolidate_and_write_for_subadmin({
            "username": subadmin,
            "role": "SubAdmin"
        })
    
        if ok:
            messages.append("Consolidated ledgers regenerated")
        else:
            messages.append(f"⚠ Consolidation skipped: {merge_msg}")
    
        return html.Div(
            "✓ " + " | ".join(messages),
            style={"color": "green"}
        )



    # =====================================================
    # SAVE USER CHANGES
    # =====================================================
    @app.callback(
        Output("user-action-message", "children"),
        Output("pending-user-changes", "data", allow_duplicate=True),
        Output("save-button-container", "style", allow_duplicate=True),
        Output("pending-changes-count", "children", allow_duplicate=True),
        Output("users-table", "data", allow_duplicate=True),
        Output("user-count", "children", allow_duplicate=True),
        Input("save-user-changes-btn", "n_clicks"),
        State("pending-user-changes", "data"),
        prevent_initial_call=True
    )
    def save_user_changes(_, pending):

        # --------------------------------------------------
        # NO PENDING CHANGES
        # --------------------------------------------------
        if not pending:
            return (
                "",
                [],
                {"display": "none"},
                "",
                dash.no_update,
                dash.no_update
            )
    
        db = get_auth_db()
    
        admin_id = session.get("user_id", 0)
        admin_name = session.get("username", "system")
    
        success = 0
        errors = []
    
        # --------------------------------------------------
        # APPLY CHANGES
        # --------------------------------------------------
        for p in pending:
    
            user_id = p["user_id"]
            username = p["username"]
            new_status = p["new_status"]
    
            # Prevent admin from disabling themselves
            if user_id == admin_id:
                errors.append(f"Cannot change status of your own account ({username})")
                continue
    
            ok, msg = db.update_user(user_id, Is_Active=new_status)
    
            if ok:
    
                db.log_audit_trail(
                    target_user_id=user_id,
                    target_username=username,
                    action="ACTIVATED" if new_status else "DEACTIVATED",
                    performed_by_user_id=admin_id,
                    performed_by_username=admin_name,
                    new_value=f"Is_Active={new_status}"
                )
    
                success += 1
    
            else:
                errors.append(f"{username}: {msg}")
    
        # --------------------------------------------------
        # RELOAD USERS FROM DB
        # --------------------------------------------------
        users = db.get_all_users()
    
        active_count = 0
    
        for u in users:
    
            is_active = bool(u["Is_Active"])
    
            if is_active:
                active_count += 1
    
            # Format status for UI
            u["Is_Active"] = "✓ Active" if is_active else "✗ Inactive"
    
            # Normalize ID for table
            u["user_id"] = u["User_ID"]
    
            # Action link
            u["Actions"] = (
                f'[Deactivate User #{u["user_id"]}]'
                if is_active
                else f'[Activate User #{u["user_id"]}]'
            )
    
        total = len(users)
    
        # --------------------------------------------------
        # MESSAGE
        # --------------------------------------------------
        if errors:
            message = html.Div(
                f"✓ {success} updated • {len(errors)} error(s): {' | '.join(errors)}",
                style={"color": "orange"}
            )
        else:
            message = html.Div(
                f"✓ {success} user(s) updated",
                style={"color": "green"}
            )
    
        # --------------------------------------------------
        # RETURN UI UPDATES
        # --------------------------------------------------
        return (
            message,
            [],                          # clear pending changes
            {"display": "none"},         # hide save button
            "",                          # clear pending text
            users,                       # refresh table
            f"{active_count} active • {total} total"
        )








