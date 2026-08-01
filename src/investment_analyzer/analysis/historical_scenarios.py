"""
Definitions of historical market stress scenarios.

Dates are expressed as analysis windows for portfolio
stress testing. Monthly portfolio returns are used by
ScenarioAnalyzer.
"""


HISTORICAL_SCENARIOS = {
    "financial_crisis_2008": {
        "name": "2008 Financial Crisis",
        "start_date": "2007-10-01",
        "end_date": "2009-03-31",
        "description": (
            "Global financial crisis and major equity-market decline "
            "from the 2007 market peak through the March 2009 bottom."
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
}
