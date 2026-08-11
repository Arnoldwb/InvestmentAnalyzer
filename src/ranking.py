"""
ranking.py

Functions for displaying fund rankings, executive summaries,
and investment recommendations.
"""


def print_rankings(results):

    print()
    print("=" * 80)
    print("FUND RANKINGS (by CAGR)")
    print("=" * 80)

    ranking = sorted(
        results.items(),
        key=lambda item: item[1]["CAGR"],
        reverse=True,
    )

    for rank, (symbol, stats) in enumerate(ranking, start=1):
        print(f"{rank:>2}. {symbol:<8} {stats['CAGR']:.2%}")


def print_executive_summary(results):

    print()
    print("=" * 80)
    print("EXECUTIVE SUMMARY")
    print("=" * 80)

    best_return = max(
        results.items(),
        key=lambda x: x[1]["CAGR"],
    )
    lowest_vol = min(
        results.items(),
        key=lambda x: x[1]["Volatility"],
    )
    smallest_dd = max(
        results.items(),
        key=lambda x: x[1]["Drawdown"],
    )
    most_positive = max(
        results.items(),
        key=lambda x: x[1]["Positive Years"],
    )

    print(
        f"Best Long-Term Performer : "
        f"{best_return[0]} ({best_return[1]['CAGR']:.2%})"
    )

    print(
        f"Lowest Volatility        : "
        f"{lowest_vol[0]} ({lowest_vol[1]['Volatility']:.2%})"
    )

    print(
        f"Smallest Drawdown        : "
        f"{smallest_dd[0]} ({smallest_dd[1]['Drawdown']:.2%})"
    )

    print(
        f"Most Positive Years      : "
        f"{most_positive[0]} "
        f"({most_positive[1]['Positive Years']})"
    )


def print_recommendation(results):

    print()
    print("=" * 80)
    print("OVERALL RECOMMENDATION")
    print("=" * 80)

    scores = {}

    for symbol, stats in results.items():

        score = 0

        score += stats["CAGR"] * 100
        score -= stats["Volatility"] * 20
        score += stats["Drawdown"] * 10
        score += stats["Positive Years"]

        scores[symbol] = score

    winner = max(scores, key=scores.get)
    stats = results[winner]

    print(f"Recommended Fund : {winner}")
    print(f"CAGR             : {stats['CAGR']:.2%}")
    print(f"Volatility       : {stats['Volatility']:.2%}")
    print(f"Maximum Drawdown : {stats['Drawdown']:.2%}")
    print(f"Positive Years   : {stats['Positive Years']}")

    print()
    print("Reason:")

    highest_cagr = max(
        results.values(),
        key=lambda x: x["CAGR"],
    )["CAGR"]

    lowest_volatility = min(
        results.values(),
        key=lambda x: x["Volatility"],
    )["Volatility"]

    smallest_drawdown = max(
        results.values(),
        key=lambda x: x["Drawdown"],
    )["Drawdown"]

    most_positive_years = max(
        results.values(),
        key=lambda x: x["Positive Years"],
    )["Positive Years"]

    reasons = []

    if stats["CAGR"] == highest_cagr:
        reasons.append(
            "Strongest long-term growth among the funds analyzed."
        )

    if stats["Volatility"] == lowest_volatility:
        reasons.append(
            "Lowest volatility among the funds analyzed."
        )

    if stats["Drawdown"] == smallest_drawdown:
        reasons.append(
            "Smallest maximum drawdown among the funds analyzed."
        )

    if stats["Positive Years"] == most_positive_years:
        reasons.append(
            "Most positive years among the funds analyzed."
        )

    if not reasons:
        reasons.append(
            "Best overall combination of return, risk, "
            "drawdown, and consistency based on the scoring model."
        )

    for reason in reasons:
        print(f"• {reason}")
