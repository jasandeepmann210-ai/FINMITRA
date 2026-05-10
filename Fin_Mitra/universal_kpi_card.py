from dash import html, dcc
import dash_bootstrap_components as dbc
import plotly.graph_objects as go


def create_sparkline(data, color="#16a34a"):
    fig = go.Figure()

    fig.add_trace(go.Scatter(
        y=data,
        mode="lines",
        line=dict(color=color, width=1.8),
        fill="tozeroy"
    ))

    fig.update_layout(
        margin=dict(l=0, r=0, t=0, b=0),
        template="plotly_white",
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        xaxis=dict(visible=False, fixedrange=True),
        yaxis=dict(visible=False, fixedrange=True),
        showlegend=False
    )

    return fig

def universal_kpi_card(
    title,
    value,
    change=None,
    trend=None,
    icon_class=None,
    icon_bg="#f8f9fa",
    icon_color="#000",
    extra_text=None,
    spark_data=None   # 👈 NEW PARAM
):

    # Trend Color
    if trend == "positive":
        change_color = "success"
        spark_color = "#16a34a"
    elif trend == "negative":
        change_color = "danger"
        spark_color = "#dc2626"
    else:
        change_color = "secondary"
        spark_color = "#6b7280"

    return dbc.Card(
        dbc.CardBody([

            # Row 1
            dbc.Row([
                dbc.Col(
                    html.Div(
                        html.I(
                            className=icon_class,
                            style={"fontSize": "18px", "color": icon_color}
                        ),
                        style={
                            "backgroundColor": icon_bg,
                            "width": "36px",
                            "height": "36px",
                            "borderRadius": "6px",
                            "display": "flex",
                            "alignItems": "center",
                            "justifyContent": "center"
                        }
                    ),
                    width="auto"
                ),

                dbc.Col(
                    html.Div(
                        title,
                        className="fw-bold mb-0",
                        style={"fontSize": "14px"}
                    )
                )

            ], align="center", className="g-2 mb-3"),

            # Row 2
            dbc.Row([

                # Left Side
                dbc.Col([

                    html.H4(
                        value,
                        className="fw-bold mb-1",
                        style={"fontSize": "20px"}
                    ),

                    html.Div([
                        html.Span(
                            change,
                            className=f"text-{change_color} fw-semibold",
                            style={"fontSize": "13px"}
                        ) if change else None,

                        html.Span(
                            extra_text,
                            className="text-muted ms-2",
                            style={"fontSize": "13px"}
                        ) if extra_text else None,

                    ], style={"whiteSpace": "nowrap"})

                ], width=8),

                # Right Side → Sparkline
                dbc.Col(
    dcc.Graph(
        figure=create_sparkline(
            spark_data if spark_data else [10, 15, 12, 18, 22, 25],
            spark_color
        ),
        config={"displayModeBar": False, "responsive": True},
        style={
            "height": "100%",
            "width": "100%"
        }
    ),
    width=2,
    style={"padding": "0px"},
    className="d-flex align-items-center"
)
            ])

        ]),
        className="shadow-sm h-100",
        style={"borderRadius": "10px", "minHeight": "140px"}
    )


def monthly_fee_card(months, fees_data, chart_height=240): 

    trend_line = fees_data  

    fig = go.Figure()

    # BAR
    fig.add_trace(
        go.Bar(
            x=months,
            y=fees_data,
            marker=dict(color="rgba(59,130,246,0.7)"),
            name="Fees Used",
            width=0.5
        )
    )

    # LINE
    fig.add_trace(
        go.Scatter(
            x=months,
            y=trend_line,
            mode="lines+markers",
            line=dict(color="#10b981", width=3),
            marker=dict(size=6),
            name="Trend"
        )
    )

    fig.update_layout(
        height=chart_height,   # 🔥 dynamic height
        margin=dict(l=20, r=20, t=10, b=10),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        xaxis=dict(showgrid=False, tickfont=dict(size=12)),
        yaxis=dict(
            showgrid=True,
            gridcolor="rgba(200,200,200,0.2)",
            tickprefix="₹"
        ),
        showlegend=False
    )

    return dbc.Card(
        dbc.CardBody([

            dbc.Row([
                dbc.Col(
                    html.H5("Fee Receipts",
                            className="fw-bold mb-3"),
                    md=8
                ),
                dbc.Col(
                    dcc.Dropdown(
                        id="fee-view-type",
                        options=[
                            {"label": "Month", "value": "month"},
                            {"label": "Quarter", "value": "quarter"},
                        ],
                        value="month",
                        clearable=False,
                        style={"borderRadius": "10px",
                               "fontSize": "13px"}
                    ),
                    md=4
                )
            ]),

            dcc.Graph(
                id="financial-overview-graph", 
                figure=fig,
                config={"displayModeBar": False},
                style={"height": f"{chart_height}px"}   # 🔥 match layout
            )

        ]),
        className="shadow",
        style={
            "borderRadius": "20px",
            "backgroundColor": "#f8fafc"
        }
    )



def bank_closing_dropdown_card(
    bank_options,
    value="₹ 0",
    trend=None,
    selected_bank_label="Select Bank",
    spark_data=None,
    default_value=None
):

    if trend == "positive":
        value_color = "#16a34a"
    elif trend == "negative":
        value_color = "#dc2626"
    else:
        value_color = "#0f172a"

    return dbc.Card(
        dbc.CardBody([

            dbc.Row([

                dbc.Col(
                    html.Div(
                        html.I(
                            className="bi bi-bank",
                            style={"fontSize": "18px", "color": "#0284c7"}
                        ),
                        style={
                            "backgroundColor": "#e0f2fe",
                            "width": "38px",
                            "height": "38px",
                            "borderRadius": "8px",
                            "display": "flex",
                            "alignItems": "center",
                            "justifyContent": "center"
                        }
                    ),
                    width="auto"
                ),

                dbc.Col(
                    html.Div(
                        "Bank Closing Balance",
                        className="fw-bold",
                        style={"fontSize": "14px"}
                    )
                ),

                dbc.Col(
                    dcc.Dropdown(
                        id="dashboard-bank-selector",
                        options=bank_options,
                        value=default_value,   # ✅ FIXED
                        clearable=False,
                        style={
                            "fontSize": "12px",
                            "minWidth": "140px"
                        }
                    ),
                    width="auto"
                )

            ], align="center", className="g-2 mb-3"),

            html.Div(
                selected_bank_label,
                id="dashboard-selected-bank-name",
                className="text-muted mb-1",
                style={"fontSize": "12px"}
            ),

            html.H3(
                value,
                id="dashboard-bank-closing-value",
                className="fw-bold",
                style={
                    "fontSize": "28px",
                    "color": value_color
                }
            ),

        ]),
        className="shadow-sm h-100",
        style={
            "borderRadius": "14px",
            "minHeight": "140px",
            "backgroundColor": "#f8fafc"
        }
    )


def birthday_card(students):

    count = len(students)

    if not students:

        content = html.Div(
            "No birthdays today 🎉",
            className="text-muted text-center",
            style={"fontSize": "14px", "padding": "20px"}
        )

    else:

        content = html.Div(

            [
                html.Div(
                    [

                        html.I(
                            className="bi bi-gift-fill",
                            style={
                                "color": "#f97316",
                                "marginRight": "8px"
                            }
                        ),

                        html.Span(
                            s["name"],
                            className="fw-semibold"
                        ),

                        html.Span(
                            f" • Class {s['class']}",
                            className="text-muted ms-1",
                            style={"fontSize": "13px"}
                        ),

                    ],

                    className="d-flex align-items-center",

                    style={
                        "background": "#f8f9fa",
                        "padding": "8px 10px",
                        "borderRadius": "6px",
                        "marginBottom": "6px"
                    }
                )

                for s in students

            ],

            # 🔥 SCROLL LOGIC
            style={
                "maxHeight": "90px",
                "overflowY": "auto",
                "paddingRight": "4px"
            }

        )

    return dbc.Card(

        dbc.CardBody(

            [

                # Header
                dbc.Row(

                    [

                        dbc.Col(

                            html.Div(

                                html.I(
                                    className="bi bi-cake2-fill",
                                    style={
                                        "fontSize": "18px",
                                        "color": "#f97316"
                                    }
                                ),

                                style={
                                    "backgroundColor": "#fff3e0",
                                    "width": "36px",
                                    "height": "36px",
                                    "borderRadius": "8px",
                                    "display": "flex",
                                    "alignItems": "center",
                                    "justifyContent": "center"
                                }

                            ),

                            width="auto"
                        ),

                        dbc.Col(

                            html.Div(
                                "Today's Birthdays",
                                className="fw-bold",
                                style={"fontSize": "15px"}
                            )

                        ),

                        dbc.Col(

                            html.Span(
                                f"{count}",
                                className="badge",
                                style={
                                    "background": "#f97316",
                                    "fontSize": "12px"
                                }
                            ),

                            width="auto"

                        )

                    ],

                    align="center",
                    className="mb-3 g-2"

                ),

                content

            ]

        ),

        className="shadow-sm h-100",

        style={
            "borderRadius": "14px",
            "backgroundColor": "#ffffff",
            "minHeight": "130px"
        }

    )




def upcoming_events_card(events):

    count = len(events)

    if not events:

        content = html.Div(
            "No upcoming events",
            className="text-muted text-center",
            style={"fontSize": "14px", "padding": "20px"}
        )

    else:

        content = html.Div(

            [
                html.Div(

                    [

                        html.I(
                            className="bi bi-calendar-event",
                            style={
                                "color": "#2563eb",
                                "marginRight": "8px"
                            }
                        ),

                        html.Span(
                            e["title"],
                            className="fw-semibold"
                        ),

                        html.Span(
                            f" • {e['date']}",
                            className="text-muted ms-1",
                            style={"fontSize": "13px"}
                        ),

                    ],

                    className="d-flex align-items-center",

                    style={
                        "background": "#f8fafc",
                        "padding": "8px 10px",
                        "borderRadius": "6px",
                        "marginBottom": "6px"
                    }
                )

                for e in events

            ],

            # scroll
            style={
                "maxHeight": "120px",
                "overflowY": "auto",
                "paddingRight": "4px"
            }

        )

    return dbc.Card(

        dbc.CardBody(

            [

                dbc.Row(

                    [

                        dbc.Col(

                            html.Div(

                                html.I(
                                    className="bi bi-calendar2-event-fill",
                                    style={
                                        "fontSize": "18px",
                                        "color": "#2563eb"
                                    }
                                ),

                                style={
                                    "backgroundColor": "#e0f2fe",
                                    "width": "36px",
                                    "height": "36px",
                                    "borderRadius": "8px",
                                    "display": "flex",
                                    "alignItems": "center",
                                    "justifyContent": "center"
                                }

                            ),

                            width="auto"
                        ),

                        dbc.Col(

                            html.Div(
                                "Upcoming Events",
                                className="fw-bold",
                                style={"fontSize": "15px"}
                            )

                        ),

                        dbc.Col(

                            html.Span(
                                f"{count}",
                                className="badge",
                                style={
                                    "background": "#2563eb",
                                    "fontSize": "12px"
                                }
                            ),

                            width="auto"

                        )

                    ],

                    align="center",
                    className="mb-3 g-2"

                ),

                content

            ]

        ),

        className="shadow-sm h-100",

        style={
            "borderRadius": "14px",
            "backgroundColor": "#ffffff",
            "minHeight": "140px"
        }

    )




 

def student_overview_card(total, boys, girls, left_students):

    return dbc.Card(

        dbc.CardBody([

            # Title
            html.Div(
                "Student Overview",
                className="fw-bold mb-2",
                style={"fontSize": "clamp(14px, 1.2vw, 16px)"}
            ),

            html.Hr(style={"marginTop": "4px", "marginBottom": "12px"}),

            # Total / Boys / Girls
            dbc.Row([

                dbc.Col([
                    html.H4(str(total),
                            style={
                                "color": "#2563eb",
                                "marginBottom": "0",
                                "fontSize": "clamp(18px,2vw,22px)"
                            }),
                    html.Small("Total", className="text-muted")
                ], xs=4, sm=3),

                dbc.Col([
                    html.H4(str(boys),
                            style={
                                "color": "#dc2626",
                                "marginBottom": "0",
                                "fontSize": "clamp(18px,2vw,22px)"
                            }),
                    html.Small("Boys", className="text-muted")
                ], xs=4, sm=3),

                dbc.Col([
                    html.H4(str(girls),
                            style={
                                "color": "#16a34a",
                                "marginBottom": "0",
                                "fontSize": "clamp(18px,2vw,22px)"
                            }),
                    html.Small("Girls", className="text-muted")
                ], xs=4, sm=3),

                dbc.Col(
                    html.I(
                        className="bi bi-people-fill",
                        style={
                            "fontSize": "clamp(26px,3vw,36px)",
                            "color": "#94a3b8"
                        }
                    ),
                    width="auto",
                    className="text-end"
                )

            ], align="center", className="g-2 mb-3"),

            html.Hr(),

            # Students Left
            dbc.Row([
                dbc.Col(
                    html.Div(
                        "Students Left",
                        className="text-muted",
                        style={"fontSize": "clamp(12px,1vw,14px)"}
                    )
                ),

                dbc.Col(
                    html.Div(
                        left_students,
                        className="fw-bold",
                        style={"fontSize": "clamp(14px,1.2vw,16px)"}
                    ),
                    width="auto"
                )

            ], align="center")

        ]),

        className="shadow-sm",
        style={
            "borderRadius": "12px",
            "minHeight": "150px",
            "padding": "4px"
        }
    )


def fees_collection_card(receivable, collected, due, ratio):

    return dbc.Card(

        dbc.CardBody([

            # Title
            html.Div(
                "Fees Collection Summary",
                className="fw-bold mb-2",
                style={"fontSize": "clamp(14px,1.2vw,16px)"}
            ),

            html.Hr(style={"marginTop": "4px", "marginBottom": "10px"}),

            # Fees Receivable
            dbc.Row([
                dbc.Col(
                    html.Span(
                        "Fees Receivable",
                        className="text-muted",
                        style={"fontSize": "clamp(12px,1vw,14px)"}
                    )
                ),
                dbc.Col(
                    html.Span(
                        f"₹ {receivable:,}",
                        className="fw-semibold",
                        style={"fontSize": "clamp(13px,1.1vw,15px)"}
                    ),
                    width="auto"
                )
            ], align="center", className="py-1"),

            html.Hr(className="my-1"),

            # Fees Collected
            dbc.Row([
                dbc.Col(
                    html.Span(
                        "Fees Collected",
                        className="text-muted",
                        style={"fontSize": "clamp(12px,1vw,14px)"}
                    )
                ),
                dbc.Col(
                    html.Span(
                        f"₹ {collected:,}",
                        className="fw-semibold",
                        style={"fontSize": "clamp(13px,1.1vw,15px)"}
                    ),
                    width="auto"
                )
            ], align="center", className="py-1"),

            html.Hr(className="my-1"),

            # Fees Due
            dbc.Row([
                dbc.Col(
                    html.Span(
                        "Fees Due",
                        className="text-muted",
                        style={"fontSize": "clamp(12px,1vw,14px)"}
                    )
                ),
                dbc.Col(
                    html.Span(
                        f"₹ {due:,}",
                        className="fw-semibold",
                        style={
                            "fontSize": "clamp(13px,1.1vw,15px)",
                            "color": "#dc2626"
                        }
                    ),
                    width="auto"
                )
            ], align="center", className="py-1"),

            html.Hr(className="my-1"),

            # Collection Ratio
            dbc.Row([
                dbc.Col(
                    html.Span(
                        "Collection Ratio",
                        className="text-muted",
                        style={"fontSize": "clamp(12px,1vw,14px)"}
                    )
                ),
                dbc.Col(
                    html.Span(
                        f"{ratio} %",
                        className="fw-bold",
                        style={
                            "fontSize": "clamp(14px,1.2vw,16px)",
                            "color": "#16a34a"
                        }
                    ),
                    width="auto"
                )
            ], align="center", className="py-1"),

        ]),

        className="shadow-sm",
        style={
            "borderRadius": "12px",
            "minHeight": "160px",
            "padding": "4px"
        }
    )



def attendance_card(class_data, class_options, selected_class="All"):
    # --- LOGIC ---
    if not class_data:
        class_text = "No records found"
        class_value = 0.0
    else:
        if selected_class and selected_class != "All":
            filtered = [d for d in class_data if d['class'] == selected_class]
            if filtered:
                class_text = f"Stats for {selected_class}"
                class_value = float(filtered[0]['attendance_percentage'])
            else:
                class_text = "Data Not Found"
                class_value = 0.0
        else:
            avg_val = sum(d['attendance_percentage'] for d in class_data) / len(class_data)
            class_text = "Overall School Average"
            class_value = round(avg_val, 1)

    # Performance Colors
    progress_color = "#10b981" if class_value >= 85 else "#f59e0b" if class_value >= 70 else "#ef4444"

    return dbc.Card(
        dbc.CardBody([
            # 🔽 HEADER SECTION
            dbc.Row([
                dbc.Col([
                    html.Div([
                        html.I(className="bi bi-person-check-fill", 
                               style={"fontSize": "18px", "color": "#7c3aed"}),
                    ], style={
                        "backgroundColor": "#f5f3ff",
                        "width": "40px", "height": "40px",
                        "borderRadius": "10px",
                        "display": "flex", "alignItems": "center", "justifyContent": "center"
                    })
                ], width="auto"),
                
                dbc.Col([
                    html.H6("Attendance", className="fw-bold mb-0", style={"color": "#1e293b", "fontSize": "15px"}),
                    html.Small("Student Insights", className="text-muted", style={"fontSize": "11px"})
                ], className="ps-1"),

                # ✅ IMPROVED DROPDOWN
                dbc.Col([
                    dcc.Dropdown(
                        id="attendance-class-dropdown",
                        options=class_options,
                        value=selected_class,
                        clearable=False,
                        searchable=False,
                        maxHeight=150,  
                        style={
                            "fontSize": "13px", 
                            "border": "none", 
                            "backgroundColor": "#f8fafc",
                            "borderRadius": "8px",
                            "fontWeight": "500"
                            
                        },
                        className="shadow-sm" 
                    )
                ], xs=12, sm=6, md=6, lg=5, className="mt-2 mt-sm-0")
            ], align="center", className="mb-4 g-0"),

            # 📊 MAIN DISPLAY
            html.Div([
                html.Div([
                    html.Span(f"{class_value}", style={"fontSize": "34px", "fontWeight": "800", "color": "#1e293b", "letterSpacing": "-1px"}),
                    html.Span("%", style={"fontSize": "18px", "fontWeight": "600", "marginLeft": "2px", "color": "#94a3b8"}),
                ], className="d-flex align-items-baseline mb-1"),
                
                html.Div(class_text, className="text-muted small fw-medium mb-3"),
                
                # Dynamic Progress Bar
                dbc.Progress(
                    value=class_value,
                    color=progress_color,
                    style={"height": "7px", "borderRadius": "10px", "backgroundColor": "#f1f5f9"},
                )
            ]),

        ], style={"padding": "1.25rem"}),
        className="h-100 border-0 shadow-sm",
        style={
            "borderRadius": "20px",
            "backgroundColor": "#ffffff",
        }
    )



def teacher_attendance_card(teacher_data, selected_teacher="All"):

    # 🔽 DROPDOWN OPTIONS
    teacher_options = [{"label": "All", "value": "All"}]

    if teacher_data:
        teacher_options += [
            {"label": d["teacher"], "value": d["teacher"]}
            for d in teacher_data
        ]

    # --- LOGIC ---
    if not teacher_data:
        text = "No records found"
        value = 0.0

    else:
        if selected_teacher != "All":
            filtered = [d for d in teacher_data if d["teacher"] == selected_teacher]

            if filtered:
                value = float(filtered[0]["attendance_percentage"])
                text = f"Stats for {selected_teacher}"
            else:
                value = 0.0
                text = "Data Not Found"

        else:
            avg_val = sum(d['attendance_percentage'] for d in teacher_data) / len(teacher_data)
            value = round(avg_val, 1)
            text = "Overall Faculty Attendance"

    # 🎨 COLOR
    progress_color = "#10b981" if value >= 85 else "#f59e0b" if value >= 70 else "#ef4444"

    return dbc.Card(
        dbc.CardBody([

            # 🔽 HEADER + DROPDOWN
            dbc.Row([

                dbc.Col([
                    html.Div([
                        html.I(className="bi bi-person-badge-fill",
                               style={"fontSize": "18px", "color": "#0284c7"}),
                    ], style={
                        "backgroundColor": "#e0f2fe",
                        "width": "40px", "height": "40px",
                        "borderRadius": "10px",
                        "display": "flex", "alignItems": "center", "justifyContent": "center"
                    })
                ], width="auto"),

                dbc.Col([
                    html.H6("Teacher Attendance", className="fw-bold mb-0",
                            style={"color": "#1e293b", "fontSize": "15px"}),
                    html.Small("Faculty Insights", className="text-muted",
                               style={"fontSize": "11px"})
                ], className="ps-1"),

                # 🔥 DROPDOWN
                dbc.Col([
                    dcc.Dropdown(
                        id="teacher-dropdown",
                        options=teacher_options,
                        value=selected_teacher,
                        clearable=False,
                        searchable=False,
                        style={
                            "fontSize": "13px",
                            "backgroundColor": "#f8fafc",
                            "borderRadius": "8px",
                        },
                    )
                ], xs=12, sm=6, md=6, lg=5, className="mt-2 mt-sm-0")

            ], align="center", className="mb-4 g-0"),

            # 📊 VALUE
            html.Div([
                html.Div([
                    html.Span(f"{value}", style={
                        "fontSize": "34px",
                        "fontWeight": "800",
                        "color": "#1e293b"
                    }),
                    html.Span("%", style={
                        "fontSize": "18px",
                        "marginLeft": "2px",
                        "color": "#94a3b8"
                    }),
                ], className="d-flex align-items-baseline mb-1"),

                html.Div(text, className="text-muted small fw-medium mb-3"),

                dbc.Progress(
                    value=value,
                    color=progress_color,
                    style={
                        "height": "7px",
                        "borderRadius": "10px",
                        "backgroundColor": "#f1f5f9"
                    },
                )
            ])

        ], style={"padding": "1.25rem"}),

        className="h-100 border-0 shadow-sm",
        style={
            "borderRadius": "20px",
            "backgroundColor": "#ffffff",
        }
    )


