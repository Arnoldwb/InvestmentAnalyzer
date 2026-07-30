from dataclasses import dataclass

import pandas as pd

from investment_analyzer.models.portfolio import Portfolio


@dataclass
class PortfolioAnalyzer:

    portfolio: Portfolio

    def summary(self):

        print()

        print("Portfolio Analysis")

        print("-" * 40)

        self.portfolio.summary()
