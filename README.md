# Machine Sentinel

A final-year engineering portfolio project for predictive maintenance and fault detection.

## What this repository contains

1. `docs/01_PRD.md`
2. `docs/02_ARCHITECTURE.md`
3. `docs/03_DATABASE_API_SPEC.md`
4. `docs/04_IMPLEMENTATION_PLAN.md`
5. working MVP code

Also see `PROJECT_IDEAS.md` for three project options.

---

## Tech Stack

- Python
- FastAPI
- SQLAlchemy
- SQLite locally / PostgreSQL-ready
- Streamlit
- Pytest

---

## Run Locally

### 1. Create environment

```bash
python -m venv .venv
source .venv/bin/activate
```

Windows PowerShell:

```powershell
.venv\Scripts\Activate.ps1
```

### 2. Install

```bash
pip install -r requirements.txt
```

### 3. Seed database

```bash
python -m backend.seed
```

### 4. Start API

```bash
uvicorn backend.main:app --reload
```

Open:

- Swagger API docs: `http://localhost:8000/docs`
- API health: `http://localhost:8000/health`

### 5. Start dashboard

In another terminal:

```bash
streamlit run frontend/app.py
```

Open `http://localhost:8501`.

---

## Try an API Reading

```bash
curl -X POST "http://localhost:8000/readings" \
  -H "Content-Type: application/json" \
  -d '{
    "machine_id": 1,
    "temperature": 78,
    "vibration": 7.2,
    "current": 12,
    "rpm": 3000,
    "pressure": 8.1
  }'
```

Then submit a critical example:

```bash
curl -X POST "http://localhost:8000/readings" \
  -H "Content-Type: application/json" \
  -d '{
    "machine_id": 1,
    "temperature": 94,
    "vibration": 11,
    "current": 21,
    "rpm": 3700,
    "pressure": 13
  }'
```

---

## Run Tests

```bash
pytest -q
```

---

## Best Portfolio Upgrade

After the MVP works, add an ML comparison:
- baseline threshold engine
- Isolation Forest
- autoencoder

Then evaluate false alarms, recall and detection lead time. That gives you a strong technical story for interviews and your final-year report.
