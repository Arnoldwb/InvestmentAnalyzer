from pathlib import Path
from datetime import datetime

from investment_analyzer.core.paths import REPORTS_DIR
class BaseReport:
    """
    Base class for all report generators.
    """

    def __init__(self):
       self.output_folder = REPORTS_DIR
       self.output_folder.mkdir(parents=True, exist_ok=True)

    @property
    def timestamp(self) -> str:
        return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    def report_path(self, filename: str) -> Path:
        return self.output_folder / filename
