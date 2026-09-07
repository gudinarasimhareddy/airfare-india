# AirfareX India — Presentation Screenshot & Walkthrough Plan

> **10 Key Visual Artifacts for Pitch Decks, Demos & Documentation**  
> *Strict Secret Redaction & Compliance Checklist Included.*

---

## 📸 10 Essential Screenshots

### 1. Homepage & Hero Banner
- **URL:** `http://127.0.0.1:8000/`
- **What should be visible:** Hero heading (*"Travel smarter with aviation intelligence."*), subcopy, origin/destination inputs, airport swap button (`⇄`), and National Airfare Index (**APIx**) cards.
- **What must NOT be visible:** Browser developer console, localhost network debug bars.
- **Demonstrates:** Modern typography, dark-mode glassmorphic aesthetics, and instant sector discovery.

### 2. Natural Language AI Search
- **URL:** `http://127.0.0.1:8000/` (Hero section)
- **What should be visible:** Populated `#heroNlSearchInput` with query: `"cheapest morning non-stop flight from Delhi to Mumbai tomorrow"`, and active `#heroAskAiBtn` (*"Ask AirfareX"*).
- **What must NOT be visible:** Partial query truncation.
- **Demonstrates:** Conversational intent parsing and regional accessibility.

### 3. Flight Results & AI Category Summary
- **URL:** `http://127.0.0.1:8000/?tab=explorer`
- **What should be visible:** Top 4 AI cards (`👑 AirfareX Pick`, `💎 Best Value`, `💸 Lowest Price`, `⚡ Fastest Travel`) and flight cards with `[DEVELOPMENT]` / `[⚡ CACHED]` source tags.
- **What must NOT be visible:** Stale fallback error text.
- **Demonstrates:** High-level decision intelligence and clean categorization.

### 4. "Why This Flight?" Explainability Modal
- **URL:** `http://127.0.0.1:8000/?tab=explorer` (Click *"💡 Why this flight?"*)
- **What should be visible:** 5-factor scoring progress bars (Price, Duration, Stops, Convenience, Value: 0–100), factual reasoning bullets, and 14-day price projection (`BUY_NOW` / `WAIT`).
- **What must NOT be visible:** Ungrounded placeholder text.
- **Demonstrates:** Transparent, explainable mathematical AI recommendations.

### 5. Conversational Copilot & Execution Trace
- **URL:** `http://127.0.0.1:8000/` (Bottom-right Copilot drawer open)
- **What should be visible:** Chat bubble answering *"Which flight should I choose?"*, prompt chips, and expanded *"🧠 Agentic Execution Trace"*.
- **What must NOT be visible:** Unhandled promise rejections.
- **Demonstrates:** Context-aware travel copilot and autonomous reasoning visibility.

### 6. Side-by-Side Flight Comparison
- **URL:** `http://127.0.0.1:8000/?tab=comparison`
- **What should be visible:** 2 selected flights with exact price delta (`+₹380`), duration delta (`-2h 05m`), itinerary breakdown, and AI verdict.
- **What must NOT be visible:** Blank comparison rows.
- **Demonstrates:** Objective trade-off evaluation between competing options.

### 7. Server-Authoritative Booking Review
- **URL:** `http://127.0.0.1:8000/booking.html`
- **What should be visible:** Itemized fare breakdown (Base Fare, Fuel Surcharge YQ, Airport UDF, Statutory ASF, 5% Indian GST), passenger inputs, and DGCA cancellation policy note.
- **What must NOT be visible:** Editable price inputs (zero-trust pricing).
- **Demonstrates:** Civil aviation statutory compliance and pricing transparency.

### 8. Sandbox Payment Simulator
- **URL:** `http://127.0.0.1:8000/booking.html` (Payment Modal open)
- **What should be visible:** Order ID, verified amount, Sandbox authorization switch (*"✓ Authorize Sandbox Payment"*, *"✕ Decline / Simulate Payment Failure"*).
- **What must NOT be visible:** Real credit card credentials.
- **Demonstrates:** Cryptographic payment state machine with instant verification.

### 9. Confirmed Booking & Honest Notice
- **URL:** `http://127.0.0.1:8000/booking.html` (Confirmation screen)
- **What should be visible:** `✓ Booking Confirmed`, Booking Reference (`AXI...`), Sector (`DEL ➔ BOM`), Payment Gateway (`Sandbox / Verified`), and prominent notice: *"Development booking — airline ticket issuance is not connected in this environment."*
- **What must NOT be visible:** Fake simulated airline e-ticket strings or barcode mockups.
- **Demonstrates:** Honest engineering disclosures and booking confirmation.

### 10. My Trips Customer Management
- **URL:** `http://127.0.0.1:8000/?tab=trips`
- **What should be visible:** List of confirmed trips with booking references, dates, passenger count, total amount, and development data source badges.
- **What must NOT be visible:** Cross-user data leakage.
- **Demonstrates:** Multi-tenant customer data isolation and trip management.

---

## 🔒 Security & Privacy Rules for Screenshots
1. **Never Capture API Keys:** Ensure `.env` or configuration strings are never open in background editor windows.
2. **Redact Sensitive PII:** Use dummy passenger names (e.g. `Rajesh Sharma`, `Priya Patel`).
3. **No Fake Claims:** Ensure screenshots faithfully represent the active `[DEVELOPMENT]` data source and `Sandbox` payment mode.
