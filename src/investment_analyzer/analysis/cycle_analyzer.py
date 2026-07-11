"""
Market Cycle Analyzer
Version 2.0
"""

import pandas as pd


class MarketCycleAnalyzer:

    def __init__(self, fund):
        self.fund = fund

    def detect_turning_points(self):

        prices = self.fund.data.copy()

        prices["Prev"] = prices["Adj Close"].shift(1)
        prices["Next"] = prices["Adj Close"].shift(-1)

        peaks = prices[
            (prices["Adj Close"] > prices["Prev"]) &
            (prices["Adj Close"] > prices["Next"])
        ].copy()

        valleys = prices[
            (prices["Adj Close"] < prices["Prev"]) &
            (prices["Adj Close"] < prices["Next"])
        ].copy()

        return peaks, valleys