from abc import ABC, abstractmethod
from datetime import datetime, timedelta
import numpy as np
import pandas as pd

class MarketDataProvider(ABC):
    @abstractmethod
    def history(self, symbol: str, days: int = 400) -> pd.DataFrame: ...

class DemoMarketDataProvider(MarketDataProvider):
    def history(self, symbol: str, days: int = 400) -> pd.DataFrame:
        seed = sum(ord(c) for c in symbol)
        rng = np.random.default_rng(seed)
        dates = pd.bdate_range(end=datetime.now(), periods=days)
        base = 5000 + (seed % 4000)
        returns = rng.normal(0.00035, 0.018, days)
        close = base * np.cumprod(1 + returns)
        open_ = close * (1 + rng.normal(0, .004, days))
        high = np.maximum(open_, close) * (1 + rng.uniform(.001, .015, days))
        low = np.minimum(open_, close) * (1 - rng.uniform(.001, .015, days))
        volume = rng.integers(5_000_000, 60_000_000, days)
        return pd.DataFrame({"ts": dates, "open": open_, "high": high, "low": low, "close": close, "volume": volume})

class IDXProvider(MarketDataProvider):
    """Adapter placeholder for licensed IDX/Data Vendor feed. Keep credentials server-side."""
    def __init__(self, api_key: str):
        self.api_key = api_key
    def history(self, symbol: str, days: int = 400) -> pd.DataFrame:
        raise NotImplementedError("Pasang endpoint/vendor IDX berlisensi di adapter ini.")
