# StockAnalyzer Pro V3.2 — GitHub Ready

StockAnalyzer Pro is a full-stack stock-analysis and paper-trading application with a premium dark trading UI, FastAPI backend, PostgreSQL storage, AI/technical analysis, risk controls, server-side backtesting, and a paper robot scanner.

> **Important:** this release uses `DATA_PROVIDER=demo` by default. Demo prices are synthetic and are not live IDX prices. Live broker execution is disabled.

## What is new in V3.2

- GitHub-ready repository structure
- `.gitignore`, `.env.example`, security policy and contribution guide
- GitHub Actions validation for Python and JavaScript
- Railway deployment configuration (`railway.json`)
- Docker Compose for local full-stack use
- API health version updated to `3.2.0`
- Paper Trading remains the default and safest mode
- Production secrets are kept out of source control

## 1. Upload to GitHub

### Option A — GitHub website

1. Create a new repository on GitHub, for example `stockanalyzer-pro`.
2. Open the repository and choose **Add file → Upload files**.
3. Extract this ZIP on your computer.
4. Upload **all files and folders inside the extracted project**.
5. Commit to `main`.

Do not upload `.env`. The repository already includes `.env.example` as a safe template.

### Option B — Git command

```bash
git init
git add .
git commit -m "StockAnalyzer Pro V3.2"
git branch -M main
git remote add origin YOUR_GITHUB_REPOSITORY_URL
git push -u origin main
```

## 2. Run locally

Install Docker Desktop, then:

```bash
docker compose up --build
```

Open:

- Web app: `http://localhost:8080`
- API docs: `http://localhost:8000/docs`
- API health: `http://localhost:8000/api/health`

Stop the stack with:

```bash
docker compose down
```

## 3. Deploy the full application on Railway

This V3.2 package is configured so **one Railway service serves both the frontend and FastAPI backend**. The repository root contains the production `Dockerfile`, and `railway.json` points Railway to that file.

1. Push the repository to GitHub.
2. Create a Railway project and deploy the GitHub repository.
3. Add a **PostgreSQL** service to the same Railway project.
4. In the StockAnalyzer service, add these variables:

```text
DATABASE_URL=<Railway PostgreSQL connection string>
DATA_PROVIDER=demo
BROKER_MODE=paper
IDX_API_KEY=
CORS_ORIGINS=*
```

`DATABASE_URL` is required for persistent paper-trading data. Do not commit the real database URL or API keys to GitHub.

5. Railway will build the root `Dockerfile`. The image contains both `backend/` and `frontend/`.
6. The public Railway URL opens the StockAnalyzer web interface directly.
7. The API health endpoint is:

```text
https://YOUR-RAILWAY-DOMAIN/api/health
```

The application now retries the PostgreSQL connection during startup to tolerate a short Railway database startup delay.

### Important

- `DATA_PROVIDER=demo` uses synthetic market data and is not live IDX data.
- `BROKER_MODE=paper` keeps live broker execution disabled.
- For a production frontend/backend split, `window.STOCKANALYZER_API` can still be used, but it is not required for the default Railway deployment.

## 4. GitHub Pages limitation

GitHub Pages can host the static frontend, but it **cannot run the FastAPI server or PostgreSQL database**. Therefore:

- GitHub = source-code repository
- GitHub Pages = optional static frontend hosting
- Railway/Docker/server = backend + database

If you want the easiest full-stack deployment, use GitHub for the repository and Railway for the backend/database.

## Safety and trading status

This project is a research and paper-trading application. It is not financial advice. Historical backtests and model predictions do not guarantee future results.

- Live broker: **LOCKED**
- Default trading mode: **PAPER**
- Default market data: **DEMO / SYNTHETIC**
- Production market data: use an official/licensed provider
- Never put broker/API secrets in frontend JavaScript or GitHub source files

## Project structure

```text
stockanalyzer-pro/
├── .github/workflows/validate.yml
├── Dockerfile
├── backend/
│   ├── app/
│   │   ├── api/
│   │   ├── core/
│   │   ├── db/
│   │   ├── models/
│   │   └── services/
│   ├── Dockerfile
│   └── requirements.txt
├── frontend/
│   ├── index.html
│   ├── app.js
│   └── styles.css
├── docker-compose.yml
├── railway.json
├── nginx.conf
├── .env.example
├── .gitignore
├── SECURITY.md
├── CONTRIBUTING.md
└── README.md
```
