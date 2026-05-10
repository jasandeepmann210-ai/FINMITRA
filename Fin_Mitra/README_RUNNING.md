# How to Run the Application

## Problem: bcrypt Import Error

If you're seeing:
```
ERROR: bcrypt module is not installed!
```

This means the app is running with a Python interpreter that doesn't have bcrypt installed.

## Solution

### Option 1: Use the Batch Script (Windows - Easiest)
```bash
activate_and_run.bat
```
This script will:
- Automatically detect and activate your virtual environment
- Check if bcrypt is installed
- Install bcrypt if needed
- Run the application

### Option 2: Manual Activation (Recommended)

**Step 1: Activate Virtual Environment**

If you have a `.venv` in the project directory:
```bash
.venv\Scripts\activate
```

If you have a `.venv` in the parent directory (`C:\Users\virendra\Projects\agents\.venv`):
```bash
cd C:\Users\virendra\Projects\agents
.venv\Scripts\activate
cd School_Accounting\Sheep_FinMitra
```

**Step 2: Verify bcrypt is installed**
```bash
python -c "import bcrypt; print(bcrypt.__version__)"
```

**Step 3: Install bcrypt if needed**
```bash
pip install bcrypt
```

**Step 4: Run the app**
```bash
python app_fin_mitra.py
```

### Option 3: Use the Fix Script
```bash
python fix_bcrypt.py
```
This will detect your virtual environment and install bcrypt in the correct location.

### Option 4: Run Without Virtual Environment

If you want to use the system Python (where bcrypt is already installed):
```bash
C:\Users\virendra\AppData\Local\Programs\Python\Python311\python.exe app_fin_mitra.py
```

## IDE Configuration

If you're running from an IDE (VS Code, PyCharm, etc.):

1. **VS Code:**
   - Press `Ctrl+Shift+P`
   - Type "Python: Select Interpreter"
   - Choose the interpreter from your `.venv` folder
   - Or choose: `C:\Users\virendra\AppData\Local\Programs\Python\Python311\python.exe`

2. **PyCharm:**
   - File → Settings → Project → Python Interpreter
   - Select the interpreter from your `.venv` folder
   - Or add the system Python interpreter

## Verify Your Setup

Run this to check everything:
```bash
python diagnose_bcrypt.py
```

Or check manually:
```bash
python -c "import sys; print('Python:', sys.executable); import bcrypt; print('bcrypt:', bcrypt.__version__)"
```

## Found Virtual Environments

The fix script detected:
- `C:\Users\virendra\Projects\agents\.venv` - bcrypt is installed here ✓

Make sure your IDE or command line is using this Python interpreter!

