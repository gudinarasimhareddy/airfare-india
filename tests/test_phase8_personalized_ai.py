"""
Test Suite for Phase 8 & 8.5: Central Agentic AI Travel Advisor & Live Voice Engine
AirfareX India
"""
import sys
import unittest
import json
import os
import re

try:
    if hasattr(sys.stdout, "reconfigure") and not sys.stdout.closed:
        sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

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

    def test_01_central_agent_object(self):
        """Test Step 3: Central agent window.AirfareXAgent is defined with all required methods."""
        self.assertIn("window.AirfareXAgent =", self.agent_js)
        
        required_methods = [
            "processUserRequest",
            "getState",
            "resetSession",
            "executeTool",
            "getCustomerProfile",
            "analyzeTravelHistory",
            "calculatePersonalMatch",
            "tools"
        ]
        for m in required_methods:
            self.assertIn(m, self.agent_js, f"Method or property {m} must exist on window.AirfareXAgent")

    def test_02_all_19_tools_registered(self):
        """Test Step 10: Explicit 19-tool registry on AirfareXAgent.tools."""
        required_19_tools = [
            "searchFlights",
            "filterFlights",
            "sortFlights",
            "getFlightDetails",
            "calculateFlightScore",
            "explainScore",
            "getRecommendations",
            "getCheapestFlight",
            "getFastestFlight",
            "getMostReliableFlight",
            "getBestOverallFlight",
            "getBestForCustomer",
            "compareFlights",
            "getCustomerProfile",
            "getTravelHistory",
            "analyzeTravelHistory",
            "calculatePersonalMatch",
            "createDemoBooking",
            "confirmDemoBooking"
        ]
        for tool in required_19_tools:
            self.assertIn(f"{tool}:", self.agent_js, f"Tool '{tool}' must be explicitly registered in AgentTools")

    def test_03_three_demo_profiles_with_exact_weights(self):
        """Test Step 24: 3 demo customer profiles with 10 past bookings and exact weights."""
        self.assertIn("DEMO-1001", self.agent_js)
        self.assertIn("Rajesh Sharma", self.agent_js)
        self.assertIn("DEMO-1002", self.agent_js)
        self.assertIn("Priya Patel", self.agent_js)
        self.assertIn("DEMO-1003", self.agent_js)
        self.assertIn("Vikram Reddy", self.agent_js)

        # Exact weights verification (Step 24)
        # Budget: Price 0.60, Reliability 0.20, Comfort 0.10, Speed 0.10
        self.assertIn("priceImportance: 0.60", self.agent_js)
        # Comfort: Comfort 0.60, Reliability 0.20, Price 0.10, Speed 0.10
        self.assertIn("comfortImportance: 0.60", self.agent_js)
        # Time-Critical: Speed 0.50, Reliability 0.30, Price 0.10, Comfort 0.10
        self.assertIn("speedImportance: 0.50", self.agent_js)

        # 10 trips per profile
        rajesh_trips = len(re.findall(r'id:\s*"TRIP-1', self.agent_js))
        self.assertEqual(rajesh_trips, 10, "Rajesh Sharma must have 10 past bookings")

        priya_trips = len(re.findall(r'id:\s*"TRIP-2', self.agent_js))
        self.assertEqual(priya_trips, 10, "Priya Patel must have 10 past bookings")

        vikram_trips = len(re.findall(r'id:\s*"TRIP-3', self.agent_js))
        self.assertEqual(vikram_trips, 10, "Vikram Reddy must have 10 past bookings")

    def test_04_history_analysis_engine(self):
        """Test Step 5: analyzeTravelHistory calculates all required behavioral signals."""
        self.assertIn("function analyzeTravelHistory", self.agent_js)
        expected_signals = [
            "preferredAirline",
            "averageFare",
            "typicalBudget",
            "preferredDeparture",
            "preferredStops",
            "priceSensitivity",
            "comfortSensitivity",
            "reliabilitySensitivity"
        ]
        for sig in expected_signals:
            self.assertIn(sig, self.agent_js, f"Signal {sig} must be computed in analyzeTravelHistory")

    def test_05_personal_match_formula(self):
        """Test Step 9: Personal Match formula with distinct factors."""
        self.assertIn("function calculatePersonalMatch", self.agent_js)
        self.assertIn("priceFit", self.agent_js)
        self.assertIn("comfortFit", self.agent_js)
        self.assertIn("reliabilityFit", self.agent_js)
        self.assertIn("punctualityFit", self.agent_js)
        self.assertIn("convenienceFit", self.agent_js)

    def test_06_current_request_priority_override(self):
        """Test Step 6 & 7: Current request natural language intent overrides history."""
        self.assertIn("comfort is more important", self.agent_js)
        self.assertIn("comfort matters more", self.agent_js)
        self.assertIn("price is most important", self.agent_js)
        self.assertIn("priorityOverride", self.agent_js)

    def test_07_live_voice_assistant_engine(self):
        """Test Step 12-18: Live Voice AI Engine with SpeechRecognition, SpeechSynthesis & 7 states."""
        self.assertIn("SpeechRecognition", self.agent_js)
        self.assertIn("speechSynthesis", self.agent_js)
        self.assertIn("startVoiceListening", self.agent_js)
        self.assertIn("stopVoiceListening", self.agent_js)
        self.assertIn("speakResponse", self.agent_js)
        self.assertIn("stopSpeaking", self.agent_js)

        # 7 States
        states = [
            "🎙️ Ready",
            "🔴 Listening...",
            "🧠 Understanding...",
            "🔎 Searching...",
            "📊 Analyzing...",
            "💬 Responding...",
            "✓ Ready"
        ]
        for s in states:
            self.assertIn(s, self.agent_js, f"Voice state '{s}' must be handled in aiAgent.js")

    def test_08_voice_interruption_support(self):
        """Test Step 17: Voice interruption stops speech synthesis immediately."""
        self.assertIn("stopSpeaking()", self.agent_js)
        self.assertIn("window.speechSynthesis.cancel()", self.agent_js)

    def test_09_accessibility_preferences_privacy(self):
        """Test Step 19 & 20: User-provided accessibility preferences and privacy toggle."""
        self.assertIn("wheelchairAssistance", self.agent_js)
        self.assertIn("reducedWalking", self.agent_js)
        self.assertIn("airportAssistance", self.agent_js)
        self.assertIn("historyUsageEnabled", self.agent_js)
        self.assertIn("IGNORE_HISTORY", self.agent_js)
        self.assertIn("USE_HISTORY", self.agent_js)

    def test_10_html_ui_integration(self):
        """Test HTML elements for Voice Agent Modal, profile switcher, and script loading order."""
        self.assertIn('id="voiceAgentModal"', self.index_html)
        self.assertIn('id="voiceOrb"', self.index_html)
        self.assertIn('id="voiceStateBadge"', self.index_html)
        self.assertIn('id="voiceTranscriptBox"', self.index_html)
        self.assertIn('id="voiceFallbackAlert"', self.index_html)
        self.assertIn('id="voiceMainControlBtn"', self.index_html)

        # Script loading order
        agent_idx = self.index_html.find('/js/aiAgent.js')
        app_idx = self.index_html.find('/js/app.js')
        self.assertGreater(agent_idx, 0, "aiAgent.js must be included in index.html")
        self.assertGreater(app_idx, 0, "app.js must be included in index.html")
        self.assertLess(agent_idx, app_idx, "aiAgent.js MUST load before app.js")

    def test_11_css_voice_and_card_styling(self):
        """Test CSS styles for voice modal, animated orb, waveform rings, and match badges."""
        required_classes = [
            ".voice-agent-modal-card",
            ".voice-orb",
            ".voice-orb-ring",
            ".voice-state-badge",
            ".voice-fallback-alert",
            ".voice-transcript-box",
            ".personal-match-badge",
            ".ai-recommendation-spotlight-card"
        ]
        for cls in required_classes:
            self.assertIn(cls, self.components_css, f"CSS rule '{cls}' must be defined in components.css")

    def test_12_app_js_voice_and_agent_exports(self):
        """Test app.js window bindings for all Voice and Agent controller functions."""
        required_exports = [
            "window.openVoiceAgentModal",
            "window.closeVoiceAgentModal",
            "window.toggleVoiceListening",
            "window.toggleVoiceMute",
            "window.handleVoiceQuickCommand",
            "window.switchDemoProfile",
            "window.aiChangePriority",
            "window.openPersonalizationModal",
            "window.handleSavePreferences"
        ]
        for exp in required_exports:
            self.assertIn(exp, self.app_js, f"Export '{exp}' must exist in app.js")


if __name__ == "__main__":
    unittest.main()
