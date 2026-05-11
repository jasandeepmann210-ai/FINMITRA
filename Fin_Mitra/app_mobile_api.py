#!/usr/bin/env python3
"""
Mobile API Server - Serves CSV data for FinMitra mobile app
Deploy to Render without needing local machine
"""
from flask import Flask, jsonify, request
import csv
import json
import os
import time
import uuid
from pathlib import Path

app = Flask(__name__)

# Base directory for CSV data
# Try current directory first, then parent directory
DATA_DIR = Path(__file__).parent / "Data_Dummy"
if not DATA_DIR.exists():
    DATA_DIR = Path(__file__).parent.parent / "Data_Dummy"
if not DATA_DIR.exists():
    print(f"Warning: Data_Dummy not found at {DATA_DIR}")


def _enquiries_path() -> Path:
    return DATA_DIR / "parent_enquiries.json"


def _load_enquiries() -> list:
    p = _enquiries_path()
    if not p.exists():
        return []
    try:
        with open(p, "r", encoding="utf-8") as f:
            data = json.load(f)
        return data if isinstance(data, list) else []
    except Exception:
        return []


def _save_enquiries(items: list) -> None:
    p = _enquiries_path()
    p.parent.mkdir(parents=True, exist_ok=True)
    with open(p, "w", encoding="utf-8") as f:
        json.dump(items, f, indent=2, ensure_ascii=False)


def _teacher_key() -> str:
    return os.environ.get("TEACHER_API_KEY", "teacher-demo-key")


@app.route("/api/v1/read", methods=["GET"])
def read_file():
    """API endpoint that reads CSV files and returns as JSON"""
    path = request.args.get("path", "")
    
    if not path:
        return jsonify({"error": "path parameter required"}), 400
    
    # Security: prevent path traversal
    full_path = (DATA_DIR / path).resolve()
    if not str(full_path).startswith(str(DATA_DIR.resolve())):
        return jsonify({"error": "Invalid path"}), 403
    
    if not full_path.exists():
        return jsonify({"error": f"File not found: {path}"}), 404
    
    if full_path.is_dir():
        return jsonify({"error": "Path is a directory"}), 400
    
    if str(full_path).endswith(".csv"):
        rows = []
        try:
            with open(full_path, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    rows.append(dict(row))
            return jsonify({"path": path, "format": "csv", "data": rows})
        except Exception as e:
            return jsonify({"error": str(e)}), 500
    else:
        return jsonify({"error": "Only CSV files supported"}), 400

@app.route("/api/v1/enquiries", methods=["GET"])
def list_enquiries():
    """Parent: list enquiries for a mobile number."""
    mobile = (request.args.get("parent_mobile") or "").strip()
    if not mobile:
        return jsonify({"error": "parent_mobile required"}), 400
    items = _load_enquiries()
    mine = [e for e in items if str(e.get("parent_mobile", "")).strip() == mobile]
    mine.sort(key=lambda x: x.get("created_at", ""), reverse=True)
    return jsonify({"enquiries": mine})


@app.route("/api/v1/enquiries", methods=["POST"])
def create_enquiry():
    """Parent posts a new question."""
    body = request.get_json(silent=True) or {}
    parent_mobile = str(body.get("parent_mobile", "")).strip()
    student_name = str(body.get("student_name", "")).strip()
    admission_no = str(body.get("admission_no", "")).strip()
    message = str(body.get("message", "")).strip()
    if not parent_mobile or not message:
        return jsonify({"error": "parent_mobile and message required"}), 400
    items = _load_enquiries()
    entry = {
        "id": str(uuid.uuid4()),
        "parent_mobile": parent_mobile,
        "student_name": student_name,
        "admission_no": admission_no,
        "message": message,
        "reply": None,
        "created_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "replied_at": None,
    }
    items.append(entry)
    _save_enquiries(items)
    return jsonify({"enquiry": entry}), 201


@app.route("/api/v1/enquiries/<eid>/reply", methods=["POST"])
def reply_enquiry(eid):
    """Teacher replies (requires X-Teacher-Key header)."""
    key = request.headers.get("X-Teacher-Key", "")
    if key != _teacher_key():
        return jsonify({"error": "Unauthorized"}), 401
    body = request.get_json(silent=True) or {}
    reply = str(body.get("reply", "")).strip()
    if not reply:
        return jsonify({"error": "reply required"}), 400
    items = _load_enquiries()
    for e in items:
        if e.get("id") == eid:
            e["reply"] = reply
            e["replied_at"] = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
            _save_enquiries(items)
            return jsonify({"enquiry": e})
    return jsonify({"error": "Not found"}), 404


@app.route("/health", methods=["GET"])
def health():
    """Health check endpoint"""
    return jsonify({"status": "ok", "service": "FinMitra Mobile API"})

@app.route("/", methods=["GET"])
def home():
    """Home endpoint"""
    return jsonify({
        "message": "FinMitra Mobile API Server",
        "endpoints": {
            "/api/v1/read": "Read CSV file - ?path=file.csv (relative to Data_Dummy)",
            "/api/v1/enquiries": "GET ?parent_mobile=… | POST JSON enquiry",
            "/api/v1/enquiries/<id>/reply": "POST JSON {reply} + X-Teacher-Key",
            "/health": "Health check"
        }
    })

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False)
