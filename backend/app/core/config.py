from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    app_name: str = "StockAnalyzer Pro API"
    database_url: str = "postgresql+psycopg://stock:stock@db:5432/stockanalyzer"
    cors_origins: str = "http://localhost:8080,http://127.0.0.1:8080"
    data_provider: str = "demo"
    idx_api_key: str = ""
    broker_mode: str = "paper"
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

settings = Settings()
