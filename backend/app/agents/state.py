from typing import TypedDict, Optional, List, Dict, Any
from datetime import datetime


class FarmerContext(TypedDict):
    farmer_id:       str
    name:            str
    latitude:        float
    longitude:       float
    district:        str
    state:           str
    land_area_acres: float
    soil_type:       str
    irrigation:      str
    language:        str
    crop_history:    List[Dict]


class WeatherData(TypedDict):
    temperature_celsius: float
    humidity_percent:    float
    rainfall_mm_month:   float
    season:              str
    forecast_7_days:     List[Dict]
    risk_alerts:         List[str]
    suitable_for_sowing: bool


class CropData(TypedDict):
    recommended_crops:   List[Dict]
    avoid_crops:         List[str]
    best_sowing_window:  str


class MarketData(TypedDict):
    price_forecasts:     List[Dict]
    best_selling_month:  str
    market_risk:         str


class ResourceData(TypedDict):
    fertilizer_plan:     Dict
    irrigation_schedule: str
    estimated_cost_inr:  float
    expected_profit_inr: float


class MemoryData(TypedDict):
    past_successful_crops:    List[str]
    past_failed_crops:        List[str]
    personalized_tips:        List[str]
    similar_farmer_insights:  str


class AgentState(TypedDict):
    # Input
    query:          str
    farmer_context: FarmerContext

    # Agent outputs
    weather_data:   Optional[WeatherData]
    crop_data:      Optional[CropData]
    market_data:    Optional[MarketData]
    resource_data:  Optional[ResourceData]
    memory_data:    Optional[MemoryData]

    # Gemini's final output
    final_response:  Optional[str]
    structured_plan: Optional[Dict]

    # Metadata
    errors:       List[str]
    started_at:   str
    completed_at: Optional[str]
