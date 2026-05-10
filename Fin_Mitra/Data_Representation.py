from dash import html, Input, Output, State
import dash_bootstrap_components as dbc
import Extracurricular_activities 
import Report_Card
import TC_Form

# IMPORT SUBMODULES
import Student_Log
import Due_Fee_Retreiver
import fee_student_uploader
import dash_core_components as dcc
import Report_Template
import Student_Attendance
import Student_Promote

def get_layout(SessionData):
    return dbc.Container(
        [
            html.H2(
                "🎓 Student & Fee Management",
                className="text-center my-4 fw-bold",
                style={"letterSpacing": "0.5px"},
            ),
            dbc.Card(
                dbc.CardBody(
                    dbc.Tabs(
                        id="student-fee-tabs",
                        active_tab="create-student",
                        class_name="custom-tabs",
                        children=[
                            dbc.Tab(
                                Student_Log.get_create_student_content(SessionData),
                                label="➕ Create Student",
                                tab_id="create-student",
                                tab_class_name="custom-tab",
                                active_tab_class_name="custom-tab-active",
                            ),
                            dbc.Tab(
                                Student_Log.get_search_student_content(SessionData),
                                label="🔍 Search Student",
                                tab_id="search-student",
                                tab_class_name="custom-tab",
                                active_tab_class_name="custom-tab-active",
                            ),
                            dbc.Tab(
                                Due_Fee_Retreiver.get_fee_structure_layout(SessionData),
                                label="📊 Fee Structure",
                                tab_id="fee-structure",
                                tab_class_name="custom-tab",
                                active_tab_class_name="custom-tab-active",
                            ),
                            dbc.Tab(
                                Due_Fee_Retreiver.get_fee_due_content(SessionData),
                                label="💰 Fee Due",
                                tab_id="fee-due",
                                tab_class_name="custom-tab",
                                active_tab_class_name="custom-tab-active",
                            ),
                            dbc.Tab(
                                fee_student_uploader.get_upload_content(SessionData),
                                label="⬆️ Upload Data",
                                tab_id="upload",
                                tab_class_name="custom-tab",
                                active_tab_class_name="custom-tab-active",
                            ),
                            dbc.Tab(
                                Student_Attendance.student_attendance_layout(SessionData),
                                label="Attendace",
                                tab_id="attendance",
                                tab_class_name="custom-tab",
                                active_tab_class_name="custom-tab-active",
                            ),
                            dbc.Tab(
                                TC_Form.get_tc_form_content(SessionData),
                                label="Transfer Certificate",
                                tab_id="tc",
                                tab_class_name="custom-tab",
                                active_tab_class_name="custom-tab-active",
                            ),
                            dbc.Tab(
                                Report_Card.get_report_card_content(SessionData),
                                label="📄 Report Card",
                                tab_id="report-card",
                                tab_class_name="custom-tab",
                                active_tab_class_name="custom-tab-active",
                            ),
                            dbc.Tab(
                                Report_Template.get_report_template_content(SessionData),
                                label="📄 Report Template",
                                tab_id="report-template",
                                tab_class_name="custom-tab",
                                active_tab_class_name="custom-tab-active",
                            ),
                            dbc.Tab(
    Student_Promote.get_promote_layout(SessionData),
    label="🚀 Promote",
    tab_id="promote",
    tab_class_name="custom-tab",
                                active_tab_class_name="custom-tab-active",
),
dbc.Tab(
    Extracurricular_activities.get_sports_layout(SessionData),
    label="🏆 Sports",
    tab_id="sports",
    tab_class_name="custom-tab",
    active_tab_class_name="custom-tab-active",
)
                        ],
                    )
                ),
                className="shadow-lg rounded-4 border-0",
            ),
        ],
        fluid=True,
    )


def get_upload_student_content(SessionData):
    return dbc.Card(
        dbc.CardBody(
            [
                html.H5(
                    "Upload Student / Fee Data",
                    style={"color": "#1B5E20", "fontWeight": "600"},
                ),
                html.Hr(),
                dcc.Upload(
                    id="upload-student-file",
                    children=dbc.Button(
                        "Upload CSV / Excel",
                        color="success",
                    ),
                    multiple=False,
                ),
                html.Div(
                    "Supported formats: .csv, .xlsx",
                    className="text-muted mt-2",
                ),
                html.Div(id="upload-status", className="mt-3"),
            ]
        ),
        className="shadow-sm",
    )


# =====================================================
# CALLBACK REGISTRATION
# =====================================================


def register_callbacks(app):
    Student_Log.register_callbacks(app)
    Due_Fee_Retreiver.register_callbacks(app)
    fee_student_uploader.register_callbacks(app)
    TC_Form.register_callbacks(app)
    Report_Card.register_Callbacks(app)
    Report_Template.register_callbacks(app)
    Student_Attendance.register_callbacks(app)
    Student_Promote.register_callbacks(app)
    Extracurricular_activities.register_sports_callbacks(app)
    
    @app.callback(
        Output("student-fee-tabs", "active_tab"),
        Input("url", "pathname"),
        prevent_initial_call=False,
    )
    def switch_student_tab(pathname):
        if pathname == "/datarep/fee-due":
            return "fee-due"
        return "create-student"
