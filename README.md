# Investment Analyzer

A Python application for analyzing and comparing the historical performance of mutual funds.

The program loads historical price data from CSV files and calculates a variety of investment performance statistics, including growth, returns, volatility, and drawdowns. It also generates charts to visualize long-term investment performance.

---

## Features

- Import historical mutual fund data from CSV files
- Calculate:
  - Compound Annual Growth Rate (CAGR)
  - Annualized Return
  - Annualized Volatility
  - Maximum Drawdown
  - Best Year
  - Worst Year
  - Positive vs. Negative Years
- Compare multiple funds side-by-side
- Generate growth charts beginning with a hypothetical $10,000 investment

---

## Current Funds Included

- VBIAX
- VWENX
- VGSTX
- VSMGX

Additional funds can easily be added by placing their CSV files in the `data` folder.

---

## Project Structure

```
InvestmentAnalyzer/
│
├── data/
│   ├── VBIAX.csv
│   ├── VGSTX.csv
│   ├── VSMGX.csv
│   └── VWENX.csv
│
├── src/
│   ├── main.py
│   ├── loader.py
│   ├── returns.py
│   ├── statistics.py
│   └── charts.py
│
├── output/
│
├── reports/
│
└── README.md
```

---

## Requirements

- Python 3.14+
- pandas
- matplotlib

Install dependencies:

```bash
pip install pandas matplotlib
```

---

## Running the Program

From the project directory:

```bash
cd src
python main.py
```

The program will:

- Load fund data
- Calculate investment statistics
- Print a comparison table
- Generate growth charts

---

## Example Statistics

Typical output includes:

- CAGR
- Annualized Return
- Annualized Volatility
- Maximum Drawdown
- Best Year
- Worst Year
- Positive Years
- Negative Years

---

## Future Enhancements

Planned improvements include:

- Risk-adjusted performance measures
- Sharpe Ratio
- Sortino Ratio
- Rolling returns
- Correlation matrix
- Portfolio optimization
- PDF reports
- Interactive charts
- ETF support
- Automatic data downloads

---

## Author

Arnold W. Barnett

---

## License

This project is provided for educational and personal investment analysis purposes.

It is not intended as financial advice.
