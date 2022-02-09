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

        buy_value_per_segment = self.exchange.balances[Currency.USD] / (num_segments - 1)

        if buy_value_per_segment > 0.01:
            for i in range(num_segments):
                # We don't want to buy anything in the segment closest to the prediction
                if i == 0:
                    continue

                price = buy_prices[i]
                quantity = buy_value_per_segment / price

                orders.append(Order(OrderType.Buy, quantity, price))

        # Selling
        segment_size = (prediction.upper - prediction.prediction) / num_segments
        sell_prices = [prediction.prediction + (i * segment_size) for i in range(num_segments)]

        sell_value_per_segment = self.exchange.balances[market.currency] / (num_segments - 1)
        if sell_value_per_segment > 0.01:
            for i in range(num_segments):
                if i == 0:
                    continue

                price = sell_prices[i]
                quantity = sell_value_per_segment

                orders.append(Order(OrderType.Sell, quantity, price))

        return orders
