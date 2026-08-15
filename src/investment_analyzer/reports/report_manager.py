from .base_report import BaseReport
from .pdf_report import PDFReport
from .text_report import TextReport
from .portfolio_excel_report import PortfolioExcelReport


class ReportManager(BaseReport):
    """
    Coordinates report creation.
    """

    def __init__(self):
        super().__init__()
        self.text = TextReport()
        self.pdf = PDFReport()
        self.portfolio_excel = PortfolioExcelReport()

    def create_portfolio_report(self, portfolio):
        return self.text.create_portfolio_report(portfolio)

    def create_portfolio_pdf_report(self, portfolio):
        return self.pdf.create_portfolio_report(portfolio)

    def create_portfolio_excel_report(self, portfolio):
        return self.portfolio_excel.create_portfolio_report(portfolio)

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
            target_survival_probability=(target_survival_probability),
            simulations=simulations,
            seed=seed,
            inflation_rate=inflation_rate,
            result=result,
        )

    def create_withdrawal_strategy_comparison_report(
        self,
        portfolio,
        initial_value,
        annual_withdrawals,
        years,
        simulations=10000,
        seed=None,
        inflation_rate=0.0,
        results=None,
    ):
        return self.text.create_withdrawal_strategy_comparison_report(
            portfolio=portfolio,
            initial_value=initial_value,
            annual_withdrawals=annual_withdrawals,
            years=years,
            simulations=simulations,
            seed=seed,
            inflation_rate=inflation_rate,
            results=results,
        )

    def create_comparison_report(self, portfolio_a, portfolio_b):
        return self.text.create_comparison_report(
            portfolio_a,
            portfolio_b,
        )
