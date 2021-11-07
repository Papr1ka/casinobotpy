from time import time
from collections import namedtuple
from typing import NamedTuple

seller = namedtuple('SELLER', ['id', 'name', 'size'])
seller_type = NamedTuple("SELLER", [("id", int), ("name", str), ("size", int)])

buyer = namedtuple('BUYER', ['id', 'name', 'size'])
buyer_type = NamedTuple("BUYER", [("id", int), ("name", str), ("size", int)])

coin_prev = namedtuple('COIN_PREV', ['name', 'cost'])
coin_prev_type = NamedTuple("COIN_PREV", [("name", str), ("cost", int)])

def createCoin(name, cost: int, size: int, init_seller: seller_type):
    return {
            '_id': name,
            'cost': cost,
            'size': size,
            'volume': 0,
            'sellers': [init_seller],
            'buyers': [],
            'create_time': time(),
            'top_cost': cost
        }
