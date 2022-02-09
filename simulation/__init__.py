import datetime

import pandas

from predictor import Predictor


def simulate_period(start_date: datetime.date, end_date: datetime.date, start_balance_usd: float):
    history = pandas.DataFrame(columns=["Date", "Balance (in USD)"])

    full_history = pandas.read_csv("max.csv")
    full_history.columns = ["ds", "y"]

    initial_data = full_history[full_history["ds"].dt < start_date]

    predictor = Predictor()

    predictor.new_model(initial_data)

