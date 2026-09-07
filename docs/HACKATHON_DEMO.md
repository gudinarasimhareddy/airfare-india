# AirfareX India — Hackathon Live Demonstration Guide

> **Official Demo Runbook for Evaluators & Judges**  
> *Demonstrating Explainable Aviation Intelligence, Natural Language Discovery, Zero-Trust Pricing & Transparent Booking.*

---

## 🎯 Demonstration Objective
Demonstrate that AirfareX India is **not just another flight search UI**, but an **aviation decision intelligence platform** that answers:
> *"What is the best flight for my journey, and WHY?"*

---

## ⚙️ Prerequisites & Runtime Environment

| Dimension | Active Demo Mode | Truth / Disclosure |
| :--- | :--- | :--- |
| **Flight Search Data** | `DEVELOPMENT / MockDevelopmentProvider` | High-fidelity Indian domestic schedules (DEL, BOM, BLR, HYD, MAA, CCU, GOI, PNQ). *Optional live Amadeus GDS supported when configured.* |
| **Payment Gateway** | `SANDBOX Simulator` | Cryptographic HMAC-SHA256 authorization switch. *Optional live Razorpay supported when configured.* |
| **Carrier Booking** | `DEVELOPMENT BOOKING` (`BOOKING_CONFIRMED`) | **Real airline ticket issuance is NOT connected.** Honest development notice displayed on all passes. |
| **AI Intelligence** | `RuleBasedAIProvider` | 100% deterministic local fallback requiring **no external API keys or credentials**. |

---

## 🚀 Step-by-Step 10-Stage Golden Demo Journey

### 1. Launch Portal
1. Open web browser to `http://127.0.0.1:8000`.
2. Observe the dark-mode glassmorphic aviation interface, typography, and National Airfare Index (**APIx**) KPI cards.

### 2. Instant Sector Benchmark & Airport Swap
1. In the hero search box, click the **`⇄` Swap Airports button**.
2. Notice immediate reciprocal swap between `Delhi (DEL)` and `Hyderabad (HYD)` / `Mumbai (BOM)` and real-time benchmark chart recalculation.

### 3. Natural Language AI Search
1. In the hero input (`#heroNlSearchInput`), enter the prompt:
   ```text
   cheapest morning non-stop flight from Delhi to Mumbai tomorrow
   ```
2. Click **"Ask AirfareX"** (`#heroAskAiBtn`).
3. Notice the query is instantly parsed into structured parameters (`DEL ➔ BOM`, `Nonstop`, `Morning`, `Lowest Price`), switches to the **Search Flights** tab, and triggers live execution.

### 4. Search Results & Shimmer Skeletons
1. Watch the animated CSS shimmer skeleton cards while flight data and 5-factor AI scores compute.
2. Inspect the **Data Source banner**: `[DEVELOPMENT]` or `[⚡ CACHED] · Refreshes in 15m`.

### 5. AI Recommendations & Badging Summary
Observe the top 4 AI category winner cards:
- 👑 **AirfareX Pick** (Highest overall score balancing price, duration, stops, convenience, and value).
- 💎 **Best Value** (Optimal cost-benefit ratio saving meaningful travel time).
- 💸 **Lowest Price** (Absolute lowest route base fare).
- ⚡ **Fastest Travel** (Shortest elapsed non-stop journey).

### 6. "💡 Why This Flight?" Explainability Modal
1. Click **"💡 Why this flight?"** on the AirfareX Pick (e.g. `IndiGo 6E-205`).
2. Inspect the transparent **5-factor score breakdown (0–100)**:
   - Price Score, Duration Score, Stops Score, Convenience Score, and Value Score.
3. Review factual reasoning bullets: *₹420 above cheapest, saves 1h 45m, non-stop departure*.
4. Inspect the **14-day price forecast** (Buy Now vs Wait signal with confidence percentage).

### 7. Side-by-Side Flight Comparison
1. Check the **Compare** checkbox on 2 different flights (e.g. 1-stop vs non-stop).
2. Click **"Compare Now ➔"** in the floating comparison bar.
3. View exact mathematical deltas: `+₹380`, `-2h 05m`, and AI comparative trade-off verdict.

### 8. Conversational Copilot
1. Click the floating bottom-right **`🤖 AI Copilot`** launcher button.
2. Click the quick suggestion chip: **"✨ Which flight should I choose?"**.
3. Inspect concise grounded answer and toggle the **"🧠 Agentic Execution Trace"** to view autonomous decision steps.

### 9. Secure Checkout & Zero-Trust Pricing
1. On the recommended flight, click **"Book Now"**.
2. On `/booking.html`, enter traveler information (e.g., `Rajesh Sharma`, `rajesh@example.com`, `+91 9876543210`).
3. Review authoritative server-decomposed pricing (Base Fare, Fuel Surcharge YQ, Airport UDF, Statutory ASF, and 5% Indian GST).
4. Click **"🔒 Proceed to Secure Payment"**.
5. In the Sandbox Payment Simulator, click **"✓ Authorize Sandbox Payment"**.

### 10. Honest Confirmation & My Trips
1. Review confirmed boarding pass card:
   - `✓ Booking Confirmed`
   - Booking Reference: `AXI...`
   - Payment Gateway: `Sandbox / Verified`
   - Prominent honest notice: *"Development booking — airline ticket issuance is not connected in this environment."*
2. Click **"🧳 View My Trips"** to inspect isolated user trip history and real-time status.

---

## 🔄 Resetting Demo State

To reset cached searches and restore pristine state before another demo:
```powershell
curl -X POST http://127.0.0.1:8000/api/v1/flights/demo-reset
```
*Note: This endpoint is strictly disabled in production (`HTTP 403 Forbidden`).*

---

## 🛠️ Troubleshooting

| Issue | Cause | Fix |
| :--- | :--- | :--- |
| Server not responding | Process not running | Execute `python run_server.py` |
| Empty search results | Strict active filters | Click *"Reset Filters & Show All"* |
| Auth dialog prompts on My Trips | Session expired / logged out | Sign in with test credentials or click Sign In |
