from investment_analyzer.core.historical_security_mapping import (
    historical_security_to_symbol,
)


def main():
    assert (
        historical_security_to_symbol("Vanguard Wellington Admiral")
        == "VWENX"
    )

    assert (
        historical_security_to_symbol("Vanguard Health Care-Admiral")
        == "VGHAX"
    )

    # The Federal Money Market currently has no local historical
    # price file, so it must remain unmapped.
    assert (
        historical_security_to_symbol(
            "Vanguard Federal Money Market Fund"
        )
        is None
    )

    # Unknown securities must never be guessed.
    assert historical_security_to_symbol("Unknown Security") is None

    # Blank input must return None.
    assert historical_security_to_symbol("") is None
    assert historical_security_to_symbol("   ") is None

    print("Historical security mapping regression test PASSED.")


if __name__ == "__main__":
    main()
