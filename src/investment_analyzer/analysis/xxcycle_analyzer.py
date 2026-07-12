"""
Market Cycle Analyzer
Version 2.1

Threshold-based market cycle detection.
"""

from investment_analyzer.models.market_cycle import MarketCycle


class MarketCycleAnalyzer:
    """
    Detects major bull and bear market cycles using a configurable
    percentage reversal threshold.
    """

def __init__(self, fund, threshold=0.10, min_days=30):
    """
    Parameters
    ----------
    threshold : float
        Minimum percentage reversal required.

    min_days : int
        Minimum duration of a market cycle.
    """
    self.fund = fund
    self.threshold = threshold
    self.min_days = min_days
    def detect_major_cycles(self):
        prices = self.fund.data

        if prices.empty:
            return []

        cycles = []

        state = "Bull"

        cycle_start_date = prices.iloc[0]["Date"]
        cycle_start_price = prices.iloc[0]["Adj Close"]

        extreme_date = cycle_start_date
        extreme_price = cycle_start_price

        for _, row in prices.iloc[1:].iterrows():

            date = row["Date"]
            price = row["Adj Close"]

            if state == "Bull":

                if price >= extreme_price:
                    extreme_price = price
                    extreme_date = date
                    continue

                decline = (extreme_price - price) / extreme_price

                if decline >= self.threshold:

                    cycles.append(
                        MarketCycle(
                            cycle_type="Bull",
                            start_date=cycle_start_date,
                            end_date=extreme_date,
                            start_price=cycle_start_price,
                            end_price=extreme_price,
                        )
                    )

                    state = "Bear"
                    cycle_start_date = extreme_date
                    cycle_start_price = extreme_price
                    extreme_date = date
                    extreme_price = price

            else:

                if price <= extreme_price:
                    extreme_price = price
                    extreme_date = date
                    continue

                recovery = (price - extreme_price) / extreme_price

                if recovery >= self.threshold:

                    cycles.append(
                        MarketCycle(
                            cycle_type="Bear",
                            start_date=cycle_start_date,
                            end_date=extreme_date,
                            start_price=cycle_start_price,
                            end_price=extreme_price,
                        )
                    )

                    state = "Bull"
                    cycle_start_date = extreme_date
                    cycle_start_price = extreme_price
                    extreme_date = date
                    extreme_price = price

        final_price = prices.iloc[-1]["Adj Close"]
        final_date = prices.iloc[-1]["Date"]

cycle = MarketCycle(
    cycle_type="Bull",
    start_date=cycle_start_date,
    end_date=extreme_date,
    start_price=cycle_start_price,
    end_price=extreme_price,
)

if cycle.days >= self.min_days:
    cycles.append(cycle)
         return cycles

    # Backward compatibility
    def build_cycles(self):
        return self.detect_major_cycles()
