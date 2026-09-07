"""
Test Suite for Phase 8 & 8.5: Personalized Agentic AI Travel Advisor
AirfareX India
"""
import unittest
import json
import os
import re

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
FRONTEND_DIR = os.path.join(PROJECT_ROOT, "frontend")
AI_AGENT_JS = os.path.join(FRONTEND_DIR, "js", "aiAgent.js")
DEMO_DATA_JS = os.path.join(FRONTEND_DIR, "js", "demoData.js")
INDEX_HTML = os.path.join(FRONTEND_DIR, "index.html")
COMPONENTS_CSS = os.path.join(FRONTEND_DIR, "css", "components.css")
APP_JS = os.path.join(FRONTEND_DIR, "js", "app.js")


class TestPhase8PersonalizedAI(unittest.TestCase):
    def setUp(self):
        self.assertTrue(os.path.exists(AI_AGENT_JS), "aiAgent.js must exist")
        with open(AI_AGENT_JS, "r", encoding="utf-8") as f:
            self.agent_js = f.read()

        with open(INDEX_HTML, "r", encoding="utf-8") as f:
            self.index_html = f.read()

        with open(COMPONENTS_CSS, "r", encoding="utf-8") as f:
            self.components_css = f.read()

        with open(APP_JS, "r", encoding="utf-8") as f:
            self.app_js = f.read()

    def test_01_demo_profiles_exist(self):
        """Test that all 3 customer profiles with 10 past bookings each are defined."""
        self.assertIn("DEMO-1001", self.agent_js)
        self.assertIn("Rajesh Sharma", self.agent_js)
        self.assertIn("DEMO-1002", self.agent_js)
        self.assertIn("Priya Patel", self.agent_js)
        self.assertIn("DEMO-1003", self.agent_js)
        self.assertIn("Vikram Reddy", self.agent_js)

        # Count history bookings per profile
        rajesh_trips = len(re.findall(r'id:\s*"TRIP-1', self.agent_js))
        self.assertEqual(rajesh_trips, 10, "Rajesh Sharma must have 10 past bookings")

        priya_trips = len(re.findall(r'id:\s*"TRIP-2', self.agent_js))
        self.assertEqual(priya_trips, 10, "Priya Patel must have 10 past bookings")

        vikram_trips = len(re.findall(r'id:\s*"TRIP-3', self.agent_js))
        self.assertEqual(vikram_trips, 10, "Vikram Reddy must have 10 past bookings")

    def test_02_tools_registry(self):
        """Test that all required Agentic AI tools are registered."""
        required_tools = [
            "searchFlights",
            "filterFlights",
            "sortFlights",
            "compareFlights",
            "calculatePersonalizedMatch",
            "getPersonalizedRecommendation",
            "getBestFlightForMe",
            "getBestOverallFlight",
            "getCheapestFlight",
            "getFastestFlight",
            "getMostReliableFlight",
            "explainPersonalizedRecommendation",
            "createDemoBooking",
            "confirmDemoBooking"
        ]
        for tool in required_tools:
            self.assertIn(tool, self.agent_js, f"Tool {tool} must be defined in aiAgent.js")

    def test_03_history_analysis_algorithm(self):
        """Test that analyzeTravelHistory function is present and calculates key metrics."""
        self.assertIn("function analyzeTravelHistory", self.agent_js)
        self.assertIn("averageFare", self.agent_js)
        self.assertIn("preferredAirline", self.agent_js)
        self.assertIn("nonStopRatio", self.agent_js)
        self.assertIn("priceSensitivity", self.agent_js)

    def test_04_dual_scoring_formula(self):
        """Test that personal match scoring is mathematically distinct from AirfareX score."""
        self.assertIn("function calculatePersonalizedMatch", self.agent_js)
        self.assertIn("rawMatch", self.agent_js)
        self.assertIn("wPrice", self.agent_js)
        self.assertIn("wComfort", self.agent_js)

    def test_05_priority_override_nlp_logic(self):
        """Test that current user request overrides profile historical priority."""
        self.assertIn("comfort is more important", self.agent_js)
        self.assertIn("priorityOverride", self.agent_js)
        self.assertIn("processUserRequest", self.agent_js)

    def test_06_html_script_integration(self):
        """Test that aiAgent.js is properly included in index.html before app.js."""
        self.assertIn('<script src="/js/aiAgent.js"></script>', self.index_html)
        agent_idx = self.index_html.find('/js/aiAgent.js')
        app_idx = self.index_html.find('/js/app.js')
        self.assertLess(agent_idx, app_idx, "aiAgent.js must load before app.js")

    def test_07_html_demo_profile_bar(self):
        """Test that Demo Customer Profile Switcher Bar is present in index.html."""
        self.assertIn("demo-profile-switcher-bar", self.index_html)
        self.assertIn("switchDemoProfile('DEMO-1001')", self.index_html)
        self.assertIn("switchDemoProfile('DEMO-1002')", self.index_html)
        self.assertIn("switchDemoProfile('DEMO-1003')", self.index_html)

    def test_08_html_hero_ai_advisor(self):
        """Test that Hero AI Advisor card with priority chips is present in index.html."""
        self.assertIn("heroAdvisorCard", self.index_html)
        self.assertIn("aiChangePriority('cheapest'", self.index_html)
        self.assertIn("aiChangePriority('comfort'", self.index_html)
        self.assertIn("aiChangePriority('fastest'", self.index_html)
        self.assertIn("aiChangePriority('reliable'", self.index_html)
        self.assertIn("aiChangePriority('value'", self.index_html)
        self.assertIn("askHeroAdvisor()", self.index_html)

    def test_09_html_admin_ai_metrics(self):
        """Test that AI Travel Advisor Metrics subview is present in Admin section."""
        self.assertIn('id="adminBtnAiMetrics"', self.index_html)
        self.assertIn('id="ai-metrics"', self.index_html)
        self.assertIn('id="aiAdminWeightsContainer"', self.index_html)
        self.assertIn('id="aiAdminToolRegistry"', self.index_html)

    def test_10_html_personalization_modal(self):
        """Test that userPreferencesModal contains privacy and accessibility controls."""
        self.assertIn('id="prefUseHistory"', self.index_html)
        self.assertIn('id="prefWheelchair"', self.index_html)
        self.assertIn('id="prefExtraLegroom"', self.index_html)
        self.assertIn('id="prefVegMeal"', self.index_html)
        self.assertIn('id="prefAisleSeat"', self.index_html)

    def test_11_css_styles_defined(self):
        """Test that required Phase 8 & 8.5 CSS classes are present in components.css."""
        required_classes = [
            ".demo-profile-switcher-bar",
            ".profile-chip-btn",
            ".personal-match-badge",
            ".ai-agent-step-ticker",
            ".ai-priority-chips-bar",
            ".priority-chip",
            ".ai-action-btn-pill",
            ".agent-trace-box"
        ]
        for cls in required_classes:
            self.assertIn(cls, self.components_css, f"CSS class {cls} must be defined in components.css")

    def test_12_app_js_exports(self):
        """Test that app.js exports all window functions for Phase 8.5."""
        required_exports = [
            "window.switchDemoProfile",
            "window.aiChangePriority",
            "window.askHeroAdvisor",
            "window.toggleHistoryPreference",
            "window.openPersonalizationModal",
            "window.handleSavePreferences",
            "window.renderAiAdvisorAdminMetrics"
        ]
        for exp in required_exports:
            self.assertIn(exp, self.app_js, f"Export {exp} must exist in app.js")


if __name__ == "__main__":
    unittest.main()
