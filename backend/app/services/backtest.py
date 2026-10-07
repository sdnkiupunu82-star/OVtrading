from dataclasses import dataclass
import math
import pandas as pd

@dataclass
class BacktestConfig:
    initial_cash: float = 100_000_000
    risk_per_trade: float = 0.01
    stop_loss_pct: float = 0.05
    take_profit_pct: float = 0.10
    trailing_stop_pct: float = 0.03
    fee_rate: float = 0.0015
    slippage_pct: float = 0.0005
    min_probability: float = 0.62
    max_position_pct: float = 0.25


def _features(df: pd.DataFrame) -> pd.DataFrame:
    x = df.copy()
    x["ret1"] = x.close.pct_change()
    x["ret5"] = x.close.pct_change(5)
    x["ma20"] = x.close.rolling(20).mean()
    x["ma50"] = x.close.rolling(50).mean()
    d = x.close.diff()
    gain = d.clip(lower=0).rolling(14).mean()
    loss = (-d.clip(upper=0)).rolling(14).mean()
    x["rsi"] = 100 - 100 / (1 + gain / loss.replace(0, float("nan")))
    x["vol20"] = x.ret1.rolling(20).std()
    x["vol_ratio"] = x.volume / x.volume.rolling(20).mean()
    return x


def _signal(row) -> str:
    if row.ma20 > row.ma50 and 50 <= row.rsi <= 70 and row.vol_ratio >= 1.0 and row.ret5 > 0:
        return "BUY"
    if row.ma20 < row.ma50 or row.rsi >= 75:
        return "SELL"
    return "HOLD"


def run_backtest(df: pd.DataFrame, cfg: BacktestConfig) -> dict:
    x = _features(df).dropna().reset_index(drop=True)
    if len(x) < 80:
        raise ValueError("Data historis tidak cukup untuk backtest")

    cash = float(cfg.initial_cash)
    qty = 0
    entry = 0.0
    highest = 0.0
    trades = []
    equity = []
    peak = cfg.initial_cash
    max_dd = 0.0

    for _, row in x.iterrows():
        price = float(row.close)
        if qty:
            highest = max(highest, price)
            stop = entry * (1 - cfg.stop_loss_pct)
            take = entry * (1 + cfg.take_profit_pct)
            trail = highest * (1 - cfg.trailing_stop_pct)
            reason = None
            if price <= stop: reason = "STOP_LOSS"
            elif price >= take: reason = "TAKE_PROFIT"
            elif price <= trail: reason = "TRAILING_STOP"
            elif _signal(row) == "SELL": reason = "SIGNAL_EXIT"
            if reason:
                fill = price * (1 - cfg.slippage_pct)
                gross = qty * fill
                fee = gross * cfg.fee_rate
                cash += gross - fee
                pnl = (fill - entry) * qty - fee
                trades.append({"side":"SELL","qty":qty,"price":fill,"fee":fee,"pnl":pnl,"reason":reason})
                qty = 0; entry = 0.0; highest = 0.0
        if not qty and _signal(row) == "BUY":
            risk_cash = cash * cfg.risk_per_trade
            risk_per_share = max(price * cfg.stop_loss_pct, 1e-9)
            risk_qty = math.floor(risk_cash / risk_per_share)
            cap_qty = math.floor((cash * cfg.max_position_pct) / (price * (1 + cfg.fee_rate + cfg.slippage_pct)))
            buy_qty = min(risk_qty, cap_qty)
            if buy_qty > 0:
                fill = price * (1 + cfg.slippage_pct)
                gross = buy_qty * fill
                fee = gross * cfg.fee_rate
                if gross + fee <= cash:
                    cash -= gross + fee
                    qty = buy_qty; entry = fill; highest = fill
                    trades.append({"side":"BUY","qty":qty,"price":fill,"fee":fee,"pnl":0.0,"reason":"SIGNAL_ENTRY"})
        value = cash + qty * price
        peak = max(peak, value)
        dd = (value / peak) - 1
        max_dd = min(max_dd, dd)
        equity.append({"ts": row.ts.isoformat() if hasattr(row.ts, "isoformat") else str(row.ts), "equity": value})

    if qty:
        price = float(x.iloc[-1].close)
        fill = price * (1 - cfg.slippage_pct)
        gross = qty * fill; fee = gross * cfg.fee_rate
        cash += gross - fee
        trades.append({"side":"SELL","qty":qty,"price":fill,"fee":fee,"pnl":(fill-entry)*qty-fee,"reason":"END_OF_TEST"})
        qty = 0

    final_equity = cash
    sells = [t for t in trades if t["side"] == "SELL"]
    wins = [t for t in sells if t["pnl"] > 0]
    losses = [t for t in sells if t["pnl"] < 0]
    gross_profit = sum(t["pnl"] for t in wins)
    gross_loss = abs(sum(t["pnl"] for t in losses))
    daily = pd.Series([e["equity"] for e in equity]).pct_change().dropna()
    sharpe = float((daily.mean() / daily.std()) * math.sqrt(252)) if len(daily) > 1 and daily.std() else 0.0
    years = max((x.ts.iloc[-1] - x.ts.iloc[0]).days / 365.25, 1/365.25)
    cagr = (final_equity / cfg.initial_cash) ** (1 / years) - 1
    return {
        "initial_cash": round(cfg.initial_cash, 2), "final_equity": round(final_equity, 2),
        "total_return": round(final_equity / cfg.initial_cash - 1, 6),
        "cagr": round(cagr, 6), "max_drawdown": round(max_dd, 6),
        "win_rate": round(len(wins) / len(sells), 6) if sells else 0,
        "profit_factor": round(gross_profit / gross_loss, 4) if gross_loss else (float("inf") if gross_profit else 0),
        "sharpe": round(sharpe, 4), "trades": len(sells), "gross_profit": round(gross_profit,2),
        "gross_loss": round(gross_loss,2), "fees": round(sum(t["fee"] for t in trades),2),
        "equity_curve": equity, "trades_detail": trades,
    }
