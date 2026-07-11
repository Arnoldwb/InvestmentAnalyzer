from investment_analyzer.models.fund import Fund
from investment_analyzer.analysis.cycle_analyzer import MarketCycleAnalyzer


def main():

    fund = Fund("VBIAX")
    fund.load_data()

    print(fund)

    print()
    print("Current Price :", fund.current_price)
    print("First Price   :", fund.first_price)
    print("Rows          :", len(fund))
    print("First Date    :", fund.first_date.date())
    print("Last Date     :", fund.last_date.date())

    analyzer = MarketCycleAnalyzer(fund)

    peaks, valleys = analyzer.detect_turning_points()

    print()
    print("First Five Peaks")
    print("----------------")
    print(peaks[["Date", "Adj Close"]].head())

    print()
    print("First Five Valleys")
    print("------------------")
    print(valleys[["Date", "Adj Close"]].head())