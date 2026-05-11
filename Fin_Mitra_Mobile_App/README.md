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

Replies are stored in `Data_Dummy/parent_enquiries.json` on the server. Teachers (or admin scripts) can reply with:

- `POST /api/v1/enquiries/<id>/reply` with JSON `{ "reply": "…" }` and header `X-Teacher-Key` (default `teacher-demo-key`, override with env `TEACHER_API_KEY` on Render).

After changing `pubspec.yaml`, run `flutter pub get` locally.

## App icon & login screen art

Flutter bundles images from **`assets/branding/`** (not directly from `Data_Dummy/`).

1. Keep your masters in **`Data_Dummy/logo1.png`** and **`Data_Dummy/opening_screen.jpg`**.
2. Run **`scripts/sync_branding_from_data_dummy.ps1`** (from PowerShell) to copy them into `assets/branding/`.
3. Regenerate Android/iOS launcher icons from the logo:

```bash
dart run flutter_launcher_icons
```
