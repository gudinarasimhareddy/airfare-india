# AirfareX India — Technical Architecture Specification

> **Comprehensive Engineering & System Design Document**  
> *Detailed overview of frontend client, FastAPI backend, provider abstraction, scoring engine, security, and persistence.*

---

## 🏗️ High-Level System Architecture

```
                                  +---------------------------------------+
                                  |       AirfareX Web Client (SPA)       |
                                  | (Vanilla HTML5 / CSS3 / ES6 Modules)  |
                                  +-------------------+-------------------+
                                                      |
                                          HTTPS / WSS | REST API + JWT
                                                      v
                                  +---------------------------------------+
                                  |         FastAPI Backend Engine        |
                                  |    (Uvicorn / Pydantic v2 / Starlette)|
                                  +---+---------------+---------------+---+
                                      |               |               |
             +------------------------+               |               +-----------------------+
             v                                        v                                       v
+------------------------+               +------------------------+              +------------------------+
| Flight Search Service  |               | Payment State Machine  |              | Supabase Auth & RLS    |
| - BaseFlightProvider   |               | - Server Authoritative |              | - Multi-tenant Cloud DB|
| - MockDevelopmentProv  |               | - Razorpay Live API    |              | - JWT Token Validation |
| - Amadeus Self-Service |               | - HMAC Sandbox Engine  |              | - SQLite Local Fallback|
| - 15-Min TTL In-Memory |               | - Webhook Replay Guard |              | - Row Level Security   |
+------------------------+               +------------------------+              +------------------------+
             |                                        |                                       |
             v                                        v                                       v
+------------------------+               +------------------------+              +------------------------+
| GDS / NDC Ticketing    |               | Banking & UPI Gateway  |              | PostgreSQL Master DB   |
| - BaseBookingProvider  |               | - Webhook Signature    |              | - Profiles, Bookings,  |
| - Honest Dev Labeling  |               | - Constant-Time HMAC   |              |   Payments, Refunds,   |
+------------------------+               +------------------------+              |   Watchlist, Alerts    |
                                                                                 +------------------------+
```

---

## 🧩 Component Breakdown

### 1. Frontend Web Client (Single Page Application)
- **Architecture:** Zero-dependency, modular Vanilla ES6 Javascript architecture (`app.js`, `api.js`, `auth.js`, `booking.js`, `i18n.js`).
- **Styling System:** Modular CSS with design tokens (`style.css`, `components.css`), full dark-mode glassmorphism, focus-visible accessibility rings, and responsive media queries (320px–1440px).
- **Navigation & URL Sync:** Synchronizes URL parameters (`?tab=...&from=...&to=...&date=...`) via `history.pushState` and `window.onpopstate` without page reloading.

### 2. FastAPI Backend Engine
- **Framework:** FastAPI with Uvicorn ASGI server and asynchronous request handling.
- **Data Validation:** Strict Pydantic v2 data contracts for all API inputs and outputs.
- **Middleware Layer:**
  - `CorrelationIdMiddleware`: Injects a unique `X-Request-ID` into every HTTP transaction.
  - `CORSMiddleware`: Whitelists trusted frontend origins.
  - `ProductionExceptionMiddleware`: Sanitizes internal stack traces in production mode.

### 3. Flight Provider Abstraction Layer (`backend/services/flight_providers/`)
- **`BaseFlightProvider`**: Abstract base class enforcing standard search signatures:
  ```python
  class BaseFlightProvider(ABC):
      @abstractmethod
      async def search_flights(self, params: FlightSearchParams) -> NormalizedSearchResponse:
          pass
  ```
- **`MockDevelopmentProvider`**: High-performance local provider with realistic domestic Indian airline schedules and multi-segment layover routes.
- **`AmadeusFlightProvider`**: Live GDS provider integration with OAuth2 token rotation, rate-limiting, and error fallback.
- **15-Minute TTL Cache (`FlightSearchCache`)**: In-memory cache keyed on sector, date, stops, and filters, preventing unnecessary external provider costs.

### 4. AI Decision & Scoring Engine (`backend/services/ai/`)
- **5-Dimension Flight Scoring:**
  $$\text{Score} = w_p \cdot S_{\text{price}} + w_d \cdot S_{\text{duration}} + w_s \cdot S_{\text{stops}} + w_c \cdot S_{\text{convenience}} + w_v \cdot S_{\text{value}}$$
  - $S_{\text{price}}$: Continuous scaling relative to lowest route fare.
  - $S_{\text{duration}}$: Penalty relative to fastest non-stop flight.
  - $S_{\text{stops}}$: 100 for non-stop, 70 for 1-stop, 40 for 2+ stops.
  - $S_{\text{convenience}}$: Daylight departure slots (06:00–21:00) vs red-eyes.
  - $S_{\text{value}}$: Time-value savings metric (grounded in ₹450/hr travel benchmark).
- **Zero-Key Deterministic Fallback (`RuleBasedAIProvider`)**: Implements rule-based heuristics to guarantee 100% feature availability without external LLM keys.

### 5. Server-Authoritative Booking & Payment Engine
- **Lifecycle:**
  $$\text{DRAFT} \longrightarrow \text{PRICE\_CALCULATED} \longrightarrow \text{PAYMENT\_PENDING} \longrightarrow \text{PAYMENT\_VERIFIED} \longrightarrow \text{BOOKING\_CONFIRMED}$$
- **Zero-Trust Fare Decomposition:**
  $$\text{Total Paid} = \text{Base Fare} + \text{Airline Fuel Surcharge (YQ)} + \text{Airport UDF} + \text{Statutory ASF} + \text{5\% GST} - \text{Discount}$$
- **Anti-Tampering:** If client attempts to send an unverified fare or modified price, backend returns `HTTP 409 Conflict (PRICE_CHANGED)`.
- **HMAC Payment Security:** Live webhooks and sandbox calls use constant-time `hmac.compare_digest()` to prevent timing attacks.

### 6. Persistence & Multi-Tenant Security
- **Cloud Database:** Supabase PostgreSQL with Row Level Security (RLS) policies.
- **Local Fallback:** SQLite with Write-Ahead Logging (WAL) mode and automatic connection pooling.
- **Production Fail-Safe:** In `ENVIRONMENT=production`, Supabase connection is mandatory, preventing split-brain SQLite fallback.
- **Tenant Isolation:** Bookings, price alerts, saved flights, and user preferences strictly require matching JWT sub claims (`HTTP 403 Forbidden` on cross-user access).

---

## 🔒 Security Summary Matrix

| Vector | Protection Mechanism |
| :--- | :--- |
| **Price Tampering** | Server-authoritative price calculation (`/payments/calculate-price`). |
| **Payment Spoofing** | HMAC-SHA256 signature verification with constant-time equality check. |
| **Credential Leakage** | Backend-only `.env` isolation; secrets omitted from telemetry and client scripts. |
| **Cross-Tenant Snooping** | Supabase RLS and token ownership enforcement on all user entities. |
| **Replay Attacks** | Idempotency keys on booking requests and payment verification. |
| **Production Misconfiguration** | Fail-safe database check and disabled demo reset in production mode. |
