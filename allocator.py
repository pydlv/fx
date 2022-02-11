from decimal import Decimal
from typing import List, Dict

from markets import Market, Currency


class Allocator(object):
    @staticmethod
    def get_target_allocation(total_account_value: Decimal, markets: List[Market]) -> Dict[Currency, Decimal]:
        """
        Returns the target balance for each currency.
        :param total_account_value: Total tradable account value in USD.
        :param markets: List of markets to be considered in the calculation.
        :return: Dictionary of target balance of each currency including USD.
        """
        num_currencies = len(markets) + 1  # Add 1 for USD

        even_val = total_account_value / num_currencies

        target_allocations: Dict[Currency, Decimal] = {}

        for market in markets:
            upper_spread = market.prediction.upper - market.prediction.prediction
            lower_spread = market.prediction.lower - market.prediction.prediction

            difference = market.price - market.prediction.prediction

            if difference >= 0:
                # Sell (upper)
                signal = min(Decimal("1"), max(Decimal("0"), difference / upper_spread))
                target_allocation = (Decimal("1") - signal) * even_val
            else:
                # Buy (lower)
                signal = min(Decimal("0.999"), max(Decimal("0"), difference / lower_spread))
                target_allocation = even_val / (Decimal("1") - signal)

            target_allocations[market.currency] = target_allocation

        target_allocations[Currency.USD] = even_val

        # Scale the target_allocations to the funds we actually have
        total_target_allocations = sum([a for a in target_allocations.values()])

        result: Dict[Currency, Decimal] = {}

        for currency, target in target_allocations.items():
            percentage_of_whole = target / total_target_allocations

            scaled = total_account_value * percentage_of_whole

            result[currency] = scaled

        return result


# Testing scenario
# gbp = Market(Currency.GBP, "gbpmax.csv")
# chf = Market(Currency.CHF, "chfmax.csv")
#
# gbp.price = Decimal("1.4")
# chf.price = Decimal(".7")
#
# chf.prediction = Prediction(Decimal(".69"), Decimal(".64"), Decimal(".73"))
# gbp.prediction = Prediction(Decimal("1.45"), Decimal("1.38"), Decimal("1.5"))
#
# result = Allocator.get_target_allocation(Decimal("1326"), [gbp, chf])
#
# for i, v in result.items():
#     print(i, v)
