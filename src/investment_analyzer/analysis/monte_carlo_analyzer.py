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
        target_value: float | None = None,
    ) -> dict:
        """
        Return summary statistics for simulated ending values.
        """

        if target_value is not None and target_value <= 0:
            raise ValueError(
                "Target portfolio value must be greater than zero."
            )

        ending_values = self.simulate(
            initial_value=initial_value,
            years=years,
            simulations=simulations,
            seed=seed,
        )

        results = {
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

        if target_value is not None:
            results["target_value"] = target_value
            results["probability_above_target"] = float(
                np.mean(ending_values >= target_value)
            )

        return results
    def simulate_withdrawals(
        self,
        initial_value: float,
        annual_withdrawal: float,
        years: int,
        simulations: int = 10000,
        seed: int | None = None,
    ) -> np.ndarray:
        """
        Return ending portfolio values from Monte Carlo simulations
        with fixed monthly withdrawals.

        The annual withdrawal is divided into 12 equal monthly
        withdrawals. Portfolio values cannot fall below zero.
        """

        if initial_value <= 0:
            raise ValueError(
                "Initial portfolio value must be greater than zero."
            )

        if annual_withdrawal < 0:
            raise ValueError(
                "Annual withdrawal cannot be negative."
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
        monthly_withdrawal = annual_withdrawal / 12.0

        rng = np.random.default_rng(seed)

        sampled_returns = rng.choice(
            historical_returns,
            size=(simulations, months),
            replace=True,
        )

        values = np.full(
            simulations,
            initial_value,
            dtype=float,
        )

        for month in range(months):
            values *= 1.0 + sampled_returns[:, month]

            if monthly_withdrawal > 0:
                values -= monthly_withdrawal
                values = np.maximum(values, 0.0)

        return values
