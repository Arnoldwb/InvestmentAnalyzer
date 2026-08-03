import sys

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QApplication,
    QComboBox,
    QDialog,
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)

from investment_analyzer.core.portfolio_storage import (
    list_portfolios,
    load_portfolio,
)


class PortfolioWindow(QDialog):
    """
    Display saved Investment Analyzer portfolios.
    """

    def __init__(self, parent=None):
        super().__init__(parent)

        self.setWindowTitle("Portfolio Analysis")
        self.resize(650, 450)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(30, 25, 30, 25)
        layout.setSpacing(15)

        title = QLabel("Saved Portfolio")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)

        title_font = title.font()
        title_font.setPointSize(20)
        title_font.setBold(True)
        title.setFont(title_font)

        layout.addWidget(title)

        selector_layout = QHBoxLayout()

        selector_label = QLabel("Portfolio:")
        self.portfolio_selector = QComboBox()

        selector_layout.addWidget(selector_label)
        selector_layout.addWidget(self.portfolio_selector, 1)

        layout.addLayout(selector_layout)

        self.portfolio_name = QLabel("")
        self.portfolio_name.setAlignment(
            Qt.AlignmentFlag.AlignCenter
        )

        name_font = self.portfolio_name.font()
        name_font.setPointSize(16)
        name_font.setBold(True)
        self.portfolio_name.setFont(name_font)

        layout.addWidget(self.portfolio_name)

        self.holdings_table = QTableWidget()
        self.holdings_table.setColumnCount(2)
        self.holdings_table.setHorizontalHeaderLabels(
            ["Fund", "Allocation"]
        )

        self.holdings_table.horizontalHeader().setStretchLastSection(
            True
        )
        self.holdings_table.setEditTriggers(
            QTableWidget.EditTrigger.NoEditTriggers
        )

        layout.addWidget(self.holdings_table)

        self.total_label = QLabel("Total Allocation: --")
        self.total_label.setAlignment(
            Qt.AlignmentFlag.AlignRight
        )
        layout.addWidget(self.total_label)

        close_button = QPushButton("Close")
        close_button.setMinimumHeight(40)
        close_button.clicked.connect(self.accept)

        layout.addWidget(close_button)

        self.load_portfolio_list()

        self.portfolio_selector.currentIndexChanged.connect(
            self.display_selected_portfolio
        )

        if self.portfolio_selector.count() > 0:
            self.display_selected_portfolio()

    def load_portfolio_list(self):
        """
        Load saved portfolio filenames into the selector.
        """

        self.portfolio_selector.clear()

        for filename in list_portfolios():
            self.portfolio_selector.addItem(
                filename.removesuffix(".json"),
                filename,
            )

    def display_selected_portfolio(self):
        """
        Display the selected portfolio holdings.
        """

        filename = self.portfolio_selector.currentData()

        if not filename:
            self.portfolio_name.setText(
                "No saved portfolios found."
            )
            self.holdings_table.setRowCount(0)
            self.total_label.setText("Total Allocation: --")
            return

        try:
            portfolio = load_portfolio(filename)
        except Exception as error:
            QMessageBox.critical(
                self,
                "Portfolio Error",
                f"Unable to load portfolio:\n\n{error}",
            )
            return

        self.portfolio_name.setText(portfolio.name)

        self.holdings_table.setRowCount(
            len(portfolio.holdings)
        )

        for row, holding in enumerate(portfolio.holdings):
            symbol_item = QTableWidgetItem(
                holding.fund.symbol
            )
            allocation_item = QTableWidgetItem(
                f"{holding.allocation:.1f}%"
            )

            self.holdings_table.setItem(
                row,
                0,
                symbol_item,
            )
            self.holdings_table.setItem(
                row,
                1,
                allocation_item,
            )

        self.holdings_table.resizeColumnsToContents()

        self.total_label.setText(
            f"Total Allocation: "
            f"{portfolio.total_allocation:.1f}%"
        )


class InvestmentAnalyzerWindow(QMainWindow):
    """
    Main graphical window for Investment Analyzer.
    """

    def __init__(self):
        super().__init__()

        self.setWindowTitle("Investment Analyzer")
        self.resize(800, 600)

        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        layout = QVBoxLayout(central_widget)
        layout.setContentsMargins(60, 50, 60, 50)
        layout.setSpacing(18)

        title = QLabel("Investment Analyzer")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)

        title_font = title.font()
        title_font.setPointSize(28)
        title_font.setBold(True)
        title.setFont(title_font)

        subtitle = QLabel("Version 5.0")
        subtitle.setAlignment(Qt.AlignmentFlag.AlignCenter)

        subtitle_font = subtitle.font()
        subtitle_font.setPointSize(16)
        subtitle.setFont(subtitle_font)

        description = QLabel(
            "Portfolio Analysis and Retirement Planning"
        )
        description.setAlignment(Qt.AlignmentFlag.AlignCenter)

        layout.addWidget(title)
        layout.addWidget(subtitle)
        layout.addWidget(description)
        layout.addSpacing(30)

        self.portfolio_button = QPushButton(
            "Portfolio Analysis"
        )
        self.monte_carlo_button = QPushButton(
            "Monte Carlo & Withdrawal Analysis"
        )
        self.reports_button = QPushButton("Reports")
        self.exit_button = QPushButton("Exit")

        for button in (
            self.portfolio_button,
            self.monte_carlo_button,
            self.reports_button,
            self.exit_button,
        ):
            button.setMinimumHeight(48)
            layout.addWidget(button)

        layout.addStretch()

        status = QLabel(
            "Version 5.0 Mac Application Development"
        )
        status.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(status)

        self.portfolio_button.clicked.connect(
            self.open_portfolio_window
        )
        self.exit_button.clicked.connect(self.close)

    def open_portfolio_window(self):
        """
        Open the saved portfolio analysis window.
        """

        window = PortfolioWindow(self)
        window.exec()


def run_gui():
    """
    Start the Investment Analyzer graphical application.
    """

    app = QApplication(sys.argv)

    window = InvestmentAnalyzerWindow()
    window.show()

    return app.exec()


if __name__ == "__main__":
    run_gui()
