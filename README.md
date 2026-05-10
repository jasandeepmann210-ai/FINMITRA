# FinMitra

This repo contains:

- **`Fin_Mitra/`**: Python Dash web app + Flask blueprint APIs (Render web service)
- **`Fin_Mitra/app_mobile_api.py`**: lightweight Flask API used by the Flutter app (Render web service)
- **`Fin_Mitra_Mobile_App/`**: Flutter mobile app (parent portal)
- **`Data_Dummy/`**: demo CSV data used by the mobile API

## Mobile API (Render)

- **Health**: `GET /health`
- **Read CSV**: `GET /api/v1/read?path=student_log.csv`
  - Do **not** prefix `Data_Dummy/` in the query. The server already anchors inside that folder.
  - Subfolders work like: `GET /api/v1/read?path=marks/7.csv`

## Flutter mobile app

The canonical Flutter project is **`Fin_Mitra_Mobile_App/`**.

From `Fin_Mitra_Mobile_App/`:

```bash
flutter pub get
flutter run
```

Config:
- `Fin_Mitra_Mobile_App/lib/config.dart` contains `BASE_URL`.

## Repo hygiene

- A vendored Flutter SDK folder (`/flutter/`) was removed from git tracking (it’s huge and should not be committed).
- Usual build artifacts and secrets are ignored via `.gitignore`.

