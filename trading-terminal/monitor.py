#!/usr/bin/python

from requests import get
from time import time, sleep
import pandas as pd
import plotly.graph_objects as go
import numpy as np
import os

def open_stop_order(client, stop_price, stop_side, price, quantity):
    try:
        order = client.Conditional.Conditional_new(order_type="Market",side=stop_side,symbol="BTCUSD",qty=quantity,price=0,base_price=price,stop_px=stop_price,time_in_force="ImmediateOrCancel").result()
        sleep(3)
        new_stop_order_id = order[0]["result"]["stop_order_id"]
        print(f"OPENED: {new_stop_order_id}\tAT: {stop_price}")
    except Exception as e:
        print("=== OPEN FAILED ===")
        print(str(e))

def replace_stop_order(client, stop_price, stop_id, quantity):
    try:
        order = client.Conditional.Conditional_replace(symbol="BTCUSD", order_id=stop_id, p_r_qty=quantity, p_r_trigger_price=stop_price).result()
        print(f"UPDATED: {stop_id}\tTO: {stop_price}" if order[0]["ret_msg"]=="ok" else order[0]["ret_msg"])
    except Exception as e:
        print("=== UPDATE FAILED ===")
        print(str(e))

def cancel_stop_order(client, stop_id):
    try:
        res = client.Conditional.Conditional_cancel(symbol="BTCUSD", stop_order_id=stop_id).result()
        print(f"CANCELLED: {existing_stop_id}")
    except Exception as e:
        print("=== CANCELLING FAILED ===")
        print(str(e))

def monitor_stop_order(client, t=30):

    while True:

        # clear screen
        os.system("clear")

        print("\n=== MONITORING ===")

        # get info
        info = client.Positions.Positions_myPosition().result()

        side = info[0]['result'][0]["side"]
        size = info[0]['result'][0]["size"]
        entry = np.around(info[0]['result'][0]["entry_price"],0)
        price = np.around(float(client.Market.Market_symbolInfo(symbol="BTCUSD").result()[0]['result'][0]['bid_price']),0)
        stop = client.Conditional.Conditional_getOrders(stop_order_status="Untriggered").result()[0]["result"]["data"]
        stop_side = "Sell" if side=="Buy" else "Buy"

        # prep details
        delta = price - entry
        quantity = 2 * size

        print(f"SIDE: {side}")
        print(f"SIZE: {size}")
        print(f"DELTA: {delta}")

        if not stop:
            if np.abs(delta)>=0 and np.abs(delta)<t:
                stop_price = entry-t if side=="Buy" else entry+t
                open_stop_order(client, stop_price, stop_side, price, quantity)

            elif np.abs(delta)>=t and np.abs(delta)<2*t:
                open_stop_order(client, entry, stop_side, price, quantity)

            elif np.abs(delta)>=2*t and np.abs(delta)<3*t:
                stop_price = entry+t if side=="Buy" else entry-t
                open_stop_order(client, stop_price, stop_side, price, quantity)

            else:
                thresh_price = entry+3*t if side=="Buy" else entry-3*t
                print(f"PRICE OUTSIDE THRESHOLD: {thresh_price}")
        else:
            # get info of existing stop order
            stop_id = stop[0]["stop_order_id"]
            stop_price = float(stop[0]["stop_px"])
            stop_size = stop[0]["qty"]

            above_entry = np.around(stop_price,0) == np.around(entry+t,0) if side=="Buy" else np.around(stop_price,0) == np.around(entry-t,0)
            at_entry = np.around(stop_price,0) == np.around(entry,0)
            below_entry = np.around(stop_price,0) == np.around(entry-t,0) if side=="Buy" else np.around(stop_price,0) == np.around(entry+t,0)

            if np.abs(delta)>=0 and np.abs(delta)<t and not above_entry and not at_entry and not below_entry or stop_size != quantity:
                stop_price = entry-t if side=="Buy" else entry+t
                replace_stop_order(client, stop_price, stop_id, quantity)

            elif np.abs(delta)>=t and np.abs(delta)<2*t and not above_entry and not at_entry or stop_size != quantity:
                replace_stop_order(client, entry, stop_id, quantity)

            elif np.abs(delta)>=2*t and np.abs(delta)<3*t and not above_entry or stop_size != quantity:
                stop_price = entry+t if side=="Buy" else entry-t
                replace_stop_order(client, stop_price, stop_id, quantity)

            elif np.abs(delta)>3*t:
                thresh_price = entry+3*t if side=="Buy" else entry-3*t
                print(f"PRICE OUTSIDE THRESHOLD: {thresh_price}")
                print(f"CANCELLING {stop_id}")
                res = client.Conditional.Conditional_cancel(symbol="BTCUSD",stop_order_id=stop_id).result()[0]["ret_msg"]
                print(f"STATUS: {res}")
            else:
                print("POSITION CORRECT")
        sleep(15)

def breakeven_stop_order(client):

    while True:

        # clear screen
        # os.system("clear")

        print("\n=== MONITORING ===")

        # get price
        price = np.around(float(client.Market.Market_symbolInfo(symbol="BTCUSD").result()[0]['result'][0]['bid_price']),0)

        # get position info
        info = client.Positions.Positions_myPosition().result()
        side = info[0]['result'][0]["side"]
        size = info[0]['result'][0]["size"]
        entry = np.around(info[0]['result'][0]["entry_price"],0)

        # wallet balance
        wb = client.Wallet.Wallet_getBalance(coin="BTC").result()[0]["result"]["BTC"]["wallet_balance"]
        wb = int(wb * price)

        # reduce by
        quantity = wb - size

        # stop above/below entry by delta amount
        delta = int(entry * 0.001)
        stop_price = entry + delta if side=="Buy" else entry - delta
        stop_side = "Sell" if side=="Buy" else "Buy"

        print(f"SIDE: {side}")
        print(f"SIZE: {size}")
        print(f"DELTA: {delta}")
        print(f"WB: {wb}")
        print(f"QUANTITY: {quantity}")

        # check for existing stop
        stop = client.Conditional.Conditional_getOrders(stop_order_status="Untriggered").result()[0]["result"]["data"]

        if not stop and quantity > 0:
            if side=="Buy" and price > stop_price or side=="Sell" and price < stop_price:
                open_stop_order(client, stop_price, stop_side, price, quantity)
            elif price < stop_price and price > entry or price > stop_price and price < entry:
                print("=== PRICE INSIDE DELTA ===")
            else:
                print("=== PRICE OUTSIDE DELTA ===")
        elif quantity > 0:
            # get info of existing stop order
            existing_stop_id = stop[0]["stop_order_id"]
            existing_stop_price = float(stop[0]["stop_px"])
            existing_stop_size = stop[0]["qty"]

            if side=="Buy" and price > stop_price and existing_stop_price==stop_price or side=="Sell" and price < stop_price and existing_stop_price==stop_price:
                print("=== STOP POSITION CORRECT ===")
            elif side=="Buy" and price > stop_price and existing_stop_price != stop_price or side=="Sell" and price < stop_price and existing_stop_price != stop_price:
                replace_stop_order(client, stop_price, existing_stop_id, quantity)
            else:
                cancel_stop_order(client, existing_stop_id)

        sleep(15)
