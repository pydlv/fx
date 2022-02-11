import datetime
from decimal import Decimal
from enum import Enum
from typing import Dict, TYPE_CHECKING

from pandas import DataFrame

from other import PRECISION
from util import load_data

if TYPE_CHECKING:
    from predictor import Prediction


class Currency(Enum):
    NZD = "NZD"
    JPY = "JPY"
    USD = "USD"
    GBP = "GBP"
    CAD = "CAD"
    CHF = "CHF"
    EUR = "EUR"
    AUD = "AUD"


class Market(object):
    currency: Currency
    datasource: str
    df: DataFrame
    prices: Dict[datetime.date, Decimal]
    price: Decimal
    prediction: "Prediction"

    def __init__(self, currency: Currency, datasource: str):
        self.currency = currency
        self.datasource = datasource
        self.df = load_data("datasource/" + self.datasource)

        self.prices = {}
        for i, row in self.df.iterrows():
            date = datetime.datetime.strptime(row["ds"], "%Y-%m-%d").date()
            self.prices[date] = Decimal(row["y"]).quantize(PRECISION)

    def get_price_by_date(self, date: datetime.date) -> Decimal:
        return self.prices[date]
