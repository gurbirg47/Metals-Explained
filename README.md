# Metals, Explained

A learning-focused dashboard for understanding how gold and silver markets respond to macroeconomic forces.

**Live Demo:** [metals-explained.vercel.app](https://metals-explained.vercel.app)

---

## Overview

Metals, Explained is an educational tool designed to help students understand the behavior of precious metals markets. It provides real-time and historical context for gold and silver prices, along with the key macroeconomic indicators that influence them.

The project is intended for students learning about financial markets and macroeconomics.

**This is not a trading system, forecasting tool, or investment platform. It is strictly an educational reference.**

---

## Architecture

This is a **Next.js** application with integrated API routes:

```
Dashboard/
├── src/
│   ├── app/                  # Pages and API routes
│   │   ├── api/              # Next.js API endpoints
│   │   │   ├── health/       # Health check
│   │   │   └── market/       # Market data endpoints
│   │   ├── page.tsx          # Today (main dashboard)
│   │   ├── drivers/          # Drivers tab
│   │   ├── history/          # History tab
│   │   └── ...               # Other educational tabs
│   ├── components/           # Reusable UI components
│   └── lib/                  # API client and utilities
├── public/                   # Static assets
├── package.json
└── README.md
```

---

## Getting Started

### Prerequisites

- Node.js 18+
- npm

### Running Locally

```bash
npm install
npm run dev
```

The application will be available at http://localhost:3000

---

## API Endpoints

All endpoints are Next.js API routes (no separate backend required):

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/health` | GET | Health check |
| `/api/market/snapshot` | GET | Current prices, yields, and volatility |
| `/api/market/timeseries` | GET | OHLC price history for charting |
| `/api/market/explain` | POST | Structured market explanation |

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

### Vercel (Recommended)

1. Connect your GitHub repository to Vercel
2. Vercel will auto-detect Next.js and deploy
3. No environment variables required

---

## Disclaimer

This application is for educational purposes only. It does not provide investment advice, trading signals, price forecasts, or recommendations of any kind.

---

## Author

Created by **Gurbir Gill**

Accounting & Finance student with an interest in financial markets.
