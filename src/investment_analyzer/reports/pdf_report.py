from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.platypus import (
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)

from investment_analyzer.analysis.portfolio_analyzer import (
    PortfolioAnalyzer,
)

from .base_report import BaseReport


class PDFReport(BaseReport):
    """
    Creates professional PDF portfolio reports.
    """

    def create_portfolio_report(self, portfolio):
        safe_name = portfolio.name.strip().replace(" ", "_")

        if not safe_name:
            safe_name = "Portfolio"

        filename = self.report_path(
            f"{safe_name}_Report.pdf"
        )

        analyzer = PortfolioAnalyzer(portfolio)
        returns = analyzer.monthly_returns()
        growth = analyzer.growth_index(10000)

        document = SimpleDocTemplate(
            str(filename),
            pagesize=letter,
            rightMargin=0.65 * inch,
            leftMargin=0.65 * inch,
            topMargin=0.65 * inch,
            bottomMargin=0.65 * inch,
            title=f"{portfolio.name} Portfolio Analysis Report",
            author="Investment Analyzer",
        )

        styles = getSampleStyleSheet()

        title_style = ParagraphStyle(
            "ReportTitle",
            parent=styles["Title"],
            alignment=TA_CENTER,
            fontSize=20,
            leading=24,
            spaceAfter=8,
        )

        subtitle_style = ParagraphStyle(
            "ReportSubtitle",
            parent=styles["Normal"],
            alignment=TA_CENTER,
            fontSize=10,
            leading=13,
            spaceAfter=16,
        )

        section_style = ParagraphStyle(
            "SectionHeading",
            parent=styles["Heading2"],
            fontSize=14,
            leading=18,
            spaceBefore=10,
            spaceAfter=8,
        )

        body_style = ParagraphStyle(
            "ReportBody",
            parent=styles["BodyText"],
            fontSize=10,
            leading=14,
            spaceAfter=6,
        )

        story = []

        story.append(
            Paragraph(
                "Investment Analyzer",
                title_style,
            )
        )
        story.append(
            Paragraph(
                "Version 5.4<br/>Portfolio Analysis Report",
                subtitle_style,
            )
        )

        story.append(
            Paragraph(
                f"<b>Portfolio:</b> {portfolio.name}",
                body_style,
            )
        )
        story.append(
            Paragraph(
                f"<b>Generated:</b> {self.timestamp}",
                body_style,
            )
        )

        story.append(Spacer(1, 10))

        story.append(
            Paragraph("Holdings", section_style)
        )

        holdings_data = [
            ["Fund", "Allocation"],
        ]

        for holding in portfolio.holdings:
            holdings_data.append(
                [
                    holding.fund.symbol,
                    f"{holding.allocation:.1f}%",
                ]
            )

        holdings_data.append(
            [
                "Total Allocation",
                f"{portfolio.total_allocation:.1f}%",
            ]
        )

        holdings_table = Table(
            holdings_data,
            colWidths=[3.5 * inch, 2.0 * inch],
            hAlign="LEFT",
        )

        holdings_table.setStyle(
            TableStyle(
                [
                    (
                        "BACKGROUND",
                        (0, 0),
                        (-1, 0),
                        colors.lightgrey,
                    ),
                    (
                        "FONTNAME",
                        (0, 0),
                        (-1, 0),
                        "Helvetica-Bold",
                    ),
                    (
                        "FONTNAME",
                        (0, -1),
                        (-1, -1),
                        "Helvetica-Bold",
                    ),
                    (
                        "ALIGN",
                        (1, 0),
                        (1, -1),
                        "RIGHT",
                    ),
                    (
                        "GRID",
                        (0, 0),
                        (-1, -1),
                        0.5,
                        colors.grey,
                    ),
                    (
                        "BOTTOMPADDING",
                        (0, 0),
                        (-1, -1),
                        6,
                    ),
                    (
                        "TOPPADDING",
                        (0, 0),
                        (-1, -1),
                        6,
                    ),
                ]
            )
        )

        story.append(holdings_table)

        story.append(
            Paragraph(
                "Performance Statistics",
                section_style,
            )
        )

        first_month = returns.index.min().strftime("%b %Y")
        last_month = returns.index.max().strftime("%b %Y")

        statistics_data = [
            ["Statistic", "Value"],
            [
                "Analysis Period",
                f"{first_month} - {last_month}",
            ],
            [
                "Months Analyzed",
                f"{len(returns):,}",
            ],
            [
                "CAGR",
                f"{analyzer.cagr():.2%}",
            ],
            [
                "Annualized Average Return",
                f"{analyzer.annualized_return():.2%}",
            ],
            [
                "Annualized Volatility",
                f"{analyzer.annualized_volatility():.2%}",
            ],
            [
                "Maximum Drawdown",
                f"{analyzer.max_drawdown():.2%}",
            ],
            [
                "Sharpe Ratio",
                f"{analyzer.sharpe_ratio():.2f}",
            ],
        ]

        statistics_table = Table(
            statistics_data,
            colWidths=[3.5 * inch, 2.0 * inch],
            hAlign="LEFT",
        )

        statistics_table.setStyle(
            TableStyle(
                [
                    (
                        "BACKGROUND",
                        (0, 0),
                        (-1, 0),
                        colors.lightgrey,
                    ),
                    (
                        "FONTNAME",
                        (0, 0),
                        (-1, 0),
                        "Helvetica-Bold",
                    ),
                    (
                        "ALIGN",
                        (1, 0),
                        (1, -1),
                        "RIGHT",
                    ),
                    (
                        "GRID",
                        (0, 0),
                        (-1, -1),
                        0.5,
                        colors.grey,
                    ),
                    (
                        "BOTTOMPADDING",
                        (0, 0),
                        (-1, -1),
                        6,
                    ),
                    (
                        "TOPPADDING",
                        (0, 0),
                        (-1, -1),
                        6,
                    ),
                ]
            )
        )

        story.append(statistics_table)

        story.append(
            Paragraph(
                "Growth of $10,000",
                section_style,
            )
        )

        growth_data = [
            ["Beginning Value", "$10,000.00"],
            [
                "Ending Value",
                f"${growth.iloc[-1]:,.2f}",
            ],
        ]

        growth_table = Table(
            growth_data,
            colWidths=[3.5 * inch, 2.0 * inch],
            hAlign="LEFT",
        )

        growth_table.setStyle(
            TableStyle(
                [
                    (
                        "GRID",
                        (0, 0),
                        (-1, -1),
                        0.5,
                        colors.grey,
                    ),
                    (
                        "ALIGN",
                        (1, 0),
                        (1, -1),
                        "RIGHT",
                    ),
                    (
                        "BOTTOMPADDING",
                        (0, 0),
                        (-1, -1),
                        6,
                    ),
                    (
                        "TOPPADDING",
                        (0, 0),
                        (-1, -1),
                        6,
                    ),
                ]
            )
        )

        story.append(growth_table)

        story.append(
            Paragraph(
                "Performance Interpretation",
                section_style,
            )
        )

        interpretation = analyzer.interpretation()

        interpretation_labels = [
            ("Growth", "growth"),
            ("Risk", "risk"),
            ("Drawdown", "drawdown"),
            (
                "Risk-Adjusted Performance",
                "risk_adjusted",
            ),
        ]

        for label, key in interpretation_labels:
            story.append(
                Paragraph(
                    f"<b>{label}:</b> "
                    f"{interpretation[key]}",
                    body_style,
                )
            )

        try:
            portfolio.validate()
            validation = "PASSED"
        except ValueError:
            validation = "FAILED"

        story.append(
            Paragraph(
                f"<b>Portfolio Validation:</b> {validation}",
                body_style,
            )
        )

        document.build(story)

        return filename
