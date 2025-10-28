Binance Futures Trading Bot (Testnet)

A Python-based trading bot for the Binance Futures Testnet, allowing users to safely test trading logic without using real funds.
It supports Market, Limit, Stop-Limit, and Stop-Market orders with balance tracking and order management.

Features

Connects to Binance Futures Testnet

Fetches live prices and account balances

Places Market, Limit, and Stop orders

Views and cancels open orders

Tracks logs for all activities

Installation
pip install python-binance

Setup

Get Binance Futures Testnet API keys:

https://testnet.binancefuture.com/en/futures/BTCUSDT

Create API and Secret keys with Futures Trading enabled.

Requirements
pip install python-binance


Run the bot interactively:

python basic_binance_bot.py --api-key YOUR_API_KEY --api-secret YOUR_API_SECRET --interactive

Interactive CLI Menu
1. View Balance
2. Check Current Price
3. Place Market Order
4. Place Limit Order
5. Place Stop-Limit Order
6. View Open Orders
7. View Positions
8. Cancel Order
9. Cancel All Orders
0. Exit
