import datetime
import warnings
from typing import Iterable, Dict

import pandas

from agent import Agent
from markets import Market, Currency
from predictor import Predictor
from simulation.exchange import Exchange

warnings.filterwarnings("ignore")


def simulate_period(start_date: datetime.date, end_date: datetime.date, markets: Iterable[Market], exchange: Exchange):
    results = []

    predictors: Dict[Market, Predictor] = {}

    for market in markets:
        predictor = Predictor(market)

        try:
            predictor.load()
        except FileNotFoundError:
            print("Model not found. Generating new model for " + market.currency.name)

            predictor.new_model(market.df)

            predictor.save()

        predictor.make_forecast()

        predictors[market] = predictor

    agent = Agent(exchange)

    current_date = start_date
    while current_date < end_date:
        if current_date.isoweekday() in [6, 7]:
            current_date += datetime.timedelta(days=1)
            continue  # Skip weekends

        for market in markets:
            price = market.get_price_by_date(current_date)

            # Update the latest price and process orders
            exchange.update_price(market, price)

            # Clear any leftover orders in preparation for new calculations
            exchange.orders[market].clear()

            prediction = predictors[market].get_prediction_for_date(current_date)

            new_orders = agent.decide(market, prediction)

            for order in new_orders:
                exchange.add_order(market, order)

        total_account_value = sum(
            [
                exchange.balances[market.currency] * exchange.prices[market] for market in markets
            ],
            exchange.balances[Currency.USD]
        )
        results.append([
            current_date, total_account_value
        ])

        current_date += datetime.timedelta(days=1)

    pandas.DataFrame(results, columns=["Date", "Value (USD)"]).to_csv("simulation_results.csv")
