# AirfareX India — Hackathon Judge FAQ

> **Anticipated Judge Questions & Authoritative Technical Answers**

---

### 1. What problem are you solving?
**Answer:** While existing flight aggregators list dozens of flight options, they leave the hard work of comparing price, duration, layovers, and real-world value entirely to the user. AirfareX combines flight search, price forecasting, and explainable AI to answer: *"Which flight is best for me, and why?"*

---

### 2. What makes AirfareX different from MakeMyTrip or Google Flights?
**Answer:** Google Flights and MakeMyTrip are search engines and ticketing storefronts; they show you raw lists sorted by price or time. AirfareX is a **decision intelligence engine**. We evaluate flights across 5 objective dimensions (Price, Duration, Stops, Convenience, Value), provide transparent reasoning, and explain exact trade-offs (e.g. paying ₹380 more saves 2 hours).

---

### 3. Where does the flight data come from?
**Answer:** AirfareX uses a provider-agnostic flight architecture (`BaseFlightProvider`). In development/demo mode, it uses `MockDevelopmentProvider` with realistic Indian domestic schedules. When configured with API keys, it connects to live GDS inventory via `AmadeusFlightProvider`.

---

### 4. Is the flight data live in this demo?
**Answer:** In this hackathon demonstration environment, the system runs in `DEVELOPMENT` mode using `MockDevelopmentProvider` to guarantee 100% offline availability and consistent evaluation without external third-party quota limits. It is clearly labeled as `[DEVELOPMENT]` in the UI.

---

### 5. Is ticket booking real?
**Answer:** The booking flow and payment state machine are complete (`DRAFT` -> `PRICE_CALCULATED` -> `PAYMENT_PENDING` -> `PAYMENT_VERIFIED` -> `BOOKING_CONFIRMED`). However, real airline ticket issuance requires an accredited airline ticketing contract (IATA / NDC). In this environment, bookings are transparently labeled as **Development Booking** and simulated ticket numbers are not generated.

---

### 6. Is the payment real?
**Answer:** This demo uses our Sandbox Payment Simulator, which performs cryptographic backend state machine transitions. The backend is fully wired to live Razorpay checkout when configured with live API credentials.

---

### 7. How does the AI recommendation engine work?
**Answer:** AirfareX uses a multi-factor mathematical scoring model that evaluates Price, Duration, Stops, Convenience (departure time slots), and Value (time-cost ratio). The recommendations (`AirfareX Pick`, `Best Value`, `Cheapest`, `Fastest`) are calculated deterministically from backend flight data.

---

### 8. Can the AI manipulate booking prices or confirm payments?
**Answer:** **No.** We enforce strict architectural isolation. The AI layer is read-only decision support. It cannot modify payment amounts, create orders, or bypass payment verification.

---

### 9. How do you prevent client-side price tampering?
**Answer:** Zero-trust server-side pricing. The client cannot send a self-calculated price. The backend recalculates the full statutory fare decomposition (Base, YQ, UDF, ASF, 5% GST) on `POST /payments/calculate-price`. If a client submits a modified fare, it is rejected with `HTTP 409 Conflict`.

---

### 10. How do you protect user data and privacy?
**Answer:** All customer data (itineraries, saved flights, price drop alerts, preferences) is strictly bound to the authenticated user ID and protected via Supabase Row Level Security (RLS) policies and JWT validation. Cross-user data access returns `HTTP 403 Forbidden`.

---

### 11. How does the system scale to high traffic?
**Answer:** 
1. **Asynchronous Architecture:** FastAPI and Uvicorn handle high-concurrency I/O.
2. **15-Minute TTL Cache:** Flight searches are cached in-memory, reducing downstream provider queries by up to 80%.
3. **Stateless Web Tier:** Backend instances can scale horizontally behind a load balancer.

---

### 12. What happens if an external flight provider fails?
**Answer:** The provider abstraction layer implements automatic error isolation. If an external provider experiences downtime or rate limits, the system catches the failure cleanly and falls back without crashing the user session.

---

### 13. What happens if the AI LLM service is unavailable?
**Answer:** AirfareX includes a built-in `RuleBasedAIProvider` fallback. It calculates all 5-factor scores, category badges, and trade-off verdicts locally with **zero external API dependencies**.

---

### 14. What is the business model?
**Answer:**
1. **Affiliate / OTA Commission:** Commission on completed flight and holiday package reservations.
2. **B2B API Licensing:** Licensing our explainable decision engine to OTAs, corporate travel desks, and search aggregators.
3. **Premium Traveler Subscriptions:** Advanced price drop alerts, automatic rebooking on fare drops, and personalized business travel copilot.

---

### 15. What is the future scope?
**Answer:** Live IATA NDC carrier integration, corporate multi-traveler booking policies, international route intelligence, and dynamic multimodal travel combinations (e.g. Flight + Vande Bharat Train connections).

---

### 16. How can airlines integrate with AirfareX?
**Answer:** Airlines can connect via standard IATA NDC APIs or direct inventory feeds, allowing them to showcase premium seat pitch, ancillary benefits, and punctuality scores directly to value-conscious flyers.

---

### 17. What was your biggest technical challenge?
**Answer:** Building a robust, server-authoritative payment and booking state machine that reconciles complex statutory Indian civil aviation fees (UDF, ASF, CGST, SGST) while maintaining zero-trust security and sub-second decision scoring.

---

### 18. What is your biggest innovation?
**Answer:** Transforming opaque search results into **explainable aviation intelligence**—quantifying whether spending an extra ₹400 is objectively worth saving 2 hours of transit time, and proving it to the traveler with transparent mathematical reasoning.
