from dash import html
import dash_bootstrap_components as dbc
import io
import base64
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib.utils import ImageReader
from reportlab.platypus import Table, TableStyle
from reportlab.lib import colors


def generate_report_card_pdf(student, exam_data, extra_data, school, exam_max, exam_pass):

    buffer = io.BytesIO()
    c = canvas.Canvas(buffer, pagesize=A4)

    width, height = A4
    y = height - 50

    # -------------------
    # SCHOOL HEADER
    # -------------------

    section = student.get("section")
    class_text = f"{student['class']} - {section}" if section else student["class"]

    if school.get("logo"):
        try:
            imgdata = base64.b64decode(school["logo"].split(",")[1])
            img = ImageReader(io.BytesIO(imgdata))
            c.drawImage(img, width/2-40, y-60, 80, 60)
        except:
            pass

    y -= 80

    c.setFont("Helvetica-Bold", 16)
    c.drawCentredString(width/2, y, school["name"])

    y -= 20
    c.setFont("Helvetica", 11)
    c.drawCentredString(width/2, y, school["address"])

    y -= 30
    c.setFont("Helvetica-Bold", 14)
    c.drawCentredString(width/2, y, "REPORT CARD")

    y -= 15
    c.line(40, y, width-40, y)

    # -------------------
    # STUDENT INFO
    # -------------------

    y -= 40
    c.setFont("Helvetica", 11)

    c.drawString(50, y, f"Name: {student['name']}")
    c.drawString(300, y, f"Roll No: {student['roll']}")

    y -= 20
    c.drawString(50, y, f"Class: {class_text}")
    c.drawString(300, y, f"Session: {student['session']}")

    y -= 20
    c.drawString(50, y, f"Father: {student['father']}")

    y -= 15
    c.line(40, y, width-40, y)

    # -------------------
    # EXAM MARKS TABLE
    # -------------------

    y -= 40

    subjects = list(exam_data.keys())

    exams = set()
    for sub in exam_data.values():
        exams.update(sub.keys())

    exams = list(exams)

    table_data = []
    header = ["Subject"] + exams + ["Total"]
    table_data.append(header)

    grand_total = 0

    for sub in subjects:

        row = [sub]
        subject_total = 0

        for e in exams:

            mark = exam_data[sub].get(e, "")

            if mark not in ["", None]:
                mark = float(mark)
                subject_total += mark
                if mark < exam_pass.get(e, 0):
                  mark = f"{mark} (F)"
                else:
                 mark = f"{mark} (P)"

            row.append(mark)

        row.append(subject_total)
        grand_total += subject_total
        table_data.append(row)

    # -------------------
    # RESPONSIVE COLUMN WIDTH
    # -------------------

    available_width = width - 80

    subject_width = 180
    total_width = 80

    remaining_width = available_width - subject_width - total_width

    exam_width = remaining_width / len(exams) if len(exams) > 0 else remaining_width

    if exam_width < 40:
        exam_width = 40

    col_widths = [subject_width] + [exam_width]*len(exams) + [total_width]

    table = Table(table_data, colWidths=col_widths)

    table.setStyle(TableStyle([

        ("BACKGROUND",(0,0),(-1,0),colors.HexColor("#dce8d6")),
        ("TEXTCOLOR",(0,0),(-1,0),colors.HexColor("#2e5d34")),

        ("GRID",(0,0),(-1,-1),0.5,colors.grey),

        ("FONTNAME",(0,0),(-1,0),"Helvetica-Bold"),

        ("ALIGN",(1,1),(-1,-1),"CENTER"),

        ("ROWBACKGROUNDS",(0,1),(-1,-1),[colors.white, colors.HexColor("#f7f7f7")])

    ]))

    if len(exams) > 6:
        table.setStyle([("FONTSIZE",(0,0),(-1,-1),8)])

    table.wrapOn(c,width,height)
    table.drawOn(c,40,y-(22*len(table_data)))

    y = y - (22*len(table_data)) - 20

    c.line(40, y, width-40, y)


    # -------------------
# ATTENDANCE TABLE
# -------------------

    attendance = student.get("attendance", {})

    attendance_data = [
    ["Total Days", attendance.get("total", 0), "Present", attendance.get("present", 0)],
    ["Absent", attendance.get("absent", 0), "Holiday", attendance.get("holiday", 0)],
    ["Attendance %", f"{attendance.get('percentage', 0)}%", "", ""]
]

    table_att = Table(attendance_data, colWidths=[120,120,120,120])

    table_att.setStyle(TableStyle([
    ("GRID",(0,0),(-1,-1),0.5,colors.grey),
    ("FONTNAME",(0,0),(-1,-1),"Helvetica"),
    ("ALIGN",(0,0),(-1,-1),"CENTER"),
    ("BACKGROUND",(0,0),(-1,0),colors.whitesmoke),
]))

    y  -= 80
    table_att.wrapOn(c, width, height)
    table_att.drawOn(c, 50, y)

    y -= 20
    c.line(40, y, width-40, y)


    # -------------------
    # EXTRACURRICULAR
    # -------------------

    y -= 20

    c.setFont("Helvetica-Bold",12)
    c.drawString(50,y,"Extracurricular Activities")

    y -= 20

    extra_table = [["Activity","Marks / Grade"]]

    for item in extra_data:

        value = item.get("marks")

        if value in ["",None]:
            value = item.get("grade","")

        extra_table.append([item["name"], value])

    table2 = Table(extra_table,colWidths=[250,250])

    table2.setStyle(TableStyle([

        ("BACKGROUND",(0,0),(-1,0),colors.HexColor("#dce8d6")),
        ("TEXTCOLOR",(0,0),(-1,0),colors.HexColor("#2e5d34")),

        ("GRID",(0,0),(-1,-1),0.5,colors.grey),

        ("FONTNAME",(0,0),(-1,0),"Helvetica-Bold"),

        ("ROWBACKGROUNDS",(0,1),(-1,-1),[colors.white, colors.HexColor("#f7f7f7")])

    ]))

    table2.wrapOn(c,width,height)
    table2.drawOn(c,50,y-(20*len(extra_table)))

    y = y - (20*len(extra_table)) - 40

    # -------------------
    # RESULT
    # -------------------

    max_marks = 0

    for sub in subjects:
     for e in exams:
        max_marks += exam_max.get(e, 0)
    percentage = 0

    if max_marks > 0:
        percentage = round((grand_total/max_marks)*100,2)

    c.setFont("Helvetica-Bold",11)

    c.drawString(50,y,f"Total Obtained: {grand_total}")
    c.drawString(250,y,f"Maximum Marks: {max_marks}")
    c.drawString(450,y,f"Percentage: {percentage}%")

    y -= 60

    # -------------------
    # SIGNATURES
    # -------------------

    c.line(80,y,200,y)
    c.drawCentredString(140,y-15,"Class Teacher")

    c.line(260,y,380,y)
    c.drawCentredString(320,y-15,"Exam Incharge")

    c.line(440,y,560,y)
    c.drawCentredString(500,y-15,"Principal")

    c.save()
    buffer.seek(0)

    return buffer

def report_card_template(student, exam_data, extra_data, school, exam_max, exam_pass):

    subjects = list(exam_data.keys())

    exams = set()
    for sub in exam_data.values():
        exams.update(sub.keys())

    exams = list(exams)

    # ---------- HEADER ----------

    header = [html.Th("Subject")]

    for e in exams:
        header.append(html.Th(e))

    header.append(html.Th("Total"))

    rows = []

    grand_total = 0

    # ---------- SUBJECT ROWS ----------

    for sub in subjects:

        row = [html.Td(sub)]

        subject_total = 0
        subject_max=0

        for e in exams:

         mark = exam_data[sub].get(e, "")
         status = ""
     
         if mark not in [None, ""]:
             mark = float(mark)
             subject_total += mark
     
             # 🔥 FAIL CHECK
             if mark < exam_pass.get(e, 0):
                 status = "FAIL"
             else:
                 status = "PASS"
     
         subject_max += exam_max.get(e, 0)
     
         row.append(
        html.Td(
            [
                mark,
                html.Br(),
                html.Small(
                    status,
                    style={"color": "red"} if status == "FAIL" else {"color": "green"},
                ),
            ]
        )
    )
        row.append(html.Td(html.B(subject_total)))

        grand_total += subject_total

        rows.append(html.Tr(row))

    # ---------- MAX MARKS ----------

    max_marks =0
    for sub in subjects:
        for e in exams:
            max_marks+=exam_max.get(e,0)

    percentage = 0
    if max_marks > 0:
        percentage = round((grand_total / max_marks) * 100, 2)

    # ---------- EXTRA ACTIVITIES ----------

    extra_rows = []

    for item in extra_data:

        value = item.get("marks")
        if value in [None, ""]:
            value = item.get("grade", "")

        extra_rows.append(
            html.Tr([
                html.Td(item.get("name")),
                html.Td(value)
            ])
        )

    attendance = student.get("attendance", {})

    attendance_table = dbc.Table(

    [
        html.Tbody([

            html.Tr([
                html.Th("Total Days"),
                html.Td(attendance.get("total", 0)),
                html.Th("Present"),
                html.Td(attendance.get("present", 0)),
            ]),

            html.Tr([
                html.Th("Absent"),
                html.Td(attendance.get("absent", 0)),
                html.Th("Holiday"),
                html.Td(attendance.get("holiday", 0)),
            ]),

            html.Tr([
                html.Th("Attendance %"),
                html.Td(
                    f"{attendance.get('percentage', 0)}%",
                    colSpan=3,
                    className="fw-bold text-center"
                ),
            ]),

        ])
    ],

    bordered=True,
    striped=True,
    className="mb-3 text-center"
) 

        

    # ---------- LAYOUT ----------

    return dbc.Card(

        dbc.CardBody([

            # SCHOOL HEADER

            html.Div(

                [
                    html.Img(
                        src=school.get("logo"),
                        style={
                            "height": "80px",
                            "display": "block",
                            "margin": "auto",
                        },
                    ),

                    html.H4(
                        school.get("name", ""),
                        className="text-center fw-bold mt-2"
                    ),

                    html.P(
                        school.get("address", ""),
                        className="text-center text-muted"
                    ),

                    html.H4(
                        "REPORT CARD",
                        className="text-center fw-bold mt-2"
                    ),

                ]
            ),

            html.Hr(),

            # STUDENT INFO BOX

            dbc.Row(

                [
                    dbc.Col(html.P(f"Name: {student['name']}"), md=4),
                    dbc.Col(
                        html.P(
                            f"Class: {student['class']} - {student.get('section','')}"
                        ),
                        md=4
                    ),
                    dbc.Col(html.P(f"Roll No: {student['roll']}"), md=4),
                ],

                className="mb-2",
            ),

            dbc.Row(

                [
                    dbc.Col(html.P(f"Father: {student['father']}"), md=6),
                    dbc.Col(html.P(f"Session: {student['session']}"), md=6),
                ],

                className="mb-3",
            ),

            html.Hr(),

            # EXAM TABLE

            html.H5("Exam Marks", className="fw-bold"),

            dbc.Table(

                [
                    html.Thead(html.Tr(header)),
                    html.Tbody(rows),
                ],

                bordered=True,
                striped=True,
                hover=True,
                responsive=True,
                className="mt-2",
            ),

            html.Br(),
            html.Hr(),
            attendance_table,

            # EXTRA ACTIVITIES

            html.H5("Extracurricular Activities", className="fw-bold"),

            dbc.Table(

                [
                    html.Thead(
                        html.Tr(
                            [
                                html.Th("Activity"),
                                html.Th("Marks / Grade"),
                            ]
                        )
                    ),
                    html.Tbody(extra_rows),
                ],

                bordered=True,
                striped=True,
                hover=True,
                responsive=True,
            ),

            html.Hr(),

            # RESULT SUMMARY

            dbc.Row(

                [
                    dbc.Col(
                        html.H5(f"Total Obtained: {grand_total}"),
                        md=4
                    ),
                    dbc.Col(
                        html.H5(f"Maximum Marks: {max_marks}"),
                        md=4
                    ),
                    dbc.Col(
                        html.H5(f"Percentage: {percentage}%"),
                        md=4
                    ),
                ],

                className="mt-2",
            ),

            html.Br(),

            # SIGNATURES

            dbc.Row(

                [
                    dbc.Col(
                        html.Div(
                            [
                                html.Hr(),
                                html.P("Class Teacher", className="text-center"),
                            ]
                        ),
                        md=4,
                    ),

                    dbc.Col(
                        html.Div(
                            [
                                html.Hr(),
                                html.P("Exam Incharge", className="text-center"),
                            ]
                        ),
                        md=4,
                    ),

                    dbc.Col(
                        html.Div(
                            [
                                html.Hr(),
                                html.P("Principal", className="text-center"),
                            ]
                        ),
                        md=4,
                    ),
                ],

                className="mt-4",
            ),

        ]),

        className="shadow-lg p-3",
    )