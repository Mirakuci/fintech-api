# Fintech API (FastAPI)

Spuštění:
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install fastapi "uvicorn[standard]"
uvicorn app.main:app --reload --port 8400
```

Dokumentace: http://localhost:8400/docs

Příklady:
- `/api/hypo/monthly?principal=3000000&annual_rate=5.2&years=30`
- `/api/rates`
