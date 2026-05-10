import dash
from dash import html, dcc, Input, Output, State, ALL
import dash_bootstrap_components as dbc
import pandas as pd
import os

import datetime

# =========================================================
# CONFIG
# =========================================================
PAGE_SIZE = 10
KPMG_GREEN = "#2E8B57"
LIGHT_BG = "#FAFFFB"
BORDER = "#D5F5E3"


# =========================================================
# HELPERS
# =========================================================
def list_csv_files(SessionData):

    username = SessionData["username"]

    base_dir = f"/var/Data/{username}"

    files = []

    # ---------- Root CSV files ----------
    if os.path.exists(base_dir):

        for f in os.listdir(base_dir):

            path = os.path.join(base_dir, f)

            if f.endswith(".csv") and os.path.isfile(path):

                files.append(f)

    # ---------- Marks CSV files ----------
    marks_dir = os.path.join(base_dir, "marks")

    if os.path.exists(marks_dir):

        for class_folder in os.listdir(marks_dir):

            class_path = os.path.join(marks_dir, class_folder)

            if os.path.isdir(class_path):

                for f in os.listdir(class_path):

                    if f.endswith(".csv"):

                        files.append(f"marks/{class_folder}/{f}")

    return sorted(files)


def load_file(filepath):
    return pd.read_csv(filepath)


def append_deletion_log(rows, filename, SessionData):
    LOG_PATH = "/var/Data/" + str(SessionData["username"]) + "/deletion_log.csv"

    log_df = pd.DataFrame(
        {
            "timestamp": [datetime.datetime.now()] * len(rows),
            "file": [filename] * len(rows),
            "deleted_row_index": rows,
        }
    )

    if os.path.exists(LOG_PATH):
        log_df.to_csv(LOG_PATH, mode="a", header=False, index=False)
    else:
        log_df.to_csv(LOG_PATH, index=False)


# =========================================================
# LAYOUT
# =========================================================
def get_layout(SessionData):
    return html.Div(
        style={"padding": "30px"},
        children=[
            # ================= STORES =================
            dcc.Store(id="delete-page-store", data=0),
            dcc.Store(id="delete-search-store", data=""),
            dcc.Store(id="delete-numeric-search-store", data=None),
            dcc.Store(id="edit-row-store"),
            html.H3(
                "Delete File Entries", style={"color": KPMG_GREEN, "fontWeight": "600"}
            ),
            html.Hr(),
            # ================= FILE SELECT =================
            dbc.Row(
                [
                    dbc.Col(
                        [
                            dbc.Label("Select File"),
                            dcc.Dropdown(
                                id="delete-file-dropdown",
                                options=[
                                    {"label": f, "value": f}
                                    for f in list_csv_files(SessionData)
                                ],
                                placeholder="Select CSV file",
                            ),
                        ],
                        md=6,
                    ),
                    dbc.Col(
                        [
                            dbc.Label(" "),
                            dbc.Button(
                                "Refresh",
                                id="refresh-files-btn",
                                color="success",
                                outline=True,
                                className="mt-4",
                            ),
                        ],
                        md=2,
                    ),
                ]
            ),
            html.Hr(),
            # ================= SEARCH SECTION =================
            dbc.Row(
                [
                    # 🔎 TEXT SEARCH
                    dbc.Col(
                        [
                            dbc.Label("Text Search"),
                            dbc.Input(
                                id="delete-search-input",
                                type="text",
                                placeholder="Search across all columns...",
                                debounce=True,
                            ),
                        ],
                        md=4,
                    ),
                    # 🔢 NUMERIC SEARCH
                    dbc.Col(
                        [
                            dbc.Label("Numeric Search (Exact Match)"),
                            dbc.Input(
                                id="delete-numeric-search-input",
                                type="number",
                                placeholder="Enter exact number...",
                                debounce=True,
                            ),
                        ],
                        md=4,
                    ),
                ],
                className="mb-3",
            ),
            html.Hr(),
            # ================= TABLE =================
            html.Div(id="delete-table-container"),
            # ================= BOTTOM ACTIONS =================
            dbc.Row(
                className="mt-3",
                children=[
                    dbc.Col(
                        dbc.Button("⬅ Previous", id="prev-page-btn", outline=True),
                        width="auto",
                    ),
                    dbc.Col(
                        dbc.Button("Next ➡", id="next-page-btn", outline=True),
                        width="auto",
                    ),
                    dbc.Col(
                        dbc.Button(
                            "Delete Selected",
                            id="init-delete-btn",
                            color="danger",
                            className="ms-auto",
                        ),
                        width="auto",
                    ),
                ],
            ),
            # ================= DELETE CONFIRM MODAL =================
            dbc.Modal(
                [
                    dbc.ModalHeader("Confirm Deletion"),
                    dbc.ModalBody(
                        "Are you sure you want to permanently delete the selected entries?"
                    ),
                    dbc.ModalFooter(
                        [
                            dbc.Button("Cancel", id="cancel-delete-btn", outline=True),
                            dbc.Button(
                                "Yes, Delete", id="confirm-delete-btn", color="danger"
                            ),
                        ]
                    ),
                ],
                id="delete-confirm-modal",
                centered=True,
                is_open=False,
            ),
            # ================= EDIT MODAL =================
            dbc.Modal(
                [
                    dbc.ModalHeader("Edit Row"),
                    dbc.ModalBody(id="edit-modal-body"),
                    dbc.ModalFooter(
                        [
                            dbc.Button("Cancel", id="edit-cancel-btn", outline=True),
                            dbc.Button(
                                "Save Changes", id="edit-save-btn", color="success"
                            ),
                        ]
                    ),
                ],
                id="edit-modal",
                centered=True,
                is_open=False,
            ),
            html.Div(id="delete-status-msg", className="mt-3"),
        ],
    )


# =========================================================
# CALLBACKS
# =========================================================
def register_callbacks(app):

    # ---------------- Refresh file list ----------------
    @app.callback(
        Output("delete-file-dropdown", "options"),
        Input("refresh-files-btn", "n_clicks"),
        State("session", "data"),
        prevent_initial_call=True,
    )
    def refresh_files(_, SessionData):
        return [{"label": f, "value": f} for f in list_csv_files(SessionData)]

    # ---------------- Pagination state ----------------
    @app.callback(
        Output("delete-page-store", "data"),
        Input("delete-file-dropdown", "value"),
        Input("next-page-btn", "n_clicks"),
        Input("prev-page-btn", "n_clicks"),
        State("delete-page-store", "data"),
        prevent_initial_call=True,
    )
    def update_page(filename, next_clicks, prev_clicks, page):
        ctx = dash.callback_context.triggered_id

        if ctx == "delete-file-dropdown":
            return 0

        if ctx == "next-page-btn":
            return page + 1

        if ctx == "prev-page-btn":
            return max(page - 1, 0)

        return page

    # ---------------- Render paginated table ----------------
    @app.callback(
        Output("delete-table-container", "children"),
        Input("delete-file-dropdown", "value"),
        Input("delete-page-store", "data"),
        Input("delete-search-store", "data"),
        Input("delete-numeric-search-store", "data"),
        State("session", "data"),
        prevent_initial_call=True,
    )
    def render_table(filename, page, search_text, numeric_value, SessionData):

        if not filename:
            return None

        DATA_DIR = "/var/Data/" + str(SessionData["username"])
        path = os.path.join(DATA_DIR, filename)
        df = load_file(path)

        # ---------------- TEXT FILTER ----------------
        if search_text:
            mask = df.astype(str).apply(
                lambda col: col.str.contains(search_text, case=False, na=False)
            )
            df = df[mask.any(axis=1)]

        # ---------------- NUMERIC FILTER ----------------
        if numeric_value is not None:
            numeric_cols = df.select_dtypes(include="number")

            if not numeric_cols.empty:
                num_mask = numeric_cols.eq(numeric_value)
                df = df[num_mask.any(axis=1)]

        total_pages = max((len(df) - 1) // PAGE_SIZE + 1, 1)
        page = min(page, total_pages - 1)

        start = page * PAGE_SIZE
        end = start + PAGE_SIZE

        slice_df = df.iloc[start:end].copy()
        slice_df["__rowid__"] = slice_df.index

        return dbc.Card(
            body=True,
            style={"background": LIGHT_BG, "border": f"1px solid {BORDER}"},
            children=[
                html.Small(f"Page {page + 1} of {total_pages}", className="text-muted"),
                html.Table(
                    className="table table-sm mt-2",
                    children=[
                        # ================= TABLE HEADER =================
                        html.Thead(
                            html.Tr(
                                [html.Th("Delete"), html.Th("Edit")]
                                + [
                                    html.Th(c)
                                    for c in slice_df.columns
                                    if c != "__rowid__"
                                ]
                            )
                        ),
                        # ================= TABLE BODY =================
                        html.Tbody(
                            [
                                html.Tr(
                                    [
                                        # DELETE CHECKBOX
                                        html.Td(
                                            dcc.Checklist(
                                                options=[
                                                    {
                                                        "label": "",
                                                        "value": r["__rowid__"],
                                                    }
                                                ],
                                                id={
                                                    "type": "delete-row-check",
                                                    "index": r["__rowid__"],
                                                },
                                            )
                                        ),
                                        # EDIT BUTTON
                                        html.Td(
                                            dbc.Button(
                                                "Edit",
                                                size="sm",
                                                color="secondary",
                                                outline=True,
                                                id={
                                                    "type": "edit-row-btn",
                                                    "index": r["__rowid__"],
                                                },
                                            )
                                        ),
                                    ]
                                    + [
                                        html.Td(r[c])
                                        for c in slice_df.columns
                                        if c != "__rowid__"
                                    ]
                                )
                                for _, r in slice_df.iterrows()
                            ]
                        ),
                    ],
                ),
            ],
        )

    # ---------------- Modal toggle ----------------
    @app.callback(
        Output("delete-confirm-modal", "is_open"),
        Input("init-delete-btn", "n_clicks"),
        Input("cancel-delete-btn", "n_clicks"),
        Input("confirm-delete-btn", "n_clicks"),
        State("delete-confirm-modal", "is_open"),
        prevent_initial_call=True,
    )
    def toggle_modal(init, cancel, confirm, is_open):
        ctx = dash.callback_context.triggered_id
        if ctx == "init-delete-btn":
            return True
        if ctx in ["cancel-delete-btn", "confirm-delete-btn"]:
            return False
        return is_open

    # ---------------- Perform delete ----------------
    @app.callback(
        Output("delete-status-msg", "children"),
        Input("confirm-delete-btn", "n_clicks"),
        State({"type": "delete-row-check", "index": ALL}, "value"),
        State("delete-file-dropdown", "value"),
        State("session", "data"),
        prevent_initial_call=True,
    )
    def perform_delete(_, selected_rows, filename, SessionData):

        rows = sorted({v for sub in selected_rows if sub for v in sub})
        if not rows:
            return dbc.Alert("No rows selected.", color="warning")

        DATA_DIR = "/var/Data/" + str(SessionData["username"])
        path = os.path.join(DATA_DIR, filename)

        df = load_file(path)
        df = df.drop(index=rows)
        df.to_csv(path, index=False)

        append_deletion_log(rows, filename, SessionData)

        return dbc.Alert(f"Deleted {len(rows)} row(s) from {filename}", color="success")

    @app.callback(
        Output("delete-search-store", "data"),
        Output("delete-numeric-search-store", "data"),
        Output("delete-page-store", "data", allow_duplicate=True),
        Input("delete-search-input", "value"),
        Input("delete-numeric-search-input", "value"),
        prevent_initial_call=True,
    )
    def apply_search(search_text, numeric_value):
        return search_text or "", numeric_value, 0

    @app.callback(
        Output("delete-search-store", "data", allow_duplicate=True),
        Output("delete-numeric-search-store", "data", allow_duplicate=True),
        Output("delete-page-store", "data", allow_duplicate=True),
        Input("delete-file-dropdown", "value"),
        prevent_initial_call=True,
    )
    def reset_search_on_file_change(_):
        return "", None, 0

    @app.callback(
        Output("edit-modal", "is_open"),
        Output("delete-status-msg", "children", allow_duplicate=True),
        Output("delete-page-store", "data", allow_duplicate=True),
        Input("edit-save-btn", "n_clicks"),
        State({"type": "edit-input", "column": ALL}, "value"),
        State({"type": "edit-input", "column": ALL}, "id"),
        State("edit-row-store", "data"),
        State("delete-file-dropdown", "value"),
        State("session", "data"),
        prevent_initial_call=True,
    )
    def save_edit(_, values, ids, row_store, filename, SessionData):
        path = f"/var/Data/{SessionData['username']}/{filename}"
        df = pd.read_csv(path)

        row_id = row_store["row_id"]
        for v, i in zip(values, ids):
            df.at[row_id, i["column"]] = v

        df.to_csv(path, index=False)

        return (
            False,
            dbc.Alert("Row updated successfully.", color="success"),
            0,  # 🔥 force table refresh
        )

    @app.callback(
        Output("edit-modal", "is_open", allow_duplicate=True),
        Output("edit-modal-body", "children", allow_duplicate=True),
        Output("edit-row-store", "data", allow_duplicate=True),
        Input({"type": "edit-row-btn", "index": ALL}, "n_clicks"),
        State("delete-file-dropdown", "value"),
        State("session", "data"),
        prevent_initial_call=True,
    )
    def open_edit_modal(n_clicks, filename, SessionData):
        ctx = dash.callback_context
        trigger = ctx.triggered_id

        # 🚫 Agar Edit button actually click nahi hua → kuch mat karo
        if (
            not isinstance(trigger, dict)
            or trigger.get("type") != "edit-row-btn"
            or not n_clicks
            or not any(n_clicks)
        ):
            return False, dash.no_update, dash.no_update

        row_id = trigger["index"]

        path = f"/var/Data/{SessionData['username']}/{filename}"
        df = pd.read_csv(path)
        row = df.loc[row_id]

        inputs = [
            dbc.Row(
                [
                    dbc.Col(dbc.Label(col), md=4),
                    dbc.Col(
                        dbc.Input(
                            id={"type": "edit-input", "column": col}, value=row[col]
                        ),
                        md=8,
                    ),
                ],
                className="mb-2",
            )
            for col in df.columns
        ]

        return True, inputs, {"row_id": row_id}
