from investment_analyzer.models.fund import Fund


def main():

    fund = Fund("VBIAX")

    fund.load_data()

    print()

    print(fund)

    print()

    print("Current Price :", fund.current_price)

    print("First Price   :", fund.first_price)

    print("Rows          :", len(fund))

    print("First Date    :", fund.first_date.date())

    print("Last Date     :", fund.last_date.date())
    print()
print("Performance")
print("-------------------------")

print(f"CAGR : {fund.cagr():.2%}")

print()
print("Yearly Returns")
print("-------------------------")
print(fund.yearly_returns().tail())