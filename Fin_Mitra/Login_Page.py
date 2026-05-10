# --- Login Layout ---
from dash import Dash, html, dcc, Input, Output, State
import dash
from flask import session, redirect, request


def get_login_layout():
    return html.Div(
        [
            html.Div(
                [
                    html.Img(
                        src="/assets/logo.png",
                        style={"height": "80px", "marginBottom": "25px"}
                    ),

                    # Brand title
                    html.Span(
                        "Sheep.AI FinMitra",
                        style={
                            "fontSize": "32px",
                            "fontWeight": "700",
                            "color": "#1F3A5F",
                            "marginBottom": "6px"
                        }
                    ),

                    html.Span(
                        "Sheep.AI Advisory LLP",
                        style={
                            "fontSize": "15px",
                            "fontWeight": "500",
                            "color": "#6B7C93",
                            "marginBottom": "35px"
                        }
                    ),

                    # ================= LOGIN CARD =================
                    html.Div(
                        [
                            html.Div(
                                "Login to your account",
                                style={
                                    "fontSize": "20px",
                                    "fontWeight": "600",
                                    "color": "#243447",
                                    "marginBottom": "25px",
                                    "textAlign": "center"
                                }
                            ),

                            # Username
                            html.Div(
                                [
                                    html.Label(
                                        "Username",
                                        style={
                                            "fontSize": "13px",
                                            "color": "#243447",
                                            "fontWeight": "600",
                                            "marginBottom": "6px",
                                            "display": "block"
                                        }
                                    ),
                                    dcc.Input(
                                        id="username",
                                        type="text",
                                        placeholder="Enter your username",
                                        style={
                                            "width": "100%",
                                            "padding": "12px 14px",
                                            "border": "1.5px solid #E3EAF0",
                                            "borderRadius": "6px",
                                            "fontSize": "14px",
                                            "fontFamily": "Segoe UI, Arial, sans-serif",
                                            "boxSizing": "border-box"
                                        }
                                    ),
                                ],
                                style={"marginBottom": "20px"}
                            ),

                            # Password
                            html.Div(
                                [
                                    html.Label(
                                        "Password",
                                        style={
                                            "fontSize": "13px",
                                            "color": "#243447",
                                            "fontWeight": "600",
                                            "marginBottom": "6px",
                                            "display": "block"
                                        }
                                    ),
                                    dcc.Input(
                                        id="password",
                                        type="password",
                                        placeholder="Enter your password",
                                        style={
                                            "width": "100%",
                                            "padding": "12px 14px",
                                            "border": "1.5px solid #E3EAF0",
                                            "borderRadius": "6px",
                                            "fontSize": "14px",
                                            "fontFamily": "Segoe UI, Arial, sans-serif",
                                            "boxSizing": "border-box"
                                        }
                                    ),
                                ],
                                style={"marginBottom": "25px"}
                            ),

                            # Error message
                            html.Div(
                                id="login-message",
                                style={
                                    "color": "#D64545",
                                    "marginBottom": "15px",
                                    "height": "20px",
                                    "textAlign": "center",
                                    "fontSize": "13px",
                                    "fontWeight": "600"
                                }
                            ),

                            # Login button
                            html.Button(
                                "Login",
                                id="login-button",
                                n_clicks=0,
                                style={
                                    "width": "100%",
                                    "padding": "14px",
                                    "backgroundColor": "#6BBF59",
                                    "color": "white",
                                    "border": "none",
                                    "borderRadius": "8px",
                                    "cursor": "pointer",
                                    "fontSize": "16px",
                                    "fontWeight": "600",
                                    "transition": "all 0.25s ease"
                                }
                            ),
                        ],
                        style={
                            "backgroundColor": "#FFFFFF",
                            "padding": "35px 40px",
                            "borderRadius": "14px",
                            "width": "400px",
                            "border": "1px solid #E3EAF0",
                            "boxShadow": "0 10px 30px rgba(31, 58, 95, 0.12)"
                        }
                    ),
                ],
                style={
                    "display": "flex",
                    "flexDirection": "column",
                    "alignItems": "center",
                    "justifyContent": "center",
                    "height": "100vh",
                    "backgroundColor": "#FAFCFE"
                }
            )
        ]
    )


