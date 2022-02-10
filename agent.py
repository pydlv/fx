from decimal import Decimal
from typing import List

from markets import Currency, Market
from predictor import Prediction
from simulation.exchange import Exchange, Order, OrderType


class Agent(object):
    exchange: Exchange

    def __init__(self, exchange):
        self.exchange = exchange

    def decide(self, market: Market, prediction: Prediction) -> List[Order]:
        orders = []

        num_segments = 4

        # Buying
        segment_size = (prediction.prediction - prediction.lower) / num_segments
        buy_prices = [prediction.prediction - (i * segment_size) for i in range(num_segments)]

        unallocated_USD = self.exchange.balances[Currency.USD] - self.exchange.balance_allocations[Currency.USD]
        buy_value_per_segment = unallocated_USD / (num_segments - 1)

        if buy_value_per_segment > 0.01:
            for i in range(num_segments):
                # We don't want to buy anything in the segment closest to the prediction
                if i == 0:
                    continue

                price = buy_prices[i]
                quantity = buy_value_per_segment / price

                self.exchange.balance_allocations[Currency.USD] += buy_value_per_segment
                orders.append(Order(OrderType.Buy, quantity, price))

        # Selling
        segment_size = (prediction.upper - prediction.prediction) / num_segments
        sell_prices = [prediction.prediction + (i * segment_size) for i in range(num_segments)]

        unallocated_counter = self.exchange.balances[market.currency] - self.exchange.balance_allocations[market.currency]
        sell_value_per_segment = unallocated_counter / (num_segments - 1)

        if sell_value_per_segment > 0.01:
            for i in range(num_segments):
                if i == 0:
                    continue

                price = sell_prices[i]
                quantity = sell_value_per_segment

                self.exchange.balance_allocations[market.currency] += quantity
                orders.append(Order(OrderType.Sell, quantity, price))

        return orders

    def decide_v2(self, market: Market, prediction: Prediction) -> List[Order]:
        min_order_size = Decimal("0.1")

        price_percents = [Decimal("0.5"), Decimal("0.75"), Decimal("0.9")]
        quantity_percent = Decimal("0.05")

        orders = []

        upper_spread = prediction.upper - prediction.prediction

        sell_price = upper_spread * price_percent + prediction.prediction

        sell_quantity = self.exchange.balances[market.currency] * quantity_percent

        if sell_quantity >= min_order_size:
            orders.append(Order(OrderType.Sell, sell_quantity, sell_price))

        lower_spread = prediction.prediction - prediction.lower

        buy_price = prediction.prediction - lower_spread * price_percent
        buy_value = self.exchange.balances[Currency.USD] * quantity_percent
        buy_quantity = buy_value / buy_price



        if buy_quantity >= min_order_size:
            orders.append(Order(OrderType.Buy, buy_quantity, buy_price))

        return orders

