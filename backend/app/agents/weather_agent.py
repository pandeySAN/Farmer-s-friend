import httpx
from datetime import datetime
from app.core.config import settings
from app.agents.state import AgentState, WeatherData


def determine_season(month: int) -> str:
    """India's 3 agricultural seasons"""
    if 6 <= month <= 11:
        return "kharif"   # rice, maize, cotton
    elif month >= 11 or month <= 3:
        return "rabi"     # wheat, mustard, peas
    else:
        return "zaid"     # watermelon, vegetables


async def weather_agent(state: AgentState) -> AgentState:
    """
    Calls OpenWeatherMap API for the farmer's location.
    Extracts: temperature, rainfall, humidity, alerts.
    """
    ctx = state["farmer_context"]
    lat = ctx.get("latitude",  26.85)  # default: Lucknow
    lon = ctx.get("longitude", 80.91)

    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            # Current weather
            current_resp = await client.get(
                "https://api.openweathermap.org/data/2.5/weather",
                params={
                    "lat":   lat,
                    "lon":   lon,
                    "appid": settings.OPENWEATHER_API_KEY,
                    "units": "metric",
                },
            )
            current_resp.raise_for_status()
            current = current_resp.json()

            # 7-day forecast
            forecast_resp = await client.get(
                "https://api.openweathermap.org/data/2.5/forecast",
                params={
                    "lat":   lat,
                    "lon":   lon,
                    "appid": settings.OPENWEATHER_API_KEY,
                    "units": "metric",
                    "cnt":   7,
                },
            )
            forecast_resp.raise_for_status()
            forecast = forecast_resp.json()

        temp      = current["main"]["temp"]
        humidity  = current["main"]["humidity"]
        rainfall  = current.get("rain", {}).get("1h", 0) * 24 * 30  # estimate monthly

        forecast_days = []
        for item in forecast["list"]:
            forecast_days.append({
                "date":    item["dt_txt"],
                "temp":    item["main"]["temp"],
                "weather": item["weather"][0]["description"],
                "rain_mm": item.get("rain", {}).get("3h", 0),
            })

        alerts = []
        if temp > 40:
            alerts.append("Extreme heat warning — avoid sowing for 2 weeks")
        if temp < 10:
            alerts.append("Frost risk — protect seedlings at night")
        if humidity < 20:
            alerts.append("Very low humidity — drought risk, ensure irrigation")
        if humidity > 90:
            alerts.append("High humidity — monitor for fungal disease")
        if rainfall < 20:
            alerts.append("Low rainfall expected — irrigation required")

        season   = determine_season(datetime.now().month)
        suitable = temp > 15 and temp < 38 and humidity > 30

        weather_data: WeatherData = {
            "temperature_celsius": round(temp, 1),
            "humidity_percent":    round(humidity, 1),
            "rainfall_mm_month":   round(rainfall, 1),
            "season":              season,
            "forecast_7_days":     forecast_days,
            "risk_alerts":         alerts,
            "suitable_for_sowing": suitable,
        }

        return {**state, "weather_data": weather_data}

    except Exception as e:
        error_msg = f"Weather agent error: {str(e)}"
        return {
            **state,
            "weather_data": {
                "temperature_celsius": 28.0,
                "humidity_percent":    60.0,
                "rainfall_mm_month":   80.0,
                "season":              determine_season(datetime.now().month),
                "forecast_7_days":     [],
                "risk_alerts":         ["Could not fetch live weather — using estimates"],
                "suitable_for_sowing": True,
            },
            "errors": state.get("errors", []) + [error_msg],
        }
