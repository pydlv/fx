import enum
from typing import Set


class OrderType(enum.Enum):
    Buy = "BUY"
    Sell = "SELL"


class Order(object):
    order_type: OrderType
    quantity: float
    price: float

    def __init__(self, order_type: OrderType, quantity: float, price: float):
        self.order_type = order_type
        self.quantity = quantity
        self.price = price

    def __str__(self):
        return f"{self.order_type} {self.quantity} @ {self.price}"


class Exchange(object):
    balance_USD: float
    balance_GBP: float

    orders: Set[Order]

    market_price: float

    def __init__(self, balance_USD: float, balance_GBP: float, market_price: float):
        self.balance_USD = balance_USD
        self.balance_GBP = balance_GBP
        self.market_price = market_price

        self.orders = set()

    def __str__(self):
        return f"Balance USD: {self.balance_USD}\n" + \
               f"Balance GBP: {self.balance_GBP}\n" + \
               f"Market price: {self.market_price}\n" + \
               f"Orders:\n" + \
               "\n".join(str(order) for order in self.orders)

    def update_price(self, new_price: float):
        self.market_price = new_price
        self.process_orders()

    def add_order(self, order: Order):
        self.orders.add(order)
        self.process_orders()

    def cancel_order(self, order: Order):
        self.orders.remove(order)

    def process_orders(self):
        """
        Updates the market price and fills orders accordingly.
        :param new_price:
        :return:
        """
        for order in self.orders.copy():
            if order.order_type == OrderType.Buy and self.market_price <= order.price:
                # Execute the order at order.price
                order_total = order.price * order.quantity
                assert self.balance_USD >= order_total  # Make sure we have enough funds or throw

                self.balance_USD -= order_total
                self.balance_GBP += order.quantity

                self.orders.remove(order)
            elif order.order_type == OrderType.Sell and self.market_price >= order.price:
                assert self.balance_GBP >= order.quantity  # Make sure we have the required GBP to execute

                order_total = order.price * order.quantity

                self.balance_USD += order_total
                self.balance_GBP -= order.quantity

                self.orders.remove(order)
