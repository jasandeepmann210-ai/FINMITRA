@echo off
REM Quick Start Script for Fin Mitra Parent Portal APK Build

echo.
echo ========================================
echo Fin Mitra Mobile App - Build Script
echo Parent Portal Version (Mobile Number Login)
echo ========================================
echo.

REM Check if Flutter is installed
flutter --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Flutter not found. Please install Flutter SDK.
    pause
    exit /b 1
)

echo [✓] Flutter SDK detected
echo.

REM Navigate to app directory
cd /d "C:\Users\LENOVO\Desktop\FinMitra\Fin_Mitra_Mobile_App"

echo [STEP 1] Fetching dependencies...
call flutter pub get
if errorlevel 1 (
    echo ERROR: Failed to fetch dependencies
    pause
    exit /b 1
)
echo [✓] Dependencies fetched
echo.

echo [STEP 2] Checking Android SDK...
set ANDROID_SDK=C:\Android\sdk
if not exist "%ANDROID_SDK%" (
    echo.
    echo WARNING: Android SDK not found at default location
    echo Please ensure Android SDK is installed at: %ANDROID_SDK%
    echo Or set it manually using: flutter config --android-sdk "C:\path\to\sdk"
    echo.
    pause
)

echo.
echo [STEP 3] Building APK...
echo This may take 5-10 minutes on first build...
echo.
call flutter build apk --release

if errorlevel 1 (
    echo.
    echo ERROR: APK build failed
    echo Ensure Android SDK is properly installed and configured
    pause
    exit /b 1
)

echo.
echo ========================================
echo [✓] APK Build Successful!
echo ========================================
echo.
echo Output APK:
echo %CD%\build\app\outputs\apk\release\app-release.apk
echo.
echo [NEXT STEPS]
echo 1. Transfer APK to Android device
echo 2. Install APK (enable "Unknown sources" if needed)
echo 3. Run mock API server: python mock_api_server.py
echo 4. Launch app and login with mobile: 9844476654
echo.
pause
