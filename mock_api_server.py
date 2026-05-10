#!/usr/bin/env python3
"""
Mock API server for serving dummy CSV data locally
Serves Data_Dummy folder similar to the real /api/v1/read endpoint
"""
from flask import Flask, jsonify, request
import csv
import os
import json
from pathlib import Path

app = Flask(__name__)

# Base directory for dummy data
DATA_DIR = Path(__file__).parent / "Data_Dummy"

@app.route("/api/v1/read", methods=["GET"])
def read_file():
    """Mock API endpoint that reads CSV files and returns as JSON"""
    path = request.args.get("path", "")
    
    if not path:
        return jsonify({"error": "path parameter required"}), 400
    
    # Security: prevent path traversal
    full_path = (DATA_DIR / path).resolve()
    if not str(full_path).startswith(str(DATA_DIR.resolve())):
        return jsonify({"error": "Invalid path"}), 403
    
    if not full_path.exists():
        return jsonify({"error": "File not found"}), 404
    
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
    return jsonify({"status": "ok"}), 200

if __name__ == "__main__":
    print(f"Starting mock API server...")
    print(f"Data directory: {DATA_DIR}")
    print(f"Serving on http://127.0.0.1:5000")
    print(f"Example: http://127.0.0.1:5000/api/v1/read?path=student_log.csv")
    app.run(debug=True, host="127.0.0.1", port=5000, use_reloader=False)
