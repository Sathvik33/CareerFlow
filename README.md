# CareerFlow 🚀

> **Autonomous Agentic AI Job Search, Hybrid Matching & Career Intelligence Platform**

CareerFlow is an end-to-end autonomous job search assistant that unifies multi-channel job discovery, hybrid semantic matching, resume gap analysis, and application pipeline tracking. Built with **FastAPI**, **LangGraph**, **PostgreSQL with pgvector**, and **React 19**, CareerFlow actively scrapes top job boards, scores postings against your resume, uncovers skill gaps, researches hiring companies via autonomous ReAct agents, and delivers daily leads directly to your inbox and Telegram.

---

## 📑 Table of Contents

- [Key Features](#-key-features)
- [System Architecture](#-system-architecture)
- [Tech Stack](#-tech-stack)
- [Project Structure](#-project-structure)
- [Prerequisites](#-prerequisites)
- [Getting Started](#-getting-started)
  - [1. Database Setup (pgvector)](#1-database-setup-pgvector)
  - [2. Backend Setup](#2-backend-setup)
  - [3. Database Migrations (Alembic)](#3-database-migrations-alembic)
  - [4. Frontend Setup](#4-frontend-setup)
- [Environment Configuration](#-environment-configuration)
- [Running the Application](#-running-the-application)
- [Testing & Smoke Tests](#-testing--smoke-tests)
- [API Overview](#-api-overview)
- [License](#-license)

---

## ✨ Key Features

- **Multi-Source Job Ingestion**:
  - **Direct REST/JSON APIs**: Greenhouse, Lever, RemoteOK, Himalayas, Adzuna, USAJobs.
  - **JobSpy Scraping Engine**: Headless TLS emulation for LinkedIn, Indeed, Glassdoor, Google Jobs, ZipRecruiter, and Naukri.
  - **Headless Browser Crawling**: Crawlee + Playwright for dynamic, JavaScript-rendered boards like Wellfound and WorkAtAStartup.
- **Hybrid Matching Engine**:
  - **Dense Semantic Embeddings**: 384-dimensional vector embeddings powered by `SentenceTransformer('all-MiniLM-L6-v2')` and PostgreSQL `pgvector`.
  - **Sparse Keyword Match**: Okapi BM25 scoring with soft hyperbolic tangent ($\tanh$) normalization.
  - **Weighted Scoring**:
    $$\text{Final Score} = (0.7 \times \text{Semantic Score}) + (0.3 \times \text{BM25 Score}) + \text{Remote Bonus (+5)}$$
- **Agentic LangGraph Workflow**:
  - Orchestrates job collection, deduplication, structured JD parsing, gap analysis, career trend forecasting, and report generation in a state machine.
- **Autonomous Company Research**:
  - ReAct agent (`create_react_agent`) equipped with DuckDuckGo web search and HTML scraping to summarize company products, culture, and recent news.
- **Real-Time Stream Scan (SSE)**:
  - Watch the agent work live! Server-Sent Events stream pipeline execution steps directly to the interactive dashboard terminal.
- **Full Application Lifecycle Tracker**:
  - Kanban/pipeline management: `matched` ➔ `saved` ➔ `applied` ➔ `interview` ➔ `offer` ➔ `rejected` / `dismissed`.
- **Multi-Channel Delivery**:
  - Automated SMTP emails with attached `careerflow_leads.csv` and Telegram Bot notifications.
- **Automated Scheduling**:
  - Background scheduler (APScheduler) triggers the daily scanning and matching workflow at 21:00 UTC.

---

## 🏗 System Architecture

```mermaid
flowchart TD
    subgraph Frontend ["Frontend (React 19 + Vite)"]
        UI["Dashboard & Job Tracker UI"]
        SSE["SSE Stream Listener (/reports/stream-scan)"]
    end

    subgraph Backend ["Backend (FastAPI + LangGraph)"]
        API["FastAPI REST Endpoints"]
        Scheduler["APScheduler (Daily Cron at 21:00)"]
        Graph["LangGraph Daily Pipeline"]
    end

    subgraph Ingestion ["Ingestion Connectors"]
        APIs["Direct APIs (Greenhouse, Lever, RemoteOK, Adzuna, USAJobs, Himalayas)"]
        JobSpy["JobSpy (LinkedIn, Indeed, Glassdoor, ZipRecruiter, Naukri)"]
        Playwright["Crawlee + Playwright (Wellfound, WorkAtAStartup)"]
    end

    subgraph Intelligence ["AI & Scoring Engine"]
        LLM["LLM: Ollama (qwen2.5:7b) / Groq"]
        ST["SentenceTransformers (all-MiniLM-L6-v2)"]
        BM25["Rank-BM25 Engine"]
        ReAct["ReAct Company Researcher (DuckDuckGo + BS4)"]
    end

    subgraph Storage ["Database Layer"]
        PG[("PostgreSQL 17 + pgvector")]
    end

    subgraph Dispatcher ["Notification Dispatcher"]
        Email["SMTP Email + Leads CSV"]
        TG["Telegram Bot"]
    end

    UI --> API
    SSE -.-> API
    API --> Graph
    Scheduler --> Graph
    Graph --> Ingestion
    Graph --> Intelligence
    Graph --> PG
    Graph --> Dispatcher
```

---

## 🛠 Tech Stack

### Backend
- **Framework**: FastAPI, Uvicorn, Pydantic v2
- **Agentic AI & Orchestration**: LangGraph, LangChain Core, LangChain Ollama / Groq
- **NLP & Search**: `sentence-transformers` (`all-MiniLM-L6-v2`), `rank-bm25`, `pdfplumber`
- **Database & Vectors**: PostgreSQL 17, `pgvector`, SQLAlchemy 2.0, Alembic
- **Scraping & Ingestion**: `python-jobspy`, `crawlee[playwright]`, `beautifulsoup4`, `httpx`
- **Scheduler**: APScheduler
- **Security**: JWT (`python-jose`), bcrypt (`passlib`)

### Frontend
- **Framework**: React 19, Vite
- **Routing**: React Router v7 (`react-router-dom`)
- **HTTP Client**: Axios with Bearer token interceptor
- **Icons & Styling**: Lucide React, Modern CSS3

---

## 📂 Project Structure

```text
CareerFlow/
├── backend/
│   ├── app/
│   │   ├── agents/               # AI agents and connectors
│   │   │   ├── connectors/       # Modular scrapers & API clients
│   │   │   │   ├── adzuna.py
│   │   │   │   ├── greenhouse.py
│   │   │   │   ├── jobspy.py
│   │   │   │   ├── lever.py
│   │   │   │   ├── remoteok.py
│   │   │   │   └── ...
│   │   │   ├── tools/            # Tools for ReAct agents (scraper, DDG search)
│   │   │   ├── bm25_match.py     # Lexical matching
│   │   │   ├── semantic_match.py # Cosine vector similarity
│   │   │   ├── gap_analysis.py   # LLM gap analysis
│   │   │   ├── recommendation.py # Action item generator
│   │   │   ├── researcher.py     # ReAct company researcher
│   │   │   └── url_generator.py  # Query builder from user preferences
│   │   ├── core/                 # Auth & JWT utilities
│   │   ├── db/                   # Database engine & session setup
│   │   ├── models/               # SQLAlchemy ORM schemas
│   │   ├── pipeline/             # LangGraph state machine (daily_pipeline.py)
│   │   ├── routers/              # FastAPI API routes (jobs, resume, reports, etc.)
│   │   ├── schemas/              # Pydantic request/response schemas
│   │   └── scheduler.py          # APScheduler cron configuration
│   ├── scripts/                  # Scraping setup & smoke tests
│   ├── main.py                   # FastAPI server entrypoint
│   ├── requirements.txt          # Python dependencies
│   └── SCRAPING.md               # Scraping configuration & notes
├── frontend/
│   ├── src/
│   │   ├── components/           # Navigation & Layout components
│   │   ├── context/              # AuthContext & live scanning state
│   │   ├── pages/                # Dashboard, Jobs, Preferences, Resume, etc.
│   │   └── services/             # Axios API client
│   ├── package.json
│   └── vite.config.js
├── alembic/                      # Database migrations
├── docker-compose.yml            # PostgreSQL + pgvector container definition
└── README.md
```

---

## 📋 Prerequisites

Ensure you have the following installed on your machine:
- **Python**: 3.11, 3.12, or 3.13 (64-bit)
- **Node.js**: 18.x or later and **npm**
- **Docker & Docker Compose** (for PostgreSQL with `pgvector`)
- **Ollama**: (Optional for local LLM inference) running `qwen2.5:7b`, or a **Groq API Key**.

---

## 🚀 Getting Started

### 1. Database Setup (pgvector)

Start the PostgreSQL container equipped with `pgvector`:

```bash
docker-compose up -d
```

Verify that the database is running:
```bash
docker ps
```

---

### 2. Backend Setup

1. Navigate to the backend directory and create a virtual environment:
   ```bash
   cd backend
   python -m venv .venv
   ```

2. Activate the virtual environment:
   - **Windows (PowerShell)**:
     ```powershell
     .\.venv\Scripts\Activate.ps1
     ```
   - **Linux / macOS**:
     ```bash
     source .venv/bin/activate
     ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

   > [!TIP]
   > On Windows with Python 3.13, JobSpy pins `numpy==1.26.3` which may lack binary wheels. Ensure you run:
   > ```bash
   > pip install "numpy>=2.1,<2.3" "pandas>=2.2,<3" --force-reinstall
   > ```

4. Install Playwright browser binaries for Crawlee:
   ```bash
   python -m playwright install chromium
   ```

---

### 3. Database Migrations (Alembic)

From the project root directory, apply all database migrations:

```bash
alembic upgrade head
```

---

### 4. Frontend Setup

1. Open a new terminal and navigate to `frontend`:
   ```bash
   cd frontend
   npm install
   ```

---

## ⚙️ Environment Configuration

Create a `.env` file in the root directory (and optionally in `backend/`):

```ini
# Database
DATABASE_URL="postgresql+psycopg2://postgres:Sathvik%40333@localhost:5433/careerflow"

# JWT Authentication
SECRET_KEY="your-super-secret-jwt-key"
ALGORITHM="HS256"
ACCESS_TOKEN_EXPIRE_MINUTES=1440
REFRESH_TOKEN_EXPIRE_DAYS=30

# LLM Providers (Ollama or Groq)
GROQ_API_KEY="your_groq_api_key_if_using_groq"

# Job Board API Keys
ADZUNA_APP_ID="your_adzuna_app_id"
ADZUNA_APP_KEY="your_adzuna_app_key"

# Email Notifications (SMTP)
SMTP_EMAIL="your.email@gmail.com"
SMTP_PASSWORD="your-app-specific-password"

# Telegram Notifications (Optional)
TELEGRAM_BOT_TOKEN="your_telegram_bot_token"

# Ingestion Engine Settings
JOBSPY_ENABLED=true
JOBSPY_RESULTS_WANTED=20
JOBSPY_PROXIES=""
CONNECTOR_TIMEOUT_SECONDS=90
```

---

## 🏃 Running the Application

### Start the Backend Server

```bash
cd backend
python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000
```
- API Documentation (Swagger UI): [http://localhost:8000/docs](http://localhost:8000/docs)
- Interactive ReDoc: [http://localhost:8000/redoc](http://localhost:8000/redoc)

### Start the Frontend

```bash
cd frontend
npm run dev
```
- Application Web UI: [http://localhost:5173](http://localhost:5173)

---

## 🧪 Testing & Smoke Tests

Verify that scraping connectors, JobSpy, and Crawlee are operational without running a full matching pipeline:

```bash
cd backend
python -m scripts.smoke_scrape
```

You can optionally specify role and location:
```powershell
$env:SMOKE_ROLE="Frontend Developer"; $env:SMOKE_LOCATION="Remote"; python -m scripts.smoke_scrape
```

---

## 📡 API Overview

| Method | Endpoint | Description |
| :--- | :--- | :--- |
| `POST` | `/user/register` | Register a new user account |
| `POST` | `/user/token` | Login and receive JWT access token |
| `GET` | `/user/me` | Fetch current authenticated user |
| `POST` | `/resume/upload` | Upload PDF resume, extract text, and parse into structured JSON |
| `GET` | `/resume/mine` | Retrieve uploaded resumes and parsed skill breakdowns |
| `POST` | `/preferences/` | Save target roles, locations, remote preference, and salary |
| `GET` | `/jobs/` | List scored and matched jobs with status & score filtering |
| `PUT` | `/jobs/{match_id}/status` | Update pipeline status (`applied`, `interview`, `saved`, etc.) |
| `GET` | `/jobs/pipeline/summary` | Get count aggregations for the application tracker |
| `GET` | `/reports/latest` | Fetch the latest daily career intelligence report |
| `POST` | `/reports/stream-scan` | SSE endpoint triggering the LangGraph pipeline with live logs |
| `POST` | `/reports/email` | Trigger immediate email delivery with attached CSV leads |

---

## 📄 License

This project is licensed under the terms of the [Apache 2.0 License](LICENSE).

