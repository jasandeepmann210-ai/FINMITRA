# FinMitra Mobile App (Flutter)

This is the **canonical** Flutter app in the repo.

## Run

From this folder:

```bash
flutter pub get
flutter run
```

## Config

- `lib/config.dart`:
  - `BASE_URL`: should point to your Render mobile API service (example: `https://finmitra-msay.onrender.com`)

## API expectations

The mobile API endpoint is:

- `GET /api/v1/read?path=<relative-path-inside-Data_Dummy>`

Examples:
- `student_log.csv`
- `marks/7.csv`
- `classroom_streams.csv`
- `student_attendance.csv`
- `events.csv`

## Parent ↔ school enquiries (API)

The app posts and lists enquiries via:

- `GET /api/v1/enquiries?parent_mobile=…`
- `POST /api/v1/enquiries` with JSON: `parent_mobile`, `student_name`, `admission_no`, `message`

Enquiries and notices use **class code** from `Data_Dummy/school_log.csv` (`class_code` column on each student row).

- `Data_Dummy/class_teachers.csv` — class POC + `access_pin`; add `role` column (`teacher` or `admin`)
- Admin row example: `ADMIN,School Admin,…,admin123,…,admin`
- Replies stored in `Data_Dummy/parent_enquiries.json`

**Parent app:** Enquiry tab → message goes to that class’s teacher.

**Teacher app:** On login screen tap **Class teacher login** → enter class + PIN (demo: `10A` / `class10a`) → reply to pending enquiries.

API:

- `POST /api/v1/teacher/login` — `{ "class_code", "pin" }`
- `GET /api/v1/teacher/enquiries?class_code=10A` — headers `X-Class-Code`, `X-Teacher-Pin`
- `POST /api/v1/enquiries/<id>/reply` — same headers + `{ "reply" }`

After changing `pubspec.yaml`, run `flutter pub get` locally.

## App icon & login screen art

Flutter bundles images from **`assets/branding/`** (not directly from `Data_Dummy/`).

1. Keep your masters in **`Data_Dummy/logo1.png`** and **`Data_Dummy/opening_screen.jpg`**.
2. Run **`scripts/sync_branding_from_data_dummy.ps1`** (from PowerShell) to copy them into `assets/branding/`.
3. Regenerate Android/iOS launcher icons from the logo:

```bash
dart run flutter_launcher_icons
```
