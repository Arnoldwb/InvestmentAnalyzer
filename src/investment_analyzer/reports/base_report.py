from pathlib import Path
from datetime import datetime


class BaseReport:
    """
    Base class for all report generators.
    """

    def __init__(self):
        self.project_root = Path(__file__).resolve().parents[3]
        self.output_folder = self.project_root / "reports"
        self.output_folder.mkdir(exist_ok=True)

    @property
    def timestamp(self) -> str:
        return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    def report_path(self, filename: str) -> Path:
        return self.output_folder / filename
