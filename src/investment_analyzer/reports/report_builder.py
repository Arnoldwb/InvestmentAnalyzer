from pathlib import Path


class ReportBuilder:
    """
    Builds formatted text reports.
    """

    def __init__(self):
        self.lines = []

    def blank(self):
        self.lines.append("")

    def title(self, text):
        self.lines.append("=" * 60)
        self.lines.append(text)
        self.lines.append("=" * 60)
        self.blank()

    def section(self, text):
        self.lines.append(text)
        self.lines.append("-" * 60)

    def line(self, text=""):
        self.lines.append(text)

    def field(self, label, value):
        self.lines.append(f"{label:<25}{value}")

    def save(self, filename: Path):
        with open(filename, "w", encoding="utf-8") as f:
            f.write("\n".join(self.lines) + "\n")
