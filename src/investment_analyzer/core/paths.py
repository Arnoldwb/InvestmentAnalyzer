from pathlib import Path

# Project root (InvestmentAnalyzer)
PROJECT_ROOT = Path(__file__).resolve().parents[3]

# Standard folders
DATA_DIR = PROJECT_ROOT / "data"
OUTPUT_DIR = PROJECT_ROOT / "output"
DOCS_DIR = PROJECT_ROOT / "docs"

# Ensure the output directory exists
OUTPUT_DIR.mkdir(exist_ok=True)