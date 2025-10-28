from binance.client import Client

# Your API credentials
api_key = "WTP4LlfySgu8EkV1uFLrypDjQrQ9DvBIr94aVGaDVKqtjV11T6IgCAsIaHSeBWiH"
api_secret = "Cpi3yYUsPGusnyjfRWrQfzoAIqVTwGerdZtK1eYI7QWI7VWv9YnhsAKfVbRdhV5V"

# Initialize client
client = Client(api_key, api_secret, testnet=True)
client.API_URL = "https://testnet.binancefuture.com"

# Get current price
ticker = client.futures_symbol_ticker(symbol="BTCUSDT")
current_price = float(ticker['price'])

print(f"\n{'='*50}")
print(f"💲 Current BTCUSDT Price: ${current_price:,.2f}")
print(f"{'='*50}\n")

# Suggest correct stop-limit values
print("📊 Example STOP-LIMIT Orders:")
print(f"\n🟢 BUY STOP-LIMIT (Breakout):")
print(f"   --side BUY --type STOP_LIMIT")
print(f"   --stop-price {current_price + 1000:.2f}")
print(f"   --price {current_price + 1500:.2f}")
print(f"   --quantity 0.02")

print(f"\n🔴 SELL STOP-LIMIT (Stop-Loss):")
print(f"   --side SELL --type STOP_LIMIT")
print(f"   --stop-price {current_price - 1000:.2f}")
print(f"   --price {current_price - 1500:.2f}")
print(f"   --quantity 0.02")

print(f"\n✅ Simple MARKET BUY Order:")
print(f"   --side BUY --type MARKET --quantity 0.02")

print(f"\n✅ Simple LIMIT SELL Order:")
print(f"   --side SELL --type LIMIT --price {current_price + 500:.2f} --quantity 0.02")