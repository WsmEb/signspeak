# SignSpeak 🤟
> ترجمة لغة الإشارة بالذكاء الاصطناعي — في الوقت الفعلي

## Quick Start with Docker

```bash
# 1. Build and start both services
docker compose up --build

# 2. Open the app
#    Frontend  →  http://localhost:3000
#    API docs  →  http://localhost:8000/docs

# 3. Stop
docker compose down
```

## Run in background (detached)
```bash
docker compose up --build -d
docker compose logs -f          # follow logs
docker compose down             # stop
```

## Project structure
```
signspeak/
├── docker-compose.yml
├── backend/
│   ├── Dockerfile              ← python:3.11-alpine
│   ├── main.py                 ← FastAPI classifier
│   └── requirements.txt
└── frontend/
    ├── Dockerfile              ← nginx:1.27-alpine
    └── index.html              ← single-file app (HTML + JS)
```

## Images used
| Service  | Base image          | Approx size |
|----------|---------------------|-------------|
| backend  | python:3.11-alpine  | ~70 MB      |
| frontend | nginx:1.27-alpine   | ~10 MB      |

## Without Docker (manual)
```bash
# Backend
cd backend
pip install -r requirements.txt
uvicorn main:app --reload

# Frontend — just open in browser
open frontend/index.html
# or serve with Python
python3 -m http.server 3000 --directory frontend
```
