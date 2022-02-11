import datetime
import json
from decimal import Decimal
from typing import Union, Dict

import pandas
import prophet
from pandas import DataFrame, Series
from prophet import Prophet
from prophet.serialize import model_from_json, model_to_json

from markets import Market
from other import PRECISION
from predictor.prediction import Prediction


def stan_init(m):
    """Retrieve parameters from a trained model.

    Retrieve parameters from a trained model in the format
    used to initialize a new Stan model.

    Parameters
    ----------
    m: A trained model of the Prophet class.

    Returns
    -------
    A Dictionary containing retrieved parameters of m.

    """
    res = {}
    for pname in ['k', 'm', 'sigma_obs']:
        res[pname] = m.params[pname][0][0]
    for pname in ['delta', 'beta']:
        res[pname] = m.params[pname][0]
    return res


class Predictor(object):
    m: prophet.Prophet
    forecast: Union[DataFrame, Series]
    predictions: Dict[datetime.date, Prediction]
    market: Market

    def __init__(self, market: Market):
        self.predictions = {}
        self.market = market

    def load(self):
        with open("models/" + self.market.currency.value + ".json", 'r') as fin:
            self.m = model_from_json(json.load(fin))

    def save(self):
        with open("models/" + self.market.currency.value + ".json", 'w') as fout:
            json.dump(model_to_json(self.m), fout)

    def new_model(self, training_data: DataFrame):
        self.m = Prophet()

        self.m.fit(training_data)

    def update_model(self, date: datetime.date, price: float):
        new_df = pandas.concat([self.m.history, pandas.DataFrame([(date, price)], columns=["ds", "y"])], ignore_index=True)
        self.m = Prophet().fit(new_df, init=stan_init(self.m))

    def make_forecast(self, number_of_days=10):
        future = self.m.make_future_dataframe(periods=number_of_days)
        future = future[future["ds"].dt.dayofweek < 5]  # Remove weekends from future df

        self.forecast = self.m.predict(future)

        for i, row in self.forecast.iterrows():
            self.predictions[row["ds"].date()] = Prediction(
                Decimal(row["yhat"]).quantize(PRECISION),
                Decimal(row["yhat_lower"]).quantize(PRECISION),
                Decimal(row["yhat_upper"]).quantize(PRECISION)
            )

    def get_prediction_for_date(self, date: datetime.date) -> Prediction:
        return self.predictions[date]
