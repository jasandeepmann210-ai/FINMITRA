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


def _bus_locations_path() -> Path:
    return DATA_DIR / "bus_locations.json"


def _bus_events_path() -> Path:
    return DATA_DIR / "bus_events.json"


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


def _student_ids_for_parent_mobile(mobile: str) -> set:
    m = str(mobile or "").strip()
    ids = set()
    for filename in _student_log_files():
        for row in _read_csv_rows(filename):
            if str(row.get("mobile", "")).strip() != m:
                continue
            sid = str(row.get("student_id", "")).strip()
            if sid:
                ids.add(sid)
    return ids


def _bus_assignment(student_id: str):
    sid = str(student_id or "").strip()
    if not sid:
        return None
    for row in _read_csv_rows("student_bus.csv"):
        if str(row.get("student_id", "")).strip() == sid:
            bus_id = str(row.get("bus_id", "")).strip()
            bus_row = None
            for b in _read_csv_rows("buses.csv"):
                if str(b.get("bus_id", "")).strip() == bus_id:
                    bus_row = b
                    break
            return {
                "student_id": sid,
                "bus_id": bus_id,
                "pickup_stop": row.get("pickup_stop", ""),
                "drop_stop": row.get("drop_stop", ""),
                "route_name": bus_row.get("route_name", "") if bus_row else "",
                "vehicle_no": bus_row.get("vehicle_no", "") if bus_row else "",
                "driver_name": bus_row.get("driver_name", "") if bus_row else "",
                "driver_mobile": bus_row.get("driver_mobile", "") if bus_row else "",
            }
    return None


def _load_bus_locations() -> dict:
    path = _bus_locations_path()
    if not path.exists():
        return {}
    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        return data if isinstance(data, dict) else {}
    except Exception:
        return {}


def _save_bus_locations(locations: dict) -> None:
    path = _bus_locations_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(locations, f, indent=2, ensure_ascii=False)


def _load_bus_events() -> list:
    return _load_json_list(_bus_events_path())


def _save_bus_events(items: list) -> None:
    _save_json_list(_bus_events_path(), items)


def _bus_row_for(bus_id: str, pin: str):
    bid = str(bus_id or "").strip().upper()
    p = str(pin or "").strip()
    if not bid or not p:
        return None
    for row in _read_csv_rows("buses.csv"):
        if str(row.get("bus_id", "")).strip().upper() != bid:
            continue
        if str(row.get("access_pin", "")).strip() != p:
            continue
        return row
    return None


def _auth_driver():
    bus_id = str(request.headers.get("X-Bus-Id", "")).strip().upper()
    pin = str(request.headers.get("X-Driver-Pin", "")).strip()
    row = _bus_row_for(bus_id, pin)
    if not row:
        return None, (jsonify({"error": "Invalid bus ID or driver PIN"}), 401)
    return row, None


def _bus_state(bus_id: str) -> dict:
    locations = _load_bus_locations()
    state = locations.get(bus_id, {})
    if not isinstance(state, dict):
        state = {}
    return state


def _set_bus_state(bus_id: str, state: dict) -> None:
    locations = _load_bus_locations()
    locations[bus_id] = state
    _save_bus_locations(locations)


def _student_name(student_id: str) -> str:
    sid = str(student_id or "").strip()
    for filename in _student_log_files():
        for row in _read_csv_rows(filename):
            if str(row.get("student_id", "")).strip() == sid:
                return str(row.get("student_name", "")).strip()
    return ""


def _roster_for_bus(bus_id: str, trip_id: str = "") -> list:
    bid = str(bus_id or "").strip().upper()
    state = _bus_state(bid)
    alighted = set(state.get("alighted_student_ids") or [])
    roster = []
    for row in _read_csv_rows("student_bus.csv"):
        if str(row.get("bus_id", "")).strip().upper() != bid:
            continue
        sid = str(row.get("student_id", "")).strip()
        roster.append({
            "student_id": sid,
            "student_name": _student_name(sid) or sid,
            "pickup_stop": row.get("pickup_stop", ""),
            "drop_stop": row.get("drop_stop", ""),
            "alighted": sid in alighted,
        })
    roster.sort(key=lambda x: x.get("student_name", ""))
    return roster


def _notify_parent_bus_event(student_id: str, title: str, message: str) -> None:
    items = _load_notifications()
    items.append({
        "id": str(uuid.uuid4()),
        "scope": "bus",
        "student_id": student_id,
        "class_code": "",
        "title": title,
        "message": message,
        "posted_by": "Bus tracking",
        "posted_by_role": "system",
        "created_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
    })
    _save_notifications(items)


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
    parent_students = _student_ids_for_parent_mobile(mobile) if mobile else set()
    if class_code:
        parent_classes.add(class_code)

    items = _load_notifications()
    visible = []
    for n in items:
        scope = str(n.get("scope", "")).strip().lower()
        if scope == "all":
            visible.append(n)
            continue
        if scope == "bus":
            sid = str(n.get("student_id", "")).strip()
            if sid and sid in parent_students:
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


# --- School bus tracking (driver phone GPS + alight marks) ---

@app.route("/api/v1/driver/login", methods=["POST"])
def driver_login():
    body = request.get_json(silent=True) or {}
    bus_id = str(body.get("bus_id", "")).strip().upper()
    pin = str(body.get("pin", "")).strip()
    row = _bus_row_for(bus_id, pin)
    if not row:
        return jsonify({"error": "Invalid bus ID or PIN"}), 401
    state = _bus_state(bus_id)
    return jsonify({
        "bus_id": bus_id,
        "route_name": row.get("route_name", ""),
        "vehicle_no": row.get("vehicle_no", ""),
        "driver_name": row.get("driver_name", ""),
        "trip_active": bool(state.get("trip_active")),
        "trip_id": state.get("trip_id", ""),
    })


@app.route("/api/v1/driver/trip", methods=["GET"])
def driver_trip_status():
    """Driver: current trip + roster."""
    row, err = _auth_driver()
    if err:
        return err
    bus_id = str(row.get("bus_id", "")).strip().upper()
    state = _bus_state(bus_id)
    trip_id = str(state.get("trip_id", ""))
    return jsonify({
        "bus_id": bus_id,
        "route_name": row.get("route_name", ""),
        "trip_active": bool(state.get("trip_active")),
        "trip_id": trip_id,
        "trip_started_at": state.get("trip_started_at", ""),
        "location": {
            "lat": state.get("lat"),
            "lng": state.get("lng"),
            "updated_at": state.get("updated_at", ""),
        },
        "roster": _roster_for_bus(bus_id, trip_id),
    })


@app.route("/api/v1/driver/trip/start", methods=["POST"])
def driver_trip_start():
    """Driver starts route — parents can track phone GPS."""
    row, err = _auth_driver()
    if err:
        return err
    bus_id = str(row.get("bus_id", "")).strip().upper()
    state = _bus_state(bus_id)
    if state.get("trip_active"):
        return jsonify({"error": "Route already active. End it first or continue."}), 400
    trip_id = str(uuid.uuid4())
    now = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    state = {
        "trip_active": True,
        "trip_id": trip_id,
        "trip_started_at": now,
        "alighted_student_ids": [],
        "lat": None,
        "lng": None,
        "updated_at": None,
    }
    _set_bus_state(bus_id, state)
    return jsonify({"bus_id": bus_id, "trip_id": trip_id, "trip_active": True})


@app.route("/api/v1/driver/trip/end", methods=["POST"])
def driver_trip_end():
    row, err = _auth_driver()
    if err:
        return err
    bus_id = str(row.get("bus_id", "")).strip().upper()
    state = _bus_state(bus_id)
    state["trip_active"] = False
    state["trip_ended_at"] = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    _set_bus_state(bus_id, state)
    return jsonify({"bus_id": bus_id, "trip_active": False})


@app.route("/api/v1/driver/location", methods=["POST"])
def driver_post_location():
    """Driver phone GPS while route is active."""
    row, err = _auth_driver()
    if err:
        return err
    body = request.get_json(silent=True) or {}
    try:
        lat = float(body.get("lat"))
        lng = float(body.get("lng"))
    except (TypeError, ValueError):
        return jsonify({"error": "lat and lng required"}), 400

    bus_id = str(row.get("bus_id", "")).strip().upper()
    state = _bus_state(bus_id)
    if not state.get("trip_active"):
        return jsonify({"error": "Start the route before sharing location"}), 400

    state["lat"] = lat
    state["lng"] = lng
    state["updated_at"] = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    _set_bus_state(bus_id, state)
    return jsonify({
        "bus_id": bus_id,
        "lat": lat,
        "lng": lng,
        "updated_at": state["updated_at"],
    })


@app.route("/api/v1/driver/alight", methods=["POST"])
def driver_mark_alight():
    """Driver marks a child got off the bus — notifies parent."""
    row, err = _auth_driver()
    if err:
        return err
    body = request.get_json(silent=True) or {}
    student_id = str(body.get("student_id", "")).strip()
    stop_name = str(body.get("stop_name", "")).strip()

    if not student_id:
        return jsonify({"error": "student_id required"}), 400

    assignment = _bus_assignment(student_id)
    if not assignment:
        return jsonify({"error": "Student not on a bus"}), 404

    bus_id = str(row.get("bus_id", "")).strip().upper()
    if str(assignment.get("bus_id", "")).strip().upper() != bus_id:
        return jsonify({"error": "Student is not on your bus"}), 403

    state = _bus_state(bus_id)
    if not state.get("trip_active"):
        return jsonify({"error": "Start the route before marking students"}), 400

    alighted = list(state.get("alighted_student_ids") or [])
    if student_id in alighted:
        return jsonify({"error": "Already marked off the bus"}), 400

    if not stop_name:
        stop_name = assignment.get("drop_stop", "") or assignment.get("pickup_stop", "")

    student_name = _student_name(student_id)
    trip_id = str(state.get("trip_id", ""))
    now = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())

    entry = {
        "id": str(uuid.uuid4()),
        "student_id": student_id,
        "student_name": student_name,
        "bus_id": bus_id,
        "trip_id": trip_id,
        "event_type": "alight",
        "stop_name": stop_name,
        "at": now,
    }
    events = _load_bus_events()
    events.append(entry)
    _save_bus_events(events)

    alighted.append(student_id)
    state["alighted_student_ids"] = alighted
    _set_bus_state(bus_id, state)

    label = student_name or "Your child"
    _notify_parent_bus_event(
        student_id,
        f"{label} got off the bus",
        f"{label} got off at {stop_name}.",
    )
    return jsonify({"event": entry, "roster": _roster_for_bus(bus_id, trip_id)}), 201


@app.route("/api/v1/bus/status", methods=["GET"])
def bus_status():
    """Parent: driver's live phone location + alight history for one child."""
    student_id = str(request.args.get("student_id", "")).strip()
    if not student_id:
        return jsonify({"error": "student_id required"}), 400

    assignment = _bus_assignment(student_id)
    if not assignment:
        return jsonify({
            "assigned": False,
            "student_id": student_id,
            "message": "No school bus assigned for this student.",
        })

    bus_id = str(assignment["bus_id"]).strip().upper()
    state = _bus_state(bus_id)
    trip_active = bool(state.get("trip_active"))
    lat = state.get("lat")
    lng = state.get("lng")
    has_location = lat is not None and lng is not None

    if not trip_active:
        status_label = "Route not started"
    elif not has_location:
        status_label = "Waiting for driver location"
    else:
        status_label = "On route"

    location = {}
    if trip_active and has_location:
        location = {
            "lat": lat,
            "lng": lng,
            "updated_at": state.get("updated_at", ""),
        }

    events = _load_bus_events()
    student_events = [
        e for e in events
        if str(e.get("student_id", "")).strip() == student_id
        and str(e.get("event_type", "")).lower() == "alight"
    ]
    student_events.sort(key=lambda x: x.get("at", ""), reverse=True)
    recent = student_events[:10]

    return jsonify({
        "assigned": True,
        "assignment": assignment,
        "trip_active": trip_active,
        "location": location,
        "status_label": status_label,
        "recent_events": recent,
        "last_event": recent[0] if recent else None,
    })


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
            "/api/v1/bus/status": "Parent bus tracking GET",
            "/api/v1/driver/login": "Bus driver login",
            "/api/v1/driver/trip": "Driver trip + roster GET",
            "/api/v1/driver/trip/start": "Start route POST",
            "/api/v1/driver/trip/end": "End route POST",
            "/api/v1/driver/location": "Driver phone GPS POST",
            "/api/v1/driver/alight": "Mark child off bus POST",
            "/api/v1/teacher/login": "Teacher or admin login",
        }
    })


if __name__ == "__main__":
    import os
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False)
