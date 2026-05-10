import dash_bootstrap_components as dbc
from dash import html, dcc, Input, Output, State, ALL
from dash.exceptions import PreventUpdate
import json
import os
import pandas as pd


# load once during layout creation
def get_class_options(username):

    path = f"/var/Data/{username}/fee_structure_static.csv"

    if not os.path.exists(path):
        return []

    df = pd.read_csv(path)

    return [
        {"label": row["standard"], "value": row["studying_class"]}
        for _, row in df.iterrows()
    ]


def get_report_template_content(SessionData):
    common_subjects = [
        "English",
        "Hindi",
        "Mathematics",
        "Science",
        "SST",
        "Computer",
        "Sanskrit",
    ]

    return dbc.Container(
        [
            dbc.Row(
                [
                    dbc.Col(
                        html.H2(
                            "📄 School Template Architect",
                            className="fw-bold text-success mb-3 border-bottom pb-2",
                        )
                    )
                ]
            ),
            dbc.Row(
                [
                    # --- LEFT COLUMN: CORE SETUP ---
                    dbc.Col(
                        [
                            dbc.Card(
                                [
                                    dbc.CardHeader(
                                        "1️⃣ Class & Section Setup",
                                        className="fw-bold bg-light",
                                    ),
                                    dbc.CardBody(
                                        [
                                            dbc.Row(
                                                [
                                                    dbc.Col(
                                                        [
                                                            dbc.Label(
                                                                "Class (No.)",
                                                                className="fw-bold small",
                                                            ),
                                                            dcc.Dropdown(
                                                                id="template-class",
                                                                placeholder="Select Class",
                                                                options=get_class_options(
                                                                    SessionData[
                                                                        "username"
                                                                    ]
                                                                ),
                                                            ),
                                                        ],
                                                        width=4,
                                                    ),
                                                    dbc.Col(
                                                        [
                                                            dbc.Label(
                                                                "Section System",
                                                                className="fw-bold small",
                                                            ),
                                                            dbc.Select(
                                                                id="template-section",
                                                                options=[
                                                                    {
                                                                        "label": "Yes (A,B,C)",
                                                                        "value": "yes",
                                                                    },
                                                                    {
                                                                        "label": "No",
                                                                        "value": "no",
                                                                    },
                                                                ],
                                                                value="yes",
                                                            ),
                                                        ],
                                                        width=8,
                                                    ),
                                                ],
                                                className="mb-4",
                                            ),
                                            dbc.Label(
                                                "Select Subjects",
                                                className="fw-bold small",
                                            ),
                                            dbc.Checklist(
                                                id="common-subjects-check",
                                                options=[
                                                    {"label": f" {s}", "value": s}
                                                    for s in common_subjects
                                                ],
                                                value=["English", "Mathematics"],
                                                inline=True,
                                                className="mb-3 p-2 border rounded bg-light",
                                            ),
                                            html.Div(
                                                id="selected-subjects-preview",
                                                className="mt-2 p-2 border rounded bg-white",
                                            ),
                                            dbc.InputGroup(
                                                [
                                                    dbc.Input(
                                                        id="custom-subject-name",
                                                        placeholder="Other Subject...",
                                                    ),
                                                    dbc.Button(
                                                        "Add",
                                                        id="add-sub-btn",
                                                        color="secondary",
                                                    ),
                                                ],
                                                size="sm",
                                            ),
                                            html.Div(
                                                id="extra-subjects-container",
                                                className="mt-2 mb-3",
                                            ),
                                        ]
                                    ),
                                ],
                                className="shadow-sm border-0 mb-4",
                            ),
                            # --- EXAM STRUCTURE ---
                            dbc.Card(
                                [
                                    dbc.CardHeader(
                                        "2️⃣ Exam Structure & Rename",
                                        className="fw-bold bg-primary text-white",
                                    ),
                                    dbc.CardBody(
                                        [
                                            dbc.Row(
                                                [
                                                    dbc.Col(
                                                        [
                                                            dbc.Label(
                                                                "Select Exams",
                                                                className="fw-bold small",
                                                            ),
                                                            dbc.Checklist(
                                                                id="exam-types",
                                                                options=[
                                                                    {
                                                                        "label": " Unit Test",
                                                                        "value": "UT",
                                                                    },
                                                                    {
                                                                        "label": " Half Yearly",
                                                                        "value": "HY",
                                                                    },
                                                                    {
                                                                        "label": " Final Exam",
                                                                        "value": "Final",
                                                                    },
                                                                ],
                                                                value=[],
                                                                switch=True,
                                                            ),
                                                        ],
                                                        width=12,
                                                        className="mb-3",
                                                    ),
                                                ]
                                            ),
                                            # Rename and Count Row (ONLY FOR UT)
                                            html.Div(
                                                id="ut-config-row",
                                                children=[
                                                    dbc.Row(
                                                        [
                                                            dbc.Col(
                                                                [
                                                                    dbc.Label(
                                                                        "Rename 'Unit Test'?",
                                                                        className="small fw-bold",
                                                                    ),
                                                                    dbc.Input(
                                                                        id="ut-rename",
                                                                        placeholder="Ex: Periodic Test",
                                                                    ),
                                                                ],
                                                                width=7,
                                                            ),
                                                            dbc.Col(
                                                                [
                                                                    dbc.Label(
                                                                        "How many?",
                                                                        className="small fw-bold",
                                                                    ),
                                                                    dbc.Input(
                                                                        id="ut-count-input",
                                                                        type="number",
                                                                        min=1,
                                                                        max=6,
                                                                        value=1,
                                                                    ),
                                                                ],
                                                                width=5,
                                                            ),
                                                        ],
                                                        className="bg-light p-2 border rounded mb-3",
                                                    )
                                                ],
                                                style={"display": "none"},
                                            ),  # Initially hidden
                                            html.Div(
                                                id="exam-marks-inputs"
                                            ),  # Max Marks dynamic inputs
                                        ]
                                    ),
                                ],
                                className="shadow-sm border-0 mb-4",
                            ),
                        ],
                        lg=7,
                    ),
                    # --- RIGHT COLUMN: EXTRA COLS & SAVE ---
                    dbc.Col(
                        [
                            dbc.Card(
                                [
                                    dbc.CardHeader(
                                        "3️⃣ Custom Columns (Practical/Internal)",
                                        className="fw-bold bg-dark text-white",
                                    ),
                                    dbc.CardBody(
                                        [
                                            dbc.Input(
                                                id="col-name",
                                                placeholder="Column Name (Ex: Project)",
                                                className="mb-2",
                                            ),
                                            dbc.Select(
                                                id="col-type",
                                                options=[
                                                    {
                                                        "label": "Marks (Numeric)",
                                                        "value": "marks",
                                                    },
                                                    {
                                                        "label": "Grade (A, B, C)",
                                                        "value": "grade",
                                                    },
                                                ],
                                                value="marks",
                                                className="mb-3",
                                            ),
                                            dbc.Button(
                                                "Add Extra Column",
                                                id="add-col-btn",
                                                color="info",
                                                className="w-100",
                                            ),
                                            html.Div(
                                                id="custom-cols-list",
                                                className="d-flex flex-wrap gap-2 mt-3",
                                            ),
                                        ]
                                    ),
                                ],
                                className="shadow-sm border-0 mb-4",
                            ),
                            dbc.Card(
                                [
                                    dbc.CardBody(
                                        [
                                            dbc.Button(
                                                "💾 Finalize Template",
                                                id="final-save-btn",
                                                color="success",
                                                size="lg",
                                                className="w-100 fw-bold shadow",
                                            ),
                                            html.Div(
                                                id="final-status", className="mt-3"
                                            ),
                                        ]
                                    )
                                ],
                                className="border-success",
                            ),
                        ],
                        lg=5,
                    ),
                ]
            ),
            dcc.Store(id="store-extra-subs", data=[]),
            dcc.Store(id="store-custom-cols", data=[]),
        ],
        fluid=True,
        className="p-4 bg-light",
    )


# =========================
# CALLBACKS
# =========================
def register_callbacks(app):
    # 1. Toggle UT Config Row and Dynamic Marks
    @app.callback(
        [Output("ut-config-row", "style"), Output("exam-marks-inputs", "children")],
        [
            Input("exam-types", "value"),
            Input("ut-count-input", "value"),
            Input("ut-rename", "value"),
        ],
    )
    def update_structure(selected_exams, ut_count, ut_name):
        ut_style = (
            {"display": "block"} if "UT" in selected_exams else {"display": "none"}
        )
        ut_label = ut_name if ut_name else "Unit Test"

        marks_elements = []

        if "UT" in selected_exams:
            for i in range(1, (ut_count or 1) + 1):
                marks_elements.append(
                    dbc.InputGroup(
    [
        dbc.InputGroupText(f"{ut_label} {i} Max"),
        dbc.Input(
            id={"type": "exam-marks", "index": f"UT{i}"},
            type="number",
        ),

        dbc.InputGroupText("Pass"),
        dbc.Input(
            id={"type": "exam-pass", "index": f"UT{i}"},
            type="number",
        ),
    ],
    className="mb-2",
    size="sm",
)
                )

        if "HY" in selected_exams:
            marks_elements.append(
                dbc.InputGroup(
    [
        dbc.InputGroupText("Half Yearly Max"),
        dbc.Input(
            id={"type": "exam-marks", "index": "HY"},
            type="number",
        ),

        dbc.InputGroupText("Pass"),
        dbc.Input(
            id={"type": "exam-pass", "index": "HY"},
            type="number",
        ),
    ],
    className="mb-2",
    size="sm",
)
            )

        if "Final" in selected_exams:
            marks_elements.append(
                dbc.InputGroup(
    [
        dbc.InputGroupText("Final Max"),
        dbc.Input(
            id={"type": "exam-marks", "index": "FINAL"},
            type="number",
            placeholder="100",
        ),

        dbc.InputGroupText("Pass"),
        dbc.Input(
            id={"type": "exam-pass", "index": "FINAL"},
            type="number",
            placeholder="33",
        ),
    ],
    className="mb-2",
    size="sm",
)
            )

        return ut_style, marks_elements

    # [Note: Add-Sub and Add-Col callbacks will remain same as previous code]
    @app.callback(
        Output("selected-subjects-preview", "children"),
        Input("common-subjects-check", "value"),
        prevent_initial_call=False,
    )
    def show_selected_subjects(subjects):

        if subjects is None:
            raise PreventUpdate

        if not subjects:
            return dbc.Alert("No subject selected", color="warning", className="p-2")

        return [
            html.Div("Selected Subjects:", className="fw-bold mb-1"),
            *[
                dbc.Badge(sub, color="success", className="me-1 mb-1 p-2")
                for sub in subjects
            ],
        ]

    @app.callback(
        Output("final-status", "children"),
        Input("final-save-btn", "n_clicks"),
        State("template-class", "value"),
        State("template-section", "value"),
        State("common-subjects-check", "value"),
        State("store-extra-subs", "data"),
        State("exam-types", "value"),
        State({"type": "exam-marks", "index": ALL}, "value"),
        State({"type": "exam-pass", "index": ALL}, "value"),
        State("store-custom-cols", "data"),
        State("session", "data"),
        prevent_initial_call=True,
    )
    def save_template(
        n,
        class_no,
        section_sys,
        subjects,
        extra_subs,
        exams,
        marks,
        pass_marks,
        custom_cols,
        SessionData,
    ):

        extra_subs = extra_subs or []
        subjects = (subjects or []) + extra_subs

        if exams and any(m is None for m in marks):
            return dbc.Alert("❌ Please enter max marks for all exams", color="danger")

        if class_no is None or not subjects:
            return dbc.Alert("❌ Please select class and subjects", color="danger")

        username = SessionData["username"]

        base_path = f"/var/Data/{username}"
        os.makedirs(base_path, exist_ok=True)

        file_path = os.path.join(base_path, "report_templates.csv")

        custom_cols = custom_cols or []

        template_row = {
            "class": class_no,
            "section_system": section_sys,
            "subjects": ",".join(subjects),
            "exams": ",".join(exams),
            "marks": ",".join([str(m) for m in marks]),
            "passing_marks": ",".join([str(p) for p in pass_marks]),
            "extra_columns": ",".join(
                [f"{c['name']}:{c['type']}" for c in custom_cols]
            ),
        }

        try:
            if os.path.exists(file_path):

                df = pd.read_csv(file_path)

                df = df[df["class"] != class_no]

                df = pd.concat([df, pd.DataFrame([template_row])])

            else:

                df = pd.DataFrame([template_row])

            df.to_csv(file_path, index=False)

            return dbc.Alert("✅ Template saved successfully", color="success")

        except Exception as e:
            return dbc.Alert(f"❌ Error saving template: {str(e)}", color="danger")

    @app.callback(
        Output("extra-subjects-container", "children"),
        Output("store-extra-subs", "data"),
        Input("add-sub-btn", "n_clicks"),
        State("custom-subject-name", "value"),
        State("store-extra-subs", "data"),
        prevent_initial_call=True,
    )
    def add_subject(n, name, data):

        if not name:
            raise PreventUpdate

        data = data or []

        if name not in data:
            data.append(name)

        badges = [dbc.Badge(s, color="primary", className="me-1") for s in data]

        return badges, data

    @app.callback(
        Output("custom-cols-list", "children"),
        Output("store-custom-cols", "data"),
        Input("add-col-btn", "n_clicks"),
        State("col-name", "value"),
        State("col-type", "value"),
        State("store-custom-cols", "data"),
        prevent_initial_call=True,
    )
    def add_custom_column(n, name, col_type, data):

        if not name:
            raise PreventUpdate

        data = data or []

        new_col = {"name": name, "type": col_type}

        if new_col not in data:
            data.append(new_col)

        badges = [
            dbc.Badge(f"{c['name']} ({c['type']})", color="dark", className="me-1 p-2")
            for c in data
        ]

        return badges, data
