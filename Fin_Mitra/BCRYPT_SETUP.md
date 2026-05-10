# Bcrypt Installation Guide

## Problem
If you're seeing errors like:
```
Warning: Could not import auth_database: No module named 'bcrypt'
Error: auth_database not available, callbacks will not work
```

This means `bcrypt` is not installed in the Python environment where your app is running.

## Solution

### Option 1: Quick Install
```bash
pip install bcrypt
```

### Option 2: Use the Installation Script
```bash
python install_dependencies.py
```

### Option 3: Use the Check Script
```bash
python check_bcrypt.py
```
This will check if bcrypt is installed and offer to install it if missing.

## Verify Installation

Run this command to verify bcrypt is installed:
```bash
python -c "import bcrypt; print('bcrypt version:', bcrypt.__version__)"
```

## Important Notes

1. **Python Environment**: Make sure you're installing bcrypt in the same Python environment where your app runs.
   - If using a virtual environment, activate it first: `venv\Scripts\activate` (Windows) or `source venv/bin/activate` (Linux/Mac)
   - Check which Python you're using: `python --version` and `where python` (Windows) or `which python` (Linux/Mac)

2. **Multiple Python Installations**: If you have multiple Python installations, make sure you're using the correct one:
   ```bash
   python -m pip install bcrypt  # Uses the 'python' command
   python3 -m pip install bcrypt  # Uses the 'python3' command
   py -3.11 -m pip install bcrypt  # Uses specific Python version (Windows)
   ```

3. **Restart Required**: After installing bcrypt, restart your application.

## Troubleshooting

If bcrypt still doesn't work after installation:

1. Check which Python your app is using:
   - Look at the error message - it should show the Python path
   - Compare it with `python --version` output

2. Install bcrypt for that specific Python:
   ```bash
   # If your app uses a specific Python path, use it directly
   C:\Users\virendra\AppData\Local\Programs\Python\Python311\python.exe -m pip install bcrypt
   ```

3. Check if you're in a virtual environment:
   - Look for `venv`, `.venv`, or `env` folders
   - Activate the virtual environment before installing

4. Verify the installation:
   ```bash
   python check_bcrypt.py
   ```

## Current Status

To check if bcrypt is currently installed in your environment:
```bash
python check_bcrypt.py
```

