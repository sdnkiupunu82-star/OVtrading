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

## 3. Deploy the backend on Railway

The repository contains `railway.json` and `backend/Dockerfile`.

1. Push the repository to GitHub.
2. Create a Railway project.
3. Deploy the GitHub repository.
4. Add a PostgreSQL service.
5. Set Railway variables, at minimum:

```text
DATABASE_URL=<Railway PostgreSQL connection string>
CORS_ORIGINS=<your frontend URL>
DATA_PROVIDER=demo
BROKER_MODE=paper
IDX_API_KEY=
```

6. Railway will build the backend using `backend/Dockerfile`.
7. Verify `/api/health`.

The current Docker Compose setup serves frontend + API together. For a production split deployment, serve `frontend/` from a static host and point it to the API URL with `window.STOCKANALYZER_API` before deployment.

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
