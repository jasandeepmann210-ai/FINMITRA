from dash import html
import dash_bootstrap_components as dbc
import pandas as pd
import os
from dash import Input, Output, State
from dash import callback

from dash import html, dcc
from datetime import datetime
from universal_kpi_card import (
    fees_collection_card,
    student_overview_card,
    upcoming_events_card,
    birthday_card,
    universal_kpi_card,
    monthly_fee_card,
    bank_closing_dropdown_card,
    attendance_card,
    teacher_attendance_card
)
from datetime import date
from CT_Exposure_Dashboard import normalize_txn_date
from Due_Fee_Retreiver import month_end, months_between, parse_account_name




# --------------------------------------
# 📊 CLASS-WISE STUDENT ATTENDANCE
# --------------------------------------


def get_class_options(username):
    path = f"/var/Data/{username}/fee_structure_static.csv"

    if not os.path.exists(path):
        return [{"label": "All Classes", "value": "All"}]

    df = pd.read_csv(path)

    options = []

    for _, row in df.iterrows():
        standard = str(row["standard"]).strip()

        # KG same rahega
        if standard in ["Pre School", "Junior KG", "Senior KG"]:
            options.append({
                "label": standard,
                "value": standard
            })

        # Class → sirf number
        elif "Class" in standard:
            num = standard.replace("Class", "").strip()

            options.append({
                "label": num,   # 👈 1,2,3
                "value": num
            })

    return [{"label": "All Classes", "value": "All"}] + options

def get_class_attendance(username, start_date=None, end_date=None):

    path = f"/var/Data/{username}/student_attendance.csv"

    if not os.path.exists(path):
        return []

    df = pd.read_csv(path)

    # 🔥 CLEAN
    df["class"] = df["class"].astype(str).str.strip()
    df["status"] = df["status"].str.lower().str.strip()

    # -----------------------------
    # ❌ NO MAPPING (REMOVE THIS)
    # -----------------------------

    # date
    df["date"] = pd.to_datetime(df["date"], errors="coerce")

    if start_date and end_date:
        df = df[(df["date"] >= start_date) & (df["date"] <= end_date)]

    # remove holidays
    df = df[df["status"] != "holiday"]

    # sirf valid numeric classes (1–12)
    df = df[df["class"].str.isnumeric()]

    if df.empty:
        return []

    result = (
        df.groupby("class")
        .apply(lambda x: round((x["status"] == "present").sum() / len(x) * 100, 2))
        .reset_index(name="attendance_percentage")
    )

    return result.to_dict("records")


# --------------------------------------
# 👨‍🏫 TEACHER ATTENDANCE %
# --------------------------------------
def get_teacher_attendance(username, start_date=None, end_date=None):

    path = f"/var/Data/{username}/teacher_attendance.csv"

    if not os.path.exists(path):
        return []

    df = pd.read_csv(path)

    # 🔥 CLEAN
    df["teacher"] = df["teacher"].astype(str).str.strip()
    df["status"] = df["status"].str.lower().str.strip()

    # date
    df["date"] = pd.to_datetime(df["date"], errors="coerce")

    if start_date and end_date:
        df = df[(df["date"] >= start_date) & (df["date"] <= end_date)]

    # ❌ holidays hata do
    df = df[df["status"] != "holiday"]

    if df.empty:
        return []

    # ✅ teacher-wise %
    result = (
        df.groupby("teacher")
        .apply(lambda x: round((x["status"] == "present").sum() / len(x) * 100, 2))
        .reset_index(name="attendance_percentage")
    )

    return result.to_dict("records")






# -----------------------------
# BIRTHDAY WISHER (DASHBOARD VERSION)
# -----------------------------




def get_today_birthdays(username):

    path = f"/var/Data/{username}/student_log.csv"

    if not os.path.exists(path):
        return []

    df = pd.read_csv(path)

    if "dob" not in df.columns:
        return []

    df["dob"] = pd.to_datetime(df["dob"], errors="coerce", dayfirst=True)

    today = pd.Timestamp.today()

    df_today = df[(df["dob"].dt.day == today.day) & (df["dob"].dt.month == today.month)]

    if df_today.empty:
        return []

    students = [
        {"name": row["student_name"], "class": row["studying_class"]}
        for _, row in df_today.iterrows()
    ]

    return students


# -----------------------------
# UPCOMING EVENTS (DASHBOARD)
# -----------------------------
def get_upcoming_events(username):

    path = f"/var/Data/{username}/events.csv"

    if not os.path.exists(path):
        return []

    try:
        df = pd.read_csv(path)

        if not {"event", "date"}.issubset(df.columns):
            return []

        df["date"] = pd.to_datetime(df["date"], errors="coerce")

        today = pd.Timestamp.today().normalize()

        df = df[df["date"] >= today]

        df = df.sort_values("date").head(10)

        events = [
            {"title": row["event"], "date": row["date"].strftime("%d %b")}
            for _, row in df.iterrows()
        ]

        return events

    except:
        return []


# -----------------------------
# FY DATE RANGE HELPER
# -----------------------------
def get_fy_date_range(selected_fy):
    if not selected_fy:
        return None, None

    fy_year = int(selected_fy.replace("FY", ""))
    end_year = 2000 + fy_year
    start_year = end_year - 1

    return datetime(start_year, 4, 1), datetime(end_year, 3, 31)


# -----------------------------
# TOTAL STUDENTS
# -----------------------------
def get_student_overview(username):

    student_path = f"/var/Data/{username}/student_log.csv"
    tc_path = f"/var/Data/{username}/tc_register.csv"

    if not os.path.exists(student_path):
        return 0, 0, 0, 0

    df = pd.read_csv(student_path)

    total_students = len(df)

    # Boys / Girls
    boys = len(df[df["gender"] == 1])
    girls = len(df[df["gender"] == 2])

    # Students Left
    if os.path.exists(tc_path):
        tc_df = pd.read_csv(tc_path)
        students_left = len(tc_df)
    else:
        students_left = 0

    # Active students
    active_students = total_students - students_left

    return active_students, boys, girls, students_left


# -----------------------------
# TOTAL RECEIPTS
# -----------------------------
def get_total_receipts(username, start_date, end_date):
    path = f"/var/Data/{username}/other_receipt_ledger.csv"

    if not os.path.exists(path):
        return 0, 0  # amount, count

    df = pd.read_csv(path)

    if "transaction_date" in df.columns:
        df["transaction_date"] = pd.to_datetime(
            df["transaction_date"], errors="coerce", dayfirst=True
        )

        if start_date and end_date:
            df = df[
                (df["transaction_date"] >= start_date)
                & (df["transaction_date"] <= end_date)
            ]

    df["total_amount"] = pd.to_numeric(df["total_amount"], errors="coerce").fillna(0)

    total_amount = df["total_amount"].sum()
    total_count = len(df)

    return total_amount, total_count


# ---------------------------------------------
# BANK CLOSING BALANCE (Dashboard KPI)
# ---------------------------------------------
def get_single_bank_closing(username, bank_col, start_date=None, end_date=None):

    path = f"/var/Data/{username}/master_ledger.csv"

    if not os.path.exists(path) or not start_date or not end_date:
        return 0

    df = pd.read_csv(path)

    # 🔒 Normalize form_name (VERY IMPORTANT)
    df["form_name"] = df["form_name"].str.strip().str.upper()

    # 🔒 Date parsing (same safe logic)
    df["transaction_date"] = pd.to_datetime(
        df["transaction_date"], errors="coerce", format="mixed"
    )

    df = df[df["transaction_date"].notna()]
    df["transaction_date"] = df["transaction_date"].dt.normalize()
    bank_amount_col = f"{bank_col.lower()}_amount"

    if bank_amount_col not in df.columns:
        return 0

    df[bank_amount_col] = pd.to_numeric(df[bank_amount_col], errors="coerce").fillna(0)

    # BANK ONLY
    df = df[df[bank_amount_col] != 0]

    start_date = pd.to_datetime(start_date).normalize()
    end_date = pd.to_datetime(end_date).normalize()

    # --------------------------------------------------
    # 🔹 OPENING BALANCE
    # --------------------------------------------------
    prior_df = df[df["transaction_date"] < start_date]

    opening_balance = (
        prior_df[prior_df["form_name"].isin(["FEES RECEIPT", "OTHER RECEIPT"])][
            bank_amount_col
        ].sum()
        - prior_df[
            prior_df["form_name"].isin(
                ["EXPENSES", "SALARY PAYMENT", "OTHER PAYMENT", "DECLARE ASSETS"]
            )
        ][bank_amount_col].sum()
    )

    # --------------------------------------------------
    # 🔹 CURRENT PERIOD
    # --------------------------------------------------
    period_df = df[
        (df["transaction_date"] >= start_date) & (df["transaction_date"] <= end_date)
    ]

    # Receipts
    receipt_df = period_df[
        period_df["form_name"].isin(["FEES RECEIPT", "OTHER RECEIPT"])
    ][bank_amount_col]

    # Payments
    payment_df = period_df[
        period_df["form_name"].isin(
            ["EXPENSES", "SALARY PAYMENT", "OTHER PAYMENT", "DECLARE ASSETS"]
        )
    ][bank_amount_col]

    # 🔥 Negative payments → receipts (ROW LEVEL FIX)
    neg_payment_sum = payment_df[payment_df < 0].abs().sum()

    total_receipts = receipt_df.sum() + neg_payment_sum
    total_payments = payment_df[payment_df > 0].sum()

    # --------------------------------------------------
    # 🔹 CLOSING
    # --------------------------------------------------
    closing_balance = opening_balance + total_receipts - total_payments

    return closing_balance


def get_monthly_fee_data(username, start_date=None, end_date=None, view_type="month"):

    path = f"/var/Data/{username}/fees_ledger.csv"

    if not os.path.exists(path):
        return [], []

    df = pd.read_csv(path)

    # -----------------------------
    # 🔥 DATA CLEANING (VERY IMPORTANT)
    # -----------------------------
    df = df.dropna(how="all")  # remove fully blank rows
    df = df[df["entry_id"].notna()]  # remove broken rows
    df = df[df["form_name"] == "FEES RECEIPT"]  # only fee receipts

    # Convert date
    df["transaction_date"] = pd.to_datetime(
        df["transaction_date"], errors="coerce", dayfirst=True
    )

    df = df[df["transaction_date"].notna()]

    # Convert amount
    df["total_amount"] = pd.to_numeric(df["total_amount"], errors="coerce").fillna(0)

    df = df[df["total_amount"] > 0]  # remove zero entries

    # -----------------------------
    # 🔥 FY FILTER
    # -----------------------------
    if start_date and end_date:
        df = df[
            (df["transaction_date"] >= start_date)
            & (df["transaction_date"] <= end_date)
        ]

    # If no FY selected, avoid crash
    if not start_date or not end_date:
        return [], []

    # -----------------------------
    # 🔥 GROUPING LOGIC
    # -----------------------------
    if view_type == "quarter":

        # FY aligned quarter (Apr-Mar)
        df["period"] = df["transaction_date"].dt.to_period("Q-MAR")

        grouped = df.groupby("period")["total_amount"].sum()

        fy_quarters = pd.period_range(start=start_date, end=end_date, freq="Q-MAR")

        grouped = grouped.reindex(fy_quarters, fill_value=0)

        labels = [f"Q{i+1}" for i in range(len(grouped))]
        values = grouped.values.tolist()

    else:

        df["period"] = df["transaction_date"].dt.to_period("M")

        grouped = df.groupby("period")["total_amount"].sum()

        fy_months = pd.period_range(start=start_date, end=end_date, freq="M")

        grouped = grouped.reindex(fy_months, fill_value=0)

        labels = grouped.index.strftime("%b").tolist()
        values = grouped.values.tolist()

    return labels, values


# ---------------------------------------------
# TOTAL FEE DUE (Dashboard Version)
# ---------------------------------------------
def get_total_fee_due(username, start_date=None, end_date=None):
    base = f"/var/Data/{username}"

    try:
        students = pd.read_csv(f"{base}/student_log.csv")
        ledger = pd.read_csv(f"{base}/fees_ledger.csv")
        fee_struct = pd.read_csv(f"{base}/fee_structure_static.csv")
        ledger = ledger[ledger["form_name"] == "FEES RECEIPT"]
    except:
        return 0, 0

    # ---------------------------
    # EXTRACT ADMISSION NUMBER ONLY (LEDGER)
    # ---------------------------
    ledger["admission_no"] = ledger["account_name"].astype(str).str.split("/").str[1]

    ledger["admission_no"] = ledger["admission_no"].astype(str)

    # ---------------------------
    # NORMALIZE TYPES
    # ---------------------------
    ledger["admission_no"] = ledger["admission_no"].astype(str)

    students["admission_no"] = students["admission_no"].astype(str)
    students["studying_class"] = students["studying_class"].astype(str)

    fee_struct["studying_class"] = fee_struct["studying_class"].astype(str)
    fee_struct["monthly_fee"] = pd.to_numeric(
        fee_struct["monthly_fee"], errors="coerce"
    ).fillna(0)

    amount_cols = [
    "cash_amount",
    "bank1_amount","bank2_amount","bank3_amount","bank4_amount",
    "bank5_amount","bank6_amount","bank7_amount","bank8_amount",
    "bank9_amount","bank10_amount"
]
 
    for col in amount_cols:
     if col not in ledger.columns:
        ledger[col] = 0

    ledger[amount_cols] = ledger[amount_cols].apply(
    pd.to_numeric, errors="coerce"
).fillna(0)

    ledger["calculated_total"] = ledger[amount_cols].sum(axis=1)

    # ---------------------------
    # AGGREGATE PAID AMOUNT (BY ADMISSION ONLY)
    # ---------------------------
    paid_df = (
        ledger.groupby(["admission_no"], as_index=False)
        .agg({"calculated_total": "sum"})
.rename(columns={"calculated_total": "amount_paid"})
    )

    # ---------------------------
    # JOIN (CLASS FROM STUDENT_LOG ONLY)
    # ---------------------------
    merged = students.merge(fee_struct, on="studying_class", how="left").merge(
        paid_df, on="admission_no", how="left"
    )

    merged["amount_paid"] = merged["amount_paid"].fillna(0)

    # ---------------------------
    # TIME-BASED FEE CALCULATION
    # ---------------------------
    today = pd.to_datetime(end_date).normalize()

    if "current_academic_year" not in merged.columns:
        merged["current_academic_year"] = merged["admission_date"]

    merged["current_academic_year"] = (
        merged["current_academic_year"]
        .fillna(merged["admission_date"])
        .astype(str)
        .str.replace("-", "/", regex=False)
    )

    merged["current_academic_year"] = pd.to_datetime(
        merged["current_academic_year"], format="%d/%m/%Y", errors="coerce"
    )

    merged["admission_month_end"] = merged["current_academic_year"].apply(month_end)

    merged["months_elapsed"] = (
        merged["admission_month_end"]
        .apply(lambda d: months_between(d, today))
        .clip(lower=0)
    )

    # ---------------------------
    # FEE CALCULATION (ALIGNED)
    # ---------------------------
    # Ensure concession column exists
    if "monthly_fee_concession" not in merged.columns:
        merged["monthly_fee_concession"] = 0
    
    merged["monthly_fee_concession"] = pd.to_numeric(
        merged["monthly_fee_concession"], errors="coerce"
    ).fillna(0)
    
    # Prevent concession > fee
    merged["monthly_fee_concession"] = merged[
        ["monthly_fee_concession", "monthly_fee"]
    ].min(axis=1)
    
    # Apply concession
    merged["effective_monthly_fee"] = (
        merged["monthly_fee"] - merged["monthly_fee_concession"]
    ).clip(lower=0)
    
    # Final expected fee
    merged["expected_fee"] = merged["months_elapsed"] * merged["effective_monthly_fee"]

    merged["fee_due"] = (merged["expected_fee"] - merged["amount_paid"]).clip(lower=0)

    # ---------------------------
    # FINAL OUTPUT
    # ---------------------------
    total_due = merged["fee_due"].sum()
    students_with_due = (merged["fee_due"] > 0).sum()

    return total_due, students_with_due


def get_fee_collection_summary(username, start_date=None, end_date=None):

    import pandas as pd
    from Due_Fee_Retreiver import month_end, months_between

    base = f"/var/Data/{username}"

    try:
        students = pd.read_csv(f"{base}/student_log.csv")
        ledger = pd.read_csv(f"{base}/fees_ledger.csv")
        fee_struct = pd.read_csv(f"{base}/fee_structure_static.csv")
    except:
        return 0, 0, 0, 0

    # ---------------------------
    # 🔥 DATE SAFETY
    # ---------------------------
    if start_date:
        start_date = pd.to_datetime(start_date)
    if end_date:
        end_date = pd.to_datetime(end_date)

    # ---------------------------
    # 🔥 CLEAN LEDGER
    # ---------------------------
    ledger = ledger.dropna(how="all")
    ledger = ledger[ledger["entry_id"].notna()]
    ledger = ledger[ledger["form_name"] == "FEES RECEIPT"]

    ledger["transaction_date"] = pd.to_datetime(
    ledger["transaction_date"], errors="coerce", format="mixed"
)
    ledger = ledger[ledger["transaction_date"].notna()]

    if start_date and end_date:
        ledger = ledger[
            (ledger["transaction_date"] >= start_date)
            & (ledger["transaction_date"] <= end_date)
        ]

    # ---------------------------
    # 🔥 SAFE admission_no extraction
    # ---------------------------
    ledger["admission_no"] = (
        ledger["account_name"]
        .astype(str)
        .str.extract(r"/(STU[_-]?\d+)", expand=False)
    )
    ledger = ledger[ledger["admission_no"].notna()]

    # ---------------------------
    # 🔥 SAFE AMOUNT CALCULATION
    # ---------------------------
    amount_cols = [
        "cash_amount",
        "bank1_amount","bank2_amount","bank3_amount","bank4_amount",
        "bank5_amount","bank6_amount","bank7_amount","bank8_amount",
        "bank9_amount","bank10_amount"
    ]

    for col in amount_cols:
        if col not in ledger.columns:
            ledger[col] = 0

    ledger[amount_cols] = ledger[amount_cols].apply(
        pd.to_numeric, errors="coerce"
    ).fillna(0)

    ledger["calculated_total"] = ledger[amount_cols].sum(axis=1)

    # ---------------------------
    # 🔥 PAID AMOUNT (PER STUDENT)
    # ---------------------------
    paid_df = (
        ledger.groupby("admission_no", as_index=False)
        .agg({"calculated_total": "sum"})
        .rename(columns={"calculated_total": "amount_paid"})
    )

    # ---------------------------
    # 🔥 CLEAN STUDENTS + FEE STRUCT
    # ---------------------------
    students["admission_no"] = students["admission_no"].astype(str)
    students["studying_class"] = students["studying_class"].astype(str)

    fee_struct["studying_class"] = fee_struct["studying_class"].astype(str)
    fee_struct["monthly_fee"] = pd.to_numeric(
        fee_struct["monthly_fee"], errors="coerce"
    ).fillna(0)

    # ---------------------------
    # 🔥 MERGE
    # ---------------------------
    merged = students.merge(fee_struct, on="studying_class", how="left").merge(
        paid_df, on="admission_no", how="left"
    )

    merged["amount_paid"] = merged["amount_paid"].fillna(0)

    # ---------------------------
    # 🔥 ACADEMIC YEAR FIX (IMPORTANT)
    # ---------------------------
    today = (
        pd.to_datetime(end_date).normalize()
        if end_date
        else pd.Timestamp.today().normalize()
    )

    merged["admission_date"] = pd.to_datetime(
        merged["admission_date"], errors="coerce", dayfirst=True
    )

    # FY START (APRIL)
    fy_start = pd.Timestamp(year=today.year, month=4, day=1)
    if today.month < 4:
        fy_start = pd.Timestamp(year=today.year - 1, month=4, day=1)

    # effective start = max(admission_date, fy_start)
    merged["effective_start"] = merged["admission_date"].apply(
        lambda d: max(d, fy_start) if pd.notna(d) else fy_start
    )

    merged["effective_start"] = merged["effective_start"].apply(month_end)

    # ---------------------------
    # 🔥 MONTH CALCULATION
    # ---------------------------
    merged["months_elapsed"] = merged["effective_start"].apply(
        lambda d: months_between(d, today)
    ).clip(lower=0)

    # ---------------------------
    # FEE CALCULATION (ALIGNED)
    # ---------------------------
    # Ensure concession column exists
    if "monthly_fee_concession" not in merged.columns:
        merged["monthly_fee_concession"] = 0
    
    merged["monthly_fee_concession"] = pd.to_numeric(
        merged["monthly_fee_concession"], errors="coerce"
    ).fillna(0)
    
    # Prevent concession > fee
    merged["monthly_fee_concession"] = merged[
        ["monthly_fee_concession", "monthly_fee"]
    ].min(axis=1)
    
    # Apply concession
    merged["effective_monthly_fee"] = (
        merged["monthly_fee"] - merged["monthly_fee_concession"]
    ).clip(lower=0)
    
    # Final expected fee
    merged["expected_fee"] = merged["months_elapsed"] * merged["effective_monthly_fee"]

    merged["fee_due"] = (
        merged["expected_fee"] - merged["amount_paid"]
    ).clip(lower=0)

    # ---------------------------
    # 🔥 FINAL OUTPUT
    # ---------------------------
    receivable = merged["expected_fee"].sum()
    collected = merged["amount_paid"].sum()
    due = merged["fee_due"].sum()

    ratio = 0
    if receivable > 0:
        ratio = round((collected / receivable) * 100, 2)

    return receivable, collected, due, ratio

# -----------------------------
# TOTAL FEES + SPARKLINE
# -----------------------------
def get_total_fees(username, start_date, end_date):
    import os
    import pandas as pd

    path = f"/var/Data/{username}/fees_ledger.csv"

    if not os.path.exists(path):
        return 0, []

    df = pd.read_csv(path)

    # Clean data
    df = df.dropna(how="all")
    df = df[df["entry_id"].notna()]

    # Only fee receipts
    df = df[df["form_name"] == "FEES RECEIPT"]

    # Remove duplicates
    df = df.drop_duplicates(subset=["entry_id"])

    # Convert date
    df["transaction_date"] = pd.to_datetime(
        df["transaction_date"],
        errors="coerce",
        dayfirst=True,
    )

    df = df[df["transaction_date"].notna()]

    # Date filter
    if start_date and end_date:
        df = df[
            (df["transaction_date"] >= start_date)
            & (df["transaction_date"] <= end_date)
        ]

    # Safe amount calculation (IMPORTANT FIX)
    amount_cols = [
        "cash_amount",
        "bank1_amount", "bank2_amount", "bank3_amount", "bank4_amount",
        "bank5_amount", "bank6_amount", "bank7_amount", "bank8_amount",
        "bank9_amount", "bank10_amount"
    ]

    df[amount_cols] = df[amount_cols].apply(
        pd.to_numeric, errors="coerce"
    ).fillna(0)

    df["calculated_total"] = df[amount_cols].sum(axis=1)

    # FINAL TOTAL
    total = df["calculated_total"].sum()

    # Monthly sparkline
    if not df.empty:
        monthly = (
            df.groupby(df["transaction_date"].dt.to_period("M"))["calculated_total"]
            .sum()
            .sort_index()
        )
        spark_data = monthly.tolist()
    else:
        spark_data = []

    return total, spark_data


def get_active_teachers(username, start_date=None, end_date=None):

    path = f"/var/Data/{username}/teacher_log.csv"

    if not os.path.exists(path):
        return 0

    df = pd.read_csv(path)

    if "created_at" in df.columns:
        df["created_at"] = pd.to_datetime(df["created_at"], errors="coerce")

        if start_date and end_date:
            df = df[(df["created_at"] >= start_date) & (df["created_at"] <= end_date)]

    return len(df)


def calculate_cash_closing_exact(username, start_date=None, end_date=None):

    ledger_path = f"/var/Data/{username}/master_ledger.csv"

    if not os.path.exists(ledger_path) or not start_date or not end_date:
        return 0

    df = pd.read_csv(ledger_path)

    # SAME DATE LOGIC
    df["transaction_date"] = df["transaction_date"].apply(normalize_txn_date)
    df = df[df["transaction_date"].notna()]
    df["transaction_date"] = df["transaction_date"].dt.normalize()

    df["cash_amount"] = pd.to_numeric(df["cash_amount"], errors="coerce").fillna(0)

    df = df[df["cash_amount"] != 0]

    start_date = pd.to_datetime(start_date).normalize()
    end_date = (
        pd.to_datetime(end_date).normalize()
        + pd.Timedelta(days=1)
        - pd.Timedelta(seconds=1)
    )

    # ---------------- OPENING ----------------
    prior_df = df[df["transaction_date"] < start_date]

    opening_balance = (
        prior_df[prior_df["form_name"].isin(["FEES RECEIPT", "OTHER RECEIPT"])][
            "cash_amount"
        ].sum()
        - prior_df[
            prior_df["form_name"].isin(["EXPENSES", "SALARY PAYMENT", "OTHER PAYMENT"])
        ]["cash_amount"].sum()
    )

    # ---------------- PERIOD ----------------
    period_df = df[
        (df["transaction_date"] >= start_date) & (df["transaction_date"] <= end_date)
    ]

    receipt_df = period_df[
        period_df["form_name"].isin(["FEES RECEIPT", "OTHER RECEIPT"])
    ]["cash_amount"]

    payment_df = period_df[
        period_df["form_name"].isin(["EXPENSES", "SALARY PAYMENT", "OTHER PAYMENT"])
    ]["cash_amount"]

    # 🔥 EXACT SAME NEGATIVE RULE
    neg_payment_sum = payment_df[payment_df < 0].abs().sum()

    total_receipts = receipt_df.sum() + neg_payment_sum
    total_payments = payment_df[payment_df > 0].sum()

    closing_balance = opening_balance + total_receipts - total_payments

    return closing_balance


def get_today_transaction(username, start_date=None, end_date=None):

    path = f"/var/Data/{username}/master_ledger.csv"

    if not os.path.exists(path):
        return 0, 0  # amount, count

    df = pd.read_csv(path)

    df["transaction_date"] = pd.to_datetime(
        df["transaction_date"], errors="coerce", dayfirst=True
    )

    df = df[df["transaction_date"].notna()].copy()

    today = pd.Timestamp(date.today()).normalize()

    # FY validation
    if start_date and end_date:
        if not (start_date <= today <= end_date):
            return 0, 0

    df_today = df[df["transaction_date"].dt.normalize() == today].copy()

    if df_today.empty:
        return 0, 0

    df_today["total_amount"] = pd.to_numeric(
        df_today["total_amount"], errors="coerce"
    ).fillna(0)

    total_amount = df_today["total_amount"].sum()
    total_count = len(df_today)

    return total_amount, total_count


# -----------------------------
# EVENT ALERT
# -----------------------------
def get_event_alert(username):

    path = f"/var/Data/{username}/events.csv"

    if not os.path.exists(path):
        return None

    try:

        df = pd.read_csv(path)

        if not {"event", "date"}.issubset(df.columns):
            return None

        df["date"] = pd.to_datetime(df["date"], errors="coerce")

        today = pd.Timestamp.today().normalize()

        df = df[df["date"] >= today]

        if df.empty:
            return None

        df = df.sort_values("date")

        next_event = df.iloc[0]

        days_left = (next_event["date"] - today).days

        if days_left <= 3:

            return dbc.Alert(
                f"📅 Upcoming Event: {next_event['event']} on {next_event['date'].strftime('%d %b')} ({days_left} days left)",
                color="warning",
                dismissable=True,
            )

        return None

    except:
        return None


# -----------------------------
# DASHBOARD LAYOUT
# -----------------------------
def get_layout(session_data=None, selected_fy=None):

    total_students = 0
    boys = 0
    girls = 0
    students_left = 0
    total_receipt_amount = 0
    total_receipt_count = 0
    
    spark_data = []
    default_closing = 0
    active_teachers = 0
    today_transaction_amount = 0
    today_transaction_count = 0
    months = []
    fees_data = []
    bank_options = []
    today_birthdays = []
    default_bank = None
    upcoming_events = []
    event_alert = None
    fees_receivable = 0
    fees_collected = 0
    total_fees = 0
    fees_due = 0
    collection_ratio = 0
    class_attendance = []
    teacher_attendance = []
    total_due = 0
    students_with_due = 0
    if session_data and "username" in session_data:

        username = session_data["username"]
        start_date, end_date = get_fy_date_range(selected_fy)
        bank_options = []
        default_bank = None

        bank_label_path = f"/var/Data/{username}/bank_name_static.csv"

        if os.path.exists(bank_label_path):
            bank_df = pd.read_csv(bank_label_path)

            bank_options = [
                {
                    "label": row["bank_label"],  # SBI, HDFC
                    "value": row["bank_code"].lower(),  # bank1, bank2
                }
                for _, row in bank_df.iterrows()
            ]

            if bank_options:
                default_bank = bank_options[0]["value"]

        try:
            total_students, boys, girls, students_left = get_student_overview(username)
            total_receipt_amount, total_receipt_count = get_total_receipts(
                username, start_date, end_date
            )
            fees_receivable, fees_collected, fees_due, collection_ratio = (
                get_fee_collection_summary(username, start_date, end_date)
            )
            total_fees = fees_collected
            total_due = fees_due 
            students_with_due =  get_total_fee_due(username, start_date, end_date)[1]
            
            
            class_attendance = get_class_attendance(username, start_date, end_date)
            teacher_attendance = get_teacher_attendance(username, start_date, end_date)
            today_birthdays = get_today_birthdays(username)
            active_teachers = get_active_teachers(username, start_date, end_date)
            today_transaction_amount, today_transaction_count = get_today_transaction(
                username, start_date, end_date
            )
            upcoming_events = get_upcoming_events(username)
            default_closing = calculate_cash_closing_exact(
                username, start_date, end_date
            )
            event_alert = get_event_alert(username)
            months, fees_data = get_monthly_fee_data(username, start_date, end_date)

        except Exception as e:
            print("Dashboard data load error:", e)

    return html.Div(
        [
            html.H3("Dashboard Overview", className="mb-4"),
            event_alert if event_alert else None,
            dbc.Row(
                [
                    dbc.Col(
                        universal_kpi_card(
                            title="Total Fees Collected",
                            value=f"₹ {total_fees:,.0f}",
                            trend="positive",
                            icon_class="bi bi-cash-coin",
                            icon_bg="#dcfce7",
                            icon_color="#16a34a",
                            extra_text="this financial year",
                            spark_data=spark_data,
                        ),
                        width=3,
                    ),
                    dbc.Col(
                        dcc.Link(
                            universal_kpi_card(
                                title="Total Fee Due",
                                value=f"₹ {total_due:,.0f}",
                                trend="negative",
                                icon_class="bi bi-exclamation-circle",
                                icon_bg="#fee2e2",
                                icon_color="#dc2626",
                                extra_text=f"{students_with_due} students pending",
                            ),
                            href="/datarep/fee-due",
                            style={"textDecoration": "none"},
                        ),
                        width=3,
                    ),
                    dbc.Col(
                        universal_kpi_card(
                            title="Total Receipts",
                            value=f"₹ {total_receipt_amount:,.0f}",
                            trend="positive",
                            icon_class="bi bi-receipt",
                            icon_bg="#dcfce7",
                            icon_color="#16a34a",
                            extra_text=f"{total_receipt_count} entries",
                        ),
                        width=3,
                    ),
                    dbc.Col(
                        student_overview_card(
                            total_students, boys, girls, students_left
                        ),
                        width=3,
                    ),
                    dbc.Row(
                        [
                            # 🔵 LEFT SIDE – Chart
                            dbc.Col(
                                monthly_fee_card(months, fees_data, chart_height=275),
                                md=6,
                            ),
                            # 🟢 RIGHT SIDE – Cards Section
                            dbc.Col(
                                [
                                    # Row 1 → Two cards
                                    dbc.Row(
                                        [
                                            dbc.Col(
                                                universal_kpi_card(
                                                    title="Active Teachers",
                                                    value=f"{active_teachers}",
                                                    trend="positive",
                                                    icon_class="bi bi-person-badge",
                                                    icon_bg="#fef3c7",
                                                    icon_color="#d97706",
                                                    extra_text="active faculty",
                                                ),
                                                md=6,
                                            ),
                                            dbc.Col(
                                                universal_kpi_card(
                                                    title="Today's Transaction",
                                                    value=f"₹ {today_transaction_amount:,.0f}",
                                                    trend="positive",
                                                    icon_class="bi bi-calendar-day",
                                                    icon_bg="#e0f2fe",
                                                    icon_color="#0284c7",
                                                    extra_text=f"{today_transaction_count} entries",
                                                ),
                                                md=6,
                                            ),
                                        ],
                                        className="g-3",
                                    ),
                                    # Row 2 → One full width card
                                    dbc.Row(
                                        [
                                            dbc.Col(
                                                bank_closing_dropdown_card(
                                                    bank_options=bank_options,
                                                    value="₹ 0",
                                                    trend=None,
                                                    selected_bank_label="Select Bank",
                                                    default_value=default_bank,  # 👈 ADD THIS
                                                ),
                                                md=6,
                                            ),
                                            dbc.Col(
                                                universal_kpi_card(
                                                    title="CLOSING BALANCE",
                                                    value=f"₹ {default_closing:,.0f}",  # 👈 YEH CHANGE
                                                    trend="positive",
                                                    icon_class="bi bi-bank",  # better icon
                                                    icon_bg="#e0f2fe",
                                                    icon_color="#0284c7",
                                                    extra_text=f"{selected_fy} closing",  # 👈 better text
                                                ),
                                                md=6,
                                            ),
                                        ],
                                        className="g-1 mt-1",
                                    ),
                                ],
                                md=6,
                            ),
                        ],
                        className="mb-4 g-2",
                    ),
                ],
                className="mb-2 g-2",
            ),
            dbc.Row(
                [
                    dbc.Col(birthday_card(today_birthdays), md=4),
                    dbc.Col(upcoming_events_card(upcoming_events), md=4),
                    dbc.Col(
                        fees_collection_card(
                            fees_receivable, fees_collected, fees_due, collection_ratio
                        ),
                        md=4,
                    ),
                ],
                className="mb-3 g-3",
            ),
            dbc.Row(
    [
        dbc.Col(
            html.Div(
                id="attendance-card-container",
                children=attendance_card(
                    [], 
                    [{"label": "All Classes", "value": "All"}], 
                    "All"
                )
            ),
            md=4
        ),

        dbc.Col(
            teacher_attendance_card(teacher_attendance),
            md=4
        )
    ],
    className="mb-3 g-3",
)
        ]
    )


@callback(
    Output("dashboard-bank-closing-value", "children"),
    Output("dashboard-selected-bank-name", "children"),
    Input("dashboard-bank-selector", "value"),
    Input("financial-year-dropdown", "value"),
    State("session", "data"),
)
def update_dashboard_bank(bank, selected_fy, session_data):

    if not session_data:
        return "₹ 0", "No Data"

    username = session_data["username"]
    start_date, end_date = get_fy_date_range(selected_fy)

    if not start_date or not end_date:
        return "₹ 0", "Invalid FY"

    # 🔥 IF BANK SELECTED → BANK LOGIC
    if bank:
        closing = get_single_bank_closing(username, bank, start_date, end_date)

        # Get Proper Bank Label
        bank_label_path = f"/var/Data/{username}/bank_name_static.csv"
        bank_label = bank.upper()

        if os.path.exists(bank_label_path):
            bank_df = pd.read_csv(bank_label_path)
            match = bank_df[bank_df["bank_code"].str.lower() == bank.lower()]
            if not match.empty:
                bank_label = match.iloc[0]["bank_label"]

        return f"₹ {closing:,.0f}", bank_label

    # 🔥 IF NO BANK → PURE CASH LOGIC
    closing = calculate_cash_closing_exact(username, start_date, end_date)

    return f"₹ {closing:,.0f}", "Cash Book"


@callback(
    Output("attendance-card-container", "children"),
    Input("attendance-class-dropdown", "value"),
    State("session", "data"),
    State("financial-year-dropdown", "value"),
)
def update_attendance_card(selected_class, session_data, selected_fy):

    if not session_data:
        return attendance_card([], [], "All")

    username = session_data["username"]

    start_date, end_date = get_fy_date_range(selected_fy)

    class_data = get_class_attendance(username, start_date, end_date)
    class_options = get_class_options(username)

    return attendance_card(class_data, class_options, selected_class)




@callback(
    Output("teacher-card-container", "children"),
    Input("teacher-dropdown", "value"),
    State("session", "data"),
    State("financial-year-dropdown", "value"),
)
def update_teacher_card(selected_teacher, session_data, selected_fy):

    if not session_data:
        return teacher_attendance_card([], "All")

    username = session_data["username"]
    start_date, end_date = get_fy_date_range(selected_fy)

    teacher_data = get_teacher_attendance(username, start_date, end_date)

    return teacher_attendance_card(teacher_data, selected_teacher)
