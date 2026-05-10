from dash import html, dcc, Input, Output, State, ALL
import dash_bootstrap_components as dbc
import pandas as pd
import os
import Template
import base64


def get_class_name(username, class_no):
    path = f"/var/Data/{username}/fee_structure_static.csv"

    if not os.path.exists(path):
        return str(class_no)

    df = pd.read_csv(path)

    df["studying_class"] = pd.to_numeric(df["studying_class"], errors="coerce")

    row = df[df["studying_class"] == int(class_no)]

    if not row.empty:
        return row.iloc[0]["standard"]

    return str(class_no)


def get_class_options(username):

    path = f"/var/Data/{username}/fee_structure_static.csv"

    if not os.path.exists(path):
        return []

    df = pd.read_csv(path)

    return [
        {"label": row["standard"], "value": row["studying_class"]}
        for _, row in df.iterrows()
    ]


def load_school_info(username):

    path = f"/var/Data/{username}/school_info.csv"

    school = {"name": "", "address": "", "pan": ""}

    if os.path.exists(path):

        df = pd.read_csv(path)

        if not df.empty:
            school["name"] = df.loc[0, "school_name"]
            school["address"] = df.loc[0, "address"]
            school["pan"] = df.loc[0, "pan_number"]

    return school


def save_marks_csv(username, student, exam_data):

    # -----------------------
    # SAFE SECTION FIX ✅
    # -----------------------
    section = str(student.get("section", "")).strip()
    if section == "":
        section = "NA"

    class_no = str(student["class_id"])
    roll = str(student["roll"]).strip().lower()

    base_path = f"/var/Data/{username}/marks"
    os.makedirs(base_path, exist_ok=True)

    file_path = f"{base_path}/{class_no}.csv"

    # -----------------------
    # LOAD TEMPLATE (for max marks) 🔥
    # -----------------------
    template_path = f"/var/Data/{username}/report_templates.csv"

    exam_max = {}
    exam_pass = {}
 
    if os.path.exists(template_path):
        df_temp = pd.read_csv(template_path)
        df_temp["class"] = df_temp["class"].astype(str)

        row = df_temp[df_temp["class"] == str(class_no)]

        if not row.empty:
            row = row.iloc[0]

            exams = str(row["exams"]).split(",")
            marks_list = str(row["marks"]).split(",")
            pass_list = str(row.get("passing_marks", "")).split(",")
            for i in range(len(exams)):
                exam_max[exams[i]] = int(marks_list[i]) if i < len(marks_list) else None
                exam_pass[exams[i]] = int(float(pass_list[i])) if i < len(pass_list) and pass_list[i] != "" else 0
    # -----------------------
    # BUILD ROW
    # -----------------------
    row = {
        "student_id": student.get("student_id"),
        "roll": roll,
        "student_name": student["name"],
        "section": section

    }
    total_obtained = 0
    total_max = 0

    for subject, exams in exam_data.items():
        for exam, mark in exams.items():

            max_val = exam_max.get(exam)

            if mark is not None:
                total_obtained += float(mark)

            if max_val is not None:
                total_max += float(max_val)

    percentage = 0
    if total_max > 0:
        percentage = round((total_obtained / total_max) * 100, 2)

    # ✅ SAVE IN ROW
    row["total_marks"] = total_obtained
    row["max_marks"] = total_max
    row["percentage"] = percentage

    for subject, exams in exam_data.items():
     for exam, mark in exams.items():

        col = f"{subject}_{exam}"
        status_col = f"{subject}_{exam}_status"

        row[col] = mark

        # 🔥 FAIL / PASS SAVE
        if mark not in [None, ""]:
            if float(mark) < exam_pass.get(exam, 0):
                row[status_col] = "FAIL"
            else:
                row[status_col] = "PASS"
        else:
            row[status_col] = ""

    df_new = pd.DataFrame([row])

    # -----------------------
    # UPDATE EXISTING FILE
    # -----------------------
    if os.path.exists(file_path):

        df_old = pd.read_csv(file_path)

        df_old["roll"] = df_old["roll"].astype(str).str.strip().str.lower()
        df_old["section"] = df_old["section"].astype(str).str.strip()

        # ✅ SAME STUDENT + SAME SECTION replace
        df_old = df_old[
            ~((df_old["student_id"] == student.get("student_id")))
        ]

        df = pd.concat([df_old, df_new], ignore_index=True)

    else:
        df = df_new

    # -----------------------
    # SAVE
    # -----------------------
    df.to_csv(file_path, index=False)


def normalize_id(val):
    return str(val).strip().lower()


def load_saved_marks(username, student):

    class_no = str(student["class_id"])
    section = str(student["section"]).strip()
    roll = normalize_id(student["roll"])

    # ✅ SAME FILE
    file_path = f"/var/Data/{username}/marks/{class_no}.csv"

    if not os.path.exists(file_path):
        return {}

    df = pd.read_csv(file_path)

    df["roll"] = df["roll"].astype(str).str.strip().str.lower()
    df["section"] = df["section"].astype(str).str.strip()

    row = df[
    df["student_id"] == student.get("student_id")
]

    if row.empty:
        return {}

    return row.iloc[0].to_dict()

def get_report_card_content(SessionData):

    return dbc.Container(
        [
            dbc.Card(
                dbc.CardBody(
                    [
                        html.H4("Generate Report Card", className="mb-3"),
                        dbc.Row(
                            [
                                dbc.Col(
                                    [
                                        dbc.Label("Select Class"),
                                        dcc.Dropdown(
                                            id="rc-class",
                                            placeholder="Select Class",
                                            options=get_class_options(
                                                SessionData["username"]
                                            ),
                                        ),
                                    ],
                                    width=4,
                                ),
                                dbc.Col(
                                    [
                                        dbc.Button(
                                            "Load Template",
                                            id="load-template-btn",
                                            color="primary",
                                            className="mt-4",
                                        )
                                    ],
                                    width=3,
                                ),
                            ]
                        ),
                        dbc.Row(
                            [
                                dbc.Col(
                                    [
                                        dbc.Label("Section"),
                                        dbc.Input(
                                            id="rc-section", placeholder="A / B / C"
                                        ),
                                    ],
                                    width=2,
                                ),
                                dbc.Col(
                                    [
                                        dbc.Label("Search By"),
                                        dcc.Dropdown(
                                            id="student-search-type",
                                            options=[
                                                {
                                                    "label": "Student Name",
                                                    "value": "name",
                                                },
                                                {
                                                    "label": "Roll Number",
                                                    "value": "roll",
                                                },
                                            ],
                                            placeholder="Search Type",
                                        ),
                                    ],
                                    width=3,
                                ),
                                dbc.Col(
                                    [
                                        dbc.Label("Select Student"),
                                        dcc.Dropdown(
                                            id="student-search-dropdown",
                                            placeholder="Select Student",
                                        ),
                                    ],
                                    width=5,
                                ),
                            ]
                        ),
                        html.Hr(),
                        dbc.Button(
                            "Save Marks",
                            id="save-marks-btn",
                            color="primary",
                            className="mb-3 me-2",
                        ),
                        dcc.Store(id="selected-student-data"),
                        html.Div(id="report-card-form"),
                        html.Hr(),
                        dbc.Button(
                            "Download PDF",
                            id="download-report-btn",
                            color="success",
                            className="mb-3",
                        ),
                        dcc.Download(id="download-report-pdf"),
                        html.Div(id="report-card-preview"),
                    ]
                )
            )
        ]
    )


def register_Callbacks(app):

    @app.callback(
        Output("report-card-form", "children"),
        Input("load-template-btn", "n_clicks"),
        Input("selected-student-data", "data"),
        State("rc-class", "value"),
        State("session", "data"),
        prevent_initial_call=True,
    )
    def load_template(n, student, class_no, SessionData):

        username = SessionData["username"]

        # -----------------------
        # LOAD SAVED MARKS
        # -----------------------
        saved_marks = {}
        if student:
            saved_marks = load_saved_marks(username, student)

        # -----------------------
        # LOAD TEMPLATE
        # -----------------------
        path = f"/var/Data/{username}/report_templates.csv"

        if not os.path.exists(path):
            return dbc.Alert("No template found", color="danger")

        df = pd.read_csv(path)
        df["class"] = df["class"].astype(str)

        row = df[df["class"] == str(class_no)]

        if row.empty:
            return dbc.Alert("Template not found for this class", color="warning")

        row = row.iloc[0]

        subjects = row["subjects"].split(",")
        exams = row["exams"].split(",")
        marks_list = str(row["marks"]).split(",")
        pass_list = str(row.get("passing_marks", "")).split(",")

        exam_max = {}
        exam_pass ={}
        for i in range(len(exams)):
          exam_max[exams[i]] = int(marks_list[i]) if i < len(marks_list) else None
          exam_pass[exams[i]] = int(float(pass_list[i])) if i < len(pass_list) and pass_list[i] != "" else 0
        extra_cols = []
        if pd.notna(row["extra_columns"]):
            extra_cols = row["extra_columns"].split(",")

        # -----------------------
        # EXAM TABLE
        # -----------------------
        exam_header = [html.Th("Subject")] + [html.Th(e) for e in exams]

        exam_rows = []

        for sub in subjects:
            cells = [html.Td(sub)]

            for e in exams:
                col = f"{sub}_{e}"
                value = saved_marks.get(col)

                cells.append(
                    html.Td(
                        dbc.Input(
                            id={"type": "marks-input", "subject": sub, "exam": e},
                            type="number",
                            value=value,
                            placeholder=f"{e} (Max {exam_max.get(e,'')})",
                        )
                    )
                )

            exam_rows.append(html.Tr(cells))

        exam_table = dbc.Table(
            [html.Thead(html.Tr(exam_header)), html.Tbody(exam_rows)],
            bordered=True,
            striped=True,
        )

        # -----------------------
        # EXTRA ACTIVITIES TABLE
        # -----------------------
        extra_table = None

        if extra_cols:

            extra_rows = []

            for col in extra_cols:

                name, col_type = col.split(":")

                if col_type == "marks":
                    value = saved_marks.get(name)
                    inp = dbc.Input(
                        id={"type": "extra-marks", "col": name},
                        type="number",
                        value=value,
                        placeholder="Marks",
                    )
                else:
                    value = saved_marks.get(name)
                    inp = dbc.Input(
                        id={"type": "extra-grade", "col": name},
                        value=value,
                        placeholder="Grade",
                    )

                extra_rows.append(html.Tr([html.Td(name), html.Td(inp)]))

            extra_table = dbc.Table(
                [
                    html.Thead(
                        html.Tr([html.Th("Activity"), html.Th("Marks / Grade")])
                    ),
                    html.Tbody(extra_rows),
                ],
                bordered=True,
                striped=True,
                className="mt-4",
            )

        # -----------------------
        # FINAL LAYOUT
        # -----------------------
        return html.Div(
            [
                html.H5("Exam Marks"),
                exam_table,
                html.H5("Extracurricular activities", className="mt-4"),
                extra_table if extra_table else html.Div(),
            ]
        )

    @app.callback(
        Output("report-card-preview", "children"),
        Input({"type": "marks-input", "subject": ALL, "exam": ALL}, "value"),
        State({"type": "marks-input", "subject": ALL, "exam": ALL}, "id"),
        State({"type": "extra-marks", "col": ALL}, "value"),
        State({"type": "extra-marks", "col": ALL}, "id"),
        State({"type": "extra-grade", "col": ALL}, "value"),
        State({"type": "extra-grade", "col": ALL}, "id"),
        State("selected-student-data", "data"),
        State("session", "data"),
        prevent_initial_call=True,
    )
    def preview_report(
    marks,
    ids,
    extra_marks,
    extra_marks_ids,
    extra_grades,
    extra_grade_ids,
    student,
    SessionData,
):

     if not student:
        return ""

    # -------------------
    # Exam Data
    # -------------------
     exam_data = {}

     for i in range(len(ids)):
        subject = ids[i]["subject"]
        exam = ids[i]["exam"]
        mark = marks[i]

        if subject not in exam_data:
            exam_data[subject] = {}

        exam_data[subject][exam] = mark

    # -------------------
    # Extra Activities
    # -------------------
     extra_data = []

     for i in range(len(extra_marks_ids)):
        extra_data.append(
            {"name": extra_marks_ids[i]["col"], "marks": extra_marks[i]}
        )

     for i in range(len(extra_grade_ids)):
        extra_data.append(
            {"name": extra_grade_ids[i]["col"], "grade": extra_grades[i]}
        )

    # -------------------
    # Logo Load
    # -------------------
     username = SessionData["username"]

     logo_path = f"/var/Data/{username}/school_fees_logo.png"

     logo_base64 = ""

     if os.path.exists(logo_path):
        with open(logo_path, "rb") as f:
            logo_base64 = base64.b64encode(f.read()).decode()

        logo_base64 = f"data:image/png;base64,{logo_base64}"

     school_info = load_school_info(username)

     school = {
        "name": school_info["name"],
        "address": school_info["address"],
        "pan": school_info["pan"],
        "logo": logo_base64,
    }

    # -------------------
    # 🔥 LOAD TEMPLATE (MAX MARKS)
    # -------------------
     template_path = f"/var/Data/{username}/report_templates.csv"

     exam_max = {}
     exam_pass={}

     if os.path.exists(template_path):
        df = pd.read_csv(template_path)

        df["class"] = df["class"].astype(str)

        row = df[df["class"] == str(student["class_id"])]

        if not row.empty:
            row = row.iloc[0]

            exams = str(row["exams"]).split(",")
            marks_list = str(row["marks"]).split(",")
            pass_list = str(row.get("passing_marks", "")).split(",")

            for i in range(len(exams)):
                exam_max[exams[i]] = int(marks_list[i]) if i < len(marks_list) else 0
                exam_pass[exams[i]] = int(float(pass_list[i])) if i < len(pass_list) and pass_list[i] != "" else 0
    # -------------------
    # FINAL CALL
    # -------------------
     return Template.report_card_template(
        student,
        exam_data,
        extra_data,
        school,
        exam_max ,
          exam_pass  # ✅ NEW PARAM
    )


    @app.callback(
        Output("selected-student-data", "data"),
        Input("student-search-dropdown", "value"),
        State("session", "data"),
        State("rc-class", "value"),
        State("rc-section", "value"),
    )
    def load_student(student_id, SessionData, class_no, section):

        if not student_id:
            return None

        username = SessionData["username"]

        # -----------------------
        # NORMALIZE SECTION
        # -----------------------
        def normalize_section(sec):
         if sec is None or str(sec).strip() == "":
          return ""
         return str(sec).strip()

        section = normalize_section(section)

        # -----------------------
        # STUDENT LOG
        # -----------------------
        student_path = f"/var/Data/{username}/student_log.csv"

        if not os.path.exists(student_path):
            return None

        df = pd.read_csv(student_path)

        row = df[df["student_id"] == student_id]

        if row.empty:
            return None

        row = row.iloc[0]

        admission_no_raw = row["admission_no"]
        admission_no = str(admission_no_raw).strip().lower()

        # -----------------------
        # ATTENDANCE LOAD
        # -----------------------
        att_path = f"/var/Data/{username}/student_attendance.csv"

        attendance_summary = {
            "present": 0,
            "absent": 0,
            "holiday": 0,
            "total": 0,
            "percentage": 0,
        }

        if os.path.exists(att_path):

            att_df = pd.read_csv(att_path)

            att_df["admission_no"] = (
                att_df["admission_no"].astype(str).str.strip().str.lower()
            )

            att_df = att_df[att_df["admission_no"] == admission_no]

            if not att_df.empty:

                total = len(att_df)
                present = len(att_df[att_df["status"] == "present"])
                absent = len(att_df[att_df["status"] == "absent"])
                holiday = len(att_df[att_df["status"] == "holiday"])

                percentage = (present / (present + absent)) * 100 if total > 0 else 0

                attendance_summary = {
                    "present": present,
                    "absent": absent,
                    "holiday": holiday,
                    "total": total,
                    "percentage": round(percentage, 2),
                }

        # -----------------------
        # CLASS NAME SAFE
        # -----------------------
        class_name = get_class_name(username, class_no) if class_no is not None else ""

        # -----------------------
        # FINAL STUDENT OBJECT
        # -----------------------
        student = {
             "student_id": row["student_id"], 
            "name": row["student_name"],
            "class": class_name,  # display
            "class_id": class_no,  # backend
            "section": section,  # normalized
            "roll": admission_no,  # normalized string
            "father": row["father_name"],
            "session": "2025-26",
            "remarks": "",
            "attendance": attendance_summary,
        }

        return student

    @app.callback(
        Output("student-search-dropdown", "options"),
        Input("rc-class", "value"),
        Input("student-search-type", "value"),
        State("session", "data"),
    )
    def load_students(class_no, search_type, SessionData):

        if class_no is None:
            return []

        username = SessionData["username"]
        path = f"/var/Data/{username}/student_log.csv"

        if not os.path.exists(path):
            return []

        df = pd.read_csv(path)

        # -----------------------
        # FIX 1: CLASS FILTER (type-safe)
        # -----------------------
        df["studying_class"] = (
            pd.to_numeric(df["studying_class"], errors="coerce").fillna(-1).astype(int)
        )

        df = df[df["studying_class"] == int(class_no)]

        # -----------------------
        # FIX 2: CLEAN ADMISSION NO (OUTSIDE LOOP)
        # -----------------------
        df["admission_no"] = df["admission_no"].astype(str).str.strip()

        # -----------------------
        # BUILD OPTIONS
        # -----------------------
        options = []

        for _, row in df.iterrows():

            label = f"{row['student_name']} ({row['admission_no']})"

            options.append({"label": label, "value": row["student_id"]})

        return options

    @app.callback(
        Output("download-report-pdf", "data"),
        Input("download-report-btn", "n_clicks"),
        State({"type": "marks-input", "subject": ALL, "exam": ALL}, "value"),
        State({"type": "marks-input", "subject": ALL, "exam": ALL}, "id"),
        State({"type": "extra-marks", "col": ALL}, "value"),
        State({"type": "extra-marks", "col": ALL}, "id"),
        State({"type": "extra-grade", "col": ALL}, "value"),
        State({"type": "extra-grade", "col": ALL}, "id"),
        State("selected-student-data", "data"),
        State("session", "data"),
        prevent_initial_call=True,
    )
    def download_pdf(
    n,
    marks,
    ids,
    extra_marks,
    extra_marks_ids,
    extra_grades,
    extra_grade_ids,
    student,
    SessionData,
):

     if not student:
        return

    # -------------------
    # Exam Data
    # -------------------
     exam_data = {}

     for i in range(len(ids)):
        subject = ids[i]["subject"]
        exam = ids[i]["exam"]
        mark = marks[i]

        if subject not in exam_data:
            exam_data[subject] = {}

        exam_data[subject][exam] = mark

    # -------------------
    # Extra Activities
    # -------------------
     extra_data = []

     for i in range(len(extra_marks_ids)):
        extra_data.append(
            {"name": extra_marks_ids[i]["col"], "marks": extra_marks[i]}
        )

     for i in range(len(extra_grade_ids)):
        extra_data.append(
            {"name": extra_grade_ids[i]["col"], "grade": extra_grades[i]}
        )

    # -------------------
    # School Info
    # -------------------
     username = SessionData["username"]

     logo_path = f"/var/Data/{username}/school_fees_logo.png"
     logo_base64 = ""

     if os.path.exists(logo_path):
        with open(logo_path, "rb") as f:
            logo_base64 = base64.b64encode(f.read()).decode()

        logo_base64 = f"data:image/png;base64,{logo_base64}"

     school_info = load_school_info(username)

     school = {
        "name": school_info["name"],
        "address": school_info["address"],
        "pan": school_info["pan"],
        "logo": logo_base64,
    }

    # -------------------
    # 🔥 LOAD TEMPLATE (MAX MARKS)
    # -------------------
     template_path = f"/var/Data/{username}/report_templates.csv"
     exam_max = {}
     exam_pass={}
     if os.path.exists(template_path):
        df = pd.read_csv(template_path)
        df["class"] = df["class"].astype(str)
        row = df[df["class"] == str(student["class_id"])]
        if not row.empty:
            row = row.iloc[0]

            exams = str(row["exams"]).split(",")
            marks_list = str(row["marks"]).split(",")
            pass_list = str(row.get("passing_marks", "")).split(",")

            for i in range(len(exams)):
                exam_max[exams[i]] = int(marks_list[i]) if i < len(marks_list) else 0
                exam_pass[exams[i]] = int(float(pass_list[i])) if i < len(pass_list) and pass_list[i] != "" else 0

    # -------------------
    # PDF GENERATION
    # -------------------
     pdf_buffer = Template.generate_report_card_pdf(
    student,
    exam_data,
    extra_data,
    school,
    exam_max,
    exam_pass   # ✅ add
)

     return dcc.send_bytes(pdf_buffer.getvalue(), filename="report_card.pdf")

    @app.callback(
        Output("report-card-preview", "children", allow_duplicate=True),
        Input("save-marks-btn", "n_clicks"),
        State({"type": "marks-input", "subject": ALL, "exam": ALL}, "value"),
        State({"type": "marks-input", "subject": ALL, "exam": ALL}, "id"),
        State("selected-student-data", "data"),
        State("session", "data"),
        prevent_initial_call=True,
    )
    def save_marks(n, marks, ids, student, SessionData):

        if not student:
            return ""

        exam_data = {}

        for i in range(len(ids)):
            subject = ids[i]["subject"]
            exam = ids[i]["exam"]
            mark = marks[i]

            if subject not in exam_data:
                exam_data[subject] = {}

            exam_data[subject][exam] = mark

        username = SessionData["username"]

        save_marks_csv(username, student, exam_data)

        return dbc.Alert("Marks Saved Successfully", color="success")
