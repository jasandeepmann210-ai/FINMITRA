from dash import html, Input, Output, State
import dash_bootstrap_components as dbc
import pandas as pd
import ast
import re

import Receipt_Payment
import Income_Expenditure
import Balance_Sheet
import Trial_Balance
import Fixed_Asset_Chart
import depreciaiton_mapper
import rs

import numpy as np

# ==================================================
# PAYMENT SIGN EXCEPTIONS (ONLY FOR MAN_ ENTRIES)
# ==================================================
ASSET_EXPENSE_GROUPS = {
    "Fixed Assets",
    "Investments",
    "Loans and Advances",
    "Cash-in-Hand",
    "Bank Accounts",
    "Current Assets",
    "Prepaid Expense",
    "Depreciation",
    "Inventories",
    "Indirect Expenses",
}

LIABILITY_INCOME_GROUPS = {
    "Current Liabilities",
    "Non-current liabilities Secured loans",
    "Non-current liabilities Unsecured loans",
    "Sundry creditors",
    "Unearned Revenue",
    "Provisions (Bad Debts, Warranty)",
    "Outstanding Expense",
    "Deferred Tax",
    "Sundry debtors",
    "Accrued Income",
    "Direct Income",
    "Indirect Income",
    "Reserve & Surplus",
}


# =====================================================
# DATE NORMALIZER (SINGLE SOURCE OF TRUTH)
# =====================================================

def normalize_txn_date(val):
    """
    Accepts:
    - DD-MM-YYYY (ledger parser / UI)
    - YYYY-MM-DD (already normalized)
    Returns:
    - YYYY-MM-DD string
    """
    if pd.isna(val):
        return None

    val = str(val).strip()

    # DD-MM-YYYY
    if re.match(r"\d{2}-\d{2}-\d{4}$", val):
        return pd.to_datetime(val, format="%d-%m-%Y").strftime("%Y-%m-%d")

    # YYYY-MM-DD
    if re.match(r"\d{4}-\d{2}-\d{2}$", val):
        return val

    raise ValueError(f"Invalid transaction_date format: {val}")


# =====================================================
# LEDGER → MELT DB BUILDER
# =====================================================

def build_melt_db(SessionData):

    ledger_df = pd.read_csv("/var/Data/"+str(SessionData["username"])+"/master_ledger.csv")
    
    # 🔐 Normalize ledger dates ONCE
    ledger_df["transaction_date"] = ledger_df["transaction_date"].apply(normalize_txn_date)
    
    BREAKUP_COLS = ["breakup_cash", "breakup_bank1", "breakup_bank2", "breakup_bank3", "breakup_bank4", "breakup_bank5"
                   , "breakup_bank6", "breakup_bank7", "breakup_bank8", "breakup_bank9", "breakup_bank10"]
    parsed_rows = []
    
    # --------------------------------------------------
    # PARSE MASTER LEDGER
    # --------------------------------------------------
    for _, row in ledger_df.iterrows():
        entry_id = row["entry_id"]
        txn_date = row["transaction_date"]
        form_name = row["form_name"]
        ledger_group = row["ledger_group"]
        is_manual = str(entry_id).startswith("MAN_")
        is_payment = "PAYMENT" in str(form_name).upper()
        is_receipt = "RECEIPT" in str(form_name).upper()
        has_breakup = False
    
        # ==================================================
        # SHAPE 1 & 2 — EXPLICIT BREAKUPS
        # ==================================================
        for col in BREAKUP_COLS:
            val = row.get(col)
            if pd.isna(val):
                continue
    
            try:
                converted = ast.literal_eval(val)
            except Exception:
                continue
    
            if not isinstance(converted, dict) or not converted:
                continue
    
            has_breakup = True
    
            for line_item, value in converted.items():
                amount = value.get("amount", 0) if isinstance(value, dict) else value
    
                try:
                    amount = float(amount)
                except Exception:
                    continue
    
                if amount != 0:
                    parsed_rows.append({
                        "entry_id": entry_id,
                        "transaction_date": txn_date,  # ✅ ISO STRING
                        "LINE_ITEM": line_item,
                        "amount": amount,
                        "source": col
                    })
    

        # ==================================================
        # SHAPE 3 — IMPLICIT SINGLE-LINE ENTRIES
        # ==================================================
        if not has_breakup:
            line_item = row.get("ledger_name")
            if not line_item:
                continue
        
            channel_map = {
                "cash_amount": "breakup_cash",
                "bank1_amount": "breakup_bank1",
                "bank2_amount": "breakup_bank2",
                "bank3_amount": "breakup_bank3",
                "bank4_amount": "breakup_bank4",
                "bank5_amount": "breakup_bank5",
                "bank6_amount": "breakup_bank6",
                "bank7_amount": "breakup_bank7",
                "bank8_amount": "breakup_bank8",
                "bank9_amount": "breakup_bank9",
                "bank10_amount": "breakup_bank10",
            }

        
            for amt_col, source in channel_map.items():
                try:
                    amt = float(row.get(amt_col, 0) or 0)
                except Exception:
                    continue
        
                if amt != 0:
                    # 🔴 SIGN OVERRIDE 
                    if is_manual:
                        if ledger_group in ASSET_EXPENSE_GROUPS:
                            if is_payment:
                                amt = abs(amt)        # Asset + on payment
                            elif is_receipt:
                                amt = -abs(amt)       # Asset - on receipt
                    
                        elif ledger_group in LIABILITY_INCOME_GROUPS:
                            if is_payment:
                                amt = -abs(amt)       # Liability - on payment
                            elif is_receipt:
                                amt = abs(amt)        # Liability + on receipt


                    # ---------------------------------
                    # WITHDRAWALS EXCEPTION FIX
                    # ---------------------------------
                    if ledger_group == "Reserve & Surplus":
                        if isinstance(line_item, str) and line_item.strip().lower() in {
                            "withdrawls",
                            "withdrawals",
                            "drawings"
                        }:
                            amt = -abs(amt)

        
                    parsed_rows.append({
                        "entry_id": entry_id,
                        "transaction_date": txn_date,  # ✅ ISO STRING
                        "LINE_ITEM": line_item,
                        "amount": amt,
                        "source": source
                    })

    
        # ==================================================
        # SHAPE 4 — JOURNAL / OPENING BALANCE STYLE ENTRIES
        # (cash, bank1, bank2 empty BUT total_amount present)
        # ==================================================
        cash = row.get("cash_amount", 0)
        bank1 = row.get("bank1_amount", 0)
        bank2 = row.get("bank2_amount", 0)
        bank3 = row.get("bank3_amount", 0)
        bank4 = row.get("bank4_amount", 0)
        bank5 = row.get("bank5_amount", 0)
        bank6 = row.get("bank6_amount", 0)
        bank7 = row.get("bank7_amount", 0)
        bank8 = row.get("bank8_amount", 0)
        bank9 = row.get("bank9_amount", 0)
        bank10 = row.get("bank10_amount", 0)
        total_amount = row.get("total_amount", 0)
    
        try:
            cash = float(cash or 0)
            bank1 = float(bank1 or 0)
            bank2 = float(bank2 or 0)
            bank3 = float(bank3 or 0)
            bank4 = float(bank4 or 0)
            bank5 = float(bank5 or 0)
            bank6 = float(bank6 or 0)
            bank7 = float(bank7 or 0)
            bank8 = float(bank8 or 0)
            bank9 = float(bank9 or 0)
            bank10 = float(bank10 or 0)
            total_amount = float(total_amount or 0)
        except Exception:
            pass
    
        if (
            cash == 0
            and bank1 == 0
            and bank2 == 0
            and bank3 == 0
            and bank4 == 0
            and bank5 == 0
            and bank6 == 0
            and bank7 == 0
            and bank8 == 0
            and bank9 == 0
            and bank10 == 0
            and total_amount != 0
        ):
            line_item = row.get("ledger_name")
            if line_item:
                parsed_rows.append({
                    "entry_id": entry_id,
                    "transaction_date": txn_date,  # ✅ ISO STRING
                    "LINE_ITEM": line_item,
                    "amount": total_amount,
                    "source": "Journal Book"
                })
    
    parsed_df = pd.DataFrame(parsed_rows)
    
    
    # --------------------------------------------------
    # JOURNAL BOOK PARSING
    # --------------------------------------------------
    journal_df = pd.read_csv("/var/Data/"+str(SessionData["username"])+"/journal_ledger.csv")

    # 🔐 Normalize journal dates ONCE
    journal_df["transaction_date"] = journal_df["transaction_date"].apply(normalize_txn_date)

    parsed_rows = []

    for _, row in journal_df.iterrows():
        entry_id = row["entry_id"]
        txn_date = row["transaction_date"]
        val = row["journal_entries"]

        if pd.isna(val):
            continue

        try:
            breakup_list = ast.literal_eval(val)
            converted = pd.DataFrame(breakup_list)

            if not {"account", "debit", "credit"}.issubset(converted.columns):
                continue

            converted["amount"] = converted["credit"] + converted["debit"]

            for _, r in converted.iterrows():
            
                amt = float(r["amount"])
                account = r["account"]
            
                # 🟢 WITHDRAWALS FIX FOR JOURNAL ALSO
                if ledger_group == "Reserve & Surplus":
                    if isinstance(account, str) and account.strip().lower() in {
                        "withdrawls",
                        "withdrawals",
                        "drawings"
                    }:
                        amt = -abs(amt)
            
                parsed_rows.append({
                    "entry_id": entry_id,
                    "transaction_date": txn_date,
                    "LINE_ITEM": account,
                    "amount": amt,
                    "source": "Journal Book"
                })


        except Exception:
            continue

    journal_parsed_df = pd.DataFrame(parsed_rows)
    parsed_df = pd.concat([parsed_df, journal_parsed_df], ignore_index=True)

    # --------------------------------------------------
    # APPLY MAPPER
    # --------------------------------------------------
    mapper_df = pd.read_excel("/var/Data/"+str(SessionData["username"])+"/Mapper.xlsx")

    def norm(x):
        return None if pd.isna(x) else re.sub(r"\s+", " ", str(x)).strip().upper()

    mapper_df["LINE_ITEM_NORM"] = mapper_df["LINE_ITEM"].apply(norm)
    parsed_df["LINE_ITEM_NORM"] = parsed_df["LINE_ITEM"].apply(norm)

    parsed_df = (
        parsed_df
        .merge(
            mapper_df[["LINE_ITEM_NORM", "GROUP", "FS_GROUP"]],
            on="LINE_ITEM_NORM",
            how="left"
        )
        .drop(columns=["LINE_ITEM_NORM"]).drop_duplicates(keep="first")
    )

    # --------------------------------------------------
    # FINAL CLEANUP
    # --------------------------------------------------
    parsed_df["amount"] = pd.to_numeric(parsed_df["amount"], errors="coerce").fillna(0)

    # 🔒 WRITE ISO DATE ONLY
    parsed_df.to_csv("/var/Data/"+str(SessionData["username"])+"/melt_db.csv", index=False)

    return {
        "rows": len(parsed_df),
        "unmapped": int(parsed_df["GROUP"].isna().sum())
    }


# =====================================================
# LAYOUT
# =====================================================

def get_layout():
    return dbc.Container(
        [
            html.H2(
                "📊 Financial Statements",
                className="text-center my-4 fw-bold",
                style={"letterSpacing": "0.5px"}
            ),

            dbc.Button(
                "⚡ Run Ledger Parser",
                id="run-ledger-parser",
                color="warning",
                className="mb-3 shadow-sm px-4"
            ),

            html.Div(id="parser-status", className="mb-4"),

            dbc.Card(
                dbc.CardBody(
                    dbc.Tabs(
                        [
                            dbc.Tab(
                                Receipt_Payment.get_layout1(),
                                label="💰 Receipt & Payment",
                                tab_class_name="custom-tab",
                                active_tab_class_name="custom-tab-active",
                            ),
                            dbc.Tab(
                                Income_Expenditure.get_layout1(),
                                label="📈 Income & Expenditure",
                                tab_class_name="custom-tab",
                                active_tab_class_name="custom-tab-active",
                            ),
                            dbc.Tab(
                                rs.get_layout1(),
                                label="📈 Reserve & Surplus",
                                tab_class_name="custom-tab",
                                active_tab_class_name="custom-tab-active",
                            ),
                            dbc.Tab(
                                Balance_Sheet.get_layout1(),
                                label="📑 Balance Sheet",
                                tab_class_name="custom-tab",
                                active_tab_class_name="custom-tab-active",
                            ),
                            dbc.Tab(
                                depreciaiton_mapper.get_layout1(),
                                label="🧮 Depreciation",
                                tab_class_name="custom-tab",
                                active_tab_class_name="custom-tab-active",
                            ),
                            dbc.Tab(
                                Trial_Balance.get_layout1(),
                                label="📊 Trial Balance",
                                tab_class_name="custom-tab",
                                active_tab_class_name="custom-tab-active",
                            ),
                            dbc.Tab(
                                Fixed_Asset_Chart.get_layout1(),
                                label="🏢 Fixed Assets",
                                tab_class_name="custom-tab",
                                active_tab_class_name="custom-tab-active",
                            ),
                        ],
                        class_name="custom-tabs",
                    )

                ),
                className="shadow-lg rounded-4 border-0"
            ),
        ],
        fluid=True,
    )



# =====================================================
# CALLBACK REGISTRATION
# =====================================================

def register_callbacks(app):

    @app.callback(
        Output("parser-status", "children"),
        Input("run-ledger-parser", "n_clicks"),
        State("session","data"),
        prevent_initial_call=True
    )
    def run_parser(_,SesionData):
        stats = build_melt_db(SesionData)
        return dbc.Alert(
            f"melt_db.csv regenerated | rows: {stats['rows']} | unmapped: {stats['unmapped']}",
            color="success",
            dismissable=True
        )

    Receipt_Payment.register_callbacks(app)
    Income_Expenditure.register_callbacks(app)
    Balance_Sheet.register_callbacks(app)
    Trial_Balance.register_callbacks(app)
    Fixed_Asset_Chart.register_callbacks(app)
    depreciaiton_mapper.register_callbacks(app)
    rs.register_callbacks(app)





