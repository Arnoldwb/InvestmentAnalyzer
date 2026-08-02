import numpy as np

from investment_analyzer.analysis.monte_carlo_analyzer import (
    MonteCarloAnalyzer,
)
from investment_analyzer.models.portfolio import Portfolio


print()
print("MONTE CARLO ANALYZER TEST")
print("=" * 60)

portfolio = Portfolio("Monte Carlo Test")

portfolio.add_fund("VBIAX", 50.0)
portfolio.add_fund("VWENX", 50.0)

portfolio.validate()

analyzer = MonteCarloAnalyzer(portfolio)

ending_values = analyzer.simulate(
    initial_value=500000.0,
    years=10,
    simulations=10000,
    seed=42,
)

assert len(ending_values) == 10000
assert np.all(np.isfinite(ending_values))
assert np.all(ending_values > 0)

print("Simulation count verification passed.")
print("Finite ending-value verification passed.")
print("Positive ending-value verification passed.")

repeat_values = analyzer.simulate(
    initial_value=500000.0,
    years=10,
    simulations=10000,
    seed=42,
)

assert np.array_equal(
    ending_values,
    repeat_values,
)

print("Fixed-seed reproducibility passed.")

summary = analyzer.summary(
    initial_value=500000.0,
    years=10,
    simulations=10000,
    seed=42,
)

assert (
    summary["percentile_10"]
    <= summary["percentile_25"]
    <= summary["median"]
    <= summary["percentile_75"]
    <= summary["percentile_90"]
)

assert 0.0 <= summary["probability_above_start"] <= 1.0

print("Percentile ordering passed.")
print("Probability range verification passed.")

for invalid_value in (0, -1000):
    try:
        analyzer.simulate(
            initial_value=invalid_value,
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
    analyzer.simulate(
        initial_value=500000.0,
        years=0,
    )
except ValueError:
    print("Invalid projection-period protection passed.")
else:
    raise AssertionError(
        "Zero projection period should raise ValueError."
    )

try:
    analyzer.simulate(
        initial_value=500000.0,
        years=10,
        simulations=0,
    )
except ValueError:
    print("Invalid simulation-count protection passed.")
else:
    raise AssertionError(
        "Zero simulations should raise ValueError."
    )

print()
print("MONTE CARLO SUMMARY")
print("-" * 60)

print(f"Starting Value       : ${summary['initial_value']:,.2f}")
print(f"Projection Period    : {summary['years']} years")
print(f"Simulations          : {summary['simulations']:,}")

print()
print("Projected Ending Values")
print("-" * 60)

print(
    f"10th Percentile      : "
    f"${summary['percentile_10']:,.2f}"
)
print(
    f"25th Percentile      : "
    f"${summary['percentile_25']:,.2f}"
)
print(
    f"Median               : "
    f"${summary['median']:,.2f}"
)
print(
    f"75th Percentile      : "
    f"${summary['percentile_75']:,.2f}"
)
print(
    f"90th Percentile      : "
    f"${summary['percentile_90']:,.2f}"
)

print()
print(
    "Probability Above Start: "
    f"{summary['probability_above_start']:.2%}"
)

print(
    f"Mean Ending Value       : "
    f"${summary['mean_ending_value']:,.2f}"
)

print()
print("All Monte Carlo analyzer tests passed.")
