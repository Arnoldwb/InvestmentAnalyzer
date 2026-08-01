"""
Definitions of historical market stress scenarios.

Dates are expressed as analysis windows for portfolio
stress testing. Monthly portfolio returns are used by
ScenarioAnalyzer.
"""


HISTORICAL_SCENARIOS = {
    "bear_market_2002": {
        "name": "2002 Bear Market",
        "start_date": "2002-03-01",
        "end_date": "2002-09-30",
        "description": (
            "Market decline associated with the final phase of the "
            "2000-2002 bear market and technology-sector collapse."
        ),
    },
    "financial_crisis_2008": {
        "name": "2008 Financial Crisis",
        "start_date": "2007-10-01",
        "end_date": "2009-03-31",
        "description": (
            "Global financial crisis and major equity-market decline "
            "from the 2007 market peak through the March 2009 bottom."
        ),
    },
    "correction_2011": {
        "name": "2011 Market Correction",
        "start_date": "2011-04-01",
        "end_date": "2011-09-30",
        "description": (
            "Market correction associated with European sovereign-debt "
            "concerns, U.S. debt-ceiling uncertainty, and slowing growth."
        ),
    },
    "covid_crash_2020": {
        "name": "2020 COVID Crash",
        "start_date": "2020-02-01",
        "end_date": "2020-03-31",
        "description": (
            "Rapid global market decline associated with the onset "
            "of the COVID-19 pandemic."
        ),
    },
    "bear_market_2022": {
        "name": "2022 Bear Market",
        "start_date": "2021-12-01",
        "end_date": "2022-09-30",
        "description": (
            "Broad market decline during a period of high inflation, "
            "rapid interest-rate increases, and tightening monetary policy."
        ),
    },
}
