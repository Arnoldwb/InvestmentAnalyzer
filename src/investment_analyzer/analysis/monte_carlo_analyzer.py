from dataclasses import dataclass

import numpy as np

from investment_analyzer.analysis.portfolio_analyzer import PortfolioAnalyzer
from investment_analyzer.models.portfolio import Portfolio


@dataclass
class MonteCarloAnalyzer:
    """
    Simulate possible future portfolio values using historical
    monthly portfolio returns.
    """

    portfolio: Portfolio

    def simulate(
        self,
        initial_value: float,
        years: int,
        simulations: int = 10000,
        seed: int | None = None,
    ) -> np.ndarray:
        """
        Return ending portfolio values from Monte Carlo simulations.

        Future monthly returns are sampled with replacement from the
        portfolio's historical monthly returns.
        """

        if initial_value <= 0:
            raise ValueError(
                "Initial portfolio value must be greater than zero."
            )

        if years <= 0:
            raise ValueError(
                "Projection years must be greater than zero."
            )

        if simulations <= 0:
            raise ValueError(
                "Number of simulations must be greater than zero."
            )

        analyzer = PortfolioAnalyzer(self.portfolio)
        historical_returns = analyzer.monthly_returns().to_numpy()

        if historical_returns.size == 0:
            raise ValueError(
                "No historical portfolio returns are available."
            )

        months = years * 12

        rng = np.random.default_rng(seed)

        sampled_returns = rng.choice(
            historical_returns,
            size=(simulations, months),
            replace=True,
        )

        growth = np.prod(
            1.0 + sampled_returns,
            axis=1,
        )

        return initial_value * growth

    def summary(
        self,
        initial_value: float,
        years: int,
        simulations: int = 10000,
        seed: int | None = None,
    ) -> dict:
        """
        Return summary statistics for simulated ending values.
        """

        ending_values = self.simulate(
            initial_value=initial_value,
            years=years,
            simulations=simulations,
            seed=seed,
        )

        return {
            "initial_value": initial_value,
            "years": years,
            "simulations": simulations,
            "percentile_10": float(
                np.percentile(ending_values, 10)
            ),
            "percentile_25": float(
                np.percentile(ending_values, 25)
            ),
            "median": float(
                np.percentile(ending_values, 50)
            ),
            "percentile_75": float(
                np.percentile(ending_values, 75)
            ),
            "percentile_90": float(
                np.percentile(ending_values, 90)
            ),
            "probability_above_start": float(
                np.mean(ending_values > initial_value)
            ),
            "mean_ending_value": float(
                np.mean(ending_values)
            ),
        }
