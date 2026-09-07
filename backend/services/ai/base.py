"""
AirfareX India — Base AI Provider Interface
Defines the abstract contract for AI intelligence providers (Rule-Based, Gemini, OpenAI).
"""

from abc import ABC, abstractmethod
from enum import Enum
from typing import Dict, Any, List, Optional
from pydantic import BaseModel

class AIProviderType(str, Enum):
    RULE_BASED = "RULE_BASED"
    GEMINI = "GEMINI"
    OPENAI = "OPENAI"

class FlightScoringBreakdown(BaseModel):
    price_score: int
    duration_score: int
    stops_score: int
    convenience_score: int
    value_score: int
    overall_score: int

class FlightRecommendationItem(BaseModel):
    flight_no: str
    airline: str
    total_fare: int
    duration: str
    stops: str
    badge: Optional[str] = None # 'CHEAPEST', 'FASTEST', 'BEST VALUE', 'AIRFAREX PICK'
    scores: FlightScoringBreakdown
    reasons: List[str] # 2-4 factual bullet points
    why_recommended: str

class NLSearchParams(BaseModel):
    origin: Optional[str] = None
    destination: Optional[str] = None
    date: Optional[str] = None
    max_price: Optional[int] = None
    stops: Optional[str] = "Any"
    cabin: Optional[str] = "Economy"
    time_of_day: Optional[str] = "Any time"
    airline: Optional[str] = "All airlines"
    preference: Optional[str] = "best_value"
    confidence: int = 100
    clarification_needed: bool = False
    clarification_message: Optional[str] = None
    raw_query: str = ""

class FlightComparisonResult(BaseModel):
    flight_a_no: str
    flight_b_no: str
    airline_a: str
    airline_b: str
    price_a: int
    price_b: int
    price_diff: int # b - a
    duration_a: str
    duration_b: str
    duration_diff_mins: int # b - a in mins
    stops_a: str
    stops_b: str
    score_a: int
    score_b: int
    recommended_flight: str
    verdict: str
    narrative: str
    comparison_points: List[str]
    provider: str

class CopilotResponse(BaseModel):
    answer: str
    recommendation: Optional[Dict[str, Any]] = None
    facts: List[str] = []
    confidence: Optional[int] = None
    provider: str = "RULE_BASED"
    action: Optional[Dict[str, Any]] = None
    suggestions: List[str] = []

class BaseAIProvider(ABC):
    """Abstract interface for all aviation intelligence engines."""

    @property
    @abstractmethod
    def provider_name(self) -> str:
        """Returns the provider name (e.g. RULE_BASED, GEMINI, OPENAI)."""
        pass

    @abstractmethod
    async def generate_copilot_response(
        self,
        query: str,
        search_context: Optional[Dict[str, Any]] = None,
        available_flights: Optional[List[Dict[str, Any]]] = None,
        selected_flight: Optional[Dict[str, Any]] = None,
        user_preferences: Optional[Dict[str, Any]] = None,
        language: str = "en"
    ) -> CopilotResponse:
        """Processes traveler chat queries using real context."""
        pass

    @abstractmethod
    def interpret_nl_query(self, query: str) -> NLSearchParams:
        """Interprets natural language queries into structured parameters."""
        pass
