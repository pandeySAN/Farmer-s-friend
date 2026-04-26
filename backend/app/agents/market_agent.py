import httpx
from app.agents.state import AgentState, MarketData
from app.core.config import settings


AGMARKNET_URL = "https://api.data.gov.in/resource/9ef84268-d588-465a-a308-a864a43d0070"

# Fallback price data (₹ per quintal — based on 2024 MSP + mandi prices)
FALLBACK_PRICES = {
    "Wheat":          {"current": 2275, "trend": "stable",   "peak_month": "April"},
    "Rice (Paddy)":   {"current": 2183, "trend": "rising",   "peak_month": "November"},
    "Maize":          {"current": 1850, "trend": "stable",   "peak_month": "December"},
    "Cotton":         {"current": 6620, "trend": "falling",  "peak_month": "February"},
    "Soybean":        {"current": 4600, "trend": "rising",   "peak_month": "January"},
    "Mustard":        {"current": 5650, "trend": "stable",   "peak_month": "March"},
    "Groundnut":      {"current": 6377, "trend": "rising",   "peak_month": "December"},
    "Chickpea":       {"current": 5440, "trend": "stable",   "peak_month": "April"},
    "Sugarcane":      {"current": 315,  "trend": "stable",   "peak_month": "March"},
    "Jowar":          {"current": 3180, "trend": "stable",   "peak_month": "January"},
    "Bajra":          {"current": 2500, "trend": "stable",   "peak_month": "December"},
    "Peas":           {"current": 3200, "trend": "rising",   "peak_month": "February"},
    "Pulses":         {"current": 6000, "trend": "stable",   "peak_month": "March"},
    "Millets":        {"current": 2000, "trend": "stable",   "peak_month": "November"},
    "Linseed":        {"current": 5500, "trend": "stable",   "peak_month": "April"},
    "Lentils":        {"current": 6800, "trend": "rising",   "peak_month": "April"},
    "Barley":         {"current": 1800, "trend": "stable",   "peak_month": "March"},
}

TREND_ADVICE = {
    "rising":  "Prices are rising — hold stock if possible, sell at peak month",
    "falling": "Prices are falling — sell quickly or process before storing",
    "stable":  "Prices are stable — standard market conditions",
}


async def market_agent(state: AgentState) -> AgentState:
    """
    Fetches current mandi prices and predicts price trends.
    Uses data.gov.in Agmarknet API (free). Falls back to MSP estimates.
    """
    crop_data = state.get("crop_data", {})
    ctx       = state["farmer_context"]

    crops_to_check = [
        c["name"] for c in (crop_data or {}).get("recommended_crops", [])
    ] or ["Wheat", "Rice (Paddy)", "Mustard"]

    price_forecasts = []

    try:
        async with httpx.AsyncClient(timeout=8.0) as client:
            for crop_name in crops_to_check:
                try:
                    resp = await client.get(
                        AGMARKNET_URL,
                        params={
                            "api-key":              "579b464db66ec23bdd000001cdd3946e44ce4aaebc7ac7b61b867c23",
                            "format":               "json",
                            "filters[commodity]":   crop_name.split(" ")[0],
                            "filters[state]":       ctx.get("state", "Uttar Pradesh"),
                            "limit":                5,
                        },
                        timeout=5.0,
                    )

                    if resp.status_code == 200:
                        data    = resp.json()
                        records = data.get("records", [])
                        if records:
                            avg_price = sum(float(r.get("modal_price", 0)) for r in records) / len(records)
                            fallback  = FALLBACK_PRICES.get(crop_name, {"trend": "stable", "peak_month": "N/A"})
                            price_forecasts.append({
                                "crop":               crop_name,
                                "current_price_inr":  round(avg_price, 0),
                                "predicted_price_inr": round(avg_price * 1.08, 0),
                                "trend":              fallback["trend"],
                                "best_selling_month": fallback["peak_month"],
                                "advice":             TREND_ADVICE[fallback["trend"]],
                                "source":             "Live mandi data",
                            })
                            continue

                except Exception:
                    pass

                # Fallback for this crop
                fb = FALLBACK_PRICES.get(crop_name, {
                    "current": 2000, "trend": "stable", "peak_month": "N/A"
                })
                price_forecasts.append({
                    "crop":               crop_name,
                    "current_price_inr":  fb["current"],
                    "predicted_price_inr": round(fb["current"] * 1.06, 0),
                    "trend":              fb["trend"],
                    "best_selling_month": fb["peak_month"],
                    "advice":             TREND_ADVICE[fb["trend"]],
                    "source":             "MSP estimate",
                })

    except Exception:
        for crop_name in crops_to_check:
            fb = FALLBACK_PRICES.get(crop_name, {"current": 2000, "trend": "stable", "peak_month": "N/A"})
            price_forecasts.append({
                "crop":               crop_name,
                "current_price_inr":  fb["current"],
                "predicted_price_inr": round(fb["current"] * 1.06, 0),
                "trend":              fb["trend"],
                "best_selling_month": fb["peak_month"],
                "advice":             TREND_ADVICE[fb["trend"]],
                "source":             "MSP estimate (offline)",
            })

    trends = [f["trend"] for f in price_forecasts]
    if trends.count("falling") >= 2:
        overall_risk = "high"
    elif trends.count("falling") == 1:
        overall_risk = "medium"
    else:
        overall_risk = "low"

    best_crop = max(price_forecasts, key=lambda x: x["predicted_price_inr"]) if price_forecasts else {}

    market_data: MarketData = {
        "price_forecasts":    price_forecasts,
        "best_selling_month": best_crop.get("best_selling_month", "N/A"),
        "market_risk":        overall_risk,
    }

    return {**state, "market_data": market_data}
