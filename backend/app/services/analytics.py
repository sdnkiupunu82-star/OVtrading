import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier

FEATURES = ["ret1","ret5","ma20_ratio","ma50_ratio","vol20","rsi"]

def indicators(df: pd.DataFrame) -> dict:
    c = df["close"]
    d = c.diff(); gain=d.clip(lower=0).rolling(14).mean(); loss=(-d.clip(upper=0)).rolling(14).mean()
    rsi=100-(100/(1+gain/loss.replace(0,np.nan)))
    ma20,ma50,ma200=c.rolling(20).mean(),c.rolling(50).mean(),c.rolling(200).mean()
    ema12,ema26=c.ewm(span=12,adjust=False).mean(),c.ewm(span=26,adjust=False).mean(); macd=ema12-ema26; sig=macd.ewm(span=9,adjust=False).mean()
    return {"rsi14":float(rsi.iloc[-1]),"ma20":float(ma20.iloc[-1]),"ma50":float(ma50.iloc[-1]),"ma200":float(ma200.iloc[-1]),"macd":float(macd.iloc[-1]),"macd_signal":float(sig.iloc[-1]),"volume":float(df.volume.iloc[-1]),"avg_volume20":float(df.volume.rolling(20).mean().iloc[-1])}

def _feature_frame(df):
    x=df.copy(); x["ret1"]=x.close.pct_change(); x["ret5"]=x.close.pct_change(5)
    x["ma20_ratio"]=x.close/x.close.rolling(20).mean()-1; x["ma50_ratio"]=x.close/x.close.rolling(50).mean()-1
    x["vol20"]=x.ret1.rolling(20).std(); x["rsi"]=indicators(x)["rsi14"] if len(x)==1 else 100-(100/(1+x.ret1.clip(lower=0).rolling(14).mean()/(-x.ret1.clip(upper=0).rolling(14).mean()).replace(0,np.nan)))
    x["target"]=(x.close.shift(-5)>x.close).astype(float)
    return x.replace([np.inf,-np.inf],np.nan)

def prediction(df: pd.DataFrame) -> dict:
    x=_feature_frame(df).dropna(subset=FEATURES+["target"]).copy()
    if len(x)<100: return {"probability_up":0.5,"confidence":0.0,"signal":"INSUFFICIENT_DATA","model":"RandomForest","horizon_days":5}
    train=x.iloc[:-1]; model=RandomForestClassifier(n_estimators=250,max_depth=7,min_samples_leaf=3,random_state=42,class_weight="balanced")
    model.fit(train[FEATURES],train.target.astype(int)); p=float(model.predict_proba(x.iloc[[-1]][FEATURES])[0,1])
    confidence=min(0.95,0.5+abs(p-0.5)*1.8); signal="BUY" if p>=.62 else "SELL" if p<=.38 else "HOLD"
    return {"probability_up":round(p,4),"confidence":round(confidence,4),"signal":signal,"model":"RandomForest","horizon_days":5,"training_rows":len(train)}

def score(df,pred):
    ind=indicators(df); technical=50+(10 if ind["ma20"]>ind["ma50"] else -8)+(8 if ind["macd"]>ind["macd_signal"] else -6)+(5 if ind["rsi14"]<70 else -3); technical=max(0,min(100,technical)); prediction_score=pred["probability_up"]*100
    return {"technical":round(technical,1),"prediction":round(prediction_score,1),"total":round(.6*technical+.4*prediction_score,1)}
