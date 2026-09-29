import requests
from app.core.config import settings

def get_quote(symbol: str) -> dict:
    url = f"{settings.FINNHUB_BASE_URL}/quote"
    params = {"symbol": symbol, "token": settings.FINNHUB_API_KEY}
    response = requests.get(url, params=params, timeout=5)
    response.raise_for_status()
    return response.json()

def get_company_profile(symbol: str) -> dict:
    url = f"{settings.FINNHUB_BASE_URL}/stock/profile2"
    params = {"symbol": symbol, "token": settings.FINNHUB_API_KEY}
    response = requests.get(url, params=params, timeout=5)
    response.raise_for_status()
    return response.json()

def fetch_stock_data(symbol: str) -> dict:
    quote = get_quote(symbol)
    profile = get_company_profile(symbol)

    if not profile or "name" not in profile:
        raise ValueError(f"Symbol '{symbol}' not found in market data")

    price = quote.get("c")
    if price is None or price == 0:
        raise ValueError(f"No live price available for '{symbol}'")

    return {
        "symbol": symbol.upper(),
        "name": profile.get("name"),
        "sector": profile.get("finnhubIndustry"),
        "current_price": price,
    }