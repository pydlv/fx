import datetime
import decimal
import logging
from datetime import date
from decimal import Decimal

from markets import Market, Currency
from other import PRECISION
from simulation import Strategy, Exchange

decimal.getcontext().prec = 8

logging.basicConfig(filename='runlog.log', encoding='utf-8', level=logging.INFO)

if __name__ == "__main__":
    markets = [
        Market(Currency.GBP, "gbpmax.csv"),
        Market(Currency.CAD, "cadmax.csv"),
        Market(Currency.CHF, "chfmax.csv"),
        Market(Currency.EUR, "eurmax.csv"),
        Market(Currency.AUD, "audmax.csv"),
        # Market(Currency.JPY, "jpymax.csv"),
        Market(Currency.NZD, "nzdmax.csv")
    ]

    start_date = date(2004, 1, 1)
    end_date = date(2022, 2, 8)

    exchange = Exchange(markets)

    for market in markets:
        try:
            market.price = market.get_price_by_date(start_date)
        except KeyError:
            # The market does not have data for the start date, just choose the first price
            market.price = Decimal(market.df.iloc[0]["y"]).quantize(PRECISION)

    exchange.set_balance(Currency.USD, Decimal(1000))

    strategy = Strategy(markets, exchange)

    # Run a simulation
    print("Running simulation")
    strategy.simulate_period(start_date, end_date)

    # For non-simulation
    # current_date = datetime.date.today() - datetime.timedelta(days=2)
    #
    # for market in markets:
    #     market.price = market.get_price_by_date(current_date)
    #
    # orders = strategy.get_orders_for_date(markets, current_date)
    # for order in orders:
    #     print(order)

    print("Finished")
