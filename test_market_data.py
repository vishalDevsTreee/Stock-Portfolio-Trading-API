from app.services import market_data

result = market_data.fetch_stock_data("AAPL")
print(result)