from datetime import date
from fastapi import FastAPI, Query
from fastapi.responses import JSONResponse

app = FastAPI(
    title="fintech-api-demo",
    description="Kalkulačky a sazby – demo API",
    version="0.3.0"
)


def vypocet_mesicni_splatky(principal: float, annual_rate: float, years: int) -> float:
    r = annual_rate / 100 / 12
    n = years * 12

    if r == 0:
        return round(principal / n, 2)

    m = principal * (r * (1 + r) ** n) / (((1 + r) ** n) - 1)
    return round(m, 2)


def vytvor_splatkovy_kalendar(principal: float, annual_rate: float, years: int):
    r = annual_rate / 100 / 12
    n = years * 12
    mesicni_splatka = vypocet_mesicni_splatky(principal, annual_rate, years)

    zustatek = principal
    kalendar = []

    for mesic in range(1, n + 1):
        if r == 0:
            urok = 0
            umor = mesicni_splatka
        else:
            urok = round(zustatek * r, 2)
            umor = round(mesicni_splatka - urok, 2)

        if umor > zustatek:
            umor = round(zustatek, 2)

        novy_zustatek = round(zustatek - umor, 2)

        if novy_zustatek < 0:
            novy_zustatek = 0.0

        kalendar.append({
            "mesic": mesic,
            "splatka_celkem": mesicni_splatka,
            "z_toho_urok": urok,
            "z_toho_umor": umor,
            "zustatek_po_splatce": novy_zustatek
        })

        zustatek = novy_zustatek

        if zustatek <= 0:
            break

    return kalendar


RATES = {
    "Česká spořitelna": 5.29,
    "ČSOB": 4.99,
    "Komerční banka": 5.49
}


@app.get(
    "/",
    summary="Kontrola API",
    description="Vrátí základní informaci, že API běží správně."
)
def root():
    return JSONResponse(
        content={"ok": True, "service": "fintech-api-demo"},
        media_type="application/json; charset=utf-8"
    )


@app.get(
    "/api/rates",
    summary="Aktuální ukázkové sazby bank",
    description="Vrátí seznam ukázkových úrokových sazeb jednotlivých bank."
)
def rates():
    return JSONResponse(
        content={
            "datum": str(date.today()),
            "sazby_bank": RATES
        },
        media_type="application/json; charset=utf-8"
    )


@app.get(
    "/api/hypo/monthly",
    summary="Výpočet měsíční splátky hypotéky",
    description="Vrátí měsíční splátku podle výše úvěru, roční úrokové sazby a délky splácení."
)
def hypo_monthly(
    principal: float = Query(
        ...,
        title="Výše úvěru",
        description="Výše hypotéky v Kč",
        example=3000000
    ),
    annual_rate: float = Query(
        ...,
        title="Roční úrok",
        description="Roční úroková sazba v procentech",
        example=5.5
    ),
    years: int = Query(
        ...,
        title="Doba splácení",
        description="Počet let splácení hypotéky",
        example=30
    )
):
    monthly = vypocet_mesicni_splatky(principal, annual_rate, years)

    return JSONResponse(
        content={
            "vyse_uveru": principal,
            "rocni_urok": annual_rate,
            "doba_splaceni_let": years,
            "mesicni_splatka": monthly
        },
        media_type="application/json; charset=utf-8"
    )


@app.get(
    "/api/hypo/compare",
    summary="Porovnání hypotéky mezi bankami",
    description="Spočítá měsíční splátku stejné hypotéky pro více bank a vrátí i nejlevnější variantu."
)
def hypo_compare(
    principal: float = Query(
        ...,
        title="Výše úvěru",
        description="Výše hypotéky v Kč",
        example=3000000
    ),
    years: int = Query(
        ...,
        title="Doba splácení",
        description="Počet let splácení hypotéky",
        example=30
    )
):
    vysledky = []

    for banka, sazba in RATES.items():
        monthly = vypocet_mesicni_splatky(principal, sazba, years)
        vysledky.append({
            "banka": banka,
            "rocni_sazba": sazba,
            "mesicni_splatka": monthly
        })

    nejlevnejsi = min(vysledky, key=lambda x: x["mesicni_splatka"])

    return JSONResponse(
        content={
            "vyse_uveru": principal,
            "doba_splaceni_let": years,
            "nejlevnejsi_varianta": nejlevnejsi,
            "porovnani_bank": vysledky
        },
        media_type="application/json; charset=utf-8"
    )


@app.get(
    "/api/hypo/schedule",
    summary="Splátkový kalendář hypotéky",
    description="Vrátí splátkový kalendář po jednotlivých měsících včetně úroku, umoření jistiny a zůstatku."
)
def hypo_schedule(
    principal: float = Query(
        ...,
        title="Výše úvěru",
        description="Výše hypotéky v Kč",
        example=3000000
    ),
    annual_rate: float = Query(
        ...,
        title="Roční úrok",
        description="Roční úroková sazba v procentech",
        example=5.5
    ),
    years: int = Query(
        ...,
        title="Doba splácení",
        description="Počet let splácení hypotéky",
        example=30
    )
):
    mesicni_splatka = vypocet_mesicni_splatky(principal, annual_rate, years)
    kalendar = vytvor_splatkovy_kalendar(principal, annual_rate, years)

    return JSONResponse(
        content={
            "vyse_uveru": principal,
            "rocni_urok": annual_rate,
            "doba_splaceni_let": years,
            "mesicni_splatka": mesicni_splatka,
            "pocet_splatek": len(kalendar),
            "splatkovy_kalendar": kalendar
        },
        media_type="application/json; charset=utf-8"
    )