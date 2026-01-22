# Metals, Explained

A learning-focused dashboard for understanding how gold and silver markets respond to macroeconomic forces.

---

## Overview

Metals, Explained is an educational tool designed to help students understand the behavior of precious metals markets. It provides real-time and historical context for gold and silver prices, along with the key macroeconomic indicators that influence them.

The project is intended for students learning about financial markets, macroeconomics, and the Sales & Trading function.

**This is not a trading system, forecasting tool, or investment platform. It is strictly an educational reference.**

---

## Architecture

This project uses a split architecture:

- **Backend**: FastAPI (Python) serving market data and explanations
- **Frontend**: Next.js (React) providing the user interface
- **Charts**: TradingView Lightweight Charts for line and candlestick visualizations

```
Dashboard/
├── backend/               # FastAPI Python API
│   ├── main.py           # API endpoints
│   ├── market_data.py    # Data fetching logic
│   ├── analysis_engine.py# Explanation generation
│   └── requirements.txt
│
├── frontend/             # Next.js React app
│   ├── src/app/         # Pages (8 tabs)
│   ├── src/components/  # Reusable UI components
│   └── src/lib/         # API client
│
└── README.md
```

---

## Getting Started

### Prerequisites

- Python 3.12+
- Node.js 18+
- npm or yarn

### Running Locally

**1. Start the Backend**

```bash
cd backend
pip install -r requirements.txt
uvicorn main:app --reload --port 8000
```

The API will be available at http://localhost:8000

**2. Start the Frontend**

```bash
cd frontend
npm install
npm run dev
```

The frontend will be available at http://localhost:3000

---

## API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/health` | GET | Health check |
| `/market/snapshot` | GET | Current prices, yields, and driver analysis |
| `/market/timeseries` | GET | OHLC price history for charting |
| `/market/explain` | POST | Structured market explanation |
| `/market/refresh` | POST | Clear cache and refresh data |

---

## Features

- Gold and silver price charts with line and candlestick views
- Supporting macro indicators: U.S. 10-Year Treasury yield, DXY, and 20-day realized volatility
- Historical context explaining long-run patterns and their economic mechanisms
- Step-by-step guidance on how to read and interpret charts
- Terminology and glossary for beginners
- Example scenarios demonstrating analytical reasoning
- Manual data refresh with visible timestamps
- Clear distinction between live and demo data modes

---

## Data Sources

- **Yahoo Finance** for market data (gold, silver, DXY, Treasury yields)
- Demo data is used automatically when live feeds are unavailable
- Data refreshes only when the user clicks "Refresh Data" or reloads the page

---

## Deployment

### Backend → Render / Railway / Fly.io

1. Push the `backend/` folder to a repository
2. Set start command: `uvicorn main:app --host 0.0.0.0 --port $PORT`
3. Set Python version to 3.12

### Frontend → Vercel

1. Connect your GitHub repository
2. Set root directory to `frontend/`
3. Add environment variable: `NEXT_PUBLIC_API_BASE_URL=https://your-backend-url.com`

---

## Disclaimer

This application is for educational purposes only. It does not provide investment advice, trading signals, price forecasts, or recommendations of any kind.

---

## Author

Created by **Gurbir Gill**

Accounting & Finance student with an interest in Sales & Trading and market structure.
