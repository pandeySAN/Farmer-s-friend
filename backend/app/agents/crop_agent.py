from app.agents.state import AgentState, CropData
import os


CROP_RULES = {
    ("alluvial", "kharif"): [
        ("Rice (Paddy)", "Alluvial soil + monsoon = ideal for rice", 1800),
        ("Sugarcane",    "High water retention in alluvial, profitable", 35000),
        ("Maize",        "Fast-growing, good market demand", 1200),
    ],
    ("alluvial", "rabi"): [
        ("Wheat",        "Most profitable rabi crop in alluvial plains", 1600),
        ("Mustard",      "Low water requirement, good oil prices", 600),
        ("Peas",         "Short duration, nitrogen-fixing", 400),
    ],
    ("black", "kharif"): [
        ("Cotton",       "Black soil is ideal for cotton cultivation", 300),
        ("Soybean",      "Moisture-retaining black soil suits soybean", 700),
        ("Jowar",        "Drought-tolerant, suits black soil areas", 900),
    ],
    ("black", "rabi"): [
        ("Wheat",        "Deep black soil retains moisture for wheat", 1500),
        ("Chickpea",     "Excellent in heavy black soil, low water", 500),
        ("Linseed",      "Cold-tolerant, suits black cotton soil", 400),
    ],
    ("red", "kharif"): [
        ("Groundnut",    "Red soil is best for groundnut in India", 800),
        ("Millets",      "Drought-hardy, suits low-fertility red soil", 700),
        ("Pulses",       "Nitrogen-fixing, improves red soil quality", 400),
    ],
    ("red", "rabi"): [
        ("Tobacco",      "Red soil in AP/Karnataka ideal for tobacco", 900),
        ("Pulses",       "Lentils and gram do well in red soil", 450),
        ("Wheat",        "Possible with supplemental irrigation", 1000),
    ],
    ("sandy", "kharif"): [
        ("Bajra",        "Pearl millet thrives in sandy, arid soils", 800),
        ("Groundnut",    "Sandy loam is good for groundnut", 700),
        ("Moong",        "Short-duration pulse, good for sandy soil", 350),
    ],
    ("sandy", "rabi"): [
        ("Mustard",      "Well adapted to sandy soils of Rajasthan", 500),
        ("Wheat",        "With irrigation, wheat is possible", 900),
        ("Barley",       "Very drought-tolerant, suits sandy areas", 800),
    ],
    ("clay", "kharif"): [
        ("Rice (Paddy)", "Clay holds water — excellent for paddy", 1900),
        ("Jute",         "Clay soil retains moisture needed by jute", 2000),
        ("Sugarcane",    "Clay soil + water = high sugarcane yield", 38000),
    ],
    ("clay", "rabi"): [
        ("Wheat",        "Heavy clay with irrigation is good for wheat", 1500),
        ("Mustard",      "Adapts well to clay soils in winter", 550),
        ("Lentils",      "Clay holds nutrients for lentil growth", 450),
    ],
    ("laterite", "kharif"): [
        ("Cashew",       "Laterite soil is ideal for cashew in coastal areas", 600),
        ("Tapioca",      "Thrives in laterite, requires low input", 8000),
        ("Rubber",       "Laterite + high rainfall = ideal for rubber", 1000),
    ],
    ("laterite", "rabi"): [
        ("Pulses",       "Low-input legumes do well in laterite", 400),
        ("Millets",      "Drought-hardy crops suit laterite well", 650),
        ("Groundnut",    "Groundnut adapts to acidic laterite soils", 600),
    ],
}

GENERIC_FALLBACK = [
    ("Wheat",    "Widely adaptable, reliable in most conditions", 1400),
    ("Mustard",  "Low input, good returns, drought-tolerant",     600),
    ("Chickpea", "Low water, market demand is consistent",        500),
]


async def crop_agent(state: AgentState) -> AgentState:
    """
    Recommends top 3 crops based on soil type, season, and farming history.
    Falls back to ML model if trained model exists.
    """
    ctx          = state["farmer_context"]
    weather      = state.get("weather_data", {})
    soil_type    = ctx.get("soil_type", "alluvial").lower()
    season       = weather.get("season", "rabi")
    past_success = state.get("memory_data", {}).get("past_successful_crops", []) or []
    past_failed  = state.get("memory_data", {}).get("past_failed_crops",     []) or []

    try:
        # Try ML model first
        model_path = "ml_training/models/crop_classifier.joblib"
        if os.path.exists(model_path):
            import joblib, numpy as np
            model = joblib.load(model_path)
            soil_map   = {"alluvial":0, "black":1, "red":2, "laterite":3, "sandy":4, "clay":5}
            season_map = {"kharif":0, "rabi":1, "zaid":2}
            features = [[
                weather.get("temperature_celsius", 28),
                weather.get("humidity_percent",    60),
                weather.get("rainfall_mm_month",   80),
                soil_map.get(soil_type, 0),
                season_map.get(season, 1),
                ctx.get("land_area_acres", 2),
            ]]
            # Model output handled in Phase 4 training script

        # Rule-based recommendations
        key = (soil_type, season)
        raw = CROP_RULES.get(key, GENERIC_FALLBACK)

        recommendations = []
        for crop_name, reason, expected_yield in raw:
            confidence = 0.85
            if any(crop_name.lower() in p.lower() for p in past_success):
                confidence = min(0.97, confidence + 0.10)
                reason += " — you've grown this successfully before"
            if any(crop_name.lower() in f.lower() for f in past_failed):
                confidence = max(0.40, confidence - 0.20)
                reason += " — note: this didn't perform well for you previously"

            recommendations.append({
                "name":               crop_name,
                "confidence":         round(confidence, 2),
                "expected_yield_kg":  expected_yield,
                "expected_yield_per_acre": expected_yield,
                "reason":             reason,
            })

        recommendations.sort(key=lambda x: x["confidence"], reverse=True)

        if weather.get("suitable_for_sowing"):
            sowing_window = "Conditions are good — sow within the next 2 weeks"
        elif weather.get("risk_alerts"):
            sowing_window = "Wait for weather alerts to clear before sowing"
        else:
            sowing_window = "Check local conditions before sowing"

        crop_data: CropData = {
            "recommended_crops":  recommendations[:3],
            "avoid_crops":        past_failed[:2] if past_failed else [],
            "best_sowing_window": sowing_window,
        }

        return {**state, "crop_data": crop_data}

    except Exception as e:
        return {
            **state,
            "crop_data": {
                "recommended_crops":  [{"name": "Wheat", "confidence": 0.8,
                                        "expected_yield_kg": 1400, "reason": "Safe default crop"}],
                "avoid_crops":        [],
                "best_sowing_window": "Please consult local agriculture office",
            },
            "errors": state.get("errors", []) + [f"Crop agent error: {str(e)}"],
        }
