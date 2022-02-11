from decimal import Decimal
from typing import List

from allocator import Allocator
from markets import Currency, Market
from predictor import Prediction
from simulation.exchange import Exchange, Order, OrderDirection, OrderType


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
                orders.append(Order(direction=OrderDirection.Buy, quantity=quantity, price=price, order_type=OrderType.Limit, market=market))

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
                orders.append(Order(direction=OrderDirection.Sell, quantity=quantity, price=price, order_type=OrderType.Limit, market=market))

        return orders

    def decide_v2(self, market: Market, prediction: Prediction) -> List[Order]:
        min_order_size = Decimal("1")  # USD

        price_percents = [Decimal("0.5"), Decimal("0.75"), Decimal("0.9")]  # 5.6
        # price_percents = [Decimal("0.3"), Decimal("0.475"), Decimal("0.65"), Decimal("0.825"), Decimal("1")]  #5.4
        # price_percents = [Decimal("0.5"), Decimal("0.75"), Decimal("1")]  # 5.4
        # price_percents = [Decimal("0.33"), Decimal("0.66"), Decimal("0.9")]  # 5.2
        quantity_percent = Decimal("0.05")
        qp = (Decimal("1") / len(price_percents))

        orders = []

        upper_spread = prediction.upper - prediction.prediction

        for price_percent in price_percents:
            sell_price = upper_spread * price_percent + prediction.prediction

            sell_quantity = self.exchange.balances[market.currency] * qp

            if sell_quantity * sell_price >= min_order_size:
                orders.append(Order(direction=OrderDirection.Sell, quantity=sell_quantity, price=sell_price, order_type=OrderType.Limit, market=market))

        lower_spread = prediction.prediction - prediction.lower

        for price_percent in price_percents:
            buy_price = prediction.prediction - lower_spread * price_percent
            buy_value = self.exchange.balances[Currency.USD] * qp
            buy_quantity = buy_value / buy_price

            if buy_value >= min_order_size:
                orders.append(Order(direction=OrderDirection.Buy, quantity=buy_quantity, price=buy_price, order_type=OrderType.Limit, market=market))

        return orders

    def decide_v3(self, markets: List[Market]) -> List[Order]:
        """
        Calculates what orders to make to reach the target allocation.
        :param markets: What markets to include in the calculation.
        :return: A list of orders that should be executed in order.
        """
        orders = []

        total_account_value = sum(
            [self.exchange.balances[market.currency] * market.price for market in markets],
            self.exchange.balances[Currency.USD]
        )

        allocations = Allocator.get_target_allocation(total_account_value, markets)

        # Sell any positions we need to
        for market in markets:
            difference = self.exchange.balances[market.currency] * market.price - allocations[market.currency]

            if difference > 0:
                sell_quantity = difference / market.price

                # Create market order to eliminate the difference
                orders.append(Order(
                    order_type=OrderType.Market,
                    direction=OrderDirection.Sell,
                    quantity=sell_quantity,
                    price=market.price,
                    market=market
                ))

        # Buy any positions we need to
        for market in markets:
            difference = allocations[market.currency] - (self.exchange.balances[market.currency] * market.price)

            if difference > 0:
                buy_quantity = difference / market.price

                orders.append(Order(
                    order_type=OrderType.Market,
                    direction=OrderDirection.Buy,
                    quantity=buy_quantity,
                    price=market.price,
                    market=market
                ))

        return orders
