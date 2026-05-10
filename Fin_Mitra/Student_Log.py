import dash
from dash import html, dcc, Input, Output, State
import dash_bootstrap_components as dbc
import pandas as pd
import os
import io
from datetime import datetime

# --------------------------------------------------
# Layout
# --------------------------------------------------

# NEW — content only (no tabs)


def get_create_student_content(SessionData):
    return create_student_form(SessionData)


def get_search_student_content(SessionData):
    return search_student_layout(SessionData)


def get_layout1(SessionData):
    return dbc.Container(
        [
            html.H3(
                "STUDENT LOG",
                className="text-center my-3",
                style={"color": "#1B5E20", "fontWeight": "700"},
            ),
            dbc.Tabs(
                [
                    dbc.Tab(label="Create Student", tab_id="create-student"),
                    dbc.Tab(label="Search Student", tab_id="search-student"),
                ],
                id="student-tabs",
                active_tab="create-student",
            ),
            html.Div(id="student-tab-content", className="mt-4"),
        ],
        fluid=True,
    )


# --------------------------------------------------
# Create Student Form - Rajasthan Government Format
# --------------------------------------------------


def create_student_form(SessionData):
    return dbc.Card(
        dbc.CardBody(
            [
                html.H5(
                    "Student Profile Data Entry",
                    className="mb-4",
                    style={"color": "#1B5E20", "fontWeight": "600"},
                ),
                # Section 1: Student Identification and Personal Details
                html.Hr(),
                html.H6(
                    "Student Identification and Personal Details",
                    className="mb-3",
                    style={"color": "#388E3C", "fontWeight": "600"},
                ),
                dbc.Row(
                    [
                        dbc.Col(
                            [
                                dbc.Label(
                                    [
                                        "Student's AADHAAR Number",
                                        html.Span(" *", style={"color": "red"}),
                                    ]
                                ),
                                dbc.Input(
                                    id="stu-aadhaar",
                                    placeholder="Enter AADHAAR Number",
                                    type="text",
                                ),
                            ],
                            md=6,
                            className="mb-3",
                        ),
                        dbc.Col(
                            [
                                dbc.Label(
                                    [
                                        "Student Name",
                                        html.Span(" *", style={"color": "red"}),
                                    ]
                                ),
                                dbc.Input(
                                    id="stu-name",
                                    placeholder="Enter Student Name",
                                    type="text",
                                ),
                            ],
                            md=6,
                            className="mb-3",
                        ),
                    ]
                ),
                dbc.Row(
                    [
                        dbc.Col(
                            [
                                dbc.Label(
                                    [
                                        "Father’s Name",
                                        html.Span(" *", style={"color": "red"}),
                                    ]
                                ),
                                dbc.Input(
                                    id="father-name",
                                    placeholder="Enter Father's Name",
                                    type="text",
                                ),
                            ],
                            md=6,
                            className="mb-3",
                        ),
                        dbc.Col(
                            [
                                dbc.Label(
                                    [
                                        "Mother’s Name",
                                        html.Span(" *", style={"color": "red"}),
                                    ]
                                ),
                                dbc.Input(
                                    id="mother-name",
                                    placeholder="Enter Mother's Name",
                                    type="text",
                                ),
                            ],
                            md=6,
                            className="mb-3",
                        ),
                    ]
                ),
                dbc.Row(
                    [
                        dbc.Col(
                            [
                                dbc.Label(
                                    [
                                        "Date of Birth",
                                        html.Span(" *", style={"color": "red"}),
                                    ]
                                ),
                                dbc.Input(
                                    id="stu-dob", type="date", placeholder="dd/mm/yyyy"
                                ),
                            ],
                            md=6,
                            className="mb-3",
                        ),
                        dbc.Col(
                            [
                                dbc.Label(
                                    ["Gender", html.Span(" *", style={"color": "red"})]
                                ),
                                dcc.Dropdown(
                                    id="stu-gender",
                                    options=[
                                        {"label": "Boy", "value": "1"},
                                        {"label": "Girl", "value": "2"},
                                        {"label": "Other/Transgender", "value": "3"},
                                    ],
                                    placeholder="--Select--",
                                ),
                            ],
                            md=6,
                            className="mb-3",
                        ),
                    ]
                ),
                dbc.Row(
                    [
                        dbc.Col(
                            [
                                dbc.Label(
                                    [
                                        "Caste Category",
                                        html.Span(" *", style={"color": "red"}),
                                    ]
                                ),
                                dcc.Dropdown(
                                    id="stu-caste",
                                    options=[
                                        {"label": "GEN", "value": "1"},
                                        {"label": "SC", "value": "2"},
                                        {"label": "ST", "value": "3"},
                                        {"label": "OBC", "value": "4"},
                                        {"label": "SBC", "value": "5"},
                                    ],
                                    placeholder="--Select--",
                                ),
                            ],
                            md=6,
                            className="mb-3",
                        ),
                        dbc.Col(
                            [
                                dbc.Label(
                                    [
                                        "Religion",
                                        html.Span(" *", style={"color": "red"}),
                                    ]
                                ),
                                dcc.Dropdown(
                                    id="stu-religion",
                                    options=[
                                        {"label": "Hindu", "value": "0"},
                                        {"label": "Muslim", "value": "5"},
                                        {"label": "Christian", "value": "6"},
                                        {"label": "Sikh", "value": "7"},
                                        {"label": "Buddhist", "value": "8"},
                                        {"label": "Parsi", "value": "9"},
                                        {"label": "Jain", "value": "10"},
                                        {"label": "Others", "value": "11"},
                                    ],
                                    placeholder="--Select--",
                                ),
                            ],
                            md=6,
                            className="mb-3",
                        ),
                    ]
                ),
                dbc.Row(
                    [
                        dbc.Col(
                            [
                                dbc.Label(
                                    [
                                        "Mother Tongue/मातृभाषा",
                                        html.Span(" *", style={"color": "red"}),
                                    ]
                                ),
                                dcc.Dropdown(
                                    id="stu-mother-tongue",
                                    options=[
                                        {"label": "--Select--", "value": "-1"},
                                        {"label": "Hindi", "value": "4"},
                                        {"label": "English", "value": "19"},
                                        {"label": "Rajasthani", "value": "56"},
                                        {"label": "Urdu", "value": "18"},
                                        {"label": "Sanskrit", "value": "14"},
                                        {"label": "Sindhi", "value": "15"},
                                        {"label": "Punjabi", "value": "13"},
                                        {"label": "Gujarati", "value": "3"},
                                        {"label": "Bengali", "value": "2"},
                                        {"label": "Kannada", "value": "5"},
                                        {"label": "Kashmiri", "value": "6"},
                                        {"label": "Konkani", "value": "7"},
                                        {"label": "Malayalam", "value": "8"},
                                        {"label": "Manipuri", "value": "9"},
                                        {"label": "Marathi", "value": "10"},
                                        {"label": "Nepali", "value": "11"},
                                        {"label": "Oriya", "value": "12"},
                                        {"label": "Tamil", "value": "16"},
                                        {"label": "Telugu", "value": "17"},
                                        {"label": "Assamese", "value": "1"},
                                        {"label": "Bodo", "value": "20"},
                                        {"label": "Mising", "value": "21"},
                                        {"label": "Dogri", "value": "22"},
                                        {"label": "Khasi", "value": "23"},
                                        {"label": "Garo", "value": "24"},
                                        {"label": "Mizo", "value": "25"},
                                        {"label": "Bhutia", "value": "26"},
                                        {"label": "Lepcha", "value": "27"},
                                        {"label": "Limboo", "value": "28"},
                                        {"label": "French", "value": "29"},
                                        {"label": "Angami", "value": "41"},
                                        {"label": "Ao", "value": "42"},
                                        {"label": "Arabic", "value": "43"},
                                        {"label": "Bhoti", "value": "44"},
                                        {"label": "Bodhi", "value": "45"},
                                        {"label": "German", "value": "46"},
                                        {"label": "Kakbarak", "value": "47"},
                                        {"label": "Konyak", "value": "48"},
                                        {"label": "Laddakhi", "value": "49"},
                                        {"label": "Lotha", "value": "50"},
                                        {"label": "Maithili", "value": "51"},
                                        {"label": "Nicobaree", "value": "52"},
                                        {"label": "Oriya(lower)", "value": "53"},
                                        {"label": "Persian", "value": "54"},
                                        {"label": "Portuguese", "value": "55"},
                                        {"label": "Russian", "value": "57"},
                                        {"label": "Sema", "value": "58"},
                                        {"label": "Spanish", "value": "59"},
                                        {"label": "Tibetan", "value": "60"},
                                        {"label": "Zeliang", "value": "61"},
                                        {"label": "Other languages", "value": "99"},
                                    ],
                                    placeholder="--Select--",
                                ),
                            ],
                            md=6,
                            className="mb-3",
                        ),
                        dbc.Col(
                            [
                                dbc.Label("Jan Aadhar No."),
                                dbc.Input(
                                    id="stu-jan-aadhar",
                                    placeholder="Enter Jan Aadhar Number",
                                    type="text",
                                ),
                            ],
                            md=6,
                            className="mb-3",
                        ),
                    ]
                ),
                dbc.Row(
                    [
                        dbc.Col(
                            [
                                dbc.Label(
                                    [
                                        "Rural/Urban",
                                        html.Span(" *", style={"color": "red"}),
                                    ]
                                ),
                                dcc.Dropdown(
                                    id="stu-rural-urban",
                                    options=[
                                        {"label": "Rural", "value": "R"},
                                        {"label": "Urban", "value": "U"},
                                    ],
                                    placeholder="--Select--",
                                ),
                            ],
                            md=6,
                            className="mb-3",
                        ),
                        dbc.Col(
                            [
                                dbc.Label(
                                    [
                                        "Name of Habitation or Locality/पता",
                                        html.Span(" *", style={"color": "red"}),
                                    ]
                                ),
                                dbc.Input(
                                    id="stu-address",
                                    placeholder="Enter Address",
                                    type="text",
                                ),
                            ],
                            md=6,
                            className="mb-3",
                        ),
                    ]
                ),
                # Section 2: Admission and Academic Details
                html.Hr(),
                html.H6(
                    "Admission and Academic Details",
                    className="mb-3",
                    style={"color": "#388E3C", "fontWeight": "600"},
                ),
                dbc.Row(
                    [
                        dbc.Col(
                            [
                                dbc.Label(
                                    [
                                        "Date of Admission",
                                        html.Span(" *", style={"color": "red"}),
                                    ]
                                ),
                                dbc.Input(
                                    id="stu-admission-date",
                                    type="date",
                                    placeholder="dd/mm/yyyy",
                                ),
                            ],
                            md=6,
                            className="mb-3",
                        ),
                        dbc.Col(
                            [
                                dbc.Label(
                                    [
                                        "Admission No. / SR No",
                                        html.Span(" *", style={"color": "red"}),
                                    ]
                                ),
                                dbc.Input(
                                    id="stu-admission-no",
                                    placeholder="Enter Admission Number",
                                    type="text",
                                ),
                            ],
                            md=6,
                            className="mb-3",
                        ),
                    ]
                ),
                dbc.Row(
                    [
                        dbc.Col(
                            [
                                dbc.Label(
                                    [
                                        "Current Academic Year",
                                        html.Span(" *", style={"color": "red"}),
                                    ]
                                ),
                                dbc.Input(
                                    id="stu-current-academic-year",
                                    type="date",
                                    placeholder="dd/mm/yyyy",
                                ),
                            ],
                            md=6,
                            className="mb-3",
                        ),

                        dbc.Col(
                            [
                                dbc.Label(
                                    [
                                        "Monthly Fee Concession",
                                        html.Span(" *", style={"color": "red"}),
                                    ]
                                ),
                                dbc.Input(
                                    id="stu-concession",
                                    placeholder="Enter Amount",
                                    type="text",
                                ),
                            ],
                            md=6,
                            className="mb-3",
                        ),
                    ]
                ),
                dbc.Row(
                    [
                        dbc.Col(
                            [
                                dbc.Label(
                                    [
                                        "Whether belong to Below Poverty Line",
                                        html.Span(" *", style={"color": "red"}),
                                    ]
                                ),
                                dcc.Dropdown(
                                    id="stu-bpl",
                                    options=[
                                        {"label": "Yes", "value": "1"},
                                        {"label": "No", "value": "2"},
                                    ],
                                    placeholder="--Select--",
                                ),
                            ],
                            md=6,
                            className="mb-3",
                        ),
                        dbc.Col(
                            [
                                dbc.Label(
                                    [
                                        "Disadvantage Group / Weaker Section",
                                        html.Span(" *", style={"color": "red"}),
                                    ]
                                ),
                                dcc.Dropdown(
                                    id="stu-disadvantage",
                                    options=[
                                        {"label": "Yes", "value": "1"},
                                        {"label": "No", "value": "2"},
                                    ],
                                    placeholder="--Select--",
                                ),
                            ],
                            md=6,
                            className="mb-3",
                        ),
                    ]
                ),
                dbc.Row(
                    [
                        dbc.Col(
                            [
                                dbc.Label(
                                    [
                                        "Getting free education as per RTE Act.",
                                        html.Span(" *", style={"color": "red"}),
                                    ]
                                ),
                                dcc.Dropdown(
                                    id="stu-rte",
                                    options=[
                                        {"label": "Not Applicable", "value": "0"},
                                        {"label": "Yes", "value": "1"},
                                        {"label": "No", "value": "2"},
                                    ],
                                    placeholder="--Select--",
                                ),
                            ],
                            md=6,
                            className="mb-3",
                        ),
                        dbc.Col(
                            [
                                dbc.Label(
                                    [
                                        "Studying in class",
                                        html.Span(" *", style={"color": "red"}),
                                    ]
                                ),
                                dcc.Dropdown(
                                    id="stu-class",
                                    options=[
                                        {"label": "PP.3+", "value": "0"},
                                        {"label": "PP.4+", "value": "1"},
                                        {"label": "PP.5+", "value": "2"},
                                        {"label": "First", "value": "3"},
                                        {"label": "Second", "value": "4"},
                                        {"label": "Third", "value": "5"},
                                        {"label": "Fourth", "value": "6"},
                                        {"label": "Fifth", "value": "7"},
                                        {"label": "Sixth", "value": "8"},
                                        {"label": "Seventh", "value": "9"},
                                        {"label": "Eight", "value": "10"},
                                        {"label": "Ninth", "value": "11"},
                                        {"label": "Tenth", "value": "12"},
                                        {"label": "Eleventh", "value": "13"},
                                        {"label": "Twelth", "value": "14"},
                                    ],
                                    placeholder="--Select--",
                                ),
                            ],
                            md=6,
                            className="mb-3",
                        ),
                    ]
                ),
                dbc.Row(
                    [
                        dbc.Col(
                            [
                                dbc.Label(
                                    [
                                        "Class studied previous year",
                                        html.Span(" *", style={"color": "red"}),
                                    ]
                                ),
                                dcc.Dropdown(
                                    id="stu-prev-class",
                                    options=[
                                        {"label": "PP.3+", "value": "0"},
                                        {"label": "PP.4+", "value": "1"},
                                        {"label": "PP.5+", "value": "2"},
                                        {"label": "First", "value": "3"},
                                        {"label": "Second", "value": "4"},
                                        {"label": "Third", "value": "5"},
                                        {"label": "Fourth", "value": "6"},
                                        {"label": "Fifth", "value": "7"},
                                        {"label": "Sixth", "value": "8"},
                                        {"label": "Seventh", "value": "9"},
                                        {"label": "Eight", "value": "10"},
                                        {"label": "Ninth", "value": "11"},
                                        {"label": "Tenth", "value": "12"},
                                        {"label": "Eleventh", "value": "13"},
                                        {"label": "Twelth", "value": "14"},
                                        {"label": "None", "value": "99"},
                                    ],
                                    placeholder="--Select--",
                                ),
                            ],
                            md=6,
                            className="mb-3",
                        ),
                        dbc.Col(
                            [
                                dbc.Label(
                                    [
                                        "if studying in class-1st, give status of previous year",
                                        html.Span(" *", style={"color": "red"}),
                                    ]
                                ),
                                dcc.Dropdown(
                                    id="stu-class1-status",
                                    options=[
                                        {"label": "NOT APPLICABLE", "value": "0"},
                                        {"label": "SAME SCHOOL", "value": "1"},
                                        {"label": "ANOTHER SCHOOL", "value": "2"},
                                        {"label": "ANGANWADI/ECCE", "value": "3"},
                                        {"label": "NONE", "value": "4"},
                                    ],
                                    placeholder="--Select--",
                                ),
                            ],
                            md=6,
                            className="mb-3",
                        ),
                    ]
                ),
                dbc.Row(
                    [
                        dbc.Col(
                            [
                                dbc.Label(
                                    "No. of days child attended school in previous year"
                                ),
                                dbc.Input(
                                    id="stu-attendance-days",
                                    placeholder="Enter number of days",
                                    type="number",
                                ),
                            ],
                            md=6,
                            className="mb-3",
                        ),
                        dbc.Col(
                            [
                                dbc.Label(
                                    [
                                        "Medium of instruction",
                                        html.Span(" *", style={"color": "red"}),
                                    ]
                                ),
                                dcc.Dropdown(
                                    id="stu-medium",
                                    options=[
                                        {"label": "Hindi", "value": "4"},
                                        {"label": "English", "value": "19"},
                                    ],
                                    placeholder="--Select--",
                                ),
                            ],
                            md=6,
                            className="mb-3",
                        ),
                    ]
                ),
                # Section 3: Facilities and Benefits
                html.Hr(),
                html.H6(
                    "Facilities and Benefits",
                    className="mb-3",
                    style={"color": "#388E3C", "fontWeight": "600"},
                ),
                dbc.Row(
                    [
                        dbc.Col(
                            [
                                dbc.Label(
                                    [
                                        "Type of Disability",
                                        html.Span(" *", style={"color": "red"}),
                                    ]
                                ),
                                dcc.Dropdown(
                                    id="stu-disability",
                                    options=[
                                        {"label": "Not Applicable", "value": "0"},
                                        {"label": "Blindness", "value": "1"},
                                        {"label": "Low-vision", "value": "2"},
                                        {"label": "Hearing", "value": "3"},
                                        {"label": "Speech", "value": "4"},
                                        {"label": "Loco Motor", "value": "5"},
                                        {"label": "Mental Retardation", "value": "6"},
                                        {"label": "Learning Disability", "value": "7"},
                                        {"label": "Cerebral Palsy", "value": "8"},
                                        {"label": "Autism", "value": "9"},
                                        {
                                            "label": "Multiple Disabilities",
                                            "value": "10",
                                        },
                                        {"label": "Mental Illness", "value": "12"},
                                        {"label": "Acid Attack Victim", "value": "13"},
                                        {"label": "Dwarfism", "value": "14"},
                                        {"label": "Muscular Dystrophy", "value": "15"},
                                        {
                                            "label": "Leprosy Cured Persons",
                                            "value": "16",
                                        },
                                        {"label": "Parkinson & Disease", "value": "17"},
                                        {"label": "Sickle Cell Disease", "value": "18"},
                                        {"label": "Thalassemia", "value": "19"},
                                        {
                                            "label": "Chronic Neurological Conditions",
                                            "value": "20",
                                        },
                                        {"label": "Hemophilia", "value": "21"},
                                        {"label": "Multiple Sclerosis", "value": "22"},
                                    ],
                                    placeholder="--Select--",
                                ),
                            ],
                            md=6,
                            className="mb-3",
                        ),
                        dbc.Col(
                            [
                                dbc.Label(
                                    [
                                        "Facilities provided to CWSN",
                                        html.Span(" *", style={"color": "red"}),
                                    ]
                                ),
                                dcc.Dropdown(
                                    id="stu-cwsn",
                                    options=[
                                        {"label": "Not Applicable", "value": "0"},
                                        {"label": "Braille Books", "value": "1"},
                                        {"label": "Braille Kit", "value": "2"},
                                        {"label": "Low vision kit", "value": "3"},
                                        {"label": "Hearing Aid", "value": "4"},
                                        {"label": "Braces", "value": "5"},
                                        {"label": "Crutches", "value": "6"},
                                        {"label": "Wheel chair", "value": "7"},
                                        {"label": "Tri-cycle", "value": "8"},
                                        {"label": "Calliper", "value": "9"},
                                        {"label": "Others", "value": "10"},
                                    ],
                                    placeholder="--Select--",
                                ),
                            ],
                            md=6,
                            className="mb-3",
                        ),
                    ]
                ),
                dbc.Row(
                    [
                        dbc.Col(
                            [
                                dbc.Label(
                                    [
                                        "No. of uniform sets received",
                                        html.Span(" *", style={"color": "red"}),
                                    ]
                                ),
                                dcc.Dropdown(
                                    id="stu-uniform",
                                    options=[
                                        {"label": "None", "value": "0"},
                                        {"label": "One Set", "value": "1"},
                                        {"label": "Two Set", "value": "2"},
                                        {"label": "Partial", "value": "3"},
                                    ],
                                    placeholder="--Select--",
                                ),
                            ],
                            md=6,
                            className="mb-3",
                        ),
                        dbc.Col(
                            [
                                dbc.Label(
                                    [
                                        "Complete set of free Textbook",
                                        html.Span(" *", style={"color": "red"}),
                                    ]
                                ),
                                dcc.Dropdown(
                                    id="stu-textbook",
                                    options=[
                                        {"label": "Not Applicable", "value": "0"},
                                        {"label": "Yes", "value": "1"},
                                        {"label": "No", "value": "2"},
                                    ],
                                    placeholder="--Select--",
                                ),
                            ],
                            md=6,
                            className="mb-3",
                        ),
                    ]
                ),
                dbc.Row(
                    [
                        dbc.Col(
                            [
                                dbc.Label(
                                    [
                                        "Free Transport facility",
                                        html.Span(" *", style={"color": "red"}),
                                    ]
                                ),
                                dcc.Dropdown(
                                    id="stu-transport",
                                    options=[
                                        {"label": "Not Applicable", "value": "0"},
                                        {"label": "Yes", "value": "1"},
                                        {"label": "No", "value": "2"},
                                    ],
                                    placeholder="--Select--",
                                ),
                            ],
                            md=6,
                            className="mb-3",
                        ),
                        dbc.Col(
                            [
                                dbc.Label(
                                    [
                                        "Free Bicycle facility",
                                        html.Span(" *", style={"color": "red"}),
                                    ]
                                ),
                                dcc.Dropdown(
                                    id="stu-bicycle",
                                    options=[
                                        {"label": "Not Applicable", "value": "0"},
                                        {"label": "Yes", "value": "1"},
                                        {"label": "No", "value": "2"},
                                    ],
                                    placeholder="--Select--",
                                ),
                            ],
                            md=6,
                            className="mb-3",
                        ),
                    ]
                ),
                dbc.Row(
                    [
                        dbc.Col(
                            [
                                dbc.Label(
                                    [
                                        "Free Escort facility",
                                        html.Span(" *", style={"color": "red"}),
                                    ]
                                ),
                                dcc.Dropdown(
                                    id="stu-escort",
                                    options=[
                                        {"label": "Not Applicable", "value": "0"},
                                        {"label": "Yes", "value": "1"},
                                        {"label": "No", "value": "2"},
                                    ],
                                    placeholder="--Select--",
                                ),
                            ],
                            md=6,
                            className="mb-3",
                        ),
                        dbc.Col(
                            [
                                dbc.Label(
                                    [
                                        "Whether the child is Mid-day Meal beneficiary",
                                        html.Span(" *", style={"color": "red"}),
                                    ]
                                ),
                                dcc.Dropdown(
                                    id="stu-midday-meal",
                                    options=[
                                        {"label": "Not Applicable", "value": "0"},
                                        {"label": "Yes", "value": "1"},
                                        {"label": "No", "value": "2"},
                                    ],
                                    placeholder="--Select--",
                                ),
                            ],
                            md=6,
                            className="mb-3",
                        ),
                    ]
                ),
                dbc.Row(
                    [
                        dbc.Col(
                            [
                                dbc.Label(
                                    [
                                        "Free Hostel facility",
                                        html.Span(" *", style={"color": "red"}),
                                    ]
                                ),
                                dcc.Dropdown(
                                    id="stu-hostel",
                                    options=[
                                        {"label": "Not Applicable", "value": "0"},
                                        {"label": "KGBV", "value": "1"},
                                        {
                                            "label": "Non KGBV (Government)",
                                            "value": "2",
                                        },
                                        {"label": "Girls Hostel", "value": "3"},
                                        {"label": "Others", "value": "4"},
                                        {"label": "None", "value": "5"},
                                    ],
                                    placeholder="--Select--",
                                ),
                            ],
                            md=6,
                            className="mb-3",
                        ),
                        dbc.Col(
                            [
                                dbc.Label(
                                    [
                                        "Whether child attended Special training",
                                        html.Span(" *", style={"color": "red"}),
                                    ]
                                ),
                                dcc.Dropdown(
                                    id="stu-special-training",
                                    options=[
                                        {"label": "Not Applicable", "value": "0"},
                                        {"label": "Residential", "value": "1"},
                                        {"label": "Non Residential", "value": "2"},
                                    ],
                                    placeholder="--Select--",
                                ),
                            ],
                            md=6,
                            className="mb-3",
                        ),
                    ]
                ),
                dbc.Row(
                    [
                        dbc.Col(
                            [
                                dbc.Label(
                                    [
                                        "Whether the child is homeless",
                                        html.Span(" *", style={"color": "red"}),
                                    ]
                                ),
                                dcc.Dropdown(
                                    id="stu-homeless",
                                    options=[
                                        {"label": "NA", "value": "0"},
                                        {"label": "With Parent/Guardian", "value": "1"},
                                        {
                                            "label": "Without Adult Protection",
                                            "value": "2",
                                        },
                                    ],
                                    placeholder="--Select--",
                                ),
                            ],
                            md=6,
                            className="mb-3",
                        ),
                    ]
                ),
                # Section 4: Academic Performance
                html.Hr(),
                html.H6(
                    "Academic Performance",
                    className="mb-3",
                    style={"color": "#388E3C", "fontWeight": "600"},
                ),
                dbc.Row(
                    [
                        dbc.Col(
                            [
                                dbc.Label(
                                    [
                                        "Appeared in the last year annual examination",
                                        html.Span(" *", style={"color": "red"}),
                                    ]
                                ),
                                dcc.Dropdown(
                                    id="stu-appeared-exam",
                                    options=[
                                        {"label": "Yes", "value": "1"},
                                        {"label": "No", "value": "2"},
                                        {"label": "NA", "value": "3"},
                                    ],
                                    placeholder="--Select--",
                                ),
                            ],
                            md=6,
                            className="mb-3",
                        ),
                        dbc.Col(
                            [
                                dbc.Label(
                                    [
                                        "Passed in the last year annual examination",
                                        html.Span(" *", style={"color": "red"}),
                                    ]
                                ),
                                dcc.Dropdown(
                                    id="stu-passed-exam",
                                    options=[
                                        {"label": "Yes", "value": "1"},
                                        {"label": "No", "value": "2"},
                                        {"label": "NA", "value": "3"},
                                    ],
                                    placeholder="--Select--",
                                ),
                            ],
                            md=6,
                            className="mb-3",
                        ),
                    ]
                ),
                dbc.Row(
                    [
                        dbc.Col(
                            [
                                dbc.Label(
                                    "% Marks obtained in last year annual exam (if available)"
                                ),
                                dbc.Input(
                                    id="stu-marks",
                                    placeholder="Enter percentage",
                                    type="number",
                                    step="0.01",
                                ),
                            ],
                            md=6,
                            className="mb-3",
                        ),
                        dbc.Col(
                            [
                                dbc.Label(
                                    [
                                        "Stream (grades 11 & 12)",
                                        html.Span(" *", style={"color": "red"}),
                                    ]
                                ),
                                dcc.Dropdown(
                                    id="stu-stream",
                                    options=[
                                        {"label": "Not Applicable", "value": "0"},
                                        {"label": "Arts", "value": "1"},
                                        {"label": "Science", "value": "2"},
                                        {"label": "Commerce", "value": "3"},
                                        {"label": "Vocational", "value": "4"},
                                        {"label": "Other stream", "value": "5"},
                                    ],
                                    placeholder="--Select--",
                                ),
                            ],
                            md=6,
                            className="mb-3",
                        ),
                    ]
                ),
                dbc.Row(
                    [
                        dbc.Col(
                            [
                                dbc.Label(
                                    [
                                        "Trade/Sector (grades 9 to 12)",
                                        html.Span(" *", style={"color": "red"}),
                                    ]
                                ),
                                dcc.Dropdown(
                                    id="stu-trade",
                                    options=[
                                        {"label": "Not Applicable", "value": "0"},
                                        {"label": "Agriculture", "value": "61"},
                                        {"label": "Apparel", "value": "62"},
                                        {"label": "Automotive", "value": "63"},
                                        {"label": "Beauty & Wellness", "value": "64"},
                                        {
                                            "label": "Banking Financial Services and Insurance (BFSI)",
                                            "value": "65",
                                        },
                                        {"label": "Construction", "value": "66"},
                                        {"label": "Electronics", "value": "67"},
                                        {"label": "Healthcare", "value": "68"},
                                        {"label": "IT-ITES", "value": "69"},
                                        {"label": "Logistics", "value": "70"},
                                        {"label": "Capital Goods", "value": "71"},
                                        {
                                            "label": "Media & Entertainment",
                                            "value": "72",
                                        },
                                        {"label": "Multi-Skilling", "value": "73"},
                                        {"label": "Retail", "value": "74"},
                                        {"label": "Security", "value": "75"},
                                        {"label": "Sports", "value": "76"},
                                        {"label": "Telecom", "value": "77"},
                                        {
                                            "label": "Tourism & Hospitality",
                                            "value": "78",
                                        },
                                    ],
                                    placeholder="--Select--",
                                ),
                            ],
                            md=6,
                            className="mb-3",
                        ),
                    ]
                ),
                # Section 5: Health and Contact Information
                html.Hr(),
                html.H6(
                    "Health and Contact Information",
                    className="mb-3",
                    style={"color": "#388E3C", "fontWeight": "600"},
                ),
                dbc.Row(
                    [
                        dbc.Col(
                            [
                                dbc.Label(
                                    [
                                        "Tablets Received Iron & Folic acid",
                                        html.Span(" *", style={"color": "red"}),
                                    ]
                                ),
                                dcc.Dropdown(
                                    id="stu-iron-folic",
                                    options=[
                                        {"label": "Not Applicable", "value": "0"},
                                        {"label": "Yes", "value": "1"},
                                        {"label": "No", "value": "2"},
                                    ],
                                    placeholder="--Select--",
                                ),
                            ],
                            md=6,
                            className="mb-3",
                        ),
                        dbc.Col(
                            [
                                dbc.Label(
                                    [
                                        "Tablets Received of Deworming",
                                        html.Span(" *", style={"color": "red"}),
                                    ]
                                ),
                                dcc.Dropdown(
                                    id="stu-deworming",
                                    options=[
                                        {"label": "Not Applicable", "value": "0"},
                                        {"label": "Yes", "value": "1"},
                                        {"label": "No", "value": "2"},
                                    ],
                                    placeholder="--Select--",
                                ),
                            ],
                            md=6,
                            className="mb-3",
                        ),
                    ]
                ),
                dbc.Row(
                    [
                        dbc.Col(
                            [
                                dbc.Label(
                                    [
                                        "Tablets Received of Vitamin-A supplement",
                                        html.Span(" *", style={"color": "red"}),
                                    ]
                                ),
                                dcc.Dropdown(
                                    id="stu-vitamin-a",
                                    options=[
                                        {"label": "Not Applicable", "value": "0"},
                                        {"label": "Yes", "value": "1"},
                                        {"label": "No", "value": "2"},
                                    ],
                                    placeholder="--Select--",
                                ),
                            ],
                            md=6,
                            className="mb-3",
                        ),
                    ]
                ),
                dbc.Row(
                    [
                        dbc.Col(
                            [
                                dbc.Label("Mobile Number"),
                                dbc.Input(
                                    id="stu-mobile",
                                    placeholder="Enter Mobile Number",
                                    type="tel",
                                    pattern="[0-9]{10}",
                                ),
                            ],
                            md=6,
                            className="mb-3",
                        ),
                        dbc.Col(
                            [
                                dbc.Label("Email Address"),
                                dbc.Input(
                                    id="stu-email",
                                    placeholder="Enter Email Address",
                                    type="email",
                                ),
                            ],
                            md=6,
                            className="mb-3",
                        ),
                    ]
                ),
                dbc.Row(
    [
        dbc.Col(
            [
                dbc.Label(
                    [
                        "Extracurricular Activities",
                        html.Span(" *", style={"color": "red"}),
                    ]
                ),
                dcc.Dropdown(
                    id="stu-activities",
                    options=[
                        {"label": "Handball", "value": "handball"},
                        {"label": "Hokey", "value": "hokey"},
                        {"label": "Football", "value": "football"},
                        {"label": "Shooting", "value": "shooting"},
                        {"label": "Cricket", "value": "cricket"},
                        {"label": "Wrestling", "value": "wrestling"},
                        {"label": "Table Tennis", "value": "tt"},
                        {"label": "Boxing", "value": "boxing"},
                        {"label": "Swimming", "value": "swimming"},
                        {"label": "Music", "value": "music"},
                        {"label": "Dance", "value": "dance"},
                        {"label": "Art", "value": "art"},
                        {"label": "Drama", "value": "drama"},
                        {"label": "Debate", "value": "debate"},
                        {"label": "Coding", "value": "coding"},
                        {"label": "Other", "value": "other"},
                    ],
                    placeholder="--Select Activities--",
                    multi=True, 
                    maxHeight=150,  

                  
                ),
                dbc.Input(
    id="stu-activities-other",
    placeholder="Enter Activity",
    type="text",
    style={"display": "none"},  # hidden by default
    className="mt-2"
)
            ],
            md=6,
            className="mb-3",
        ),
    ]
),
                html.Hr(),
                dbc.Button(
                    "Save Student",
                    id="submit-student",
                    color="success",
                    className="mt-3",
                    style={"width": "200px"},
                ),
                html.Div(id="submit-message", className="mt-3"),
            ]
        ),
        className="shadow-sm",
        style={"borderRadius": "10px", "marginTop": "20px"},
    )


# --------------------------------------------------
# Search Student Layout
# --------------------------------------------------


def search_student_layout(SessionData):
    return dbc.Container(
        [
            dbc.Row(
                [
                    dbc.Col(
                        dbc.Input(
                            id="search-student-name",
                            placeholder="Search by student name, AADHAAR, or Admission No.",
                            debounce=True,
                        ),
                        md=6,
                    ),
                    dbc.Col(
                        dbc.Button(
                            "Download Student Log + Fees",
                            id="download-student-btn",
                            color="primary",
                        ),
                        md=3,
                    ),
                ],
                className="mb-3",
            ),
            dcc.Download(id="download-student-file"),
            html.H5("Student Profile", style={"color": "#1B5E20", "fontWeight": "600"}),
            dash.dash_table.DataTable(
                id="student-search-table",
                page_size=10,
                style_cell={
                    "textAlign": "left",
                    "padding": "10px",
                    "fontFamily": "Segoe UI, Arial, sans-serif",
                },
                style_header={
                    "backgroundColor": "#E8F5E9",
                    "color": "#1B5E20",
                    "fontWeight": "600",
                },
            ),
            html.Hr(),
            html.H5(
                "Latest Fee Receipts", style={"color": "#1B5E20", "fontWeight": "600"}
            ),
            dash.dash_table.DataTable(
                id="student-fee-table",
                page_size=10,
                style_cell={
                    "textAlign": "left",
                    "padding": "10px",
                    "fontFamily": "Segoe UI, Arial, sans-serif",
                },
                style_header={
                    "backgroundColor": "#E8F5E9",
                    "color": "#1B5E20",
                    "fontWeight": "600",
                },
            ),
        ],
        fluid=True,
    )


# --------------------------------------------------
# Callbacks
# --------------------------------------------------


def register_callbacks(app):

    @app.callback(
        Output("student-tab-content", "children"),
        Input("student-tabs", "active_tab"),
    )
    def render_tab(tab):
        return (
            create_student_form()
            if tab == "create-student"
            else search_student_layout()
        )
    
    @app.callback(
    Output("stu-activities-other", "style"),
    Input("stu-activities", "value"),
)
    def show_other_input(values):
     if values and "other" in values:
        return {"display": "block"}
     return {"display": "none"}

    # ---------- Save Student ----------
    @app.callback(
    Output("submit-message", "children"),
    Input("submit-student", "n_clicks"),
    State("stu-aadhaar", "value"),
    State("stu-name", "value"),
    State("father-name", "value"),
    State("mother-name", "value"),
    State("stu-dob", "value"),
    State("stu-gender", "value"),
    State("stu-caste", "value"),
    State("stu-religion", "value"),
    State("stu-mother-tongue", "value"),
    State("stu-jan-aadhar", "value"),
    State("stu-rural-urban", "value"),
    State("stu-address", "value"),
    State("stu-admission-date", "value"),
    State("stu-current-academic-year", "value"),
    State("stu-concession", "value"),
    State("stu-admission-no", "value"),
    State("stu-bpl", "value"),
    State("stu-disadvantage", "value"),
    State("stu-rte", "value"),
    State("stu-class", "value"),
    State("stu-prev-class", "value"),
    State("stu-class1-status", "value"),
    State("stu-attendance-days", "value"),
    State("stu-medium", "value"),
    State("stu-disability", "value"),
    State("stu-cwsn", "value"),
    State("stu-uniform", "value"),
    State("stu-textbook", "value"),
    State("stu-transport", "value"),
    State("stu-bicycle", "value"),
    State("stu-escort", "value"),
    State("stu-midday-meal", "value"),
    State("stu-hostel", "value"),
    State("stu-special-training", "value"),
    State("stu-homeless", "value"),
    State("stu-appeared-exam", "value"),
    State("stu-passed-exam", "value"),
    State("stu-marks", "value"),
    State("stu-stream", "value"),
    State("stu-trade", "value"),
    State("stu-iron-folic", "value"),
    State("stu-deworming", "value"),
    State("stu-vitamin-a", "value"),
    State("stu-mobile", "value"),
    State("stu-email", "value"),
    State("session", "data"),
    State("stu-activities", "value"),
    State("stu-activities-other", "value"),
    prevent_initial_call=True,)
    def save_student(
        n_clicks,
        aadhaar,
        name,
        father,
        mother,
        dob,
        gender,
        caste,
        religion,
        mother_tongue,
        jan_aadhaar,
        rural_urban,
        address,
        admission_date,
        academic_year,
        concession,
        admission_no,
        bpl,
        disadvantage,
        rte,
        stu_class,
        prev_class,
        class1_status,
        attendance_days,
        medium,
        disability,
        cwsn,
        uniform,
        textbook,
        transport,
        bicycle,
        escort,
        midday_meal,
        hostel,
        special_training,
        homeless,
        appeared_exam,
        passed_exam,
        marks,
        stream,
        trade,
        iron,
        deworming,
        vitamin_a,
        mobile,
        email,
        SessionData,
        activities,
        other_text
    ):
        if not n_clicks:
            return None
    
        # -------------------------
        # REQUIRED FIELD CHECK
        # -------------------------
        required_fields = {
            "Student Name": name,
            "Father's Name": father,
            "Mother's Name": mother,
            "Date of Birth": dob,
            "Gender": gender,
            "Caste Category": caste,
            "Religion": religion,
            "Mother Tongue": mother_tongue,
            "Rural/Urban": rural_urban,
            "Address": address,
            "Date of Admission": admission_date,
            "Admission No.": admission_no,
        }
    
        missing = [k for k, v in required_fields.items() if not v]
        if missing:
            return dbc.Alert(
                f"Please fill required fields: {', '.join(missing)}",
                color="danger",
                dismissable=True,
            )
    
        # -------------------------
        # DATE FORMAT
        # -------------------------
        def fmt_date(d):
            try:
                return datetime.strptime(d, "%Y-%m-%d").strftime("%d/%m/%Y") if d else ""
            except:
                return d
    
        dob_fmt = fmt_date(dob)
        admission_date_fmt = fmt_date(admission_date)
        academic_year_fmt = fmt_date(academic_year)
    
        # -------------------------
        # ACTIVITIES
        # -------------------------
        final_activities = []
        if activities:
            for a in activities:
                if a == "other" and other_text:
                    final_activities.append(other_text.strip().lower())
                else:
                    final_activities.append(a)
    
        activities_str = ",".join(final_activities)
    
        # -------------------------
        # CONCESSION FIX
        # -------------------------
        try:
            concession_val = float(concession) if concession else 0
        except:
            concession_val = 0
    
        # -------------------------
        # ROW
        # -------------------------
        row = {
            "student_id": f"STU_{datetime.now().strftime('%Y%m%d%H%M%S%f')}",
            "account_name": name,
    
            "aadhaar": aadhaar,
            "student_name": name,
            "father_name": father,
            "mother_name": mother,
            "dob": dob_fmt,
            "gender": gender,
            "caste_category": caste,
            "religion": religion,
            "mother_tongue": mother_tongue,
            "jan_aadhaar": jan_aadhaar,
            "rural_urban": rural_urban,
            "habitation": address,
    
            "admission_date": admission_date_fmt,
            "current_academic_year": academic_year_fmt,
            "admission_no": admission_no,
    
            # ✅ FIXED
            "monthly_fee_concession": concession_val,
    
            "bpl": bpl,
            "disadvantaged_group": disadvantage,
    
            "is_RTE": rte,
            "studying_class": stu_class,
            "previous_class": prev_class,
            "previous_year_status": class1_status,
            "previous_year_days": attendance_days,
            "medium": medium,
    
            "disability_type": disability,
            "cwsn_facility": cwsn,
            "uniform_sets": uniform,
            "textbook_set": textbook,
            "transport_facility": transport,
            "bicycle_facility": bicycle,
            "escort_facility": escort,
            "midday_meal": midday_meal,
            "hostel_facility": hostel,
            "special_training": special_training,
    
            "homeless_status": homeless,
            "appeared_last_exam": appeared_exam,
            "passed_last_exam": passed_exam,
            "last_exam_percentage": marks,
            "stream": stream,
            "trade": trade,
    
            "iron_tablets": iron,
            "deworming_tablets": deworming,
            "vitamin_a": vitamin_a,
    
            "extracurricular_activities": activities_str,
    
            "mobile": mobile,
            "email": email,
    
            "created_at": datetime.now().isoformat(),
        }
    
        try:
            path = f"/var/Data/{SessionData['username']}/student_log.csv"
    
            pd.DataFrame([row]).to_csv(
                path,
                mode="a",
                index=False,
                header=not os.path.exists(path),
            )
    
            return dbc.Alert(
                f"✅ Student '{name}' saved successfully",
                color="success",
                dismissable=True,
            )
    
        except Exception as e:
            return dbc.Alert(
                f"❌ Error saving student: {str(e)}",
                color="danger",
                dismissable=True,
            )

    # ---------- Search ----------
    @app.callback(
        Output("student-search-table", "data"),
        Output("student-search-table", "columns"),
        Output("student-fee-table", "data"),
        Output("student-fee-table", "columns"),
        Input("search-student-name", "value"),
        State("session", "data"),
    )
    def search_student(name, SessionData):
        if not name:
            return [], [], [], []

        if not os.path.exists(
            "/var/Data/" + str(SessionData["username"]) + "/student_log.csv"
        ):
            return [], [], [], []

        try:
            students = pd.read_csv(
                "/var/Data/" + str(SessionData["username"]) + "/student_log.csv"
            )
            fees = (
                pd.read_csv(
                    "/var/Data/" + str(SessionData["username"]) + "/fees_ledger.csv"
                )
                if os.path.exists(
                    "/var/Data/" + str(SessionData["username"]) + "/fees_ledger.csv"
                )
                else pd.DataFrame()
            )

            # Search in multiple fields
            mask = (
                students["student_name"].str.contains(name, case=False, na=False)
                # | students["aadhaar_number"].astype(str).str.contains(name, case=False, na=False) |
                # students["admission_no"].astype(str).str.contains(name, case=False, na=False)
            )
            s = students[mask]

            f = (
                fees[fees["account_name"].str.contains(name, case=False, na=False)]
                if not fees.empty
                else pd.DataFrame()
            )

            return (
                s.to_dict("records"),
                [{"name": c.replace("_", " ").title(), "id": c} for c in s.columns],
                f.to_dict("records"),
                (
                    [{"name": c.replace("_", " ").title(), "id": c} for c in f.columns]
                    if not f.empty
                    else []
                ),
            )
        except Exception as e:
            print(f"Error in search: {e}")
            return [], [], [], []

    # ---------- Download ----------
    @app.callback(
        Output("download-student-file", "data"),
        Input("download-student-btn", "n_clicks"),
        State("search-student-name", "value"),
        State("session", "data"),
        prevent_initial_call=True,
    )
    def download_student(n, name, SessionData):
        if not n or not name:
            raise dash.exceptions.PreventUpdate

        if not os.path.exists(
            "/var/Data/" + str(SessionData["username"]) + "/student_log.csv"
        ):
            raise dash.exceptions.PreventUpdate

        try:
            students = pd.read_csv(
                "/var/Data/" + str(SessionData["username"]) + "/student_log.csv"
            )
            fees = (
                pd.read_csv(
                    "/var/Data/" + str(SessionData["username"]) + "/fees_ledger.csv"
                )
                if os.path.exists(
                    "/var/Data/" + str(SessionData["username"]) + "/fees_ledger.csv"
                )
                else pd.DataFrame()
            )

            # Search in multiple fields
            mask = (
                students["student_name"].str.contains(name, case=False, na=False)
                | students["admission_no"]
                .astype(str)
                .str.contains(name, case=False, na=False)
            )
            s = students[mask]

            f = (
                fees[fees["account_name"].str.contains(name, case=False, na=False)]
                if not fees.empty
                else pd.DataFrame()
            )

            output = io.BytesIO()
            with pd.ExcelWriter(output, engine="xlsxwriter") as writer:
                s.to_excel(writer, index=False, sheet_name="Student Log")
                if not f.empty:
                    f.to_excel(writer, index=False, sheet_name="Fee Receipts")

            output.seek(0)
            return dcc.send_bytes(
                output.read(), f"{name.replace(' ', '_')}_student_log.xlsx"
            )
        except Exception as e:
            print(f"Error in download: {e}")
            raise dash.exceptions.PreventUpdate
