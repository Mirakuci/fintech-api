from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from datetime import date

app = FastAPI(
    title="fintech-api-demo",
    description="Kalkulačky a sazby – demo API",
    version="0.1.0",
)

# CORS – aby Vercel frontend mohl volat API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # později můžeš zúžit na https://tvuj-projekt.vercel.app
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def root():
    return {"ok": True, "service": "fintech-api-demo"}

@app.get("/api/hypo/monthly")
def hypo_monthly(principal: float, annual_rate: float, years: int):
    r = annual_rate / 100 / 12
    n = years * 12
    m = principal * (r * (1 + r) ** n) / (((1 + r) ** n) - 1)
    return {"principal": principal, "annual_rate": annual_rate, "years": years, "monthly": round(m, 2)}

RATES = {"bankA": 5.29, "bankB": 4.99, "bankC": 5.49}

@app.get("/api/rates")
def rates():
    return {"date": str(date.today()), "rates": RATES}