from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QComboBox,
    QDialog,
    QHBoxLayout,
    QLabel,
    QMessageBox,
    QPushButton,
    QVBoxLayout,
)

from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg

from investment_analyzer.core.portfolio_storage import (
    list_portfolios,
    load_portfolio,
)
from investment_analyzer.visualization.chart_generator import (
    ChartGenerator,
)


class ChartViewerWindow(QDialog):
    """
    Display portfolio charts inside Investment Analyzer.
    """

    def __init__(self, parent=None):
        super().__init__(parent)

        self.canvas = None

        self.setWindowTitle("Chart Viewer")
        self.resize(950, 700)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(25, 20, 25, 20)
        layout.setSpacing(12)

        title = QLabel("Portfolio Chart Viewer")
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

        selector_layout.addWidget(QLabel("Chart Type:"))

        self.chart_type_selector = QComboBox()
        self.chart_type_selector.addItem(
            "Growth of $10,000",
            "growth",
        )
        self.chart_type_selector.addItem(
            "Drawdown History",
            "drawdown",
        )

        selector_layout.addWidget(
            self.chart_type_selector
        )

        self.refresh_button = QPushButton("Refresh Chart")
        selector_layout.addWidget(self.refresh_button)

        layout.addLayout(selector_layout)

        self.chart_layout = QVBoxLayout()
        layout.addLayout(self.chart_layout, 1)

        self.status_label = QLabel("")
        self.status_label.setAlignment(
            Qt.AlignmentFlag.AlignCenter
        )
        layout.addWidget(self.status_label)

        return_button = QPushButton(
            "Return to Investment Analyzer"
        )
        return_button.setMinimumHeight(40)
        layout.addWidget(return_button)

        self.refresh_button.clicked.connect(
            self.display_chart
        )
        self.portfolio_selector.currentIndexChanged.connect(
            self.display_chart
        )
        self.chart_type_selector.currentIndexChanged.connect(
            self.display_chart
        )
        return_button.clicked.connect(self.accept)

        if self.portfolio_selector.count() > 0:
            self.display_chart()
        else:
            self.status_label.setText(
                "No saved portfolios are available."
            )

    def clear_chart(self):
        """
        Remove the currently displayed chart.
        """

        if self.canvas is not None:
            self.chart_layout.removeWidget(self.canvas)
            self.canvas.deleteLater()
            self.canvas = None

    def display_chart(self):
        """
        Display Growth of $10,000 for the selected portfolio.
        """

        filename = self.portfolio_selector.currentData()

        if not filename:
            self.clear_chart()
            self.status_label.setText(
                "No saved portfolio selected."
            )
            return

        try:
            portfolio = load_portfolio(filename)

            generator = ChartGenerator()
            chart_type = self.chart_type_selector.currentData()

            if chart_type == "drawdown":
                figure = generator.portfolio_drawdown_chart(
                    portfolio
                )
                description = "Drawdown History"
            else:
                figure = generator.portfolio_growth_chart(
                    portfolio,
                    10000.0,
                )
                description = "Growth of $10,000"

        except Exception as error:
            self.clear_chart()

            QMessageBox.critical(
                self,
                "Chart Error",
                "Unable to create portfolio chart:"
                f"\n\n{error}",
            )
            return

        self.clear_chart()

        self.canvas = FigureCanvasQTAgg(figure)
        self.chart_layout.addWidget(self.canvas)
        self.canvas.draw()

        self.status_label.setText(
            f"Displaying {description} for "
            f"{portfolio.name}"
        )
