import json
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.models.models import PaperAccount, PaperPosition, PaperOrder, Strategy
from app.services.data_provider import DemoMarketDataProvider, IDXProvider
from app.services.analytics import indicators, prediction, score
from app.services.broker import PaperBroker
from app.services.backtest import BacktestConfig, run_backtest
from app.services.risk import RiskConfig, RiskEngine
from app.services.robot import PaperRobot
from app.core.config import settings

router=APIRouter(prefix="/api")
provider=IDXProvider(settings.idx_api_key) if settings.data_provider=="idx" else DemoMarketDataProvider()
broker=PaperBroker(); risk=RiskEngine()

class OrderIn(BaseModel):
    account_id:int=1; symbol:str=Field(min_length=2,max_length=10); side:str; qty:int=Field(gt=0); price:float=Field(gt=0)
class StrategyIn(BaseModel): name:str; config:dict
class BacktestIn(BaseModel):
    symbol:str="BBCA"; initial_cash:float=100_000_000; risk_per_trade:float=0.01; stop_loss_pct:float=0.05; take_profit_pct:float=0.10; trailing_stop_pct:float=0.03; fee_rate:float=0.0015; slippage_pct:float=0.0005; max_position_pct:float=0.25
class RobotScanIn(BaseModel): symbols:list[str]=["BBCA","BBRI","BMRI","TLKM","ASII"]; equity:float=100_000_000; day_start_equity:float=100_000_000; peak_equity:float=100_000_000

@router.get("/health")
def health(): return {"status":"ok","version":"3.2.0","data_provider":settings.data_provider,"broker_mode":settings.broker_mode,"live_trading_enabled":False}

@router.get("/analysis/{symbol}")
def analysis(symbol:str):
    try: df=provider.history(symbol.upper())
    except NotImplementedError as e: raise HTTPException(503,str(e))
    pred=prediction(df); return {"symbol":symbol.upper(),"last_price":round(float(df.close.iloc[-1]),2),"indicators":indicators(df),"prediction":pred,"score":score(df,pred),"data_mode":settings.data_provider}

@router.post("/backtest")
def backtest(payload:BacktestIn):
    try: df=provider.history(payload.symbol.upper(), days=1200); cfg=BacktestConfig(**payload.model_dump(exclude={"symbol"})); return {"symbol":payload.symbol.upper(),"data_mode":settings.data_provider,"config":payload.model_dump(),"result":run_backtest(df,cfg)}
    except (ValueError,NotImplementedError) as e: raise HTTPException(400,str(e))

@router.post("/robot/scan")
def robot_scan(payload:RobotScanIn):
    try: return {"mode":"PAPER","running":False,"results":PaperRobot(provider,broker,risk).scan(payload.symbols,payload.equity,payload.day_start_equity,payload.peak_equity)}
    except NotImplementedError as e: raise HTTPException(503,str(e))

@router.post("/paper/account")
def create_account(db:Session=Depends(get_db)):
    a=PaperAccount(); db.add(a); db.commit(); db.refresh(a); return {"id":a.id,"name":a.name,"cash":a.cash}

@router.get("/paper/account/{account_id}")
def account(account_id:int,db:Session=Depends(get_db)):
    a=db.get(PaperAccount,account_id)
    if not a: raise HTTPException(404,"Account tidak ditemukan")
    positions=db.query(PaperPosition).filter_by(account_id=account_id).all(); orders=db.query(PaperOrder).filter_by(account_id=account_id).order_by(PaperOrder.id.desc()).limit(50).all()
    return {"cash":a.cash,"positions":[{"symbol":p.symbol,"qty":p.qty,"avg_price":p.avg_price} for p in positions],"orders":[{"id":o.id,"symbol":o.symbol,"side":o.side,"qty":o.qty,"price":o.price,"status":o.status,"created_at":o.created_at.isoformat()} for o in orders]}

@router.post("/paper/order")
def paper_order(payload:OrderIn,db:Session=Depends(get_db)):
    side=payload.side.upper(); symbol=payload.symbol.upper()
    if side not in ("BUY","SELL"): raise HTTPException(400,"side harus BUY atau SELL")
    a=db.get(PaperAccount,payload.account_id)
    if not a: raise HTTPException(404,"Account tidak ditemukan")
    fee=payload.qty*payload.price*0.0015; gross=payload.qty*payload.price; pos=db.query(PaperPosition).filter_by(account_id=a.id,symbol=symbol).first()
    if side=="BUY":
        if a.cash<gross+fee: raise HTTPException(400,"Saldo paper tidak cukup")
        a.cash-=gross+fee
        if not pos: pos=PaperPosition(account_id=a.id,symbol=symbol,qty=0,avg_price=0); db.add(pos)
        pos.avg_price=((pos.qty*pos.avg_price)+(payload.qty*payload.price))/(pos.qty+payload.qty); pos.qty+=payload.qty
    else:
        if not pos or pos.qty<payload.qty: raise HTTPException(400,"Posisi tidak cukup")
        a.cash+=gross-fee; pos.qty-=payload.qty
        if pos.qty==0: db.delete(pos)
    o=PaperOrder(account_id=a.id,symbol=symbol,side=side,qty=payload.qty,price=payload.price); db.add(o); db.commit(); db.refresh(o)
    return {"status":"FILLED","order_id":o.id,"cash":a.cash,"fee":fee}

@router.post("/strategies")
def create_strategy(payload:StrategyIn,db:Session=Depends(get_db)):
    s=Strategy(name=payload.name,config_json=json.dumps(payload.config)); db.add(s); db.commit(); db.refresh(s); return {"id":s.id,"name":s.name,"config":payload.config}
@router.get("/strategies")
def strategies(db:Session=Depends(get_db)):
    return [{"id":s.id,"name":s.name,"active":s.active,"config":json.loads(s.config_json)} for s in db.query(Strategy).all()]
