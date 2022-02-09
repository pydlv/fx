import datetime
import json

import prophet
from pandas import DataFrame
from prophet import Prophet
from prophet.serialize import model_from_json, model_to_json


MODEL_FILENAME = "model.json"


class Prediction(object):
    prediction: float
    lower: float
    upper: float

    def __init__(self, prediction, low, high):
        self.prediction = prediction
        self.lower = low
        self.upper = high

    def __str__(self):
        return f"Prediction: {self.prediction}, Upper: {self.upper}, Lower: {self.lower}"


class Predictor(object):
    m: prophet.Prophet

    def load(self):
        with open(MODEL_FILENAME, 'r') as fin:
            self.m = model_from_json(json.load(fin))

    def save(self):
        with open(MODEL_FILENAME, 'w') as fout:
            json.dump(model_to_json(self.m), fout)

    def new_model(self, training_data: DataFrame):
        self.m = Prophet()

        self.m.fit(training_data)

    def next_day_prediction(self) -> Prediction:
        """
        :return: Returns prediction for the next trading day.
        """

        future = self.m.make_future_dataframe(periods=10)
        future = future[future["ds"].dt.dayofweek < 5]  # Remove weekends from future df

        forecast = self.m.predict(future)

        next_day = None

        for k, row in forecast.iterrows():
            if row["ds"].date() > datetime.datetime.now().date():
                next_day = row
                break

        return Prediction(next_day["yhat"], next_day["yhat_lower"], next_day["yhat_upper"])
