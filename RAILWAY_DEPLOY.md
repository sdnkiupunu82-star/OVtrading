# Railway deployment quick guide

## Required Railway service variables

- `DATABASE_URL` = the connection URL from the Railway PostgreSQL service
- `DATA_PROVIDER=demo`
- `BROKER_MODE=paper`
- `IDX_API_KEY=` (leave empty unless an official provider is configured)
- `CORS_ORIGINS=*`

## Expected deployment flow

GitHub → Railway Build → root Dockerfile → FastAPI + frontend → PostgreSQL → `/api/health`

The public root URL should show the StockAnalyzer dashboard. `/api/health` should return JSON with `status: ok`.
