from investment_analyzer.core.paths import DATA_DIR
from investment_analyzer.core.vanguard_historical_importer import (
    import_vanguard_history,
)
from investment_analyzer.models.portfolio import Portfolio
from investment_analyzer.visualization.chart_generator import ChartGenerator

CSV_FILE = DATA_DIR / "Vanguard_Import_09-01-26.csv"


def main():
    starting_positions, events = import_vanguard_history(CSV_FILE)

    portfolio = Portfolio("Historical Chart Test")

    portfolio.historical_starting_positions = starting_positions
    portfolio.historical_events = events

    figure = ChartGenerator().historical_fund_value_chart(portfolio)

    assert len(figure.axes) == 1

    axes = figure.axes[0]

    assert len(axes.lines) == 3

    lines = {line.get_label().split(" — ", 1)[0]: line for line in axes.lines}

    assert set(lines) == {
        "VGHAX",
        "VMFXX",
        "VWENX",
    }

    assert len(lines["VGHAX"].get_xdata()) == 486
    assert len(lines["VMFXX"].get_xdata()) == 2
    assert len(lines["VWENX"].get_xdata()) == 404
    # VGHAX begins with the September 25, 2024 historical
    # starting position.
    vghax = lines["VGHAX"]

    assert str(vghax.get_xdata()[0])[:10] == "2024-09-25"

    # VWENX enters the reconstructed history through its actual
    # December 23, 2024 purchase.
    vwenx = lines["VWENX"]

    assert str(vwenx.get_xdata()[0])[:10] == "2024-12-23"

    print("Historical fund value chart regression test PASSED.")
    print()
    print(f"Fund lines: {len(lines)}")
    print(f"VGHAX points: {len(vghax.get_xdata())}")
    print(f"VWENX points: {len(vwenx.get_xdata())}")


if __name__ == "__main__":
    main()
