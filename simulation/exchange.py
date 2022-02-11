import datetime
import enum
import logging
from decimal import Decimal
from typing import Set, Dict, Iterable, List, Optional

from markets import Market, Currency

ACCEPTABLE_ROUNDING_ERROR = Decimal("2e-4")


class OrderDirection(enum.Enum):
    Buy = "BUY"
    Sell = "SELL"


class OrderType(enum.Enum):
    Market = "MARKET"
    Limit = "LIMIT"


class Order(object):
    order_type: OrderType
    quantity: Decimal
    price: Decimal
    direction: OrderDirection
    market: Market

    def __init__(self, *, market: Market, order_type: OrderType, direction: OrderDirection, quantity: Decimal, price: Decimal):
        self.order_type = order_type
        self.quantity = quantity
        self.price = price
        self.direction = direction
        self.market = market

    def __str__(self):
        return f"{self.direction.name} {self.market.currency.name} {self.quantity} @ {self.price} {self.order_type.name}"


class Exchange(object):
    markets: List[Market]

    balances: Dict[Currency, Decimal]
    balance_allocations = Dict[Currency, Decimal]

    orders: Dict[Market, Set[Order]]

    date: Optional[datetime.date] = None

    def __init__(self, markets: Iterable[Market]):
        self.markets = list(markets)

        self.balances = {}
        self.balance_allocations = {}

        self.orders = {}

        for market in markets:
            self.balances[market.currency] = Decimal(0)
            self.balance_allocations[market.currency] = Decimal(0)
            self.orders[market] = set()
        self.balance_allocations[Currency.USD] = Decimal(0)

    def clear_orders(self):
        for market in self.markets:
            self.balance_allocations[market.currency] = Decimal(0)
            self.orders[market].clear()
        self.balance_allocations[Currency.USD] = Decimal(0)

    # def __str__(self):
    #     return f"Balance USD: {self.balance_USD}\n" + \
    #            f"Balance GBP: {self.balance_GBP}\n" + \
    #            f"Market price: {self.market_price}\n" + \
    #            f"Orders:\n" + \
    #            "\n".join(str(order) for order in self.orders)

    def set_balance(self, currency: Currency, new_balance: Decimal):
        self.balances[currency] = new_balance

    def add_order(self, market: Market, order: Order):
        self.orders[market].add(order)
        self.process_orders(market)

    def cancel_order(self, market: Market, order: Order):
        self.orders[market].remove(order)

    def process_orders(self, market: Market):
        """
        Updates the market price and fills orders accordingly.
        :param market:
        :return:
        """
        for order in self.orders[market].copy():
            if order.direction == OrderDirection.Buy:
                if order.order_type == OrderType.Limit and market.price > order.price:
                    continue
                else:
                    order.price = market.price

                # Execute the order at order.price
                order_total = order.price * order.quantity
                # assert self.balances[Currency.USD] >= order_total or abs(self.balances[Currency.USD] - order_total) <= ACCEPTABLE_ROUNDING_ERROR

                assert self.balances[Currency.USD] >= order_total or abs(self.balances[Currency.USD] - order_total) <= ACCEPTABLE_ROUNDING_ERROR

                self.balances[Currency.USD] -= order_total
                self.balances[market.currency] += order.quantity

                logging.info(str(self.date) + " Executing order: " + str(order))

                self.orders[market].remove(order)
            elif order.direction == OrderDirection.Sell:
                if order.order_type == OrderType.Limit and market.price < order.price:
                    continue
                else:
                    order.price = market.price

                assert self.balances[market.currency] >= order.quantity or abs(self.balances[market.currency] - order.quantity) <= ACCEPTABLE_ROUNDING_ERROR

                order_total = order.price * order.quantity

                self.balances[Currency.USD] += order_total
                self.balances[market.currency] -= order.quantity

                logging.info(str(self.date) + " Executing order: " + str(order))

                self.orders[market].remove(order)
