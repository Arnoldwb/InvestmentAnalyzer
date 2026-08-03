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
        inflation_rate: float = 0.0,
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

        if inflation_rate < 0:
            raise ValueError(
                "Inflation rate cannot be negative."
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

        values = np.full(
            simulations,
            initial_value,
            dtype=float,
        )

        for month in range(months):
            values *= 1.0 + sampled_returns[:, month]

            year_number = month // 12

            adjusted_annual_withdrawal = (
                annual_withdrawal
                * (1.0 + inflation_rate) ** year_number
            )

            monthly_withdrawal = (
                adjusted_annual_withdrawal / 12.0
            )

            if monthly_withdrawal > 0:
                values -= monthly_withdrawal
                values = np.maximum(values, 0.0)

        return values
    def withdrawal_summary(
        self,
        initial_value: float,
        annual_withdrawal: float,
        years: int,
        simulations: int = 10000,
        seed: int | None = None,
        inflation_rate: float = 0.0,
    ) -> dict:
        """
        Return summary statistics for Monte Carlo simulations
        with fixed annual withdrawals.
        """

        ending_values = self.simulate_withdrawals(
            initial_value=initial_value,
            annual_withdrawal=annual_withdrawal,
            years=years,
            simulations=simulations,
            seed=seed,
            inflation_rate=inflation_rate,
        )

        survival_probability = float(
            np.mean(ending_values > 0)
        )

        depletion_probability = float(
            np.mean(ending_values == 0)
        )

        return {
            "initial_value": initial_value,
            "annual_withdrawal": annual_withdrawal,
            "inflation_rate": inflation_rate,
            "withdrawal_rate": (
                annual_withdrawal / initial_value
            ),
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
            "mean_ending_value": float(
                np.mean(ending_values)
            ),
            "survival_probability": survival_probability,
            "depletion_probability": depletion_probability,
        }

    def sustainable_withdrawal(
        self,
        initial_value: float,
        years: int,
        target_survival_probability: float = 0.90,
        simulations: int = 10000,
        seed: int | None = None,
        inflation_rate: float = 0.0,
        tolerance: float = 1.0,
    ) -> dict:
        """
        Estimate the highest starting annual withdrawal that meets
        a requested Monte Carlo survival probability.

        The withdrawal is increased annually by the specified
        inflation rate.
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

        if inflation_rate < 0:
            raise ValueError(
                "Inflation rate cannot be negative."
            )

        if not 0 < target_survival_probability <= 1:
            raise ValueError(
                "Target survival probability must be greater than "
                "zero and no greater than one."
            )

        if tolerance <= 0:
            raise ValueError(
                "Tolerance must be greater than zero."
            )

        low = 0.0
        high = initial_value

        best_withdrawal = 0.0
        best_survival_probability = 1.0

        while high - low > tolerance:
            candidate = (low + high) / 2.0

            summary = self.withdrawal_summary(
                initial_value=initial_value,
                annual_withdrawal=candidate,
                years=years,
                simulations=simulations,
                seed=seed,
                inflation_rate=inflation_rate,
            )

            survival_probability = summary[
                "survival_probability"
            ]

            if (
                survival_probability
                >= target_survival_probability
            ):
                best_withdrawal = candidate
                best_survival_probability = (
                    survival_probability
                )
                low = candidate
            else:
                high = candidate

        return {
            "initial_value": initial_value,
            "annual_withdrawal": best_withdrawal,
            "withdrawal_rate": (
                best_withdrawal / initial_value
            ),
            "years": years,
            "simulations": simulations,
            "inflation_rate": inflation_rate,
            "target_survival_probability": (
                target_survival_probability
            ),
            "survival_probability": (
                best_survival_probability
            ),
            "tolerance": tolerance,
        }
