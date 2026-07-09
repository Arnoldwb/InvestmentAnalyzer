from loader import load_fund
from returns import monthly_returns
from statistics import (
    fund_statistics,
    cagr,
    max_drawdown,
    best_year,
    worst_year,
    positive_years,
    negative_years,
)
from charts import growth_chart

FUNDS = [
    "VBIAX",
    "VWENX",
    "VGSTX",
    "VSMGX",
]

fund_returns = {}
results = {}

print()
print("Investment Analyzer")
print("=" * 60)

for symbol in FUNDS:

    df = load_fund(symbol)

    r = monthly_returns(df)

    fund_returns[symbol] = r

    stats = fund_statistics(r)

    results[symbol] = {
        "CAGR": cagr(df),
        "Return": stats["Annualized Return"],
        "Volatility": stats["Annualized Volatility"],
        "Drawdown": max_drawdown(df),
        "Best Year": best_year(df),
        "Worst Year": worst_year(df),
        "Positive Years": positive_years(df),
        "Negative Years": negative_years(df),
    }

    print(symbol)
    print("-" * 40)

    print(f"CAGR                  : {cagr(df):.2%}")
    print(f"Annualized Return     : {stats['Annualized Return']:.2%}")
    print(f"Annualized Volatility : {stats['Annualized Volatility']:.2%}")
    print(f"Maximum Drawdown      : {max_drawdown(df):.2%}")
    print(f"Best Year             : {best_year(df):.2%}")
    print(f"Worst Year            : {worst_year(df):.2%}")
    print(f"Positive Years        : {positive_years(df)}")
    print(f"Negative Years        : {negative_years(df)}")
    print()

# <-- The loop ends here

print("=" * 80)
print("FUND COMPARISON")
...
print("=" * 80)

print(
    f"{'Fund':<8}"
    f"{'CAGR':>10}"
    f"{'Return':>10}"
    f"{'Vol':>10}"
    f"{'Max DD':>10}"
    f"{'Best':>10}"
    f"{'Worst':>10}"
)

print("-" * 68)

for symbol, data in results.items():
    print(
        f"{symbol:<8}"
        f"{data['CAGR']:>10.2%}"
        f"{data['Return']:>10.2%}"
        f"{data['Volatility']:>10.2%}"
        f"{data['Drawdown']:>10.2%}"
        f"{data['Best Year']:>10.2%}"
        f"{data['Worst Year']:>10.2%}"
    )
growth_chart(fund_returns)