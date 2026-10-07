from abc import ABC, abstractmethod

class BrokerAdapter(ABC):
    @abstractmethod
    def place_order(self, symbol: str, side: str, qty: int, price: float): ...

class PaperBroker(BrokerAdapter):
    def place_order(self, symbol, side, qty, price):
        return {"status":"FILLED","mode":"PAPER","symbol":symbol,"side":side,"qty":qty,"price":price}

class LiveBrokerAdapter(BrokerAdapter):
    """Implement per-broker official API/SDK after credentials and trading permissions are configured."""
    def place_order(self, symbol, side, qty, price):
        raise NotImplementedError("Live broker belum dikonfigurasi. Paper Trading tetap aktif.")
