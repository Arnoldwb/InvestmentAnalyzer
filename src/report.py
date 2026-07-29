from datetime import datetime
from pathlib import Path

OUTPUT_DIR = Path(__file__).resolve().parent.parent / "output"
OUTPUT_DIR.mkdir(exist_ok=True)


def save_report(results, filename=None):

    if filename is None:
        filename = OUTPUT_DIR / "Fund_Report.txt"

    with open(filename, "w") as f:
        

        f.write("=" * 70 + "\n")
        f.write("Investment Analyzer\n")
        f.write("=" * 70 + "\n\n")

        f.write(
            "Report Generated: "
            + datetime.now().strftime("%B %d, %Y %I:%M %p")
            + "\n\n"
        )

        header = (
            f"{'Fund':<8}"
            f"{'CAGR':>10}"
            f"{'Return':>10}"
            f"{'Volatility':>12}"
            f"{'Drawdown':>12}"
        )

        f.write(header + "\n")
        f.write("-" * len(header) + "\n")

        for fund, stats in results.items():

            line = (
                f"{fund:<8}"
                f"{stats['CAGR']:>10.2%}"
                f"{stats['Return']:>10.2%}"
                f"{stats['Volatility']:>12.2%}"
                f"{stats['Drawdown']:>12.2%}"
            )

            f.write(line + "\n")
    report_file = Path(filename).resolve()
    print(f"\nReport saved to: {report_file}")