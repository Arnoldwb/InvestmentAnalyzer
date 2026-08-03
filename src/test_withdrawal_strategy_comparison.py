from investment_analyzer.analysis.monte_carlo_analyzer import (
    MonteCarloAnalyzer,
)
from investment_analyzer.core.portfolio_storage import load_portfolio


print()
print("WITHDRAWAL STRATEGY COMPARISON TEST")
print("=" * 60)

portfolio = load_portfolio("Version_4_Test.json")
analyzer = MonteCarloAnalyzer(portfolio)

withdrawals = [
    20000.0,
    25000.0,
    30000.0,
    35000.0,
]

results = analyzer.compare_withdrawal_strategies(
    initial_value=500000.0,
    annual_withdrawals=withdrawals,
    years=20,
    simulations=10000,
    seed=42,
    inflation_rate=0.03,
)

assert len(results) == 4

print("Strategy-count verification passed.")

for result, withdrawal in zip(results, withdrawals):
    assert result["annual_withdrawal"] == withdrawal
    assert result["initial_value"] == 500000.0
    assert result["years"] == 20
    assert result["simulations"] == 10000
    assert result["inflation_rate"] == 0.03

    expected_rate = withdrawal / 500000.0

    assert abs(
        result["withdrawal_rate"] - expected_rate
    ) < 1e-12

    assert 0.0 <= result["survival_probability"] <= 1.0
    assert 0.0 <= result["depletion_probability"] <= 1.0

    assert abs(
        result["survival_probability"]
        + result["depletion_probability"]
        - 1.0
    ) < 1e-12

print("Strategy-result verification passed.")

survival_rates = [
    result["survival_probability"]
    for result in results
]

for earlier, later in zip(
    survival_rates,
    survival_rates[1:],
):
    assert earlier >= later

print("Survival ordering verification passed.")

median_values = [
    result["median"]
    for result in results
]

for earlier, later in zip(
    median_values,
    median_values[1:],
):
    assert earlier >= later

print("Median-ending-value ordering passed.")

try:
    analyzer.compare_withdrawal_strategies(
        initial_value=500000.0,
        annual_withdrawals=[],
        years=20,
    )
except ValueError:
    print("Empty-strategy protection passed.")
else:
    raise AssertionError(
        "Empty withdrawal list should raise ValueError."
    )

try:
    analyzer.compare_withdrawal_strategies(
        initial_value=500000.0,
        annual_withdrawals=[
            20000.0,
            -25000.0,
        ],
        years=20,
    )
except ValueError:
    print("Invalid-withdrawal protection passed.")
else:
    raise AssertionError(
        "Negative withdrawal should raise ValueError."
    )

print()
print("WITHDRAWAL STRATEGY COMPARISON")
print("-" * 78)

print(
    f"{'Withdrawal':>12} "
    f"{'Rate':>8} "
    f"{'Survival':>10} "
    f"{'Depletion':>10} "
    f"{'Median Ending':>16}"
)

print("-" * 78)

for result in results:
    print(
        f"${result['annual_withdrawal']:>11,.2f} "
        f"{result['withdrawal_rate']:>7.2%} "
        f"{result['survival_probability']:>9.2%} "
        f"{result['depletion_probability']:>9.2%} "
        f"${result['median']:>15,.2f}"
    )

print()
print("All withdrawal strategy comparison tests passed.")
