# api_routes.py
from flask import Blueprint, jsonify, request
import os, csv, json
from functools import wraps

api = Blueprint("api", __name__, url_prefix="/api/v1")

BASE_DIR = "/var/Data"

# --- Security: block path traversal attacks ---
def safe_path(relative_path):
    full_path = os.path.realpath(os.path.join(BASE_DIR, relative_path))
    if not full_path.startswith(os.path.realpath(BASE_DIR)):
        return None  # attempted escape
    return full_path

# --- API Key Auth ---
def require_api_key(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.headers.get("X-API-Key")
        if token != os.environ.get("API_SECRET_KEY"):
            return jsonify({"error": "Unauthorized"}), 401
        return f(*args, **kwargs)
    return decorated

# --- 1. List directory ---
@api.route("/files", methods=["GET"])
@require_api_key
def list_files():
    rel_path = request.args.get("path", "")
    full_path = safe_path(rel_path)

    if not full_path or not os.path.exists(full_path):
        return jsonify({"error": "Path not found"}), 404

    if os.path.isfile(full_path):
        return jsonify({"error": "Path is a file, not a directory"}), 400

    entries = []
    for name in os.listdir(full_path):
        entry_path = os.path.join(full_path, name)
        entries.append({
            "name": name,
            "type": "file" if os.path.isfile(entry_path) else "folder",
            "size": os.path.getsize(entry_path) if os.path.isfile(entry_path) else None
        })

    return jsonify({"path": rel_path, "entries": entries})

# --- 2. Read a file ---
@api.route("/read", methods=["GET"])
@require_api_key
def read_file():
    rel_path = request.args.get("path", "")
    full_path = safe_path(rel_path)

    if not full_path or not os.path.exists(full_path):
        return jsonify({"error": "File not found"}), 404

    if os.path.isdir(full_path):
        return jsonify({"error": "Path is a directory, use /files"}), 400

    ext = os.path.splitext(full_path)[1].lower()

    if ext == ".csv":
        rows = []
        with open(full_path, newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                rows.append(dict(row))
        return jsonify({"path": rel_path, "format": "csv", "data": rows})

    elif ext == ".json":
        with open(full_path, encoding="utf-8") as f:
            data = json.load(f)
        return jsonify({"path": rel_path, "format": "json", "data": data})

    else:  # plain text fallback
        with open(full_path, encoding="utf-8") as f:
            content = f.read()
        return jsonify({"path": rel_path, "format": "text", "data": content})

# --- 3. Check existence ---
@api.route("/exists", methods=["GET"])
@require_api_key
def check_exists():
    rel_path = request.args.get("path", "")
    full_path = safe_path(rel_path)
    exists = full_path is not None and os.path.exists(full_path)
    return jsonify({"path": rel_path, "exists": exists})