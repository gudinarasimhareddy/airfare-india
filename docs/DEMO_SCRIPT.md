# AirfareX India — 3-Minute Hackathon Demo Script

> **Target Duration:** 3:00 minutes  
> **Audience:** Hackathon Technical Judges & Product Evaluators  
> **Speaker Role:** Lead Engineer / Presenter

---

## ⏱️ Timeline & Speaker Notes

### `0:00 – 0:20` | Problem Hook (20 Seconds)
- **Screen:** Homepage (`http://127.0.0.1:8000`) showing Hero banner.
- **Speaker:**
  > *"Every day, millions of Indian travelers open flight portals like MakeMyTrip or Google Flights. They see hundreds of flights, confusing layovers, and flashing price tags. But none of these platforms answer the single most important question travelers actually have: **'Which flight should I choose, and WHY?'**"*

### `0:20 – 0:40` | The AirfareX Solution (20 Seconds)
- **Screen:** Scroll down slightly to highlight the **"How AirfareX Works"** 5-step pipeline diagram.
- **Speaker:**
  > *"AirfareX is India’s first explainable aviation intelligence platform. We combine multi-airline inventory aggregation, 14-day price forecasting, and objective 5-factor AI decision scoring to help travelers make smart, confident choices in seconds."*

### `0:40 – 1:10` | Natural Language Flight Search (30 Seconds)
- **Screen:** Focus on `#heroNlSearchInput`. Click submit on:
  `"cheapest morning non-stop flight from Delhi to Mumbai tomorrow"`
- **Speaker:**
  > *"Instead of fiddling with ten dropdowns, you simply tell AirfareX what you need in plain English or your regional language. Our natural language engine extracts the origin, destination, time slot, and stops preference, instantly launching a structured search."*

### `1:10 – 1:40` | AI Decision Scoring & Explainability (30 Seconds)
- **Screen:** Flight results view showing the 4 AI summary cards (`👑 AirfareX Pick`, `💎 Best Value`). Click **"💡 Why this flight?"** on AirfareX Pick.
- **Speaker:**
  > *"Look at our top recommendation: the **AirfareX Pick**. We don’t just slap a badge on a flight; we mathematically score every flight across Price, Duration, Stops, Convenience, and Value. Clicking 'Why this flight?' reveals the transparent breakdown: paying just ₹420 more over the cheapest 6-hour flight saves 1 hour and 45 minutes of travel time."*

### `1:40 – 2:00` | Explainable Side-by-Side Comparison (20 Seconds)
- **Screen:** Check compare on 2 flights and click **"Compare Now ➔"**.
- **Speaker:**
  > *"When deciding between two options, AirfareX provides a factual trade-off matrix: exact fare delta, duration difference, and an objective verdict. No marketing fluff—just clean aviation math."*

### `2:00 – 2:30` | Server-Authoritative Booking & Sandbox Payment (30 Seconds)
- **Screen:** Click **"Book Now"** ➔ `/booking.html` ➔ Proceed to Payment ➔ Authorize in Sandbox Simulator.
- **Speaker:**
  > *"When booking, AirfareX enforces zero-trust server-side pricing. Client-side price tampering is rejected. In this development demo, our sandbox payment simulator completes authorization via cryptographic backend switch, reserving the itinerary with an authentic public reference."*

### `2:30 – 2:50` | Honest Confirmation & My Trips (20 Seconds)
- **Screen:** Confirmed boarding pass view with honest development badge, then click **"View My Trips"**.
- **Speaker:**
  > *"Here is the confirmed itinerary. Notice our transparency: we clearly state that this is a development booking and sandbox payment. In My Trips, passenger records and DGCA cancellation refund rights are isolated securely per user."*

### `2:50 – 3:00` | Key Differentiation & Closing (10 Seconds)
- **Screen:** Return to hero view / Architecture summary.
- **Speaker:**
  > *"Most flight platforms only tell you what flights exist. AirfareX tells you which flight to pick, and proves why. Thank you!"*
