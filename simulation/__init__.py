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

    def get_orders_for_date(self, market: Market, date: datetime.date) -> List[Order]:
        prediction = self.predictors[market].get_prediction_for_date(date)

        return self.agent.decide_v2(market, prediction)

    def simulate_period(self, start_date: datetime.date, end_date: datetime.date):
        results = []

        current_date = start_date
        while current_date < end_date:
            if current_date.isoweekday() in [6, 7]:
                current_date += datetime.timedelta(days=1)
                continue  # Skip weekends

            exchange.date = current_date

            # Process orders with the new day's price
            for market in self.markets:
                try:
                    price = market.get_price_by_date(current_date)
                except KeyError:
                    # Some markets may be missing prices for certain days, just skip in that case
                    continue

                # Update the latest price and process orders
                self.exchange.update_price(market, price)

            # Orders should only last for 1 day, clear any old ones
            self.exchange.clear_orders()

            for market in self.markets:
                try:
                    new_orders = self.get_orders_for_date(market, current_date)
                except KeyError:
                    continue

                for order in new_orders:
                    self.exchange.add_order(market, order)

            total_account_value = sum(
                [
                    self.exchange.balances[market.currency] * self.exchange.prices[market] for market in self.markets
                ],
                self.exchange.balances[Currency.USD]
            )
            results.append([
                current_date, total_account_value
            ])

            current_date += datetime.timedelta(days=1)

        pandas.DataFrame(results, columns=["Date", "Value (USD)"]).to_csv("simulation_results.csv")
