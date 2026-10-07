from dataclasses import dataclass

@dataclass
class RiskConfig:
    risk_per_trade: float = 0.01
    max_position_pct: float = 0.25
    max_daily_loss: float = 0.03
    max_drawdown: float = 0.10
    stop_loss_pct: float = 0.05
    take_profit_pct: float = 0.10
    trailing_stop_pct: float = 0.03

class RiskEngine:
    def __init__(self, config: RiskConfig | None = None):
        self.config = config or RiskConfig()

    def size(self, equity: float, price: float) -> int:
        if equity <= 0 or price <= 0: return 0
        risk_cash = equity * self.config.risk_per_trade
        risk_per_share = price * self.config.stop_loss_pct
        by_risk = int(risk_cash / risk_per_share) if risk_per_share else 0
        by_cap = int((equity * self.config.max_position_pct) / price)
        return max(0, min(by_risk, by_cap))

    def check(self, equity: float, day_start_equity: float, peak_equity: float) -> dict:
        daily_loss = max(0.0, 1 - equity / day_start_equity) if day_start_equity else 0
        drawdown = max(0.0, 1 - equity / peak_equity) if peak_equity else 0
        allowed = daily_loss < self.config.max_daily_loss and drawdown < self.config.max_drawdown
        return {"allowed": allowed, "daily_loss": daily_loss, "drawdown": drawdown,
                "reason": None if allowed else "RISK_LIMIT_REACHED"}
