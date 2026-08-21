from PySide6.QtCore import Qt
import matplotlib.dates as mdates
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
        self.motion_connection = None
        self.crosshair = None
        self.annotation = None

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
        self.chart_type_selector.addItem(
            "Monthly Returns",
            "monthly_returns",
        )
        self.chart_type_selector.addItem(
            "Portfolio Allocation",
            "allocation",
        )
        selector_layout.addWidget(self.chart_type_selector)

        self.refresh_button = QPushButton("Refresh Chart")
        selector_layout.addWidget(self.refresh_button)

        layout.addLayout(selector_layout)

        self.chart_layout = QVBoxLayout()
        layout.addLayout(self.chart_layout, 1)

        self.status_label = QLabel("")
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.status_label)

        return_button = QPushButton("Return to Investment Analyzer")
        return_button.setMinimumHeight(40)
        layout.addWidget(return_button)

        self.refresh_button.clicked.connect(self.display_chart)
        self.portfolio_selector.currentIndexChanged.connect(self.display_chart)
        self.chart_type_selector.currentIndexChanged.connect(self.display_chart)
        return_button.clicked.connect(self.accept)

        if self.portfolio_selector.count() > 0:
            self.display_chart()
        else:
            self.status_label.setText("No saved portfolios are available.")

    def clear_chart(self):
        """
        Remove the currently displayed chart.
        """

        if self.motion_connection is not None and self.canvas is not None:
            self.canvas.mpl_disconnect(self.motion_connection)
            self.motion_connection = None

        if self.canvas is not None:
            self.chart_layout.removeWidget(self.canvas)
            self.canvas.deleteLater()
            self.canvas = None

    def enable_growth_interaction(self, figure):
        """
        Add interactive mouse tracking to a growth chart.
        """

        if not figure.axes:
            return

        axes = figure.axes[0]

        # Use the first actual data date for the crosshair.
        # This prevents the invisible crosshair from expanding
        # the chart's x-axis back to 1970.
        data_lines = axes.get_lines()

        if not data_lines:
            return

        first_x = data_lines[0].get_xdata()[0]

        self.crosshair = axes.axvline(
            first_x,
            linewidth=1,
            linestyle="--",
            visible=False,
        )

        # Make sure the crosshair does not affect the chart limits.
        axes.relim()
        axes.autoscale_view()

        self.annotation = axes.annotate(
            "",
            xy=(0, 0),
            xytext=(15, 15),
            textcoords="offset points",
            bbox=dict(
                boxstyle="round,pad=0.5",
                facecolor="white",
                edgecolor="gray",
                alpha=0.95,
            ),
            verticalalignment="bottom",
            fontsize=8,
            visible=False,
        )

        def on_motion(event):
            if event.inaxes != axes or event.xdata is None:
                self.crosshair.set_visible(False)
                self.annotation.set_visible(False)
                self.canvas.draw_idle()
                return

            target_date = event.xdata

            values = []
            nearest_date = None

            for line in data_lines:
                x_data = line.get_xdata()
                y_data = line.get_ydata()

                if len(x_data) == 0:
                    continue

                x_numeric = mdates.date2num(x_data)

                nearest_index = min(
                    range(len(x_numeric)),
                    key=lambda index: abs(x_numeric[index] - target_date),
                )

                date_value = x_data[nearest_index]
                value = y_data[nearest_index]

                if nearest_date is None:
                    nearest_date = date_value

                label = line.get_label()

                values.append(
                    (
                        label,
                        float(value),
                    )
                )

            if not values or nearest_date is None:
                return

            # Move the vertical guide line to the mouse position.
            self.crosshair.set_xdata([target_date, target_date])
            self.crosshair.set_visible(True)

            date_text = str(nearest_date).split(" ")[0]

            text_lines = [
                f"Date: {date_text}",
                "",
            ]

            for label, value in values:
                text_lines.append(f"{label}: ${value:,.0f}")

            self.annotation.set_text("\n".join(text_lines))

            self.annotation.xy = (
                target_date,
                event.ydata,
            )

            if event.x < axes.bbox.x0 + axes.bbox.width * 0.65:
                self.annotation.set_position((15, 15))
                self.annotation.set_ha("left")
            else:
                self.annotation.set_position((-15, 15))
                self.annotation.set_ha("right")

            self.annotation.set_visible(True)

            self.canvas.draw_idle()

        self.motion_connection = self.canvas.mpl_connect(
            "motion_notify_event",
            on_motion,
        )

    def display_chart(self):
        """
        Display the selected chart for the selected portfolio.
        """

        filename = self.portfolio_selector.currentData()

        if not filename:
            self.clear_chart()
            self.status_label.setText("No saved portfolio selected.")
            return

        try:
            portfolio = load_portfolio(filename)

            generator = ChartGenerator()
            chart_type = self.chart_type_selector.currentData()

            if chart_type == "drawdown":
                figure = generator.portfolio_drawdown_chart(portfolio)
                description = "Drawdown History"

            elif chart_type == "monthly_returns":
                figure = generator.portfolio_monthly_returns_chart(portfolio)
                description = "Monthly Returns"

            elif chart_type == "allocation":
                figure = generator.portfolio_allocation_chart(portfolio)
                description = "Portfolio Allocation"

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
                "Unable to create portfolio chart:" f"\n\n{error}",
            )
            return

        self.clear_chart()

        self.canvas = FigureCanvasQTAgg(figure)
        self.chart_layout.addWidget(self.canvas)

        if chart_type == "growth":
            self.enable_growth_interaction(figure)

        self.canvas.draw()

        self.status_label.setText(f"Displaying {description} for " f"{portfolio.name}")
