"""
AirfareX India — Phase 8 Final Product Polish, UX, Demo Experience & Performance Test Suite
Tests all 20 Phase 8 requirements:
1. Hero messaging and subcopy
2. Airport swap button and accessibility
3. Standardized search CTA
4. Natural Language AI search UI elements
5. How AirfareX Works 5-step pipeline diagram
6. Copilot prompt chips
7. Copilot floating launcher FAB
8. Booking confirmation screen hierarchy
9. Honest development booking notice (no fake ticket numbers)
10. Booking confirmation action buttons (View My Trips, Back to Flights, Print)
11. Flight card Book Now microcopy
12. Skeleton loading state components
13. Friendly empty and error states
14. Accessibility focus-visible rules
15. Mobile responsive CSS breakpoints
16. Footer demo disclaimer
17. URL query state synchronization
18. Flight filter reset helper
19. Backend health and API version integrity
20. End-to-end regression compatibility across Phases 1-7
"""

import os
import sys
import pytest
from starlette.testclient import TestClient

# Ensure workspace root is on sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from backend.app import app

client = TestClient(app)

FRONTEND_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "frontend"))


def read_file_content(relative_path: str) -> str:
    path = os.path.join(FRONTEND_DIR, relative_path)
    with open(path, "r", encoding="utf-8") as f:
        return f.read()


def test_01_hero_messaging_and_subcopy():
    """1. Verify hero copy matches Phase 8 specifications."""
    index_html = read_file_content("index.html")
    assert "Travel smarter with aviation intelligence." in index_html
    assert "Search flights. Understand prices. Compare options. Let AirfareX help you decide." in index_html


def test_02_airport_swap_button_and_accessibility():
    """2. Verify airport swap button has accessible aria-label and onclick handler."""
    index_html = read_file_content("index.html")
    assert 'id="swapAirportsBtn"' in index_html
    assert 'onclick="swapOriginDest()"' in index_html
    assert 'aria-label="Swap origin and destination"' in index_html


def test_03_standardized_search_cta():
    """3. Verify primary hero search button text is standardized to 'Search Flights'."""
    index_html = read_file_content("index.html")
    assert 'id="heroSearchBtn"' in index_html
    assert "Search Flights" in index_html


def test_04_nl_search_ui_elements():
    """4. Verify natural language AI search input placeholder and button."""
    index_html = read_file_content("index.html")
    assert 'id="heroNlSearchInput"' in index_html
    assert 'placeholder="Try: cheapest non-stop flight from Delhi to Mumbai tomorrow"' in index_html
    assert 'id="heroAskAiBtn"' in index_html
    assert "Ask AirfareX" in index_html


def test_05_how_airfarex_works_pipeline():
    """5. Verify the 5-step 'How AirfareX Works' judge-facing pipeline diagram."""
    index_html = read_file_content("index.html")
    assert 'id="howAirfarexWorks"' in index_html
    assert "How AirfareX Works" in index_html
    assert "Flight Ingestion" in index_html
    assert "Price Intelligence" in index_html
    assert "AI Recommendation" in index_html
    assert "Secure Booking" in index_html
    assert "Trip Management" in index_html


def test_06_copilot_prompt_chips():
    """6. Verify Copilot prompt chips match the requested conversational questions."""
    index_html = read_file_content("index.html")
    assert "Which flight should I choose?" in index_html
    assert "Why is this flight better?" in index_html
    assert "Is this price good?" in index_html
    assert "Show me the cheapest option" in index_html
    assert "Find a faster option" in index_html
    assert "Compare these flights" in index_html


def test_07_copilot_floating_launcher_fab():
    """7. Verify Copilot floating launcher FAB exists with accessibility attribute."""
    index_html = read_file_content("index.html")
    assert 'id="copilotFabBtn"' in index_html
    assert 'aria-label="Open AirfareX AI Copilot"' in index_html
    assert "toggleAiAssistant()" in index_html or "toggleAiCopilotDrawer()" in index_html


def test_08_booking_confirmation_hierarchy():
    """8. Verify booking confirmation hierarchy includes reference, sector, and payment verification."""
    booking_html = read_file_content("booking.html")
    assert "Booking Confirmed" in booking_html
    assert "Booking Reference" in booking_html
    assert "Payment Gateway" in booking_html or "Sandbox" in booking_html
    assert "Reserved Sector" in booking_html


def test_09_honest_development_booking_notice():
    """9. Verify honest development notice is displayed and no fake e-ticket string exists."""
    booking_html = read_file_content("booking.html")
    booking_js = read_file_content("js/booking.js")
    assert "Development booking — airline ticket issuance is not connected in this environment." in booking_html
    # Ensure no simulated fake e-ticket number like 098-8492019482 remains in either file
    assert "098-8492019482" not in booking_html
    assert "098-8492019482" not in booking_js
    assert "e-Ticket / Barcode" not in booking_html


def test_10_booking_confirmation_actions():
    """10. Verify confirmation action buttons (View My Trips, Back to Flights, Print)."""
    booking_html = read_file_content("booking.html")
    assert "View My Trips" in booking_html
    assert "Back to Flights" in booking_html
    assert "Print Booking Summary" in booking_html or "window.print()" in booking_html


def test_11_flight_card_book_now_microcopy():
    """11. Verify flight card primary booking button uses 'Book Now' microcopy."""
    app_js = read_file_content("js/app.js")
    assert 'Book Now</button>' in app_js


def test_12_skeleton_loading_components():
    """12. Verify skeleton shimmer loading classes in CSS and usage in JS."""
    components_css = read_file_content("css/components.css")
    app_js = read_file_content("js/app.js")
    assert ".skeleton-card" in components_css
    assert ".skeleton-shimmer" in components_css
    assert "skeleton-card" in app_js


def test_13_friendly_empty_and_error_states():
    """13. Verify friendly empty and error state CSS classes and implementation in app.js."""
    components_css = read_file_content("css/components.css")
    app_js = read_file_content("js/app.js")
    assert ".friendly-empty-card" in components_css
    assert ".friendly-error-card" in components_css
    assert "friendly-empty-card" in app_js
    assert "friendly-error-card" in app_js


def test_14_accessibility_focus_visible():
    """14. Verify accessibility focus-visible ring styles."""
    components_css = read_file_content("css/components.css")
    assert ":focus-visible" in components_css
    assert "outline" in components_css


def test_15_mobile_responsive_css_breakpoints():
    """15. Verify mobile responsive CSS media queries."""
    components_css = read_file_content("css/components.css")
    assert "@media (max-width: 768px)" in components_css or "@media screen and (max-width: 768px)" in components_css


def test_16_footer_demo_disclaimer():
    """16. Verify transparent footer disclaimer on development data & sandbox payment."""
    index_html = read_file_content("index.html")
    assert "Current demo uses development flight data and sandbox payment." in index_html
    assert "Real airline ticket issuance requires an authorized ticketing provider." in index_html


def test_17_url_query_state_sync():
    """17. Verify URL query state synchronization and navigation helpers."""
    app_js = read_file_content("js/app.js")
    assert "function showTab" in app_js
    assert "initUrlState" in app_js
    assert "popstate" in app_js
    assert "window.showTab = showTab" in app_js


def test_18_flight_filter_reset_helper():
    """18. Verify resetFlightFilters helper exists and is exposed to window."""
    app_js = read_file_content("js/app.js")
    assert "function resetFlightFilters" in app_js
    assert "window.resetFlightFilters = resetFlightFilters" in app_js


def test_19_backend_health_and_api_version():
    """19. Verify backend health endpoint returns healthy status and metadata."""
    res = client.get("/health")
    assert res.status_code == 200
    data = res.json()
    assert data.get("status") == "healthy"
    assert "version" in data or "timestamp" in data


def test_20_end_to_end_regression_integrity():
    """20. Verify flight search and AI recommendation API endpoints respond correctly."""
    # Test flight search
    search_res = client.get("/api/v1/flights/search?from_city=DEL&to_city=BOM")
    assert search_res.status_code == 200
    s_data = search_res.json()
    assert "flights" in s_data
    assert len(s_data["flights"]) > 0

    # Test NL search
    nl_res = client.post("/api/v1/ai/interpret-search", json={"query": "cheapest flight from Delhi to Mumbai tomorrow"})
    assert nl_res.status_code == 200
    nl_data = nl_res.json()
    assert "origin" in nl_data or "interpreted_query" in nl_data

    # Test AI recommend
    rec_res = client.post("/api/v1/ai/recommend", json={
        "flights": s_data["flights"][:4],
        "user_preferences": {"prioritize_price": True},
        "search_params": {"from_city": "DEL", "to_city": "BOM"}
    })
    assert rec_res.status_code == 200
    rec_data = rec_res.json()
    assert "status" in rec_data or "airfarex_pick" in rec_data


if __name__ == "__main__":
    print("==================================================")
    print("RUNNING PHASE 8 UX & POLISH TEST SUITE")
    print("==================================================")
    for name, func in list(globals().items()):
        if name.startswith("test_") and callable(func):
            func()
            print(f"[PASS] {name}")
    print("==================================================")
    print("ALL 20 PHASE 8 UX & POLISH TESTS PASSED!")
    print("==================================================")

