#!/usr/bin/env python3
"""
Mobile API Server - Serves CSV data for FinMitra mobile app
"""
from flask import Flask, jsonify, request
import csv
import json
import time
import uuid
from pathlib import Path

app = Flask(__name__)

DATA_DIR = Path(__file__).parent / "Data_Dummy"
if not DATA_DIR.exists():
    DATA_DIR = Path(__file__).parent.parent / "Data_Dummy"


def _enquiries_path() -> Path:
    return DATA_DIR / "parent_enquiries.json"


def _notifications_path() -> Path:
    return DATA_DIR / "parent_notifications.json"


def _load_json_list(path: Path) -> list:
    if not path.exists():
        return []
    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        return data if isinstance(data, list) else []
    except Exception:
        return []


def _save_json_list(path: Path, items: list) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(items, f, indent=2, ensure_ascii=False)


def _load_enquiries() -> list:
    return _load_json_list(_enquiries_path())


def _save_enquiries(items: list) -> None:
    _save_json_list(_enquiries_path(), items)


def _load_notifications() -> list:
    return _load_json_list(_notifications_path())


def _save_notifications(items: list) -> None:
    _save_json_list(_notifications_path(), items)


def _read_csv_rows(filename: str) -> list:
    path = DATA_DIR / filename
    if not path.exists():
        return []
    with open(path, "r", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def _normalize_class_code(code: str) -> str:
    return str(code or "").strip().upper().replace(" ", "")


def _student_log_files():
    """Prefer school_log.csv; fall back to student_log.csv."""
    if (DATA_DIR / "school_log.csv").exists():
        return ["school_log.csv", "student_log.csv"]
    return ["student_log.csv", "school_log.csv"]


def _class_code_for_student(student_id: str, admission_no: str) -> str:
    sid = str(student_id or "").strip()
    adm = str(admission_no or "").strip()
    for filename in _student_log_files():
        for row in _read_csv_rows(filename):
            row_sid = str(row.get("student_id", "")).strip()
            cc = str(row.get("class_code", "")).strip()
            if not cc:
                continue
            if sid and row_sid == sid:
                return _normalize_class_code(cc)
            if adm and (row_sid == adm or str(row.get("admission_no", "")).strip() == adm):
                return _normalize_class_code(cc)
    return ""


def _class_codes_for_parent_mobile(mobile: str) -> set:
    m = str(mobile or "").strip()
    codes = set()
    for filename in _student_log_files():
        for row in _read_csv_rows(filename):
            if str(row.get("mobile", "")).strip() != m:
                continue
            cc = str(row.get("class_code", "")).strip()
            if cc:
                codes.add(_normalize_class_code(cc))
    return codes


def _teacher_row_for(class_code: str, pin: str):
    cc = _normalize_class_code(class_code)
    p = str(pin or "").strip()
    if not p:
        return None
    for row in _read_csv_rows("class_teachers.csv"):
        row_pin = str(row.get("access_pin", "")).strip()
        if row_pin != p:
            continue
        role = str(row.get("role", "teacher")).strip().lower()
        row_cc = _normalize_class_code(row.get("class_code", ""))
        if role == "admin" and cc in ("ADMIN", "ALL", ""):
            return row
        if row_cc == cc:
            return row
    # Fallback admin if CSV locked / missing admin row
    if cc in ("ADMIN", "ALL", "") and p == "admin123":
        return {
            "class_code": "ADMIN",
            "teacher_name": "School Admin",
            "role": "admin",
        }
    return None


def _is_admin(teacher_row) -> bool:
    return str(teacher_row.get("role", "teacher")).strip().lower() == "admin"


def _auth_teacher(required_class_code: str = None):
    cc = _normalize_class_code(request.headers.get("X-Class-Code", ""))
    pin = str(request.headers.get("X-Teacher-Pin", "")).strip()
    teacher = _teacher_row_for(cc, pin)
    if not teacher:
        return None, (jsonify({"error": "Invalid class code or teacher PIN"}), 401)
    if _is_admin(teacher):
        return teacher, None
    if required_class_code:
        req = _normalize_class_code(required_class_code)
        tcc = _normalize_class_code(teacher.get("class_code", ""))
        if req and tcc != req:
            return None, (jsonify({"error": "Not authorized for this class"}), 403)
    return teacher, None


@app.route("/api/v1/read", methods=["GET"])
def read_file():
    path = request.args.get("path", "")
    if not path:
        return jsonify({"error": "path parameter required"}), 400
    full_path = (DATA_DIR / path).resolve()
    if not str(full_path).startswith(str(DATA_DIR.resolve())):
        return jsonify({"error": "Invalid path"}), 403
    if not full_path.exists():
        return jsonify({"error": f"File not found: {path}"}), 404
    if full_path.is_dir():
        return jsonify({"error": "Path is a directory"}), 400
    if str(full_path).endswith(".csv"):
        rows = []
        with open(full_path, "r", encoding="utf-8") as f:
            for row in csv.DictReader(f):
                rows.append(dict(row))
        return jsonify({"path": path, "format": "csv", "data": rows})
    return jsonify({"error": "Only CSV files supported"}), 400


# --- Enquiries ---

@app.route("/api/v1/enquiries", methods=["GET"])
def list_enquiries():
    mobile = (request.args.get("parent_mobile") or "").strip()
    student_id = (request.args.get("student_id") or "").strip()
    if not mobile:
        return jsonify({"error": "parent_mobile required"}), 400
    items = _load_enquiries()
    mine = [e for e in items if str(e.get("parent_mobile", "")).strip() == mobile]
    if student_id:
        mine = [
            e for e in mine
            if str(e.get("student_id", "")).strip() == student_id
            or str(e.get("admission_no", "")).strip() == student_id
        ]
    mine.sort(key=lambda x: x.get("created_at", ""), reverse=True)
    return jsonify({"enquiries": mine})


@app.route("/api/v1/enquiries", methods=["POST"])
def create_enquiry():
    body = request.get_json(silent=True) or {}
    parent_mobile = str(body.get("parent_mobile", "")).strip()
    student_name = str(body.get("student_name", "")).strip()
    student_id = str(body.get("student_id", "")).strip()
    admission_no = str(body.get("admission_no", "")).strip()
    message = str(body.get("message", "")).strip()
    class_code = _normalize_class_code(body.get("class_code", ""))

    if not parent_mobile or not message:
        return jsonify({"error": "parent_mobile and message required"}), 400

    if not class_code:
        class_code = _class_code_for_student(student_id, admission_no)
    if not class_code:
        return jsonify({
            "error": "class_code missing — set class_code on student in school_log.csv"
        }), 400

    teacher_row = None
    for row in _read_csv_rows("class_teachers.csv"):
        if _normalize_class_code(row.get("class_code", "")) == class_code:
            teacher_row = row
            break

    entry = {
        "id": str(uuid.uuid4()),
        "parent_mobile": parent_mobile,
        "student_id": student_id,
        "student_name": student_name,
        "admission_no": admission_no,
        "class_code": class_code,
        "assigned_teacher": teacher_row.get("teacher_name", "") if teacher_row else "",
        "message": message,
        "reply": None,
        "replied_by": None,
        "status": "open",
        "created_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "replied_at": None,
    }
    items = _load_enquiries()
    items.append(entry)
    _save_enquiries(items)
    return jsonify({"enquiry": entry}), 201


@app.route("/api/v1/teacher/login", methods=["POST"])
def teacher_login():
    body = request.get_json(silent=True) or {}
    class_code = _normalize_class_code(body.get("class_code", ""))
    pin = str(body.get("pin", "")).strip()
    teacher = _teacher_row_for(class_code, pin)
    if not teacher:
        return jsonify({"error": "Invalid class code or PIN"}), 401
    role = str(teacher.get("role", "teacher")).strip().lower()
    is_admin = role == "admin"
    return jsonify({
        "class_code": "ADMIN" if is_admin else _normalize_class_code(teacher.get("class_code", class_code)),
        "teacher_name": teacher.get("teacher_name", ""),
        "teacher_mobile": teacher.get("teacher_mobile", ""),
        "poc_email": teacher.get("poc_email", ""),
        "role": role,
        "is_admin": is_admin,
    })


@app.route("/api/v1/teacher/enquiries", methods=["GET"])
def teacher_list_enquiries():
    filter_class = _normalize_class_code(request.args.get("class_code", ""))
    teacher, err = _auth_teacher(None)
    if err:
        return err

    status_filter = (request.args.get("status") or "").strip().lower()
    items = _load_enquiries()
    if _is_admin(teacher):
        if filter_class:
            mine = [e for e in items if _normalize_class_code(e.get("class_code", "")) == filter_class]
        else:
            mine = items
    else:
        cc = _normalize_class_code(teacher.get("class_code", ""))
        mine = [e for e in items if _normalize_class_code(e.get("class_code", "")) == cc]

    if status_filter == "open":
        mine = [e for e in mine if not e.get("reply")]
    elif status_filter == "answered":
        mine = [e for e in mine if e.get("reply")]

    mine.sort(key=lambda x: x.get("created_at", ""), reverse=True)
    return jsonify({
        "class_code": filter_class or teacher.get("class_code", ""),
        "teacher_name": teacher.get("teacher_name", ""),
        "is_admin": _is_admin(teacher),
        "enquiries": mine,
        "open_count": sum(1 for e in mine if not e.get("reply")),
    })


@app.route("/api/v1/enquiries/<eid>/reply", methods=["POST"])
def reply_enquiry(eid):
    body = request.get_json(silent=True) or {}
    reply = str(body.get("reply", "")).strip()
    if not reply:
        return jsonify({"error": "reply required"}), 400

    items = _load_enquiries()
    target = next((e for e in items if e.get("id") == eid), None)
    if not target:
        return jsonify({"error": "Not found"}), 404

    enquiry_class = _normalize_class_code(target.get("class_code", ""))
    teacher, err = _auth_teacher(enquiry_class)
    if err:
        return err

    for e in items:
        if e.get("id") == eid:
            e["reply"] = reply
            e["replied_by"] = teacher.get("teacher_name", "")
            e["status"] = "answered"
            e["replied_at"] = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
            _save_enquiries(items)
            return jsonify({"enquiry": e})
    return jsonify({"error": "Not found"}), 404


# --- Notifications ---

@app.route("/api/v1/notifications", methods=["GET"])
def list_notifications():
    """Parents: school-wide + class-specific for their children."""
    mobile = (request.args.get("parent_mobile") or "").strip()
    class_code = _normalize_class_code(request.args.get("class_code", ""))
    if not mobile and not class_code:
        return jsonify({"error": "parent_mobile or class_code required"}), 400

    parent_classes = _class_codes_for_parent_mobile(mobile) if mobile else set()
    if class_code:
        parent_classes.add(class_code)

    items = _load_notifications()
    visible = []
    for n in items:
        scope = str(n.get("scope", "")).strip().lower()
        if scope == "all":
            visible.append(n)
            continue
        ncc = _normalize_class_code(n.get("class_code", ""))
        if ncc and ncc in parent_classes:
            visible.append(n)

    visible.sort(key=lambda x: x.get("created_at", ""), reverse=True)
    return jsonify({"notifications": visible})


@app.route("/api/v1/notifications", methods=["POST"])
def create_notification():
    """Teacher: class only. Admin: all parents."""
    body = request.get_json(silent=True) or {}
    title = str(body.get("title", "")).strip()
    message = str(body.get("message", "")).strip()
    scope = str(body.get("scope", "class")).strip().lower()
    class_code = _normalize_class_code(body.get("class_code", ""))

    if not title or not message:
        return jsonify({"error": "title and message required"}), 400

    header_cc = _normalize_class_code(request.headers.get("X-Class-Code", ""))
    pin = str(request.headers.get("X-Teacher-Pin", "")).strip()
    teacher = _teacher_row_for(header_cc, pin)
    if not teacher:
        return jsonify({"error": "Unauthorized"}), 401

    is_admin = _is_admin(teacher)

    if scope == "all":
        if not is_admin:
            return jsonify({"error": "Only admin can post school-wide announcements"}), 403
        class_code = ""
    else:
        scope = "class"
        if is_admin:
            if not class_code:
                return jsonify({"error": "class_code required for class announcement"}), 400
        else:
            class_code = _normalize_class_code(teacher.get("class_code", ""))
            if not class_code:
                return jsonify({"error": "Teacher class not configured"}), 400

    entry = {
        "id": str(uuid.uuid4()),
        "scope": scope,
        "class_code": class_code,
        "title": title,
        "message": message,
        "posted_by": teacher.get("teacher_name", ""),
        "posted_by_role": "admin" if is_admin else "teacher",
        "created_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
    }
    items = _load_notifications()
    items.append(entry)
    _save_notifications(items)
    return jsonify({"notification": entry}), 201


@app.route("/api/v1/teacher/notifications", methods=["GET"])
def teacher_list_notifications():
    """Teacher/admin view posted announcements."""
    header_cc = _normalize_class_code(request.headers.get("X-Class-Code", ""))
    pin = str(request.headers.get("X-Teacher-Pin", "")).strip()
    teacher = _teacher_row_for(header_cc, pin)
    if not teacher:
        return jsonify({"error": "Unauthorized"}), 401

    items = _load_notifications()
    if _is_admin(teacher):
        visible = items
    else:
        cc = _normalize_class_code(teacher.get("class_code", ""))
        visible = [
            n for n in items
            if str(n.get("scope", "")).lower() == "all"
            or _normalize_class_code(n.get("class_code", "")) == cc
        ]
    visible.sort(key=lambda x: x.get("created_at", ""), reverse=True)
    return jsonify({"notifications": visible})


@app.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "ok", "service": "FinMitra Mobile API"})


@app.route("/", methods=["GET"])
def home():
    return jsonify({
        "message": "FinMitra Mobile API Server",
        "endpoints": {
            "/api/v1/read": "CSV read",
            "/api/v1/enquiries": "Parent enquiries",
            "/api/v1/notifications": "Announcements GET/POST",
            "/api/v1/teacher/login": "Teacher or admin login",
        }
    })


if __name__ == "__main__":
    import os
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False)
