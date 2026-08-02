from dataclasses import dataclass

from investment_analyzer.models.portfolio import Portfolio


@dataclass
class RebalancingAnalyzer:
    """
    Calculates allocation changes between a current portfolio
    and a proposed portfolio.
    """

    current: Portfolio
    proposed: Portfolio

    def allocation_changes(self) -> list[dict]:
        """
        Return current, proposed, and required allocation changes
        for every fund appearing in either portfolio.
        """
        current_allocations = {
            holding.fund.symbol: holding.allocation
            for holding in self.current.holdings
        }

        proposed_allocations = {
            holding.fund.symbol: holding.allocation
            for holding in self.proposed.holdings
        }

        symbols = sorted(
            set(current_allocations) | set(proposed_allocations)
        )

        changes = []

        for symbol in symbols:
            current = current_allocations.get(symbol, 0.0)
            proposed = proposed_allocations.get(symbol, 0.0)

            changes.append(
                {
                    "symbol": symbol,
                    "current": current,
                    "proposed": proposed,
                    "change": proposed - current,
                }
            )


        return changes

    def dollar_changes(self, portfolio_value: float) -> list[dict]:
        """
        Return the dollar changes required to move from the
        current allocation to the proposed allocation.
        """
        if portfolio_value <= 0:
            raise ValueError(
                "Portfolio value must be greater than zero."
            )

        results = []

        for item in self.allocation_changes():
            current_value = (
                portfolio_value * item["current"] / 100.0
            )
            proposed_value = (
                portfolio_value * item["proposed"] / 100.0
            )
            dollar_change = proposed_value - current_value

            results.append(
                {
                    **item,
                    "current_value": current_value,
                    "proposed_value": proposed_value,
                    "dollar_change": dollar_change,
                }
            )

        return results
