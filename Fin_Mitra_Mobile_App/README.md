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
