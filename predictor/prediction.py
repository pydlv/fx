from decimal import Decimal


class Prediction(object):
    prediction: Decimal
    lower: Decimal
    upper: Decimal

    def __init__(self, prediction: Decimal, low: Decimal, high: Decimal):
        self.prediction = prediction
        self.lower = low
        self.upper = high

    def __str__(self):
        return f"Prediction: {self.prediction}, Upper: {self.upper}, Lower: {self.lower}"