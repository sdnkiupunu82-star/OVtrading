from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.db.session import Base, engine, SessionLocal
from app.models.models import PaperAccount
from app.api.routes import router

Base.metadata.create_all(bind=engine)
with SessionLocal() as db:
    if not db.query(PaperAccount).first():
        db.add(PaperAccount(name="Demo Investor", cash=100_000_000)); db.commit()

app = FastAPI(title=settings.app_name, version="3.2.0")
app.add_middleware(CORSMiddleware, allow_origins=[x.strip() for x in settings.cors_origins.split(',')], allow_credentials=True, allow_methods=["*"], allow_headers=["*"])
app.include_router(router)
