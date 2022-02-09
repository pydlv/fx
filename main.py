import decimal
from decimal import Decimal
from datetime import date

from markets import Market, Currency
from simulation import simulate_period, Exchange

decimal.getcontext().prec = 8

if __name__ == "__main__":
    # Run a simulation
    print("Running simulation")

    markets = [
        Market(Currency.GBP, "gbpmax.csv"),
        Market(Currency.CAD, "cadmax.csv")
    ]

    start_date = date(2004, 1, 1)
    end_date = date(2021, 12, 31)

    exchange = Exchange(markets)

    for market in markets:
        exchange.update_price(market, market.get_price_by_date(start_date))

    exchange.set_balance(Currency.USD, Decimal(1000))

    simulate_period(start_date, end_date, markets, exchange)
    print("Finished")
