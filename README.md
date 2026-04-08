# Auth Component Detector

A web application that scrapes websites and detects authentication components — login forms, password fields, OAuth/SSO buttons, and forgot-password links — using a multi-signal scoring algorithm.

Built as a technical assessment for **Get Covered LLC** (AI Engineer role).

## Architecture

```
┌──────────────────────────────────────────────────────────┐
│                  Frontend (React + TypeScript)            │
│  URL Input → API Client (Axios) → Result Cards + Code    │
└────────────────────────┬─────────────────────────────────┘
                         │ POST /api/scrape
                         ▼
┌──────────────────────────────────────────────────────────┐
│                  Backend (Python FastAPI)                 │
│  ┌────────────┐  ┌──────────────┐  ┌──────────────────┐  │
│  │  Routers   │→ │   Scraper    │→ │  Auth Detector   │  │
│  │            │  │  Orchestrator│  │  (Multi-signal    │  │
│  │            │  │              │  │   scoring engine) │  │
│  └────────────┘  └──────┬───────┘  └──────────────────┘  │
│                   ┌─────┴──────┐                          │
│                   ▼            ▼                          │
│          ┌──────────────┐ ┌──────────────┐               │
│          │Static Scraper│ │  JS Scraper  │               │
│          │(requests+BS4)│ │ (Playwright) │               │
│          └──────────────┘ └──────────────┘               │
└──────────────────────────────────────────────────────────┘
```

## Features

- **Multi-signal detection**: Scores authentication components across 5+ signals (password inputs, username fields, submit buttons, form actions, CSS/ID keywords)
- **Dual scraping**: Static HTML (requests + BeautifulSoup4) for fast server-rendered pages, Playwright for JavaScript SPAs
- **Confidence scoring**: Each detected component has a 0-100% confidence score
- **Pre-scraped examples**: 5 demo sites (GitHub, Heroku Test App, SauceDemo, TestFire, Practice Test Automation)
- **CSS selector generation**: Precise selectors for each detected component
- **Copy-to-clipboard**: One-click HTML snippet copying with syntax highlighting

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Backend | Python 3.12, FastAPI, Pydantic |
| Scraping | BeautifulSoup4, Playwright, Requests |
| Frontend | React 18, TypeScript, Vite, Tailwind CSS |
| Syntax Highlighting | react-syntax-highlighter (Prism) |
| Deployment | Docker, Docker Compose |

## Quick Start

### Option 1: Docker Compose (recommended)

```bash
git clone https://github.com/yashpatil582/auth-component-detector.git
cd auth-component-detector
docker compose up --build
```

- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- API Docs (Swagger): http://localhost:8000/docs

### Option 2: Local Development

**Backend:**
```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
playwright install chromium
uvicorn main:app --reload --port 8000
```

**Frontend (separate terminal):**
```bash
cd frontend
pnpm install
pnpm dev
```

- Frontend: http://localhost:5173 (proxies API to backend)
- Backend: http://localhost:8000

### Option 3: Live Deployment

The app is deployed and accessible online:

- **Frontend (GitHub Pages)**: https://yashpatil582.github.io/auth-component-detector/
- **Backend API**: https://auth-component-detector-api.onrender.com
- **API Docs**: https://auth-component-detector-api.onrender.com/docs

> Note: The Render free tier spins down after inactivity. The first request may take ~30s to cold-start.

### Seed Example Data

To regenerate the pre-scraped demo data:
```bash
python scripts/seed_examples.py
```

## API Endpoints

### `POST /api/scrape`
Scrape a URL and detect authentication components.

**Request:**
```json
{
  "url": "https://github.com/login",
  "use_js_rendering": false,
  "timeout": 15
}
```

**Response:**
```json
{
  "url": "https://github.com/login",
  "title": "Sign in to GitHub",
  "scraped_at": "2025-01-15T12:00:00Z",
  "rendering_method": "static",
  "auth_components": [
    {
      "component_type": "login_form",
      "html_snippet": "<form action=\"/session\" method=\"post\">...</form>",
      "selector": "form[action='/session']",
      "confidence": 0.95,
      "attributes": {"action": "/session", "method": "post"}
    }
  ],
  "full_page_has_auth": true,
  "detection_summary": "Found 1 login form, 1 forgot-password link (max confidence: 100%)",
  "scrape_duration_ms": 350
}
```

### `GET /api/examples`
Returns pre-scraped results for 5 demo websites.

### `GET /api/health`
Health check with Playwright availability status.

## Detection Algorithm

The auth detector uses a multi-phase, multi-signal approach:

1. **Form scan**: Finds `<form>` elements and scores them by: password input (+0.4), username/email field (+0.2), submit button (+0.2), auth-related action URL (+0.1), keyword matches in attributes (+0.1)

2. **Formless scan**: For SPAs without `<form>` tags — finds password inputs and walks up the DOM to locate the nearest meaningful container

3. **OAuth detection**: Identifies buttons/links referencing Google, GitHub, Facebook, Apple, Microsoft, or generic SSO/SAML

4. **Forgot password**: Detects account recovery links

5. **Deduplication**: Nested components are merged and results are ranked by confidence

## Pre-Scraped Demo Sites

| Site | URL | Rendering | Components Found |
|------|-----|-----------|-----------------|
| GitHub | github.com/login | Static | Login form, forgot password |
| ParaBank | parabank.parasoft.com/parabank/index.htm | Static | Login form, forgot password |
| SauceDemo | saucedemo.com | JavaScript (React) | Login form |
| Altoro Mutual | demo.testfire.net/login.jsp | Static | Login form |
| Practice Test | practicetestautomation.com | Static | Login form |

## Design Decisions

- **FastAPI over Flask**: Async support for Playwright, auto-generated OpenAPI docs, Pydantic validation
- **Multi-signal scoring over regex**: Reduces false positives; a search bar won't be flagged as a login form
- **Dual scraping strategy**: Static-first for speed (~200ms), JS rendering opt-in for SPAs (~5s)
- **Pre-seeded examples**: Ensures the demo works immediately without network dependencies
- **Tailwind CSS**: Clean, professional UI without component library overhead
- **Monorepo**: Single repo for easy review, Docker Compose for one-command setup

## Project Structure

```
auth-component-detector/
├── backend/
│   ├── main.py                  # FastAPI app entry point
│   ├── config.py                # Settings
│   ├── routers/
│   │   ├── scrape.py            # POST /api/scrape
│   │   └── examples.py          # GET /api/examples
│   ├── services/
│   │   ├── auth_detector.py     # Core detection algorithm
│   │   ├── scraper.py           # Orchestrator
│   │   ├── static_scraper.py    # requests + BeautifulSoup
│   │   └── js_scraper.py        # Playwright
│   ├── models/
│   │   └── schemas.py           # Pydantic models
│   ├── data/
│   │   └── examples.json        # Pre-scraped demo data
│   └── tests/
│       └── test_auth_detector.py
├── frontend/
│   └── src/
│       ├── App.tsx
│       ├── api/client.ts
│       ├── types/index.ts
│       ├── pages/               # Home (Scanner), Examples
│       └── components/          # UrlInput, ResultCard, CodeBlock, etc.
├── scripts/
│   └── seed_examples.py
├── docker-compose.yml
└── README.md
```

## Running Tests

```bash
cd backend
python -m pytest tests/ -v
```
