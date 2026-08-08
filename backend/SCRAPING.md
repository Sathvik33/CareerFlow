# Hybrid scraping setup

CareerFlow uses three ingestion paths:

1. **HTTP/JSON APIs** — Greenhouse, Lever, RemoteOK, Adzuna, etc. (no browser)
2. **JobSpy** — LinkedIn, Indeed, Glassdoor, Google, ZipRecruiter, Naukri
3. **Crawlee + Playwright** — JS-heavy boards (Wellfound, WorkAtAStartup)

## Install

Use a project venv (required on Windows + Python 3.13 — system NumPy 1.26 crashes):

```bash
cd backend
python -m venv .venv
.venv\Scripts\pip install -r requirements.txt
# JobSpy pins numpy==1.26.3; force compatible wheels if pip downgrades:
.venv\Scripts\pip install "numpy>=2.1,<2.3" "pandas>=2.2,<3" --force-reinstall
.venv\Scripts\python -m playwright install chromium
```

`crawlee[playwright]` pulls Playwright; Chromium still needs `playwright install chromium`.

## Environment

| Variable | Purpose |
|----------|---------|
| `JOBSPY_ENABLED` | Default `true`. Set `false` to skip JobSpy boards. |
| `JOBSPY_PROXIES` | Optional comma-separated proxies (`user:pass@host:port` or `host:port`). Recommended for LinkedIn volume. |
| `JOBSPY_RESULTS_WANTED` | Per-site result cap (default `20`, max `50`). |
| `CONNECTOR_TIMEOUT_SECONDS` | Per-connector timeout for scans (default `90`). |
| `ADZUNA_APP_ID` / `ADZUNA_APP_KEY` | Adzuna API (existing). |

## Smoke test

```bash
cd backend
.\.venv\Scripts\python.exe -m scripts.smoke_scrape
# or after Activate.ps1:
python -m scripts.smoke_scrape
```

Optional: `SMOKE_ROLE`, `SMOKE_LOCATION` env vars.

Expect Indeed (or Google / ZipRecruiter fallback) ≥ 10 jobs with ≥ 60% relevance, plus Greenhouse API + non-empty Crawlee HTML. LinkedIn without proxies is best-effort.

Verified locally (2026-08-08): Indeed 15 jobs / 87% relevance, Greenhouse 40 jobs, Crawlee HTML OK, LinkedIn 5 jobs.
