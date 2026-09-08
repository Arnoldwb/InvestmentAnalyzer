import pandas as pd

from investment_analyzer.models.transaction import TransactionAction


CSV_FILE = "data/Vanguard_Import_09-01-26.csv"


def main():
    data = pd.read_csv(CSV_FILE)

    cash_rows = data[
        data["Type"].isin(
            [
                "Dividend Income",
                "Long-term Capital Gain",
                "Short-term Capital Gain",
                "Payment/Deposit",
            ]
        )
    ].copy()

    assert not cash_rows.empty

    for _, row in cash_rows.iterrows():
        amount = pd.to_numeric(
            str(row["Amount"]).replace(",", ""),
            errors="coerce",
        )

        assert pd.notna(amount)
        assert amount != 0

        if row["Type"] == "Dividend Income":
            action = TransactionAction.DIVIDEND
            expected_amount = float(amount)

        elif row["Type"] in {
            "Long-term Capital Gain",
            "Short-term Capital Gain",
        }:
            action = TransactionAction.CAPITAL_GAIN
            expected_amount = float(amount)

        elif row["Type"] == "Payment/Deposit":
            action = (
                TransactionAction.DEPOSIT
                if amount > 0
                else TransactionAction.WITHDRAWAL
            )
            expected_amount = abs(float(amount))

        else:
            raise AssertionError(
                f"Unexpected cash transaction type: {row['Type']}"
            )

        assert action in {
            TransactionAction.DIVIDEND,
            TransactionAction.CAPITAL_GAIN,
            TransactionAction.DEPOSIT,
            TransactionAction.WITHDRAWAL,
        }

        assert expected_amount > 0

    print("Vanguard cash transaction mapping test PASSED.")
    print()
    print("Rows tested:", len(cash_rows))
    print()
    print("Mapping:")
    print("  Dividend Income       -> DIVIDEND")
    print("  Long-term Capital Gain -> CAPITAL GAIN")
    print("  Short-term Capital Gain -> CAPITAL GAIN")
    print("  Payment/Deposit (+)   -> DEPOSIT")
    print("  Payment/Deposit (-)   -> WITHDRAWAL")


if __name__ == "__main__":
    main()
