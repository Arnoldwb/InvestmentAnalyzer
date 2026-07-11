from dataclasses import dataclass, field
from pathlib import Path
import pandas as pd

@dataclass
class Fund:
    symbol:str
    data: pd.DataFrame = field(default_factory=pd.DataFrame)

    def load_data(self):
        project_root=Path(__file__).resolve().parents[3]
        csv_file=project_root/'data'/f'{self.symbol}.csv'
        if not csv_file.exists():
            raise FileNotFoundError(csv_file)
        self.data=pd.read_csv(csv_file)
        self.data.columns=[c.strip() for c in self.data.columns]
        self.data['Date']=pd.to_datetime(self.data['Date'],errors='coerce')
        self.data['Adj Close']=pd.to_numeric(self.data['Adj Close'],errors='coerce')
        self.data=self.data.dropna(subset=['Date','Adj Close']).sort_values('Date').reset_index(drop=True)
        return self

    @property
    def current_price(self):
        return float(self.data['Adj Close'].iloc[-1])

    @property
    def first_price(self):
        return float(self.data['Adj Close'].iloc[0])

    @property
    def first_date(self):
        return self.data['Date'].iloc[0]

    @property
    def last_date(self):
        return self.data['Date'].iloc[-1]

    @property
    def number_of_days(self):
        return (self.last_date-self.first_date).days

    def monthly_returns(self):
        p=self.data.set_index('Date')['Adj Close'].resample('ME').last()
        return p.pct_change().dropna()

    def yearly_returns(self):
        p=self.data.set_index('Date')['Adj Close'].resample('YE').last()
        return p.pct_change().dropna()

    def cagr(self):
        y=self.number_of_days/365.25
        return 0.0 if y<=0 else (self.current_price/self.first_price)**(1/y)-1

    def __len__(self):
        return len(self.data)

    def __repr__(self):
        return f"Fund(symbol='{self.symbol}', rows={len(self)}, current={self.current_price:.2f})"
