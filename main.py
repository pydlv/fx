import decimal
from decimal import Decimal
from datetime import date

from markets import Market, Currency
from other import PRECISION
from simulation import simulate_period, Exchange

decimal.getcontext().prec = 8

if __name__ == "__main__":
    # Run a simulation
    print("Running simulation")

    markets = [
        Market(Currency.GBP, "gbpmax.csv"),
        Market(Currency.CAD, "cadmax.csv"),
        Market(Currency.CHF, "chfmax.csv"),
        Market(Currency.EUR, "eurmax.csv"),
        Market(Currency.AUD, "audmax.csv")
    ]

    start_date = date(2004, 1, 1)
    end_date = date(2022, 2, 8)

    exchange = Exchange(markets)

    for market in markets:
        try:
            exchange.update_price(market, market.get_price_by_date(start_date))
        except KeyError:
            # The market does not have data for the start date, just choose the first price
            exchange.update_price(market, Decimal(market.df.iloc[0]["y"]).quantize(PRECISION))

    exchange.set_balance(Currency.USD, Decimal(1000))

    simulate_period(start_date, end_date, markets, exchange)
    print("Finished")
