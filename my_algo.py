#!/usr/bin/python

from bybit import bybit
from keys import KEY, SECRET
from funcs import data, zsl
from monitor import monitor_stop_order, breakeven_stop_order
import sys

# connect
client = bybit(test=False, api_key=KEY, api_secret=SECRET)

# get positions
pos = client.Positions.Positions_myPosition().result()[0]["result"]

# find active positions
act_pos = [p for p in pos if p["size"] is not 0]

# print pos info
if act_pos:
    # current price
    price = client.Market.Market_symbolInfo(symbol="BTCUSD").result()[0]["result"][0]["bid_price"]

    _, std, _, _ = zsl()
    s = int(std.mean())
    print(f"\nSTDEV: {s}")

    print("\n=== ACTIVE POSITIONS ===")
    for p in act_pos:
        symbol, side, size = p["symbol"], p["side"], p["size"]
        liq_price_p = (float(price) - float(p["liq_price"])) / float(price)
        print(f"Symbol: {symbol}\tSide: {side}\tSize: ${size}\tLiqPriceDelta: {liq_price_p:.1%}")

    # is stop present?
    stop = client.Conditional.Conditional_getOrders(stop_order_status="Untriggered").result()[0]["result"]["data"]

    if stop:
        print("\n=== SL PRESENT ===")
        stop_size, stop_side, stop_price = stop[0]["qty"], stop[0]["side"], stop[0]["stop_px"]
        print(f"Stop Size: {stop_size}\tStop Side: {stop_side}\tStop Price: {stop_price}")
        print(f"Current Price: {price}")

        # monitor_stop_stop_order(client, t=s)

        breakeven_stop_order(client)
    else:
        print("\n=== NO STOP PRESENT ===")
        ans = str(sys.argv[1])

        if ans=="SL":
            # place stop order
            print("=== PLACING STOPLOSS ORDER ===")
            monitor_stop_order(client, t=s)
        elif ans=="BE":
            # place breakeven order
            print("=== PLACING BREAKEVEN STOP ORDER ===")
            breakeven_stop_order(client)
        else:
            print("=== EXITING ===")
else:
    print("=== NO ACTIVE POSITIONS ===")
