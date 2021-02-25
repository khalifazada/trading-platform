#!/usr/bin/python

from bybit import bybit
from keys.keys import KEY, SECRET
import sys

print(KEY, SECRET)

# # connect
# client = bybit(test=False, api_key=KEY, api_secret=SECRET)
#
# def active_positions(client):
#
#     # get positions
#     pos = client.Positions.Positions_myPosition().result()[0]["result"]
#
#     # find active positions
#     act_pos = [p for p in pos if p["size"] is not 0]
#
#     # print pos info
#     if act_pos:
#         # current price
#
#         print("\n=== ACTIVE POSITIONS ===")
#         for p in act_pos:
#             symbol, side, size, liq_price = p["symbol"], p["side"], p["size"], p["liq_price"]
#             print(f"Symbol: {symbol}\tSide: {side}\tSize: ${size}\tLiqPriceDelta: {liq_price:.1%}")
#     else:
#         print("=== NO ACTIVE POSITIONS ===")
#
# if __name__ == __main__:
#     active_positions()
