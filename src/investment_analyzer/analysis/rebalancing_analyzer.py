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
