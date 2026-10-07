from app.services.analytics import prediction
from app.services.risk import RiskEngine

class PaperRobot:
    def __init__(self, provider, broker, risk=None):
        self.provider = provider
        self.broker = broker
        self.risk = risk or RiskEngine()
        self.running = False

    def scan(self, symbols, equity=100_000_000, day_start_equity=100_000_000, peak_equity=100_000_000):
        guard = self.risk.check(equity, day_start_equity, peak_equity)
        results=[]
        for symbol in symbols:
            df=self.provider.history(symbol.upper())
            pred=prediction(df)
            price=float(df.close.iloc[-1])
            qty=self.risk.size(equity, price) if guard["allowed"] and pred["signal"] == "BUY" else 0
            results.append({"symbol":symbol.upper(),"price":round(price,2),"prediction":pred,"qty":qty,"risk":guard})
        return results
