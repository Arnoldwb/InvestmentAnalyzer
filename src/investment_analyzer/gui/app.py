import sys

from PySide6.QtCore import Qt
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg
from PySide6.QtWidgets import (
    QApplication,
    QComboBox,
    QDialog,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QMenu,
    QSpinBox,
    QDoubleSpinBox,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)

from investment_analyzer.analysis.monte_carlo_analyzer import (
    MonteCarloAnalyzer,
)
from investment_analyzer.analysis.portfolio_analyzer import (
    PortfolioAnalyzer,
)
from investment_analyzer.core.file_discovery import discover_funds
from investment_analyzer.core.portfolio_storage import (
    delete_portfolio,
    list_portfolios,
    load_portfolio,
    rename_portfolio,
    save_portfolio,
)
from investment_analyzer.models.portfolio import Portfolio
from investment_analyzer.gui.chart_viewer import ChartViewerWindow
from investment_analyzer.gui.report_center import ReportCenterWindow
from investment_analyzer.visualization.chart_generator import (
    ChartGenerator,
)


class PortfolioWindow(QDialog):
    """
    Display saved Investment Analyzer portfolios.
    """

    def __init__(self, parent=None):
        super().__init__(parent)

        self.setWindowTitle("Portfolio Analysis")
        self.resize(700, 700)

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

        performance_title = QLabel(
            "Portfolio Performance"
        )
        performance_title.setAlignment(
            Qt.AlignmentFlag.AlignCenter
        )

        performance_font = performance_title.font()
        performance_font.setPointSize(16)
        performance_font.setBold(True)
        performance_title.setFont(performance_font)

        layout.addWidget(performance_title)

        self.performance_table = QTableWidget()
        self.performance_table.setColumnCount(2)
        self.performance_table.setRowCount(6)
        self.performance_table.setHorizontalHeaderLabels(
            ["Statistic", "Value"]
        )

        statistics = [
            "CAGR",
            "Annualized Average Return",
            "Annualized Volatility",
            "Maximum Drawdown",
            "Sharpe Ratio",
            "Growth of $10,000",
        ]

        for row, statistic in enumerate(statistics):
            self.performance_table.setItem(
                row,
                0,
                QTableWidgetItem(statistic),
            )
            self.performance_table.setItem(
                row,
                1,
                QTableWidgetItem("--"),
            )

        self.performance_table.horizontalHeader().setStretchLastSection(
            True
        )
        self.performance_table.setEditTriggers(
            QTableWidget.EditTrigger.NoEditTriggers
        )
        self.performance_table.setMaximumHeight(235)

        layout.addWidget(self.performance_table)

        close_button = QPushButton(
            "Return to Investment Analyzer"
        )
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
            self.clear_performance_results()
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

        self.display_performance_results(portfolio)

    def clear_performance_results(self):
        """
        Clear displayed portfolio performance statistics.
        """

        for row in range(6):
            item = self.performance_table.item(row, 1)

            if item is not None:
                item.setText("--")

    def display_performance_results(self, portfolio):
        """
        Calculate and display portfolio performance statistics.
        """

        self.clear_performance_results()

        try:
            analyzer = PortfolioAnalyzer(portfolio)

            cagr = analyzer.cagr()
            annual_return = analyzer.annualized_return()
            volatility = analyzer.annualized_volatility()
            drawdown = analyzer.max_drawdown()
            sharpe = analyzer.sharpe_ratio()

            growth = analyzer.growth_index(10000)
            ending_value = growth.iloc[-1]

        except Exception as error:
            QMessageBox.critical(
                self,
                "Analysis Error",
                "Unable to analyze the selected portfolio:"
                f"\n\n{error}",
            )
            return

        values = [
            f"{cagr:.2%}",
            f"{annual_return:.2%}",
            f"{volatility:.2%}",
            f"{drawdown:.2%}",
            f"{sharpe:.2f}",
            f"${ending_value:,.2f}",
        ]

        for row, value in enumerate(values):
            item = self.performance_table.item(row, 1)

            if item is None:
                item = QTableWidgetItem()
                self.performance_table.setItem(
                    row,
                    1,
                    item,
                )

            item.setText(value)

        self.performance_table.resizeColumnsToContents()


class MonteCarloWindow(QDialog):
    """
    Graphical Monte Carlo and withdrawal analysis.
    """

    def __init__(self, parent=None):
        super().__init__(parent)

        self.setWindowTitle(
            "Monte Carlo & Withdrawal Analysis"
        )
        self.resize(720, 720)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(30, 25, 30, 25)
        layout.setSpacing(12)

        title = QLabel(
            "Monte Carlo & Withdrawal Analysis"
        )
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)

        title_font = title.font()
        title_font.setPointSize(20)
        title_font.setBold(True)
        title.setFont(title_font)

        layout.addWidget(title)

        # Portfolio selector
        portfolio_layout = QHBoxLayout()
        portfolio_layout.addWidget(QLabel("Portfolio:"))

        self.portfolio_selector = QComboBox()

        for filename in list_portfolios():
            self.portfolio_selector.addItem(
                filename.removesuffix(".json"),
                filename,
            )

        portfolio_layout.addWidget(
            self.portfolio_selector,
            1,
        )
        layout.addLayout(portfolio_layout)

        # Analysis selector
        analysis_layout = QHBoxLayout()
        analysis_layout.addWidget(QLabel("Analysis:"))

        self.analysis_selector = QComboBox()
        self.analysis_selector.addItem(
            "Portfolio Growth",
            "growth",
        )
        self.analysis_selector.addItem(
            "Withdrawal Sustainability",
            "withdrawal",
        )
        self.analysis_selector.addItem(
            "Sustainable Withdrawal Calculator",
            "sustainable",
        )
        self.analysis_selector.addItem(
            "Compare Withdrawal Strategies",
            "comparison",
        )

        analysis_layout.addWidget(
            self.analysis_selector,
            1,
        )
        layout.addLayout(analysis_layout)

        # Starting value
        value_layout = QHBoxLayout()
        value_layout.addWidget(
            QLabel("Starting Portfolio Value:")
        )

        self.initial_value = QDoubleSpinBox()
        self.initial_value.setRange(
            1.0,
            1000000000.0,
        )
        self.initial_value.setDecimals(2)
        self.initial_value.setValue(500000.0)
        self.initial_value.setPrefix("$")
        self.initial_value.setGroupSeparatorShown(True)
        self.initial_value.setSingleStep(10000.0)
        self.initial_value.setKeyboardTracking(False)
        self.initial_value.lineEdit().setReadOnly(False)

        value_layout.addWidget(self.initial_value)
        layout.addLayout(value_layout)

        # Withdrawal
        self.withdrawal_layout = QHBoxLayout()
        self.withdrawal_label = QLabel(
            "Annual Withdrawal:"
        )

        self.annual_withdrawal = QDoubleSpinBox()
        self.annual_withdrawal.setRange(
            0.0,
            1000000000.0,
        )
        self.annual_withdrawal.setDecimals(2)
        self.annual_withdrawal.setValue(25000.0)
        self.annual_withdrawal.setPrefix("$")
        self.annual_withdrawal.setGroupSeparatorShown(
            True
        )
        self.annual_withdrawal.setSingleStep(1000.0)
        self.annual_withdrawal.lineEdit().setReadOnly(False)

        self.withdrawal_layout.addWidget(
            self.withdrawal_label
        )
        self.withdrawal_layout.addWidget(
            self.annual_withdrawal
        )

        layout.addLayout(self.withdrawal_layout)

        # Withdrawal strategy comparison amounts
        self.comparison_layout = QHBoxLayout()
        self.comparison_label = QLabel(
            "Annual Withdrawals:"
        )

        self.comparison_amounts = QLineEdit()
        self.comparison_amounts.setText(
            "20000, 25000, 30000, 35000"
        )
        self.comparison_amounts.setPlaceholderText(
            "Example: 20000, 25000, 30000, 35000"
        )

        self.comparison_layout.addWidget(
            self.comparison_label
        )
        self.comparison_layout.addWidget(
            self.comparison_amounts,
            1,
        )

        layout.addLayout(self.comparison_layout)

        # Inflation
        self.inflation_layout = QHBoxLayout()
        self.inflation_label = QLabel(
            "Annual Inflation Rate:"
        )

        self.inflation_rate = QDoubleSpinBox()
        self.inflation_rate.setRange(0.0, 100.0)
        self.inflation_rate.setDecimals(2)
        self.inflation_rate.setValue(3.0)
        self.inflation_rate.setSuffix("%")
        self.inflation_rate.setSingleStep(0.25)
        self.inflation_rate.lineEdit().setReadOnly(False)

        self.inflation_layout.addWidget(
            self.inflation_label
        )
        self.inflation_layout.addWidget(
            self.inflation_rate
        )

        layout.addLayout(self.inflation_layout)

        # Target survival probability
        self.survival_layout = QHBoxLayout()
        self.survival_label = QLabel(
            "Target Survival Probability:"
        )

        self.target_survival = QDoubleSpinBox()
        self.target_survival.setRange(0.01, 100.0)
        self.target_survival.setDecimals(2)
        self.target_survival.setValue(90.0)
        self.target_survival.setSuffix("%")
        self.target_survival.setSingleStep(1.0)
        self.target_survival.lineEdit().setReadOnly(False)

        self.survival_layout.addWidget(
            self.survival_label
        )
        self.survival_layout.addWidget(
            self.target_survival
        )

        layout.addLayout(self.survival_layout)

        # Projection period
        years_layout = QHBoxLayout()
        years_layout.addWidget(
            QLabel("Projection Period:")
        )

        self.years = QSpinBox()
        self.years.setRange(1, 100)
        self.years.setValue(20)
        self.years.setSuffix(" years")

        years_layout.addWidget(self.years)
        layout.addLayout(years_layout)

        # Simulations
        simulations_layout = QHBoxLayout()
        simulations_layout.addWidget(
            QLabel("Number of Simulations:")
        )

        self.simulations = QSpinBox()
        self.simulations.setRange(100, 1000000)
        self.simulations.setSingleStep(1000)
        self.simulations.setValue(10000)
        self.simulations.setGroupSeparatorShown(True)

        simulations_layout.addWidget(
            self.simulations
        )
        layout.addLayout(simulations_layout)

        self.run_button = QPushButton(
            "Run Monte Carlo Analysis"
        )
        self.run_button.setMinimumHeight(44)
        self.run_button.clicked.connect(
            self.run_analysis
        )

        layout.addWidget(self.run_button)

        self.results_title = QLabel(
            "Projected Ending Values"
        )
        self.results_title.setAlignment(
            Qt.AlignmentFlag.AlignCenter
        )

        results_font = self.results_title.font()
        results_font.setPointSize(16)
        results_font.setBold(True)
        self.results_title.setFont(results_font)

        layout.addWidget(self.results_title)

        self.results_table = QTableWidget()
        self.results_table.setColumnCount(2)
        self.results_table.setHorizontalHeaderLabels(
            ["Statistic", "Result"]
        )
        self.results_table.setEditTriggers(
            QTableWidget.EditTrigger.NoEditTriggers
        )
        self.results_table.horizontalHeader().setStretchLastSection(
            True
        )
        self.results_table.setMaximumHeight(300)

        layout.addWidget(self.results_table)

        note = QLabel(
            "Monte Carlo results are simulations based on "
            "historical monthly returns and are not forecasts "
            "or guarantees."
        )
        note.setWordWrap(True)
        note.setAlignment(Qt.AlignmentFlag.AlignCenter)

        layout.addWidget(note)

        close_button = QPushButton(
            "Return to Investment Analyzer"
        )
        close_button.setMinimumHeight(40)
        close_button.clicked.connect(self.accept)

        layout.addWidget(close_button)

        self.analysis_selector.currentIndexChanged.connect(
            self.analysis_changed
        )

        self.analysis_changed()

    def analysis_changed(self):
        """
        Adjust the controls for the selected analysis.
        """

        analysis = self.analysis_selector.currentData()

        withdrawal_mode = analysis == "withdrawal"
        sustainable_mode = analysis == "sustainable"
        comparison_mode = analysis == "comparison"

        self.withdrawal_label.setVisible(
            withdrawal_mode
        )
        self.annual_withdrawal.setVisible(
            withdrawal_mode
        )

        self.comparison_label.setVisible(
            comparison_mode
        )
        self.comparison_amounts.setVisible(
            comparison_mode
        )

        show_inflation = (
            withdrawal_mode
            or sustainable_mode
            or comparison_mode
        )

        self.inflation_label.setVisible(
            show_inflation
        )
        self.inflation_rate.setVisible(
            show_inflation
        )

        self.survival_label.setVisible(
            sustainable_mode
        )
        self.target_survival.setVisible(
            sustainable_mode
        )

        if withdrawal_mode:
            self.run_button.setText(
                "Run Withdrawal Analysis"
            )
            self.results_title.setText(
                "Withdrawal Sustainability Results"
            )

        elif sustainable_mode:
            self.run_button.setText(
                "Calculate Sustainable Withdrawal"
            )
            self.results_title.setText(
                "Sustainable Withdrawal Results"
            )

        elif comparison_mode:
            self.run_button.setText(
                "Compare Withdrawal Strategies"
            )
            self.results_title.setText(
                "Withdrawal Strategy Comparison"
            )

        else:
            self.run_button.setText(
                "Run Monte Carlo Analysis"
            )
            self.results_title.setText(
                "Projected Ending Values"
            )

        self.results_table.setRowCount(0)

    def populate_results(self, labels, values):
        """
        Populate the results table.
        """

        self.results_table.setRowCount(len(labels))

        for row, (label, value) in enumerate(
            zip(labels, values)
        ):
            self.results_table.setItem(
                row,
                0,
                QTableWidgetItem(label),
            )
            self.results_table.setItem(
                row,
                1,
                QTableWidgetItem(value),
            )

        self.results_table.resizeColumnsToContents()

    def run_analysis(self):
        """
        Run the selected Monte Carlo analysis.
        """

        filename = self.portfolio_selector.currentData()

        if not filename:
            QMessageBox.warning(
                self,
                "Portfolio Required",
                "No saved portfolio is available.",
            )
            return

        try:
            portfolio = load_portfolio(filename)
            analyzer = MonteCarloAnalyzer(portfolio)

            analysis = self.analysis_selector.currentData()

            if analysis == "comparison":
                amounts_text = (
                    self.comparison_amounts.text().strip()
                )

                if not amounts_text:
                    raise ValueError(
                        "Enter at least one annual withdrawal amount."
                    )

                annual_withdrawals = []

                for item in amounts_text.split(","):
                    cleaned = (
                        item.strip()
                        .replace("$", "")
                        .replace(" ", "")
                    )

                    if not cleaned:
                        continue

                    amount = float(cleaned)

                    if amount < 0:
                        raise ValueError(
                            "Withdrawal amounts cannot be negative."
                        )

                    annual_withdrawals.append(amount)

                if not annual_withdrawals:
                    raise ValueError(
                        "Enter at least one valid withdrawal amount."
                    )

                results = (
                    analyzer.compare_withdrawal_strategies(
                        initial_value=self.initial_value.value(),
                        annual_withdrawals=annual_withdrawals,
                        years=self.years.value(),
                        simulations=self.simulations.value(),
                        inflation_rate=(
                            self.inflation_rate.value()
                            / 100.0
                        ),
                    )
                )

                labels = []
                values = []

                for result in results:
                    labels.append(
                        f"${result['annual_withdrawal']:,.2f}"
                    )

                    values.append(
                        f"Rate {result['withdrawal_rate']:.2%} | "
                        f"Survival "
                        f"{result['survival_probability']:.2%} | "
                        f"Depletion "
                        f"{result['depletion_probability']:.2%} | "
                        f"Median "
                        f"${result['median']:,.2f}"
                    )

            elif analysis == "sustainable":
                summary = analyzer.sustainable_withdrawal(
                    initial_value=self.initial_value.value(),
                    years=self.years.value(),
                    target_survival_probability=(
                        self.target_survival.value()
                        / 100.0
                    ),
                    simulations=self.simulations.value(),
                    inflation_rate=(
                        self.inflation_rate.value()
                        / 100.0
                    ),
                )

                labels = [
                    "Sustainable Annual Withdrawal",
                    "Initial Withdrawal Rate",
                    "Target Survival Probability",
                    "Actual Survival Probability",
                    "Annual Inflation Rate",
                ]

                values = [
                    (
                        f"${summary['annual_withdrawal']:,.2f}"
                    ),
                    f"{summary['withdrawal_rate']:.2%}",
                    (
                        f"{summary['target_survival_probability']:.2%}"
                    ),
                    (
                        f"{summary['survival_probability']:.2%}"
                    ),
                    f"{summary['inflation_rate']:.2%}",
                ]

            elif analysis == "withdrawal":
                summary = analyzer.withdrawal_summary(
                    initial_value=self.initial_value.value(),
                    annual_withdrawal=(
                        self.annual_withdrawal.value()
                    ),
                    years=self.years.value(),
                    simulations=self.simulations.value(),
                    inflation_rate=(
                        self.inflation_rate.value()
                        / 100.0
                    ),
                )

                labels = [
                    "Annual Withdrawal",
                    "Initial Withdrawal Rate",
                    "Survival Probability",
                    "Depletion Probability",
                    "10th Percentile",
                    "25th Percentile",
                    "Median",
                    "75th Percentile",
                    "90th Percentile",
                    "Mean Ending Value",
                ]

                values = [
                    (
                        f"${summary['annual_withdrawal']:,.2f}"
                    ),
                    f"{summary['withdrawal_rate']:.2%}",
                    (
                        f"{summary['survival_probability']:.2%}"
                    ),
                    (
                        f"{summary['depletion_probability']:.2%}"
                    ),
                    f"${summary['percentile_10']:,.2f}",
                    f"${summary['percentile_25']:,.2f}",
                    f"${summary['median']:,.2f}",
                    f"${summary['percentile_75']:,.2f}",
                    f"${summary['percentile_90']:,.2f}",
                    (
                        f"${summary['mean_ending_value']:,.2f}"
                    ),
                ]

            else:
                summary = analyzer.summary(
                    initial_value=self.initial_value.value(),
                    years=self.years.value(),
                    simulations=self.simulations.value(),
                )

                labels = [
                    "10th Percentile",
                    "25th Percentile",
                    "Median",
                    "75th Percentile",
                    "90th Percentile",
                    "Mean Ending Value",
                    "Probability Above Starting Value",
                ]

                values = [
                    f"${summary['percentile_10']:,.2f}",
                    f"${summary['percentile_25']:,.2f}",
                    f"${summary['median']:,.2f}",
                    f"${summary['percentile_75']:,.2f}",
                    f"${summary['percentile_90']:,.2f}",
                    f"${summary['mean_ending_value']:,.2f}",
                    (
                        f"{summary['probability_above_start']:.2%}"
                    ),
                ]

            self.populate_results(labels, values)

        except Exception as error:
            QMessageBox.critical(
                self,
                "Monte Carlo Error",
                "Unable to complete the analysis:"
                f"\n\n{error}",
            )



class PortfolioBuilderWindow(QDialog):
    """
    Create, edit, and delete Investment Analyzer portfolios.
    """

    def __init__(self, parent=None):
        super().__init__(parent)

        self.current_filename = None

        self.setWindowTitle("Portfolio Builder")
        self.resize(650, 720)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(30, 25, 30, 25)
        layout.setSpacing(15)

        title = QLabel("Portfolio Builder")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)

        title_font = title.font()
        title_font.setPointSize(20)
        title_font.setBold(True)
        title.setFont(title_font)

        layout.addWidget(title)

        existing_layout = QHBoxLayout()
        existing_layout.addWidget(QLabel("Saved Portfolio:"))

        self.portfolio_selector = QComboBox()
        existing_layout.addWidget(self.portfolio_selector, 1)

        self.open_button = QPushButton("Open")
        self.new_button = QPushButton("New")

        existing_layout.addWidget(self.open_button)
        existing_layout.addWidget(self.new_button)

        layout.addLayout(existing_layout)

        name_layout = QHBoxLayout()
        name_layout.addWidget(QLabel("Portfolio Name:"))

        self.name_edit = QLineEdit()
        self.name_edit.setPlaceholderText(
            "Enter a name for the portfolio"
        )

        name_layout.addWidget(self.name_edit, 1)
        layout.addLayout(name_layout)

        instructions = QLabel(
            "Enter an allocation for each fund you want to include. "
            "The total allocation must equal 100%."
        )
        instructions.setWordWrap(True)
        layout.addWidget(instructions)

        self.fund_table = QTableWidget()
        self.fund_table.setColumnCount(2)
        self.fund_table.setHorizontalHeaderLabels(
            ["Fund", "Allocation %"]
        )

        funds = discover_funds()
        self.fund_table.setRowCount(len(funds))

        for row, symbol in enumerate(funds):
            symbol_item = QTableWidgetItem(symbol)
            symbol_item.setFlags(
                symbol_item.flags()
                & ~Qt.ItemFlag.ItemIsEditable
            )
            self.fund_table.setItem(row, 0, symbol_item)

            allocation = QDoubleSpinBox()
            allocation.setRange(0.0, 100.0)
            allocation.setDecimals(1)
            allocation.setSingleStep(1.0)
            allocation.setSuffix("%")
            allocation.valueChanged.connect(
                self.update_total
            )

            self.fund_table.setCellWidget(
                row,
                1,
                allocation,
            )

        self.fund_table.horizontalHeader().setStretchLastSection(
            True
        )
        self.fund_table.resizeColumnsToContents()

        layout.addWidget(self.fund_table)

        self.total_label = QLabel("Total Allocation: 0.0%")
        self.total_label.setAlignment(
            Qt.AlignmentFlag.AlignRight
        )

        total_font = self.total_label.font()
        total_font.setBold(True)
        self.total_label.setFont(total_font)

        layout.addWidget(self.total_label)

        button_layout = QHBoxLayout()

        self.save_button = QPushButton("Save Portfolio")
        self.delete_button = QPushButton("Delete Portfolio")
        self.cancel_button = QPushButton("Return to Investment Analyzer")

        for button in (
            self.save_button,
            self.delete_button,
            self.cancel_button,
        ):
            button.setMinimumHeight(40)

        button_layout.addWidget(self.save_button)
        button_layout.addWidget(self.delete_button)
        button_layout.addWidget(self.cancel_button)

        layout.addLayout(button_layout)

        self.open_button.clicked.connect(
            self.open_selected_portfolio
        )
        self.new_button.clicked.connect(
            self.new_portfolio
        )
        self.save_button.clicked.connect(
            self.save_current_portfolio
        )
        self.delete_button.clicked.connect(
            self.delete_current_portfolio
        )
        self.cancel_button.clicked.connect(self.reject)

        self.refresh_portfolio_list()
        self.new_portfolio()

    def refresh_portfolio_list(self):
        """
        Refresh the list of saved portfolios.
        """

        self.portfolio_selector.clear()

        for filename in list_portfolios():
            self.portfolio_selector.addItem(
                filename.removesuffix(".json"),
                filename,
            )

    def clear_allocations(self):
        """
        Set every displayed fund allocation to zero.
        """

        for row in range(self.fund_table.rowCount()):
            allocation = self.fund_table.cellWidget(row, 1)
            allocation.setValue(0.0)

        self.update_total()

    def new_portfolio(self):
        """
        Prepare the builder for a new portfolio.
        """

        self.current_filename = None
        self.name_edit.clear()
        self.clear_allocations()
        self.delete_button.setEnabled(False)
        self.name_edit.setFocus()

    def open_selected_portfolio(self):
        """
        Load the selected saved portfolio into the builder.
        """

        filename = self.portfolio_selector.currentData()

        if not filename:
            QMessageBox.information(
                self,
                "No Saved Portfolio",
                "There are no saved portfolios to open.",
            )
            return

        try:
            portfolio = load_portfolio(filename)
        except Exception as error:
            QMessageBox.critical(
                self,
                "Open Error",
                f"Unable to open portfolio:\n\n{error}",
            )
            return

        self.current_filename = filename
        self.name_edit.setText(portfolio.name)
        self.clear_allocations()

        allocations = {
            holding.fund.symbol: holding.allocation
            for holding in portfolio.holdings
        }

        for row in range(self.fund_table.rowCount()):
            symbol = self.fund_table.item(row, 0).text()

            if symbol in allocations:
                allocation = self.fund_table.cellWidget(
                    row,
                    1,
                )
                allocation.setValue(allocations[symbol])

        self.update_total()
        self.delete_button.setEnabled(True)

    def total_allocation(self):
        """
        Return the total allocation currently entered.
        """

        total = 0.0

        for row in range(self.fund_table.rowCount()):
            allocation = self.fund_table.cellWidget(row, 1)
            total += allocation.value()

        return total

    def update_total(self):
        """
        Update the displayed portfolio allocation total.
        """

        total = self.total_allocation()
        self.total_label.setText(
            f"Total Allocation: {total:.1f}%"
        )

    def build_portfolio(self):
        """
        Build a Portfolio from the current form values.
        """

        name = self.name_edit.text().strip()

        if not name:
            raise ValueError("Please enter a portfolio name.")

        portfolio = Portfolio(name)

        for row in range(self.fund_table.rowCount()):
            allocation_widget = self.fund_table.cellWidget(
                row,
                1,
            )
            allocation = allocation_widget.value()

            if allocation <= 0:
                continue

            symbol = self.fund_table.item(row, 0).text()
            portfolio.add_fund(symbol, allocation)

        portfolio.validate()

        return portfolio

    def save_current_portfolio(self):
        """
        Save a new portfolio or update the currently opened one.
        """

        try:
            portfolio = self.build_portfolio()
        except ValueError as error:
            QMessageBox.warning(
                self,
                "Invalid Portfolio",
                str(error),
            )
            return

        try:
            if self.current_filename is None:
                path = save_portfolio(portfolio)
            else:
                old_filename = self.current_filename
                old_portfolio = load_portfolio(old_filename)

                if portfolio.name != old_portfolio.name:
                    renamed_path = rename_portfolio(
                        old_filename,
                        portfolio.name,
                    )
                    self.current_filename = renamed_path.name

                path = save_portfolio(
                    portfolio,
                    self.current_filename,
                )

            self.current_filename = path.name
            self.refresh_portfolio_list()

            index = self.portfolio_selector.findData(
                self.current_filename
            )
            if index >= 0:
                self.portfolio_selector.setCurrentIndex(index)

            self.delete_button.setEnabled(True)

        except Exception as error:
            QMessageBox.critical(
                self,
                "Save Error",
                f"Unable to save portfolio:\n\n{error}",
            )
            return

        QMessageBox.information(
            self,
            "Portfolio Saved",
            f"Portfolio saved successfully:\n\n{path.name}",
        )

    def delete_current_portfolio(self):
        """
        Delete the currently opened saved portfolio.
        """

        if self.current_filename is None:
            return

        answer = QMessageBox.question(
            self,
            "Delete Portfolio",
            "Are you sure you want to delete this portfolio?",
            QMessageBox.StandardButton.Yes
            | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No,
        )

        if answer != QMessageBox.StandardButton.Yes:
            return

        try:
            delete_portfolio(self.current_filename)
        except Exception as error:
            QMessageBox.critical(
                self,
                "Delete Error",
                f"Unable to delete portfolio:\n\n{error}",
            )
            return

        QMessageBox.information(
            self,
            "Portfolio Deleted",
            "The portfolio was deleted successfully.",
        )

        self.refresh_portfolio_list()
        self.new_portfolio()


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

        subtitle = QLabel("Version 5.3")
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

        self.portfolio_builder_button = QPushButton(
            "Portfolio Builder"
        )
        self.portfolio_button = QPushButton(
            "Portfolio Analysis"
        )
        self.chart_viewer_button = QPushButton(
            "Chart Viewer"
        )
        self.monte_carlo_button = QPushButton(
            "Monte Carlo & Withdrawal Analysis"
        )

        self.monte_carlo_menu = QMenu(
            self.monte_carlo_button
        )

        growth_action = self.monte_carlo_menu.addAction(
            "Portfolio Growth"
        )
        withdrawal_action = self.monte_carlo_menu.addAction(
            "Withdrawal Sustainability"
        )
        sustainable_action = self.monte_carlo_menu.addAction(
            "Sustainable Withdrawal Calculator"
        )
        comparison_action = self.monte_carlo_menu.addAction(
            "Compare Withdrawal Strategies"
        )

        growth_action.triggered.connect(
            lambda: self.open_monte_carlo_window("growth")
        )
        withdrawal_action.triggered.connect(
            lambda: self.open_monte_carlo_window("withdrawal")
        )
        sustainable_action.triggered.connect(
            lambda: self.open_monte_carlo_window("sustainable")
        )
        comparison_action.triggered.connect(
            lambda: self.open_monte_carlo_window("comparison")
        )

        self.monte_carlo_button.setMenu(
            self.monte_carlo_menu
        )
        self.monte_carlo_button.setStyleSheet(
            "QPushButton { text-align: center; }"
        )

        self.reports_button = QPushButton("Reports")
        self.exit_button = QPushButton("Exit")

        for button in (
            self.portfolio_builder_button,
            self.portfolio_button,
            self.chart_viewer_button,
            self.monte_carlo_button,
            self.reports_button,
            self.exit_button,
        ):
            button.setMinimumHeight(48)
            layout.addWidget(button)

        layout.addStretch()

        status = QLabel(
            "Version 5.3 Report Center"
        )
        status.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(status)

        self.portfolio_builder_button.clicked.connect(
            self.open_portfolio_builder
        )
        self.portfolio_button.clicked.connect(
            self.open_portfolio_window
        )
        self.chart_viewer_button.clicked.connect(
            self.open_chart_viewer
        )
        self.reports_button.clicked.connect(
            self.open_report_center
        )
        self.exit_button.clicked.connect(self.close)

    def open_portfolio_builder(self):
        """
        Open the Portfolio Builder window.
        """

        window = PortfolioBuilderWindow(self)
        window.exec()

    def open_portfolio_window(self):
        """
        Open the saved portfolio analysis window.
        """

        window = PortfolioWindow(self)
        window.exec()

    def open_report_center(self):
        """
        Open the Report Center window.
        """

        window = ReportCenterWindow(self)
        window.exec()

    def open_chart_viewer(self):
        """
        Open the portfolio Chart Viewer.
        """

        window = ChartViewerWindow(self)
        window.exec()

    def open_monte_carlo_window(self, analysis=None):
        """
        Open the Monte Carlo analysis window.

        If an analysis is supplied, select it automatically.
        """

        window = MonteCarloWindow(self)

        if analysis is not None:
            index = window.analysis_selector.findData(
                analysis
            )

            if index >= 0:
                window.analysis_selector.setCurrentIndex(
                    index
                )

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
