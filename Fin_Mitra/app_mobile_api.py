#!/usr/bin/env python3
"""
Mobile API Server - Serves CSV data for FinMitra mobile app
Deploy to Render without needing local machine
"""
from flask import Flask, jsonify, request
import csv
import os
from pathlib import Path

app = Flask(__name__)

# Base directory for CSV data
# Try current directory first, then parent directory
DATA_DIR = Path(__file__).parent / "Data_Dummy"
if not DATA_DIR.exists():
    DATA_DIR = Path(__file__).parent.parent / "Data_Dummy"
if not DATA_DIR.exists():
    print(f"Warning: Data_Dummy not found at {DATA_DIR}")

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
            "/api/v1/read": "Read CSV file - ?path=school/filename",
            "/health": "Health check"
        }
    })

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False)
