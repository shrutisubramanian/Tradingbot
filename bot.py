import argparse
import logging
import sys
from binance.client import Client
from binance.exceptions import BinanceAPIException, BinanceRequestException


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("trading_bot.log", encoding="utf-8"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger()



class BasicBot:
    """
    Simplified Trading Bot for Binance Futures Testnet (USDT-M)
    Supports Market, Limit, and Stop-Limit orders
    """
    
    def __init__(self, api_key, api_secret, testnet=True):
        """
        Initialize the trading bot
        
        Args:
            api_key (str): Binance API key
            api_secret (str): Binance API secret
            testnet (bool): Use testnet environment
        """
        self.client = Client(api_key, api_secret, testnet=testnet)
        
        
        if testnet:
            self.client.API_URL = "https://testnet.binancefuture.com"
            logger.info(" Using Binance Futures Testnet")
        
       
        try:
            self.client.futures_ping()
            logger.info(" Connected to Binance Futures Testnet successfully!")
        except Exception as e:
            logger.error(f" Connection to Binance Futures Testnet failed: {e}")
            raise

    def get_balance(self):
        """Fetch and display account balance"""
        try:
            balances = self.client.futures_account_balance()
            logger.info("💰 Balance fetched successfully.")
            print("\n" + "="*60)
            print("💰 ACCOUNT BALANCES (FUTURES TESTNET)")
            print("="*60)
            for b in balances:
                asset = b.get("asset", "Unknown")
                balance = float(b.get("balance", "0"))
                if balance > 0:  
                    print(f"  {asset:8s}: {balance:>15,.8f}")
            print("="*60 + "\n")
            return balances
        except BinanceAPIException as e:
            logger.error(f" Binance API Error fetching balance: {e.message}")
        except Exception as e:
            logger.error(f" Failed to fetch balance: {e}")

    def get_current_price(self, symbol):
        """Get current market price for a symbol"""
        try:
            ticker = self.client.futures_symbol_ticker(symbol=symbol)
            return float(ticker['price'])
        except Exception as e:
            logger.warning(f" Could not fetch current price: {e}")
            return None

    def show_current_price(self, symbol):
        """Display current market price"""
        try:
            ticker = self.client.futures_symbol_ticker(symbol=symbol)
            price = float(ticker['price'])
            logger.info(f" Current price for {symbol}: {price}")
            print("\n" + "="*60)
            print(f" CURRENT MARKET PRICE")
            print("="*60)
            print(f"  Symbol: {symbol}")
            print(f"  Price:  ${price:,.2f}")
            print("="*60 + "\n")
            return price
        except Exception as e:
            logger.error(f" Failed to fetch price: {e}")
            print(f"\n Failed to fetch price: {e}")

    def validate_order_params(self, symbol, side, order_type, quantity, price=None, stop_price=None):
        """
        Validate order parameters before placing order
        
        Returns:
            tuple: (bool, str) - (is_valid, error_message)
        """
        
        if side.upper() not in ["BUY", "SELL"]:
            return False, "Side must be 'BUY' or 'SELL'"
        
       
        valid_types = ["MARKET", "LIMIT", "STOP_LIMIT", "STOP_MARKET"]
        if order_type.upper() not in valid_types:
            return False, f"Order type must be one of {valid_types}"
        
        
        if quantity <= 0:
            return False, "Quantity must be greater than 0"
        
        
        if order_type.upper() in ["LIMIT", "STOP_LIMIT"]:
            if price is None or price <= 0:
                return False, f"{order_type} orders require a valid price"
        
       
        if order_type.upper() in ["STOP_LIMIT", "STOP_MARKET"]:
            if stop_price is None or stop_price <= 0:
                return False, f"{order_type} orders require a valid stop price"
            
           
            current_price = self.get_current_price(symbol)
            if current_price:
                if side.upper() == "BUY":
                    if stop_price <= current_price:
                        return False, (f"For BUY STOP orders, stop price ({stop_price}) must be ABOVE "
                                     f"current market price ({current_price:.2f}). "
                                     f"Stop orders trigger when price RISES to your stop price.")
                    if order_type.upper() == "STOP_LIMIT" and price > stop_price:
                        return False, (f"For BUY STOP_LIMIT, limit price ({price}) should be <= stop price ({stop_price}). "
                                     f"Limit price is where you want to buy after stop triggers.")
                else:  
                    if stop_price >= current_price:
                        return False, (f"For SELL STOP orders, stop price ({stop_price}) must be BELOW "
                                     f"current market price ({current_price:.2f}). "
                                     f"Stop orders trigger when price FALLS to your stop price.")
                    if order_type.upper() == "STOP_LIMIT" and price < stop_price:
                        return False, (f"For SELL STOP_LIMIT, limit price ({price}) should be >= stop price ({stop_price}). "
                                     f"Limit price is where you want to sell after stop triggers.")
        
        return True, ""

    def place_order(self, symbol, side, order_type, quantity, price=None, stop_price=None):
        """
        Place an order on Binance Futures
        
        Args:
            symbol (str): Trading pair (e.g., 'BTCUSDT')
            side (str): 'BUY' or 'SELL'
            order_type (str): 'MARKET', 'LIMIT', 'STOP_LIMIT', or 'STOP_MARKET'
            quantity (float): Order quantity
            price (float, optional): Limit price for LIMIT/STOP_LIMIT orders
            stop_price (float, optional): Stop price for STOP orders
        
        Returns:
            dict: Order response or None if failed
        """
        side = side.upper()
        order_type = order_type.upper()
        
        
        is_valid, error_msg = self.validate_order_params(
            symbol, side, order_type, quantity, price, stop_price
        )
        if not is_valid:
            logger.error(f" Validation Error: {error_msg}")
            print(f"\n Order Error: {error_msg}")
            return None
        
        try:
            logger.info(f" Placing {order_type} {side} order for {symbol}")
            
            if order_type == "MARKET":
                order = self.client.futures_create_order(
                    symbol=symbol,
                    side=side,
                    type="MARKET",
                    quantity=quantity
                )
            
            elif order_type == "LIMIT":
                order = self.client.futures_create_order(
                    symbol=symbol,
                    side=side,
                    type="LIMIT",
                    timeInForce="GTC",
                    quantity=quantity,
                    price=str(price)
                )
            
            elif order_type == "STOP_MARKET":
                order = self.client.futures_create_order(
                    symbol=symbol,
                    side=side,
                    type="STOP_MARKET",
                    quantity=quantity,
                    stopPrice=str(stop_price)
                )
            
            elif order_type == "STOP_LIMIT":
                order = self.client.futures_create_order(
                    symbol=symbol,
                    side=side,
                    type="STOP",
                    timeInForce="GTC",
                    quantity=quantity,
                    price=str(price),
                    stopPrice=str(stop_price)
                )
            
            logger.info(f" Order placed successfully! Order ID: {order.get('orderId')}")
            print("\n" + "="*60)
            print(" ORDER PLACED SUCCESSFULLY!")
            print("="*60)
            print(f"  Order ID:   {order.get('orderId')}")
            print(f"  Symbol:     {order.get('symbol')}")
            print(f"  Side:       {order.get('side')}")
            print(f"  Type:       {order.get('type')}")
            print(f"  Quantity:   {order.get('origQty')}")
            print(f"  Status:     {order.get('status')}")
            if order.get('price'):
                print(f"  Price:      {order.get('price')}")
            if order.get('stopPrice'):
                print(f"  Stop Price: {order.get('stopPrice')}")
            print("="*60 + "\n")
            
            return order
            
        except BinanceAPIException as e:
            logger.error(f" Binance API Error: {e.status_code} - {e.message}")
            print(f"\n Order Failed: {e.message}")
        except BinanceRequestException as e:
            logger.error(f" Request Error: {e}")
            print(f"\n Request Failed: {e}")
        except Exception as e:
            logger.error(f" Unexpected error: {e}")
            print(f"\n Order placement failed: {e}")
        
        return None

    def get_open_orders(self, symbol):
        """Get all open orders for a symbol"""
        try:
            orders = self.client.futures_get_open_orders(symbol=symbol)
            logger.info(f" Retrieved {len(orders)} open orders for {symbol}")
            
            if not orders:
                print(f"\n📭 No open orders for {symbol}\n")
            else:
                print("\n" + "="*80)
                print(f" OPEN ORDERS FOR {symbol}")
                print("="*80)
                for o in orders:
                    print(f"  ID: {o['orderId']:12d} | Side: {o['side']:4s} | "
                          f"Type: {o['type']:15s} | Qty: {o['origQty']:8s} | "
                          f"Price: {o.get('price', 'N/A')}")
                print("="*80 + "\n")
            
            return orders
        except Exception as e:
            logger.error(f" Failed to fetch open orders: {e}")
            print(f"\n Failed to retrieve orders: {e}")

    def get_positions(self, symbol=None):
        """Get current positions"""
        try:
            if symbol:
                positions = self.client.futures_position_information(symbol=symbol)
            else:
                positions = self.client.futures_position_information()
            
            active_positions = [p for p in positions if float(p["positionAmt"]) != 0]
            
            logger.info(f" Retrieved {len(active_positions)} active positions")
            
            if not active_positions:
                print(f"\n No active positions{' for ' + symbol if symbol else ''}\n")
            else:
                print("\n" + "="*90)
                print(f" ACTIVE POSITIONS{' FOR ' + symbol if symbol else ''}")
                print("="*90)
                for p in active_positions:
                    print(f"  Symbol: {p['symbol']:10s} | Position: {p['positionAmt']:>10s} | "
                          f"Entry: {float(p['entryPrice']):>10,.2f} | "
                          f"PnL: ${float(p['unRealizedProfit']):>10,.2f}")
                print("="*90 + "\n")
            
            return active_positions
        except Exception as e:
            logger.error(f" Failed to fetch positions: {e}")
            print(f"\n Failed to retrieve positions: {e}")

    def cancel_order(self, symbol, order_id):
        """Cancel a specific order"""
        try:
            result = self.client.futures_cancel_order(symbol=symbol, orderId=order_id)
            logger.info(f" Order {order_id} canceled successfully")
            print(f"\n Order {order_id} canceled for {symbol}\n")
            return result
        except BinanceAPIException as e:
            logger.error(f" Failed to cancel order: {e.message}")
            print(f"\n Cancel failed: {e.message}\n")
        except Exception as e:
            logger.error(f" Failed to cancel order: {e}")
            print(f"\n Cancel failed: {e}\n")

    def cancel_all_orders(self, symbol):
        """Cancel all open orders for a symbol"""
        try:
            result = self.client.futures_cancel_all_open_orders(symbol=symbol)
            logger.info(f" All orders canceled for {symbol}")
            print(f"\n All orders canceled for {symbol}\n")
            return result
        except Exception as e:
            logger.error(f" Failed to cancel all orders: {e}")
            print(f"\n Failed to cancel all orders: {e}\n")



def print_banner():
    """Print fancy banner"""
    banner = """
╔════════════════════════════════════════════════════════════════╗
║                                                                ║
║           BINANCE FUTURES TRADING BOT (TESTNET)                ║
║                                                                ║
║              Automated Trading Made Simple                     ║
║                                                                ║
╚════════════════════════════════════════════════════════════════╝
"""
    print(banner)

def print_menu():
    """Print main menu options"""
    menu = """
╔════════════════════════════════════════════════════════════════╗
║                        MAIN MENU                               ║
╠════════════════════════════════════════════════════════════════╣
║                                                                ║
║  1️⃣  View Account Balance                                      ║
║  2️⃣  Check Current Price                                       ║
║  3️⃣  Place Market Order (BUY/SELL)                            ║
║  4️⃣  Place Limit Order (BUY/SELL)                             ║
║  5️⃣  Place Stop-Limit Order (Advanced)                        ║
║  6️⃣  View Open Orders                                          ║
║  7️⃣  View Active Positions                                     ║
║  8️⃣  Cancel Order                                              ║
║  9️⃣  Cancel All Orders                                         ║
║  0️⃣  Exit                                                       ║
║                                                                ║
╚════════════════════════════════════════════════════════════════╝
"""
    print(menu)

def get_input(prompt, input_type=str, default=None):
    """Get validated input from user"""
    while True:
        try:
            value = input(f"{prompt}: ").strip()
            if not value and default is not None:
                return default
            if not value:
                print(" Input cannot be empty. Please try again.")
                continue
            return input_type(value)
        except ValueError:
            print(f" Invalid input. Expected {input_type.__name__}. Please try again.")

def interactive_mode(bot):
    """Run interactive CLI menu"""
    print_banner()
    
    while True:
        print_menu()
        choice = get_input("Enter your choice (0-9)", str)
        
        if choice == "1":
           
            bot.get_balance()
            input("\nPress Enter to continue...")
            
        elif choice == "2":
           
            symbol = get_input("Enter symbol (e.g., BTCUSDT)", str, "BTCUSDT").upper()
            bot.show_current_price(symbol)
            input("\nPress Enter to continue...")
            
        elif choice == "3":
           
            print("\n" + "="*60)
            print(" PLACE MARKET ORDER")
            print("="*60)
            symbol = get_input("Symbol (e.g., BTCUSDT)", str, "BTCUSDT").upper()
            side = get_input("Side (BUY/SELL)", str).upper()
            quantity = get_input("Quantity", float)
            
            bot.place_order(symbol, side, "MARKET", quantity)
            input("\nPress Enter to continue...")
            
        elif choice == "4":
           
            print("\n" + "="*60)
            print(" PLACE LIMIT ORDER")
            print("="*60)
            symbol = get_input("Symbol (e.g., BTCUSDT)", str, "BTCUSDT").upper()
            
            
            current_price = bot.get_current_price(symbol)
            if current_price:
                print(f" Current Price: ${current_price:,.2f}")
            
            side = get_input("Side (BUY/SELL)", str).upper()
            quantity = get_input("Quantity", float)
            price = get_input("Limit Price", float)
            
            bot.place_order(symbol, side, "LIMIT", quantity, price)
            input("\nPress Enter to continue...")
            
        elif choice == "5":
            
            print("\n" + "="*60)
            print(" PLACE STOP-LIMIT ORDER (ADVANCED)")
            print("="*60)
            symbol = get_input("Symbol (e.g., BTCUSDT)", str, "BTCUSDT").upper()
            
            
            current_price = bot.get_current_price(symbol)
            if current_price:
                print(f" Current Price: ${current_price:,.2f}")
                print(f"\n Quick Guide:")
                print(f"   BUY: Stop price > {current_price:.2f} (breakout)")
                print(f"   SELL: Stop price < {current_price:.2f} (stop-loss)")
            
            side = get_input("Side (BUY/SELL)", str).upper()
            quantity = get_input("Quantity", float)
            stop_price = get_input("Stop Price (trigger)", float)
            price = get_input("Limit Price (execution)", float)
            
            bot.place_order(symbol, side, "STOP_LIMIT", quantity, price, stop_price)
            input("\nPress Enter to continue...")
            
        elif choice == "6":
           
            symbol = get_input("Enter symbol (e.g., BTCUSDT)", str, "BTCUSDT").upper()
            bot.get_open_orders(symbol)
            input("\nPress Enter to continue...")
            
        elif choice == "7":
           
            symbol = get_input("Enter symbol (or press Enter for all)", str, None)
            if symbol:
                symbol = symbol.upper()
            bot.get_positions(symbol)
            input("\nPress Enter to continue...")
            
        elif choice == "8":
            
            symbol = get_input("Enter symbol (e.g., BTCUSDT)", str, "BTCUSDT").upper()
            order_id = get_input("Enter Order ID", int)
            bot.cancel_order(symbol, order_id)
            input("\nPress Enter to continue...")
            
        elif choice == "9":
           
            symbol = get_input("Enter symbol (e.g., BTCUSDT)", str, "BTCUSDT").upper()
            confirm = get_input(f" Cancel ALL orders for {symbol}? (yes/no)", str).lower()
            if confirm == "yes":
                bot.cancel_all_orders(symbol)
            else:
                print(" Cancelled.")
            input("\nPress Enter to continue...")
            
        elif choice == "0":
            
            print("\n" + "="*60)
            print(" Thank you for using Binance Futures Trading Bot!")
            print("="*60 + "\n")
            logger.info("Bot session ended by user")
            sys.exit(0)
            
        else:
            print("\n Invalid choice. Please select 0-9.\n")
            input("Press Enter to continue...")



def command_line_mode(args, bot):
    """Run in command-line mode with arguments"""
    
    bot.get_balance()
    
    
    if hasattr(args, 'show_price') and args.show_price:
        bot.show_current_price(args.symbol)
    
   
    if args.side and args.order_type:
        bot.place_order(
            symbol=args.symbol,
            side=args.side,
            order_type=args.order_type,
            quantity=args.quantity,
            price=args.price,
            stop_price=args.stop_price
        )
    
    
    if args.show_orders:
        bot.get_open_orders(args.symbol)
    
    if args.show_positions:
        bot.get_positions(args.symbol)
    
    
    if args.cancel_order:
        bot.cancel_order(args.symbol, args.cancel_order)
    
    if args.cancel_all:
        bot.cancel_all_orders(args.symbol)


def main():
    parser = argparse.ArgumentParser(
        description="Binance Futures Trading Bot (Testnet)",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Interactive menu mode (recommended)
  python bot.py --api-key YOUR_KEY --api-secret YOUR_SECRET --interactive

  # Place market buy order
  python bot.py --api-key YOUR_KEY --api-secret YOUR_SECRET --symbol BTCUSDT --side BUY --type MARKET --quantity 0.001

  # Place limit sell order
  python bot.py --api-key YOUR_KEY --api-secret YOUR_SECRET --symbol BTCUSDT --side SELL --type LIMIT --quantity 0.001 --price 50000
        """
    )
    
   
    parser.add_argument("--api-key", required=True, help="Binance API Key")
    parser.add_argument("--api-secret", required=True, help="Binance API Secret")
    parser.add_argument("--symbol", help="Trading symbol (e.g., BTCUSDT)")
    
    
    parser.add_argument("--interactive", "-i", action="store_true", 
                       help="Launch interactive menu interface")
    
    
    parser.add_argument("--side", choices=["BUY", "SELL", "buy", "sell"], 
                       help="Order side: BUY or SELL")
    parser.add_argument("--type", dest="order_type", 
                       choices=["MARKET", "LIMIT", "STOP_LIMIT", "STOP_MARKET"],
                       help="Order type")
    parser.add_argument("--quantity", type=float, help="Order quantity")
    parser.add_argument("--price", type=float, help="Limit price")
    parser.add_argument("--stop-price", type=float, help="Stop price")
    
   
    parser.add_argument("--show-orders", action="store_true", help="Show open orders")
    parser.add_argument("--show-positions", action="store_true", help="Show active positions")
    parser.add_argument("--show-price", action="store_true", help="Show current market price")
    parser.add_argument("--cancel-order", type=int, metavar="ORDER_ID", help="Cancel specific order")
    parser.add_argument("--cancel-all", action="store_true", help="Cancel all open orders")
    
    args = parser.parse_args()
    
   
    try:
        bot = BasicBot(args.api_key, args.api_secret, testnet=True)
    except Exception as e:
        logger.error(f"Failed to initialize bot: {e}")
        return
    
    
    if args.interactive:
        interactive_mode(bot)
    else:
        if not args.symbol:
            print(" Error: --symbol is required in command-line mode")
            print(" Tip: Use --interactive or -i for menu mode")
            return
        command_line_mode(args, bot)


if __name__ == "__main__":
    main()