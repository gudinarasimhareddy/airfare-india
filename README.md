# AirfareX India — Airfare Intelligence & Flight Explorer

> **Production-grade full-stack aviation pricing intelligence platform** merging consumer flight comparison with a research-grade Indian airfare index (APIx), route inflation monitoring, advance booking elasticity curves, data quality auditing, and CPI augmentation simulation.

---

## 🛫 Features

1. **Consumer-Grade Flight Explorer**:
   - High-frequency flight quotes for major Indian domestic sectors: **HYD, DEL, BOM, BLR, MAA, CCU, GOI, PNQ, JAI**.
   - Operating airlines: **IndiGo**, **Air India**, **Akasa Air**, **SpiceJet**, **Air India Express**.
   - Filters by stops (Nonstop, 1 stop), airline, maximum fare, baggage (carry-on vs. 15kg checked bag), and departure time (Morning, Afternoon, Evening).
   - Smart sorting by **Fare Score (Value)**, **Cheapest Fare**, **Fastest Flight**, and **Lowest Emissions (CO₂e)**.
   - Live Flight Status Tracker for any domestic flight number (Gate, Terminal, Schedule, On-time/Delayed status).

2. **Route Intelligence & Network Topology**:
   - Interactive Indian domestic aviation network map with active flight routes and inflation hotspot indicators.
   - Lead-Time Elasticity curves (**T+1, T+7, T+15, T+30, T+45**) tracking dynamic advance booking pricing.
   - Monitored sector table with 30-day price changes, volatility scores, and status badges.
   - One-click **CSV Export** for econometric modeling and offline analysis.

3. **APIx Index Engine**:
   - Daily, Weekly, and Monthly National Airfare Index (**Base Period 2024 = 100**).
   - 5-stage deterministic aggregation pipeline.
   - Advance booking basket weighting and domestic fare decomposition breakdown (Base fare, Taxes & GST, UDF, Convenience).
   - Interactive SVG trend charts for **30D**, **90D**, and **1Y** time horizons.

4. **Data Quality & Audit Center**:
   - Live metrics: Total quotes collected, valid quotes, duplicate deduplication, and IQR outlier screening.
   - Direct airline vs. OTA partner feed health monitoring.
   - DGCA historical backtesting (**MAPE 4.8%**, **Correlation 0.93**).
   - Missing-data, anomaly rate, and 15-minute freshness SLA compliance tracking.

5. **Persistent Saved Trips & Price Alerts**:
   - Fully persistent watchlist stored in **SQLite**.
   - Create custom threshold alerts ("Notify on 8% drop", "Drop below ₹5,000").
   - Direct alert creation from flight result cards.
   - Delete/manage active alerts with immediate persistence.

6. **CPI Augmentation Lab**:
   - Analytical policy simulator modeling how high-frequency airfare inflation flows through to Headline CPI and the Transport sub-index basket.
   - Real-time parameter sliders with instant basis-point impact calculations.

7. **Research API Console**:
   - Interactive REST catalog for central bank researchers (RBI), NSO analysts, and airline revenue teams.
   - Built-in OpenAPI / Swagger UI at `/docs`.

---

## 🛠️ Technology Stack

- **Backend**: Python 3.12, **FastAPI**, **Uvicorn**, **Pydantic v2**, **Starlette**
- **Persistence**: **SQLite3** with Write-Ahead Logging (WAL) mode
- **Frontend**: Vanilla **HTML5**, modern **CSS3** (custom design tokens, glassmorphism, responsive grid, Inter typography), and **JavaScript (ES6+)**
- **Data Visualizations**: Custom dynamic **SVG Charts** and **Interactive Route Heatmap**

---

## 🚀 Getting Started

### 1. Launch the Server

Run the single-command starter:

```powershell
python run_server.py
```

The application will start on:
- **Web App**: [http://127.0.0.1:8000](http://127.0.0.1:8000)
- **Interactive Swagger Docs**: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)
- **ReDoc Specification**: [http://127.0.0.1:8000/redoc](http://127.0.0.1:8000/redoc)

### 2. Run Automated API Tests

```powershell
python tests/test_api.py
```

---

## 📡 REST API Catalog

| Method | Endpoint | Description |
| :--- | :--- | :--- |
| `GET` | `/api/v1/flights/search` | Search flights with filters, baggage options, and sorting |
| `GET` | `/api/v1/flights/status/{flight_no}` | Live domestic flight status, gate, terminal, and aircraft |
| `GET` | `/api/v1/routes` | Monitored city-pair index, 30D changes, volatility |
| `GET` | `/api/v1/routes/{orig}/{dest}/elasticity` | Advance booking elasticity curve (T+1 to T+45) |
| `GET` | `/api/v1/routes/export/csv` | Download complete route intelligence dataset as CSV |
| `GET` | `/api/v1/apix/overview` | National APIx, basket weights, and fare decomposition |
| `GET` | `/api/v1/apix/trend?period=30D` | Time-series data points for SVG index charting |
| `GET` | `/api/v1/alerts` | Get all active price alerts from SQLite |
| `POST` | `/api/v1/alerts` | Create new persistent price alert |
| `DELETE`| `/api/v1/alerts/{id}` | Delete persistent price alert |
| `GET` | `/api/v1/quality` | Data quality audit, MAPE, DGCA correlation, source health |
| `POST` | `/api/v1/cpi-simulation` | Calculate macro CPI impact from observed airfare inflation |
