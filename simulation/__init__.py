import copy
import datetime
import warnings
from typing import Iterable, Dict, List

import pandas

from agent import Agent
from markets import Market, Currency
from predictor import Predictor
from simulation.exchange import Exchange, Order

warnings.filterwarnings("ignore")


class Strategy(object):
    markets: List[Market]
    exchange: Exchange
    predictors: Dict[Market, Predictor]
    agent: Agent

    def __init__(self, markets: Iterable[Market], exchange: Exchange):
        self.markets = list(markets)
        self.exchange = exchange

        self.predictors: Dict[Market, Predictor] = {}

        self.agent = Agent(exchange)

        for market in markets:
            predictor = Predictor(market)

            try:
                predictor.load()
            except FileNotFoundError:
                print("Model not found. Generating new model for " + market.currency.name)

                predictor.new_model(market.df)

                predictor.save()

            predictor.make_forecast()

            self.predictors[market] = predictor

    def get_orders_for_date(self, markets: List[Market], date: datetime.date) -> List[Order]:
        # Some markets might not have a prediction for a particular date, so don't include them.
        markets_to_include = []

        for market in markets:
            try:
                prediction = self.predictors[market].get_prediction_for_date(date)
                markets_to_include.append(market)
            except KeyError:
                continue

            market.prediction = prediction

        return self.agent.decide_v3(markets_to_include)

    def simulate_period(self, start_date: datetime.date, end_date: datetime.date):
        results = []

        current_date = start_date
        while current_date < end_date:
            if current_date.isoweekday() in [6, 7]:
                current_date += datetime.timedelta(days=1)
                continue  # Skip weekends

            self.exchange.date = current_date

            # Process orders with the new day's price
            for market in self.markets:
                try:
                    price = market.get_price_by_date(current_date)
                except KeyError:
                    # Some markets may be missing prices for certain days, just skip in that case
                    continue

                # Update the latest price and process orders
                market.price = price
                self.exchange.process_orders(market)

            # Orders should only last for 1 day, clear any old ones
            self.exchange.clear_orders()

            start_balances = copy.deepcopy(self.exchange.balances)

            new_orders = self.get_orders_for_date(self.markets, current_date)

            for order in new_orders:
                self.exchange.add_order(order.market, order)

            # Do a quick check to make sure all our orders filled
            for market in self.markets:
                assert len(self.exchange.orders[market]) == 0

            total_account_value = sum(
                [
                    self.exchange.balances[market.currency] * market.price for market in self.markets
                ],
                self.exchange.balances[Currency.USD]
            )
            results.append([
                current_date, total_account_value
            ])

            current_date += datetime.timedelta(days=1)

        pandas.DataFrame(results, columns=["Date", "Value (USD)"]).to_csv("simulation_results.csv")
