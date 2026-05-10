# Fin Mitra Mobile App - Parent Login Implementation Guide

## Changes Made

### 1. **Login Screen - Mobile Number Based**
- **File**: `lib/screens/login_screen.dart`
- Changed from student login (school + student name + admission number) to **parent login using mobile number**
- Parents now enter their mobile number to view their children's profiles
- Demo mobile number: `9844476654` (has multiple children in dummy data)

### 2. **Child Selection Screen - New Feature**
- **File**: `lib/screens/child_selection_screen.dart` (NEW)
- If a parent has multiple children linked to their mobile number, they see a selection screen
- Each child shows:
  - Student name with avatar
  - Current class
  - Admission number
- Tap a child to view their details

### 3. **API Configuration**
- **File**: `lib/config.dart`
- Changed `BASE_URL` from `https://sheep-finmitra.onrender.com` to `http://127.0.0.1:5000`
- Points to local mock API server for development/testing

### 4. **API Helper Updates**
- **File**: `lib/helpers/api_helper.dart`
- Added `filterByMobileNumber()` to filter students by parent's mobile
- Updated `filterFeeByMobileAndAdmNo()` to match mobile/admission format
- Retained marks filtering logic

### 5. **Dummy Data Setup**
- **Location**: `c:\Users\LENOVO\Desktop\FinMitra\Data_Dummy\`
- Organized files:
  - `student_log.csv` - student profiles (includes mobile field)
  - `fees_ledger.csv` - fee payment records (NEW - created)
  - `marks/` folder with class-wise marks:
    - `marks/0.csv`, `marks/7.csv`, `marks/10.csv`, `marks/11.csv`
  - `school_info.csv` - school metadata

### 6. **Mock API Server**
- **File**: `c:\Users\LENOVO\Desktop\FinMitra\mock_api_server.py` (NEW)
- Simple Flask server that serves CSV files as JSON
- Mimics the production `/api/v1/read` endpoint
- Runs on `http://127.0.0.1:5000`

---

## How to Build the APK

### Prerequisites
1. **Android SDK Setup** (Required)
   ```bash
   # Install Android Studio from: https://developer.android.com/studio
   # Or install Android SDK manually and set:
   flutter config --android-sdk "C:\path\to\android\sdk"
   ```

2. **Flutter SDK** (Already installed on this system: 3.41.9)

3. **Python** (For mock API server)
   ```bash
   pip install flask
   ```

### Build Steps

#### Step 1: Start Mock API Server
```bash
cd c:\Users\LENOVO\Desktop\FinMitra
python mock_api_server.py
```
Server will run on `http://127.0.0.1:5000`

#### Step 2: Build APK
```bash
cd c:\Users\LENOVO\Desktop\FinMitra\Fin_Mitra_Mobile_App

# Ensure dependencies are installed
flutter pub get

# Build release APK
flutter build apk --release
```

#### Step 3: APK Output
Built APK will be at:
```
c:\Users\LENOVO\Desktop\FinMitra\Fin_Mitra_Mobile_App\build\app\outputs\apk\release\app-release.apk
```

---

## Testing the App

### Test Scenario 1: Parent with Multiple Children
- **Mobile Number**: `9844476654`
- **Expected Behavior**:
  1. Login page shows mobile number input
  2. Enter `9844476654`
  3. App loads data for 5 children (STU_001, STU_007, STU_003, STU_004, STU_005, STU_006)
  4. Shows child selection screen
  5. Tap any child to view their profile, fees, and report card

### Test Scenario 2: Child Details
- **Available Tabs**:
  1. **Profile Tab**: Student details from `student_log.csv`
  2. **Fee Ledger Tab**: Payment records from `fees_ledger.csv`
  3. **Report Card Tab**: Marks from `marks/<class>.csv`

---

## Data Schema Reference

### student_log.csv
```
student_id, account_name, student_name, father_name, mother_name, 
dob, gender, mobile, studying_class, admission_no, email, ...
```

### fees_ledger.csv
```
student_id, account_name, transaction_date, form_name, 
total_amount, cash_amount, bank1_amount, details, breakup_cash, breakup_bank1
```

### marks/*.csv (e.g., marks/7.csv)
```
student_id, roll, student_name, section, total_marks, max_marks, percentage,
English_Final, English_Final_status, English_HY, English_HY_status, ...
```

### school_info.csv
```
school_name, address, ...
```

---

## File Structure After Setup

```
Data_Dummy/
├── student_log.csv          # Student profiles with mobile field
├── fees_ledger.csv          # Fee payment records
├── school_info.csv          # School metadata
├── marks/                   # Marks by class
│   ├── 0.csv
│   ├── 7.csv
│   ├── 10.csv
│   └── 11.csv
└── ... (other files)
```

---

## Key Features Implemented

✅ **Mobile Number Based Login**
- Parents login with their phone number instead of admission details

✅ **Multi-Child Support**
- If a parent has multiple children, app shows selection screen
- Each child's data is independently managed

✅ **Local Development**
- Mock API server for testing without internet
- Demo data structure matches production format

✅ **Three-Tab Dashboard**
- Profile Tab: Student information
- Fee Ledger Tab: Payment history
- Report Card Tab: Academic performance

---

## Next Steps for Further Changes

After building the APK, you can request:
1. UI/UX improvements (colors, layouts, fonts)
2. New features (attendance, communication, assignments)
3. Data export (PDF reports, email)
4. Parent notifications (fees due, grades)
5. Multi-language support

---

## Troubleshooting

### "No Android SDK found"
```bash
# Ensure Android Studio is installed or SDK path is set
flutter config --android-sdk "C:\Android\sdk"
```

### "Failed to load CSV"
- Ensure mock API server is running on `127.0.0.1:5000`
- Check Data_Dummy folder has the required CSV files

### "Child selection screen not showing"
- Verify `child_selection_screen.dart` exists in `lib/screens/`
- Check that dummy data has multiple students with same mobile number

---

**Build Date**: 10-May-2026
**App Version**: 1.1.0 (Parent Portal)
**Target Audience**: Parents/Guardians
