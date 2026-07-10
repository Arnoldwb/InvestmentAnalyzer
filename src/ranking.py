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

    best_return = max(results.items(), key=lambda x: x[1]["CAGR"])
    lowest_vol = min(results.items(), key=lambda x: x[1]["Volatility"])
    smallest_dd = max(results.items(), key=lambda x: x[1]["Drawdown"])
    most_positive = max(results.items(), key=lambda x: x[1]["Positive Years"])

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
        f"{most_positive[0]} ({most_positive[1]['Positive Years']})"
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

    if winner == "VGSTX":
        print("Reason:")
        print("• Highest long-term growth.")
        print("• Suitable for investors seeking maximum appreciation.")
        print("• Accepts somewhat higher volatility for higher returns.")

    elif winner == "VWENX":
        print("Reason:")
        print("• Best balance between return and risk.")
        print("• Excellent choice for long-term retirement investing.")

    elif winner == "VBIAX":
        print("Reason:")
        print("• Lowest volatility and smallest drawdown.")
        print("• Best suited for conservative investors.")

    elif winner == "VSMGX":
        print("Reason:")
        print("• Good diversification.")
        print("• Appropriate for moderate growth investors.")