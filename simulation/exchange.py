import datetime
import enum
from decimal import Decimal
from typing import Set, Dict, Iterable, List, Optional

from markets import Market, Currency

ACCEPTABLE_ROUNDING_ERROR = Decimal("2e-5")


class OrderType(enum.Enum):
    Buy = "BUY"
    Sell = "SELL"


class Order(object):
    order_type: OrderType
    quantity: Decimal
    price: Decimal

    def __init__(self, order_type: OrderType, quantity: Decimal, price: Decimal):
        self.order_type = order_type
        self.quantity = quantity
        self.price = price

    def __str__(self):
        return f"{self.order_type.name} {self.quantity} @ {self.price}"


class Exchange(object):
    markets: List[Market]

    balances: Dict[Currency, Decimal]
    balance_allocations = Dict[Currency, Decimal]

    prices: Dict[Market, Decimal]

    orders: Dict[Market, Set[Order]]

    date: Optional[datetime.date] = None

    def __init__(self, markets: Iterable[Market]):
        self.markets = list(markets)

        self.balances = {}
        self.balance_allocations = {}
        self.prices = {}

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

    def update_price(self, market: Market, new_price: Decimal):
        self.prices[market] = new_price
        self.process_orders(market)

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
            if order.order_type == OrderType.Buy and self.prices[market] <= order.price:
                # Execute the order at order.price
                order_total = order.price * order.quantity
                # assert self.balances[Currency.USD] >= order_total or abs(self.balances[Currency.USD] - order_total) <= ACCEPTABLE_ROUNDING_ERROR

                # If we don't have enough funds to execute, just skip
                if self.balances[Currency.USD] < order_total:
                    continue

                self.balances[Currency.USD] -= order_total
                self.balances[market.currency] += order.quantity

                print(self.date, "Executing order:", order, market.currency.name)

                self.orders[market].remove(order)
            elif order.order_type == OrderType.Sell and self.prices[market] >= order.price:
                # assert self.balances[market.currency] >= order.quantity or abs(self.balances[market.currency] - order.quantity) <= ACCEPTABLE_ROUNDING_ERROR

                if self.balances[market.currency] < order.quantity:
                    continue

                order_total = order.price * order.quantity

                self.balances[Currency.USD] += order_total
                self.balances[market.currency] -= order.quantity

                print(self.date, "Executing order:", order, market.currency.name)

                self.orders[market].remove(order)
