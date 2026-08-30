from pathlib import Path

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QDialog,
    QFileDialog,
    QHBoxLayout,
    QLabel,
    QMessageBox,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
)

from investment_analyzer.core.paths import TRANSACTION_DIR
from investment_analyzer.importers.schwab_import_preview import (
    SchwabImportPreview,
    analyze_transactions,
)
from investment_analyzer.importers.schwab_transaction_importer import (
    SchwabTransactionImporter,
)
from investment_analyzer.models.portfolio import Portfolio
from investment_analyzer.core.fund_metadata import get_fund_name


class SchwabImportDialog(QDialog):
    """
    Preview and approve a Schwab transaction import.

    No portfolio changes are made until the user confirms
    the import.
    """

    def __init__(self, portfolio: Portfolio, parent=None):
        super().__init__(parent)

        self.portfolio = portfolio
        self.transactions = []
        self.preview: SchwabImportPreview | None = None
        self.selected_file: Path | None = None

        self.setWindowTitle("Import Schwab Transactions")
        self.resize(950, 650)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(25, 20, 25, 20)
        layout.setSpacing(12)

        title = QLabel("SCHWAB TRANSACTION IMPORT")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)

        title_font = title.font()
        title_font.setPointSize(18)
        title_font.setBold(True)
        title.setFont(title_font)

        layout.addWidget(title)

        self.file_label = QLabel("No CSV file selected.")
        self.file_label.setWordWrap(True)
        layout.addWidget(self.file_label)

        select_button = QPushButton("Select Schwab CSV...")
        select_button.clicked.connect(self.select_file)
        layout.addWidget(select_button)

        self.summary_label = QLabel(
            "Select a Schwab transaction CSV to preview the import."
        )
        self.summary_label.setWordWrap(True)
        layout.addWidget(self.summary_label)

        self.status_label = QLabel("Status: --")
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        status_font = self.status_label.font()
        status_font.setBold(True)
        status_font.setPointSize(14)
        self.status_label.setFont(status_font)

        layout.addWidget(self.status_label)

        self.transaction_table = QTableWidget()
        self.transaction_table.setColumnCount(7)
        self.transaction_table.setHorizontalHeaderLabels(
            [
                "Date",
                "Fund",
                "Fund Name",
                "Action",
                "Shares",
                "Price",
                "Value",
            ]
        )

        self.transaction_table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)

        self.transaction_table.horizontalHeader().setStretchLastSection(True)

        layout.addWidget(self.transaction_table)

        self.message_label = QLabel("")
        self.message_label.setWordWrap(True)
        layout.addWidget(self.message_label)

        button_layout = QHBoxLayout()

        self.cancel_button = QPushButton("Cancel")
        self.import_button = QPushButton("Import Transactions")

        self.import_button.setEnabled(False)

        self.cancel_button.clicked.connect(self.reject)
        self.import_button.clicked.connect(self.accept_import)

        button_layout.addWidget(self.cancel_button)
        button_layout.addWidget(self.import_button)

        layout.addLayout(button_layout)

    def select_file(self):
        """
        Select and preview a Schwab transaction CSV.
        """

        filename, _ = QFileDialog.getOpenFileName(
            self,
            "Select Schwab Transaction CSV",
            str(TRANSACTION_DIR),
            "CSV Files (*.csv)",
        )

        if not filename:
            return

        self.selected_file = Path(filename)

        self.file_label.setText(f"Selected file: {self.selected_file}")

        try:
            importer = SchwabTransactionImporter()

            self.transactions = importer.import_file(self.selected_file)

            self.preview = analyze_transactions(
                self.transactions,
                self.portfolio,
            )

        except Exception as error:
            self.transactions = []
            self.preview = None
            self.import_button.setEnabled(False)

            self.status_label.setText("Status: ERROR")

            self.message_label.setText(f"Unable to preview the Schwab CSV:\n\n{error}")

            self.transaction_table.setRowCount(0)
            return

        self.display_preview()

    def display_preview(self):
        """
        Display the imported transactions and validation results.
        """

        if self.preview is None:
            return

        self.status_label.setText(f"Status: {self.preview.status}")

        self.summary_label.setText(
            f"Transactions: {self.preview.transaction_count}    "
            f"BUY: {self.preview.buy_count}    "
            f"SELL: {self.preview.sell_count}\n"
            f"Date range: {self.preview.first_date} "
            f"to {self.preview.last_date}"
        )

        self.transaction_table.setRowCount(len(self.transactions))

        for row, transaction in enumerate(self.transactions):
            self.transaction_table.setItem(
                row,
                0,
                QTableWidgetItem(transaction.date.strftime("%m/%d/%y")),
            )

            self.transaction_table.setItem(
                row,
                1,
                QTableWidgetItem(transaction.symbol),
            )

            self.transaction_table.setItem(
                row,
                2,
                QTableWidgetItem(get_fund_name(transaction.symbol)),
            )
            self.transaction_table.setItem(
                row,
                3,
                QTableWidgetItem(transaction.action),
            )

            self.transaction_table.setItem(
                row,
                4,
                QTableWidgetItem(f"{transaction.shares:,.3f}"),
            )

            self.transaction_table.setItem(
                row,
                5,
                QTableWidgetItem(f"${transaction.price:,.2f}"),
            )

            self.transaction_table.setItem(
                row,
                6,
                QTableWidgetItem(f"${transaction.value:,.2f}"),
            )

        self.transaction_table.resizeColumnsToContents()

        messages = []

        if self.preview.warnings:
            messages.append(
                "Warnings:\n"
                + "\n".join(f"• {warning}" for warning in self.preview.warnings)
            )

        if self.preview.errors:
            messages.append(
                "Errors:\n" + "\n".join(f"• {error}" for error in self.preview.errors)
            )

        if not messages:
            messages.append("No warnings or errors.")

        self.message_label.setText("\n\n".join(messages))

        self.import_button.setEnabled(self.preview.valid)

    def accept_import(self):
        """
        Confirm and apply the proposed transaction import.
        """

        if self.preview is None or not self.preview.valid:
            return

        confirmation = QMessageBox.question(
            self,
            "Confirm Schwab Import",
            (
                f"Import {self.preview.transaction_count} transaction(s) "
                "into the selected portfolio?\n\n"
                f"BUY: {self.preview.buy_count}\n"
                f"SELL: {self.preview.sell_count}\n\n"
                "This will update the selected portfolio."
            ),
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No,
        )

        if confirmation != QMessageBox.StandardButton.Yes:
            return

        try:
            for transaction in self.transactions:
                self.portfolio.add_transaction(transaction)

        except (ValueError, IndexError) as error:
            QMessageBox.critical(
                self,
                "Import Error",
                f"The Schwab transactions could not be imported:\n\n{error}",
            )
            return

        self.accept()
