import numpy as np

from investment_analyzer.analysis.monte_carlo_analyzer import (
    MonteCarloAnalyzer,
)
from investment_analyzer.models.portfolio import Portfolio


print()
print("MONTE CARLO WITHDRAWAL TEST")
print("=" * 60)

portfolio = Portfolio("Withdrawal Test")

portfolio.add_fund("VBIAX", 50.0)
portfolio.add_fund("VWENX", 50.0)

portfolio.validate()

analyzer = MonteCarloAnalyzer(portfolio)

ending_values = analyzer.simulate_withdrawals(
    initial_value=500000.0,
    annual_withdrawal=25000.0,
    years=10,
    simulations=10000,
    seed=42,
)

assert len(ending_values) == 10000
assert np.all(np.isfinite(ending_values))
assert np.all(ending_values >= 0)

print("Simulation count verification passed.")
print("Finite ending-value verification passed.")
print("Non-negative ending-value verification passed.")

repeat_values = analyzer.simulate_withdrawals(
    initial_value=500000.0,
    annual_withdrawal=25000.0,
    years=10,
    simulations=10000,
    seed=42,
)

assert np.array_equal(
    ending_values,
    repeat_values,
)

print("Fixed-seed reproducibility passed.")

no_withdrawal_values = analyzer.simulate_withdrawals(
    initial_value=500000.0,
    annual_withdrawal=0.0,
    years=10,
    simulations=10000,
    seed=42,
)

standard_values = analyzer.simulate(
    initial_value=500000.0,
    years=10,
    simulations=10000,
    seed=42,
)

assert np.allclose(
    no_withdrawal_values,
    standard_values,
)

print("Zero-withdrawal equivalence passed.")

for invalid_value in (0, -1000):
    try:
        analyzer.simulate_withdrawals(
            initial_value=invalid_value,
            annual_withdrawal=25000.0,
            years=10,
        )
    except ValueError:
        pass
    else:
        raise AssertionError(
            "Invalid initial value should raise ValueError."
        )

print("Invalid initial-value protection passed.")

try:
    analyzer.simulate_withdrawals(
        initial_value=500000.0,
        annual_withdrawal=-1.0,
        years=10,
    )
except ValueError:
    print("Invalid withdrawal protection passed.")
else:
    raise AssertionError(
        "Negative withdrawal should raise ValueError."
    )

try:
    analyzer.simulate_withdrawals(
        initial_value=500000.0,
        annual_withdrawal=25000.0,
        years=0,
    )
except ValueError:
    print("Invalid projection-period protection passed.")
else:
    raise AssertionError(
        "Zero projection period should raise ValueError."
    )

print()
print("All Monte Carlo withdrawal tests passed.")
