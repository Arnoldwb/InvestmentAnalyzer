from PySide6.QtCore import Qt, QUrl
from PySide6.QtGui import QDesktopServices
from PySide6.QtWidgets import (
    QDialog,
    QFileDialog,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
)

from investment_analyzer.core.fund_data_manager import (
    FundDataManager,
)
from investment_analyzer.core.fund_library import (
    FundLibrary,
)


class FundDataManagerWindow(QDialog):
    """
    Manage Investment Analyzer fund CSV files.
    """

    def __init__(self, parent=None):
        super().__init__(parent)

        self.manager = FundDataManager()
        self.library = FundLibrary()

        self.setWindowTitle("Fund Data Manager")
        self.resize(1000, 650)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(25, 20, 25, 20)
        layout.setSpacing(12)

        title = QLabel("Fund Data Manager")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)

        title_font = title.font()
        title_font.setPointSize(20)
        title_font.setBold(True)
        title.setFont(title_font)

        layout.addWidget(title)

        description = QLabel(
            "Add, validate, and safely remove fund data files."
        )
        description.setAlignment(
            Qt.AlignmentFlag.AlignCenter
        )
        layout.addWidget(description)

        lookup_layout = QHBoxLayout()

        lookup_label = QLabel(
            "Fund / Stock Symbol:"
        )

        self.lookup_symbol = QLineEdit()
        self.lookup_symbol.setPlaceholderText(
            "Example: VBIAX or AAPL"
        )
        self.lookup_symbol.setMaxLength(20)

        self.yahoo_button = QPushButton(
            "Open Yahoo Finance History"
        )
        self.yahoo_button.setMinimumHeight(36)

        lookup_layout.addWidget(lookup_label)
        lookup_layout.addWidget(
            self.lookup_symbol,
            1,
        )
        lookup_layout.addWidget(
            self.yahoo_button
        )

        layout.addLayout(lookup_layout)

        self.table = QTableWidget()
        self.table.setColumnCount(6)

        self.table.setHorizontalHeaderLabels(
            [
                "Symbol",
                "Status",
                "Usable Rows",
                "First Date",
                "Last Date",
                "Used By",
            ]
        )

        self.table.setSelectionBehavior(
            QTableWidget.SelectionBehavior.SelectRows
        )
        self.table.setSelectionMode(
            QTableWidget.SelectionMode.SingleSelection
        )
        self.table.setEditTriggers(
            QTableWidget.EditTrigger.NoEditTriggers
        )

        self.table.horizontalHeader().setStretchLastSection(
            True
        )

        self.table.setColumnWidth(0, 90)
        self.table.setColumnWidth(1, 100)
        self.table.setColumnWidth(2, 110)
        self.table.setColumnWidth(3, 120)
        self.table.setColumnWidth(4, 120)

        layout.addWidget(self.table, 1)

        self.status_label = QLabel("")
        self.status_label.setAlignment(
            Qt.AlignmentFlag.AlignCenter
        )
        layout.addWidget(self.status_label)

        button_layout = QHBoxLayout()

        self.import_button = QPushButton(
            "Import CSV..."
        )
        self.remove_button = QPushButton(
            "Remove Selected Fund"
        )
        self.validate_button = QPushButton(
            "Validate All Funds"
        )
        close_button = QPushButton(
            "Return to Investment Analyzer"
        )

        for button in (
            self.import_button,
            self.remove_button,
            self.validate_button,
            close_button,
        ):
            button.setMinimumHeight(40)
            button_layout.addWidget(button)

        layout.addLayout(button_layout)

        self.table.itemSelectionChanged.connect(
            self.use_selected_symbol
        )

        self.yahoo_button.clicked.connect(
            self.open_yahoo_history
        )
        self.lookup_symbol.returnPressed.connect(
            self.open_yahoo_history
        )

        self.import_button.clicked.connect(
            self.import_csv
        )
        self.remove_button.clicked.connect(
            self.remove_selected
        )
        self.validate_button.clicked.connect(
            self.validate_all_funds
        )
        close_button.clicked.connect(self.accept)

        self.refresh_library()

    def use_selected_symbol(self):
        """
        Put the selected fund symbol into the lookup box.
        """

        row = self.table.currentRow()

        if row < 0:
            return

        item = self.table.item(
            row,
            0,
        )

        if item is None:
            return

        self.lookup_symbol.setText(
            item.text()
        )

    def open_yahoo_history(self):
        """
        Open Yahoo Finance historical data for a symbol.
        """

        symbol = (
            self.lookup_symbol.text()
            .strip()
            .upper()
        )

        if not symbol:
            QMessageBox.warning(
                self,
                "Yahoo Finance Lookup",
                "Enter a fund or stock symbol first.",
            )
            return

        allowed = set(
            "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
            "0123456789.-^="
        )

        if any(
            character not in allowed
            for character in symbol
        ):
            QMessageBox.warning(
                self,
                "Yahoo Finance Lookup",
                "The symbol contains unsupported characters.",
            )
            return

        self.lookup_symbol.setText(symbol)

        url = QUrl(
            "https://finance.yahoo.com/quote/"
            f"{symbol}/history/"
        )

        opened = QDesktopServices.openUrl(url)

        if not opened:
            QMessageBox.warning(
                self,
                "Yahoo Finance Lookup",
                "Unable to open Yahoo Finance "
                "in the web browser.",
            )

    def refresh_library(self):
        """
        Reload and validate the complete fund library.
        """

        entries = self.library.entries()

        self.table.setRowCount(len(entries))

        for row, entry in enumerate(entries):
            first_date = ""
            last_date = ""

            if entry.first_date is not None:
                first_date = entry.first_date.strftime(
                    "%b %d, %Y"
                )

            if entry.last_date is not None:
                last_date = entry.last_date.strftime(
                    "%b %d, %Y"
                )

            used_by = ", ".join(entry.used_by)

            values = [
                entry.symbol,
                entry.status,
                f"{entry.usable_rows:,}",
                first_date,
                last_date,
                used_by,
            ]

            for column, value in enumerate(values):
                item = QTableWidgetItem(str(value))

                if column in (0, 1, 2):
                    item.setTextAlignment(
                        Qt.AlignmentFlag.AlignCenter
                    )

                self.table.setItem(
                    row,
                    column,
                    item,
                )

        errors = sum(
            1
            for entry in entries
            if entry.status == "ERROR"
        )

        warnings = sum(
            1
            for entry in entries
            if entry.status == "WARNING"
        )

        self.status_label.setText(
            f"{len(entries)} fund(s) available — "
            f"{errors} error(s), "
            f"{warnings} warning(s)"
        )

    def validate_all_funds(self):
        """
        Validate all funds and display a summary.
        """

        self.refresh_library()

        entries = self.library.entries()

        errors = sum(
            1
            for entry in entries
            if entry.status == "ERROR"
        )

        warnings = sum(
            1
            for entry in entries
            if entry.status == "WARNING"
        )

        valid = sum(
            1
            for entry in entries
            if entry.status == "VALID"
        )

        QMessageBox.information(
            self,
            "Validation Complete",
            f"{len(entries)} fund(s) checked.\n\n"
            f"Valid: {valid}\n"
            f"Warnings: {warnings}\n"
            f"Errors: {errors}",
        )

    def _validation_message(self, validation):
        """
        Create readable validation details.
        """

        lines = [
            f"Fund: {validation.symbol}",
            f"Status: {validation.status}",
            f"Usable rows: {validation.usable_rows:,}",
        ]

        if validation.errors:
            lines.append("")
            lines.append("Errors:")

            for message in validation.errors:
                lines.append(f"• {message}")

        if validation.warnings:
            lines.append("")
            lines.append("Warnings:")

            for message in validation.warnings:
                lines.append(f"• {message}")

        return "\n".join(lines)

    def import_csv(self):
        """
        Select, validate, and import a CSV file.
        """

        filename, _ = QFileDialog.getOpenFileName(
            self,
            "Import Fund CSV",
            "",
            "CSV Files (*.csv);;All Files (*)",
        )

        if not filename:
            return

        validation = self.manager.validate_file(
            filename
        )

        if not validation.valid:
            QMessageBox.critical(
                self,
                "Invalid Fund Data",
                self._validation_message(
                    validation
                ),
            )
            return

        existing = self.library.get(
            validation.symbol
        )

        replace = False

        if existing is not None:
            answer = QMessageBox.question(
                self,
                "Replace Existing Fund?",
                f"{validation.symbol} already exists.\n\n"
                "Replace the existing CSV with this file?",
                QMessageBox.StandardButton.Yes
                | QMessageBox.StandardButton.No,
                QMessageBox.StandardButton.No,
            )

            if answer != QMessageBox.StandardButton.Yes:
                return

            replace = True

        try:
            result = self.manager.import_file(
                filename,
                replace=replace,
            )

        except Exception as error:
            QMessageBox.critical(
                self,
                "Import Error",
                f"Unable to import the fund:\n\n{error}",
            )
            return

        self.refresh_library()

        action = (
            "replaced"
            if result.replaced
            else "imported"
        )

        QMessageBox.information(
            self,
            "Fund Data Imported",
            f"{result.validation.symbol} was "
            f"successfully {action}.\n\n"
            + self._validation_message(
                result.validation
            ),
        )

    def remove_selected(self):
        """
        Safely remove the selected unused fund.
        """

        row = self.table.currentRow()

        if row < 0:
            QMessageBox.warning(
                self,
                "Remove Fund",
                "Select a fund to remove.",
            )
            return

        symbol_item = self.table.item(
            row,
            0,
        )

        if symbol_item is None:
            return

        symbol = symbol_item.text()

        entry = self.library.get(symbol)

        if entry is None:
            QMessageBox.warning(
                self,
                "Remove Fund",
                f"{symbol} is no longer available.",
            )
            self.refresh_library()
            return

        if entry.used_by:
            portfolios = "\n".join(
                f"• {name}"
                for name in entry.used_by
            )

            QMessageBox.warning(
                self,
                "Fund Is In Use",
                f"{symbol} cannot be removed because "
                "it is used by:\n\n"
                f"{portfolios}",
            )
            return

        answer = QMessageBox.question(
            self,
            "Confirm Fund Removal",
            f"Remove {symbol} from the fund library?\n\n"
            "This will delete its CSV data file.",
            QMessageBox.StandardButton.Yes
            | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No,
        )

        if answer != QMessageBox.StandardButton.Yes:
            return

        try:
            self.manager.remove_fund(symbol)

        except Exception as error:
            QMessageBox.critical(
                self,
                "Remove Fund Error",
                f"Unable to remove {symbol}:\n\n{error}",
            )
            return

        self.refresh_library()

        QMessageBox.information(
            self,
            "Fund Removed",
            f"{symbol} was removed from the fund library.",
        )
