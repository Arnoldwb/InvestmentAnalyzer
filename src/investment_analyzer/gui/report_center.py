from pathlib import Path

from PySide6.QtCore import Qt, QUrl
from PySide6.QtGui import (
    QDesktopServices,
    QFontDatabase,
)
from PySide6.QtWidgets import (
    QComboBox,
    QDialog,
    QFileDialog,
    QHBoxLayout,
    QLabel,
    QMessageBox,
    QPushButton,
    QPlainTextEdit,
    QVBoxLayout,
)

from investment_analyzer.core.paths import REPORTS_DIR
from investment_analyzer.core.portfolio_storage import (
    list_portfolios,
    load_portfolio,
)
from investment_analyzer.reports.report_manager import (
    ReportManager,
)


class ReportCenterWindow(QDialog):
    """
    Generate and display Investment Analyzer reports.
    """

    def __init__(self, parent=None):
        super().__init__(parent)

        self.current_report_path = None

        self.setWindowTitle("Report Center")
        self.resize(950, 750)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(25, 20, 25, 20)
        layout.setSpacing(12)

        title = QLabel("Investment Analyzer Report Center")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)

        title_font = title.font()
        title_font.setPointSize(20)
        title_font.setBold(True)
        title.setFont(title_font)

        layout.addWidget(title)

        selector_layout = QHBoxLayout()
        selector_layout.addWidget(QLabel("Portfolio:"))

        self.portfolio_selector = QComboBox()

        for filename in list_portfolios():
            self.portfolio_selector.addItem(
                filename.removesuffix(".json"),
                filename,
            )

        selector_layout.addWidget(
            self.portfolio_selector,
            1,
        )

        self.generate_button = QPushButton(
            "Generate Portfolio Report"
        )
        selector_layout.addWidget(self.generate_button)

        layout.addLayout(selector_layout)

        self.report_viewer = QPlainTextEdit()
        self.report_viewer.setReadOnly(True)

        fixed_font = QFontDatabase.systemFont(
            QFontDatabase.SystemFont.FixedFont
        )
        self.report_viewer.setFont(fixed_font)

        self.report_viewer.setPlaceholderText(
            "Select a portfolio and generate a report."
        )

        layout.addWidget(self.report_viewer, 1)

        self.status_label = QLabel("")
        self.status_label.setAlignment(
            Qt.AlignmentFlag.AlignCenter
        )
        layout.addWidget(self.status_label)

        button_layout = QHBoxLayout()

        self.save_as_button = QPushButton(
            "Save Report As..."
        )
        self.open_folder_button = QPushButton(
            "Open Reports Folder"
        )
        return_button = QPushButton(
            "Return to Investment Analyzer"
        )

        self.save_as_button.setMinimumHeight(40)
        self.open_folder_button.setMinimumHeight(40)
        return_button.setMinimumHeight(40)

        self.save_as_button.setEnabled(False)

        button_layout.addWidget(
            self.save_as_button
        )
        button_layout.addWidget(
            self.open_folder_button
        )
        button_layout.addWidget(return_button)

        layout.addLayout(button_layout)

        self.generate_button.clicked.connect(
            self.generate_report
        )
        self.save_as_button.clicked.connect(
            self.save_report_as
        )
        self.open_folder_button.clicked.connect(
            self.open_reports_folder
        )
        return_button.clicked.connect(self.accept)

        if self.portfolio_selector.count() == 0:
            self.generate_button.setEnabled(False)
            self.status_label.setText(
                "No saved portfolios are available."
            )

    def save_report_as(self):
        """
        Save a copy of the currently displayed report.
        """

        if self.current_report_path is None:
            QMessageBox.warning(
                self,
                "Save Report",
                "Generate a report before saving a copy.",
            )
            return

        suggested_name = self.current_report_path.name

        filename, _ = QFileDialog.getSaveFileName(
            self,
            "Save Report As",
            suggested_name,
            "Text Files (*.txt);;All Files (*)",
        )

        if not filename:
            return

        destination = Path(filename)

        if destination.suffix == "":
            destination = destination.with_suffix(".txt")

        try:
            destination.write_text(
                self.report_viewer.toPlainText(),
                encoding="utf-8",
            )
        except Exception as error:
            QMessageBox.critical(
                self,
                "Save Report Error",
                "Unable to save the report:"
                f"\n\n{error}",
            )
            return

        self.status_label.setText(
            f"Report saved as {destination.name}"
        )

    def open_reports_folder(self):
        """
        Open the reports directory in the system file manager.
        """

        REPORTS_DIR.mkdir(
            parents=True,
            exist_ok=True,
        )

        opened = QDesktopServices.openUrl(
            QUrl.fromLocalFile(str(REPORTS_DIR))
        )

        if not opened:
            QMessageBox.warning(
                self,
                "Open Reports Folder",
                "Unable to open the reports folder.",
            )

    def generate_report(self):
        """
        Generate and display a report for the selected portfolio.
        """

        filename = self.portfolio_selector.currentData()

        if not filename:
            self.status_label.setText(
                "No saved portfolio selected."
            )
            return

        try:
            portfolio = load_portfolio(filename)

            manager = ReportManager()
            path = manager.create_portfolio_report(
                portfolio
            )

            report_text = path.read_text(
                encoding="utf-8"
            )

        except Exception as error:
            QMessageBox.critical(
                self,
                "Report Error",
                "Unable to generate portfolio report:"
                f"\n\n{error}",
            )
            return

        self.current_report_path = path
        self.report_viewer.setPlainText(report_text)
        self.save_as_button.setEnabled(True)

        self.status_label.setText(
            f"Report generated for {portfolio.name}"
        )
