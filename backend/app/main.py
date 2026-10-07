import time

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from sqlalchemy.exc import OperationalError

from app.core.config import settings
from app.db.session import Base, engine, SessionLocal
from app.models.models import PaperAccount
from app.api.routes import router


def init_database(max_attempts: int = 10, delay_seconds: int = 3) -> None:
    """Create tables and seed the demo paper account with DB retry support.

    Railway/PostgreSQL can take a few seconds to become reachable while the
    application container is starting. Retrying here prevents a transient
    database startup race from killing an otherwise healthy deployment.
    """
    last_error = None
    for attempt in range(1, max_attempts + 1):
        try:
            Base.metadata.create_all(bind=engine)
            with SessionLocal() as db:
                if not db.query(PaperAccount).first():
                    db.add(PaperAccount(name="Demo Investor", cash=100_000_000))
                    db.commit()
            return
        except OperationalError as exc:
            last_error = exc
            if attempt == max_attempts:
                raise
            print(f"Database connection attempt {attempt}/{max_attempts} failed; retrying...")
            time.sleep(delay_seconds)

    if last_error:
        raise last_error


init_database()

app = FastAPI(title=settings.app_name, version="3.2.0")

_cors_origins = [x.strip() for x in settings.cors_origins.split(",") if x.strip()]
_cors_is_wildcard = "*" in _cors_origins
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"] if _cors_is_wildcard else _cors_origins,
    allow_credentials=False if _cors_is_wildcard else True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# API routes must be registered before the catch-all frontend mount.
app.include_router(router)

# Serve the production frontend from the same Railway service.
# This removes the need for a second static-hosting service.
app.mount("/", StaticFiles(directory="frontend", html=True), name="frontend")
