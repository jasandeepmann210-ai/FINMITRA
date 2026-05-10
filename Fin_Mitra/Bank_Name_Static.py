import dash
from dash import html, dcc, Input, Output, State
import dash_bootstrap_components as dbc
import pandas as pd
import os

# =========================================================
# CONFIG
# =========================================================

DEFAULT_BANKS = {
    f"BANK{i}": f"Bank {i}" for i in range(1, 11)
}

# =========================================================
# LOAD / INIT CSV
# =========================================================
def load_bank_labels(SessionData):
    BANK_LABEL_PATH = "/var/Data/"+str(SessionData["username"])+"/bank_name_static.csv"

    if not os.path.exists(BANK_LABEL_PATH):
        df = pd.DataFrame(
            [{"bank_code": k, "bank_label": v} for k, v in DEFAULT_BANKS.items()]
        )
        df.to_csv(BANK_LABEL_PATH, index=False)
        return df

    return pd.read_csv(BANK_LABEL_PATH)


# =========================================================
# LAYOUT
# =========================================================
def get_layout(SessionData):
    df = load_bank_labels(SessionData)
    label_map = dict(zip(df.bank_code, df.bank_label))

    table_rows = []
    for i in range(1, 11):
        table_rows.append(
            html.Tr([
                html.Td(f"Bank {i}", className="fw-semibold"),
                html.Td(
                    dbc.Input(
                        id=f"bank-label-{i}",
                        type="text",
                        value=label_map.get(f"BANK{i}", f"Bank {i}"),
                    )
                ),
            ])
        )

    return dbc.Container(
        [
            # ================= HEADER =================
            dbc.Row(
                dbc.Col(
                    dbc.Card(
                        dbc.CardBody(
                            [
                                html.H4(
                                    "Bank Label Configuration",
                                    className="fw-bold text-center mb-1",
                                ),
                                html.P(
                                    "Rename Bank 1 to Bank 10 (UI only)",
                                    className="text-muted text-center mb-0",
                                ),
                            ]
                        ),
                        className="shadow-sm border-0",
                    ),
                    width=12,
                ),
                className="my-4",
            ),

            # ================= TABLE =================
            dbc.Row(
                dbc.Col(
                    dbc.Card(
                        dbc.CardBody(
                            [
                                dbc.Table(
                                    [
                                        html.Thead(
                                            html.Tr([
                                                html.Th("Bank Code"),
                                                html.Th("Display Name"),
                                            ])
                                        ),
                                        html.Tbody(table_rows),
                                    ],
                                    bordered=True,
                                    hover=True,
                                    responsive=True,
                                    size="sm",
                                ),

                                dbc.Button(
                                    "Submit",
                                    id="submit-bank-labels",
                                    color="primary",
                                    className="mt-3",
                                ),
                            ]
                        ),
                        className="shadow-sm border-0",
                    ),
                    md=8,
                    className="mx-auto",
                )
            ),

            # ================= SUCCESS TOAST =================
            dbc.Toast(
                "Submitted successfully",
                id="bank-label-toast",
                header="Success",
                is_open=False,
                dismissable=True,
                duration=3000,
                icon="success",
                style={
                    "position": "fixed",
                    "top": 20,
                    "right": 20,
                    "width": 350,
                    "zIndex": 2000,
                },
            ),
        ],
        fluid=True,
        className="bg-light min-vh-100 px-4",
    )


# =========================================================
# CALLBACKS
# =========================================================
def register_callbacks(app):

    @app.callback(
        Output("bank-label-toast", "is_open"),
        Input("submit-bank-labels", "n_clicks"),
        [
            State(f"bank-label-{i}", "value")
            for i in range(1, 11)
        ],
        State("session","data"),
        prevent_initial_call=True,
    )
    def save_bank_labels(_, *values):

        *bank_values, SessionData = values

        data = [
            {
                "bank_code": f"BANK{i+1}",
                "bank_label": values[i] or f"Bank {i+1}",
            }
            for i in range(10)
        ]

        BANK_LABEL_PATH = "/var/Data/"+str(SessionData["username"])+"/bank_name_static.csv"
        df = pd.DataFrame(data)
        df.to_csv(BANK_LABEL_PATH, index=False)

        return True




