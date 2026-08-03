import sys

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QApplication,
    QLabel,
    QMainWindow,
    QPushButton,
    QVBoxLayout,
    QWidget,
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

        self.portfolio_button = QPushButton("Portfolio Analysis")
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

        self.exit_button.clicked.connect(self.close)


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
