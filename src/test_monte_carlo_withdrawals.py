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

print()
print("MONTE CARLO WITHDRAWAL SUSTAINABILITY TEST")
print("=" * 60)

sustainability = analyzer.withdrawal_summary(
    initial_value=500000.0,
    annual_withdrawal=25000.0,
    years=10,
    simulations=10000,
    seed=42,
)

assert sustainability["initial_value"] == 500000.0
assert sustainability["annual_withdrawal"] == 25000.0
assert sustainability["years"] == 10
assert sustainability["simulations"] == 10000

assert np.isclose(
    sustainability["withdrawal_rate"],
    0.05,
)

assert (
    0.0
    <= sustainability["survival_probability"]
    <= 1.0
)

assert (
    0.0
    <= sustainability["depletion_probability"]
    <= 1.0
)

assert np.isclose(
    sustainability["survival_probability"]
    + sustainability["depletion_probability"],
    1.0,
)

assert (
    sustainability["percentile_10"]
    <= sustainability["percentile_25"]
    <= sustainability["median"]
    <= sustainability["percentile_75"]
    <= sustainability["percentile_90"]
)

print("Summary input verification passed.")
print("Withdrawal-rate calculation passed.")
print("Survival probability range passed.")
print("Depletion probability range passed.")
print("Probability reconciliation passed.")
print("Percentile ordering passed.")

print()
print("WITHDRAWAL SUSTAINABILITY SUMMARY")
print("-" * 60)

print(
    f"Starting Value        : "
    f"${sustainability['initial_value']:,.2f}"
)
print(
    f"Annual Withdrawal     : "
    f"${sustainability['annual_withdrawal']:,.2f}"
)
print(
    f"Initial Withdrawal Rate: "
    f"{sustainability['withdrawal_rate']:.2%}"
)
print(
    f"Projection Period     : "
    f"{sustainability['years']} years"
)
print(
    f"Simulations           : "
    f"{sustainability['simulations']:,}"
)

print()
print(
    f"Survival Probability  : "
    f"{sustainability['survival_probability']:.2%}"
)
print(
    f"Depletion Probability : "
    f"{sustainability['depletion_probability']:.2%}"
)

print()
print("Projected Ending Values")
print("-" * 60)

print(
    f"10th Percentile       : "
    f"${sustainability['percentile_10']:,.2f}"
)
print(
    f"25th Percentile       : "
    f"${sustainability['percentile_25']:,.2f}"
)
print(
    f"Median                : "
    f"${sustainability['median']:,.2f}"
)
print(
    f"75th Percentile       : "
    f"${sustainability['percentile_75']:,.2f}"
)
print(
    f"90th Percentile       : "
    f"${sustainability['percentile_90']:,.2f}"
)

print()
print("All withdrawal sustainability tests passed.")
