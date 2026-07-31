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

    def create_comparison_report(self, portfolio_a, portfolio_b):
        return self.text.create_comparison_report(
            portfolio_a,
            portfolio_b,
        )
