from pathlib import Path

import matplotlib.pyplot as plt


# Project folder
PROJECT = Path(__file__).resolve().parent.parent

# Output folder
OUTPUT = PROJECT / "output"
OUTPUT.mkdir(exist_ok=True)


def growth_chart(funds):
    """
    Plot the growth of a $10,000 investment for each fund.
    """

    plt.figure(figsize=(12, 7))

    for name, monthly_returns in funds.items():

        growth = 10000 * (1 + monthly_returns).cumprod()

        plt.plot(
            growth.index,
            growth,
            linewidth=2,
            label=name,
        )

    plt.title("Growth of $10,000")
    plt.xlabel("Date")
    plt.ylabel("Portfolio Value ($)")
    plt.grid(True)
    plt.legend()

    plt.tight_layout()

    # Save chart
    filename = OUTPUT / "Growth_of_10000.png"
    plt.savefig(filename, dpi=300)

    print(f"\nChart saved to: {filename}")

    # Display chart
    plt.show()