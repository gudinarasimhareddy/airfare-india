# AirfareX India — Product & Engineering Roadmap

> **Current Implementation vs Near-Term Milestones vs Long-Term Vision**

---

## 🟢 CURRENT: Implemented & Verified (Phases 1–9)
- ✅ **Responsive Glassmorphic UI:** Modern design tokens, dark mode, focus-visible accessibility, and mobile drawer.
- ✅ **Multi-Airline Catalog:** Master data for major Indian domestic carriers (IndiGo, Air India, Akasa Air, SpiceJet, Air India Express, Star Air).
- ✅ **Provider-Agnostic Flight Engine:** Multi-provider architecture with `MockDevelopmentProvider`, live `AmadeusFlightProvider`, and 15-minute TTL cache.
- ✅ **Multi-Factor AI Scoring (0–100):** 5-dimension objective evaluation (`Price`, `Duration`, `Stops`, `Convenience`, `Value`).
- ✅ **Explainable Badging & Insights:** Visual tags (`AirfareX Pick`, `Best Value`, `Cheapest`, `Fastest`) and *"Why This Flight?"* breakdown.
- ✅ **Natural Language Discovery:** Conversational search parser with ambiguity handling and instant search execution.
- ✅ **Side-by-Side Trade-off Analysis:** Mathematical price and duration delta comparisons.
- ✅ **Zero-Trust Pricing & Payment State Machine:** Server-authoritative fare decomposition, HMAC payment security, and sandbox authorization simulator.
- ✅ **Multi-Tenant User Isolation:** Supabase RLS policies and JWT authentication for customer bookings, alerts, and preferences.
- ✅ **Comprehensive Automated Testing:** 170 verified automated tests across all 9 phases.

---

## 🟡 NEXT: Near-Term Engineering Milestones (6–12 Months)
- 🔲 **IATA NDC Carrier Integration:** Direct API integration with Indian domestic carriers for live seat selection and real e-ticket issuance.
- 🔲 **Real-Time Webhook Price Tracking:** Asynchronous background worker monitoring route fares and triggering instant SMS / WhatsApp alerts on price drops.
- 🔲 **Production AI Fine-Tuning:** Fine-tuned domain LLM specializing in Indian DGCA passenger charter regulations, airline compensation rules, and travel advisories.
- 🔲 **Automated Price Drop Rebooking:** Automatic refund and rebooking execution when fare drops on refundable tickets exceed cancellation penalties.

---

## 🔵 FUTURE: Long-Term Vision (1–3 Years)
- 🔲 **Multimodal Indian Travel Routing:** Intelligent combinations connecting domestic flights with Indian Railways (Vande Bharat Express) for tier-2/tier-3 destinations.
- 🔲 **Corporate Travel Policy Automation:** Enterprise portals with role-based travel allowances, automated manager approvals, and GST invoice reconciliation.
- 🔲 **International Route Intelligence:** Expanding multi-currency pricing, visa validity checks, and overseas layover guidance for Indian international departures.
- 🔲 **B2B Aviation Analytics API:** Licensing real-time route volatility metrics, elasticity models, and passenger demand indices to airlines and tourism boards.
