from .base_report import BaseReport
from .text_report import TextReport


class ReportManager(BaseReport):
    """
    Coordinates report creation.
    """

    def __init__(self):
        super().__init__()
        self.text = TextReport()

    def create_portfolio_report(self, portfolio):
        return self.text.create_portfolio_report(portfolio)

    def create_monte_carlo_report(
        self,
        portfolio,
        initial_value,
        years,
        simulations=10000,
        target_value=None,
        seed=None,
        summary=None,
    ):
        return self.text.create_monte_carlo_report(
            portfolio=portfolio,
            initial_value=initial_value,
            years=years,
            simulations=simulations,
            target_value=target_value,
            seed=seed,
            summary=summary,
        )
    def create_withdrawal_report(
        self,
        portfolio,
        initial_value,
        annual_withdrawal,
        years,
        simulations=10000,
        seed=None,
        summary=None,
        inflation_rate=0.0,
    ):
        return self.text.create_withdrawal_report(
            portfolio=portfolio,
            initial_value=initial_value,
            annual_withdrawal=annual_withdrawal,
            years=years,
            simulations=simulations,
            seed=seed,
            summary=summary,
            inflation_rate=inflation_rate,
        )
    def create_sustainable_withdrawal_report(
        self,
        portfolio,
        initial_value,
        years,
        target_survival_probability,
        simulations=10000,
        seed=None,
        inflation_rate=0.0,
        result=None,
    ):
        return self.text.create_sustainable_withdrawal_report(
            portfolio=portfolio,
            initial_value=initial_value,
            years=years,
            target_survival_probability=(
                target_survival_probability
            ),
            simulations=simulations,
            seed=seed,
            inflation_rate=inflation_rate,
            result=result,
        )

    def create_comparison_report(self, portfolio_a, portfolio_b):
        return self.text.create_comparison_report(
            portfolio_a,
            portfolio_b,
        )
