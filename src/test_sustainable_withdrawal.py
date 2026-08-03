from investment_analyzer.analysis.monte_carlo_analyzer import (
    MonteCarloAnalyzer,
)
from investment_analyzer.models.portfolio import Portfolio


print()
print("SUSTAINABLE WITHDRAWAL CALCULATOR TEST")
print("=" * 60)

portfolio = Portfolio("Sustainable Withdrawal Test")

portfolio.add_fund("VBIAX", 50.0)
portfolio.add_fund("VWENX", 50.0)

portfolio.validate()

analyzer = MonteCarloAnalyzer(portfolio)

result = analyzer.sustainable_withdrawal(
    initial_value=500000.0,
    years=20,
    target_survival_probability=0.90,
    simulations=10000,
    seed=42,
    inflation_rate=0.03,
)

assert result["annual_withdrawal"] > 0

print("Positive sustainable-withdrawal verification passed.")

assert (
    result["survival_probability"]
    >= result["target_survival_probability"]
)

print("Target survival probability verification passed.")

assert result["target_survival_probability"] == 0.90
assert result["inflation_rate"] == 0.03
assert result["years"] == 20
assert result["simulations"] == 10000

print("Calculator input storage verification passed.")

expected_rate = (
    result["annual_withdrawal"] / result["initial_value"]
)

assert abs(
    result["withdrawal_rate"] - expected_rate
) < 1e-12

print("Withdrawal-rate calculation passed.")

print()
print("SUSTAINABLE WITHDRAWAL RESULT")
print("-" * 60)

print(
    f"Starting Value         : "
    f"${result['initial_value']:,.2f}"
)
print(
    f"Projection Period      : "
    f"{result['years']} years"
)
print(
    f"Inflation Rate         : "
    f"{result['inflation_rate']:.2%}"
)
print(
    f"Target Survival        : "
    f"{result['target_survival_probability']:.2%}"
)
print(
    f"Sustainable Withdrawal : "
    f"${result['annual_withdrawal']:,.2f}"
)
print(
    f"Initial Withdrawal Rate: "
    f"{result['withdrawal_rate']:.2%}"
)
print(
    f"Actual Survival        : "
    f"{result['survival_probability']:.2%}"
)

for invalid_target in (0.0, -0.10, 1.01):
    try:
        analyzer.sustainable_withdrawal(
            initial_value=500000.0,
            years=20,
            target_survival_probability=invalid_target,
            simulations=1000,
            seed=42,
            inflation_rate=0.03,
        )
    except ValueError:
        pass
    else:
        raise AssertionError(
            "Invalid survival target should raise ValueError."
        )

print()
print("Invalid survival-target protection passed.")

print()
print("All sustainable withdrawal calculator tests passed.")
