from binance.client import Client

API_KEY = "YOUR_API_KEY"
API_SECRET = "YOUR_API_SECRET"

def test_spot():
    print("\n🟡 Testing Spot Testnet...")
    try:
        client = Client(API_KEY, API_SECRET, testnet=True)
        client.API_URL = "https://testnet.binance.vision/api"
        client.ping()
        print("✅ Spot Testnet Connection Successful!")
        return True
    except Exception as e:
        print(f"❌ Spot Testnet Failed: {e}")
        return False

def test_futures():
    print("\n🟢 Testing Futures Testnet...")
    try:
        client = Client(API_KEY, API_SECRET, testnet=True)
        client.FUTURES_URL = "https://testnet.binancefuture.com/fapi/v1/"
        client.API_URL = client.FUTURES_URL
        client.futures_ping()
        print("✅ Futures Testnet Connection Successful!")
        return True
    except Exception as e:
        print(f"❌ Futures Testnet Failed: {e}")
        return False

if __name__ == "__main__":
    spot_ok = test_spot()
    futures_ok = test_futures()

    print("\n🧠 Summary:")
    if spot_ok and not futures_ok:
        print("➡️ Your keys are for the **Spot Testnet**.")
    elif futures_ok and not spot_ok:
        print("➡️ Your keys are for the **Futures Testnet**.")
    elif not spot_ok and not futures_ok:
        print("❌ Your keys failed on both. Check key validity or permissions.")
    else:
        print("⚠️ Your keys appear to work for both environments — verify usage context.")
