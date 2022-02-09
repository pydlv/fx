import datetime
from decimal import Decimal
from enum import Enum
from typing import Dict

from pandas import DataFrame

from other import PRECISION
from util import load_data


class Currency(Enum):
    USD = "USD"
    GBP = "GBP"
    CAD = "CAD"


class Market(object):
    currency: Currency
    datasource: str
    df: DataFrame
    prices = Dict[datetime.date, Decimal]

    def __init__(self, currency: Currency, datasource: str):
        self.currency = currency
        self.datasource = datasource
        self.df = load_data(self.datasource)

        self.prices = {}
        for i, row in self.df.iterrows():
            date = datetime.datetime.strptime(row["ds"], "%Y-%m-%d").date()
            self.prices[date] = Decimal(row["y"]).quantize(PRECISION)

    def get_price_by_date(self, date: datetime.date) -> Decimal:
        return self.prices[date]
