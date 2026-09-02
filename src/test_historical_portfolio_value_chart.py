from investment_analyzer.models.portfolio import Portfolio

from investment_analyzer.core.vanguard_historical_importer import (
    import_vanguard_history,
)

from investment_analyzer.visualization.chart_generator import (
    ChartGenerator,
)


CSV_FILE = "data/Vanguard_Import_09-01-26.csv"


def main():
    starting_positions, events = import_vanguard_history(CSV_FILE)

    # Exclude the known Vanguard bookkeeping reconciliation pair
    # from this historical reconstruction test.
    events = [
        event
        for event in events
        if not (
            event.date.isoformat() == "2026-04-20"
            and event.event_type in {"ADD", "REMOVE"}
        )
    ]

    portfolio = Portfolio(name="Vanguard Historical Test")

    portfolio.historical_starting_positions.extend(
        starting_positions
    )

    portfolio.historical_events.extend(events)

    figure = ChartGenerator().historical_portfolio_value_chart(
        portfolio
    )

    assert len(figure.axes) == 1

    axes = figure.axes[0]

    assert len(axes.lines) == 1

    line = axes.lines[0]

    assert len(line.get_xdata()) == 474
    assert len(line.get_ydata()) == 474

    assert abs(
        line.get_ydata()[0] - 120798.66840
    ) < 0.01

    assert abs(
        line.get_ydata()[-1] - 0.0
    ) < 0.01

    print("Historical portfolio value chart regression test PASSED.")
    print()
    print("Points:", len(line.get_ydata()))
    print("First value:", line.get_ydata()[0])
    print("Last value:", line.get_ydata()[-1])


if __name__ == "__main__":
    main()
