import asyncio
import json
from datetime import datetime
from typing import AsyncGenerator

from langgraph.graph import StateGraph, END
import google.generativeai as genai

from app.agents.state          import AgentState
from app.agents.weather_agent  import weather_agent
from app.agents.crop_agent     import crop_agent
from app.agents.market_agent   import market_agent
from app.agents.resource_agent import resource_agent
from app.agents.memory_agent   import memory_agent, save_to_memory
from app.core.config           import settings


genai.configure(api_key=settings.GEMINI_API_KEY)


async def run_initial_agents(state: AgentState) -> AgentState:
    """Weather + Memory run in parallel first."""
    weather_state, memory_state = await asyncio.gather(
        weather_agent(state),
        memory_agent(state),
    )
    return {
        **state,
        "weather_data": weather_state["weather_data"],
        "memory_data":  memory_state["memory_data"],
        "errors":       weather_state.get("errors", []) + memory_state.get("errors", []),
    }


async def run_secondary_agents(state: AgentState) -> AgentState:
    """Crop runs first, then Market uses crop output."""
    crop_state = await crop_agent(state)
    market_state = await market_agent(crop_state)  # ← gets crop_data
    return {
        **state,
        "crop_data":   crop_state["crop_data"],
        "market_data": market_state["market_data"],
        "errors":      state.get("errors", [])
                       + crop_state.get("errors", [])
                       + market_state.get("errors", []),
    }


async def run_resource_agent(state: AgentState) -> AgentState:
    """Resource agent runs last — needs crop + market data."""
    return await resource_agent(state)


def _build_gemini_prompts(state: AgentState) -> tuple[str, str]:
    ctx       = state["farmer_context"]
    weather   = state.get("weather_data",  {})
    crops     = state.get("crop_data",     {})
    market    = state.get("market_data",   {})
    resources = state.get("resource_data", {})
    memory    = state.get("memory_data",   {})

    system_prompt = """You are an expert agricultural advisor for Indian farmers.
You have deep knowledge of Indian crop cycles, mandi pricing, soil science, and farming economics.
You are helpful, practical, and speak in simple language.
When responding in Hindi (language: hi), use clear simple Hindi mixed with common English farm terms.
Always be specific — give exact quantities, timing, and rupee amounts.
Format your response with clear sections using emojis for easy reading on mobile."""

    user_prompt = f"""A farmer has asked: "{state['query']}"

FARMER PROFILE:
- Name: {ctx.get('name')}
- Location: {ctx.get('district')}, {ctx.get('state')}
- Farm size: {ctx.get('land_area_acres')} acres
- Soil type: {ctx.get('soil_type')}
- Irrigation: {ctx.get('irrigation')}
- Past successful crops: {memory.get('past_successful_crops', [])}
- Past failed crops: {memory.get('past_failed_crops', [])}

WEATHER DATA:
- Temperature: {weather.get('temperature_celsius')}°C
- Humidity: {weather.get('humidity_percent')}%
- Estimated monthly rainfall: {weather.get('rainfall_mm_month')} mm
- Current season: {weather.get('season')}
- Suitable for sowing: {weather.get('suitable_for_sowing')}
- Alerts: {weather.get('risk_alerts', [])}

TOP CROP RECOMMENDATIONS:
{json.dumps(crops.get('recommended_crops', []), indent=2, ensure_ascii=False)}
Best sowing window: {crops.get('best_sowing_window')}

MARKET PRICE FORECASTS:
{json.dumps(market.get('price_forecasts', []), indent=2, ensure_ascii=False)}
Market risk level: {market.get('market_risk')}

RESOURCE PLAN (for top crop, {ctx.get('land_area_acres')} acres):
- Fertilizer: N={resources.get('fertilizer_plan', {}).get('nitrogen_kg')}kg, P={resources.get('fertilizer_plan', {}).get('phosphorus_kg')}kg, K={resources.get('fertilizer_plan', {}).get('potassium_kg')}kg
- Urea bags needed: {resources.get('fertilizer_plan', {}).get('urea_bags_50kg')}
- Irrigation: {resources.get('irrigation_schedule')}
- Total estimated cost: ₹{resources.get('estimated_cost_inr')}
- Expected profit: ₹{resources.get('expected_profit_inr')}

PERSONALISED TIPS:
{memory.get('personalized_tips', [])}

Please write a complete, actionable recommendation for this farmer.
Respond in language code: {ctx.get('language', 'hi')}
If language is 'hi', respond primarily in Hindi but keep crop names and numbers in English.
Structure your response with these sections:
1. 🌾 Best crop recommendation (with clear reason)
2. 📅 When to sow and what to buy
3. 💰 Expected earnings and costs
4. ⚠️ Risks to watch out for
5. ✅ Immediate next steps (numbered list)"""

    return system_prompt, user_prompt


async def gemini_reasoning_node(state: AgentState) -> AgentState:
    """Passes all agent outputs to Gemini for the final recommendation."""
    system_prompt, user_prompt = _build_gemini_prompts(state)

    try:
        combined_prompt = system_prompt + "\n\n" + user_prompt
        model = genai.GenerativeModel(settings.GEMINI_MODEL)
        response = model.generate_content(
            combined_prompt,
            generation_config=genai.types.GenerationConfig(max_output_tokens=1500)
        )
        final_response = response.text
    except Exception as e:
        ctx   = state["farmer_context"]
        crops = state.get("crop_data", {})
        final_response = (
            f"🌾 Based on available data:\n\n"
            f"Top crop: {(crops.get('recommended_crops') or [{}])[0].get('name', 'Wheat')}\n\n"
            f"Please check with your local agriculture office for detailed guidance.\n"
            f"(AI reasoning temporarily unavailable: {str(e)})"
        )

    return {
        **state,
        "final_response": final_response,
        "completed_at":   datetime.utcnow().isoformat(),
    }


def build_graph():
    workflow = StateGraph(AgentState)
    workflow.add_node("initial_agents",   run_initial_agents)
    workflow.add_node("secondary_agents", run_secondary_agents)
    workflow.add_node("resource_agent",   run_resource_agent)
    workflow.add_node("gemini_reasoning", gemini_reasoning_node)

    workflow.set_entry_point("initial_agents")
    workflow.add_edge("initial_agents",   "secondary_agents")
    workflow.add_edge("secondary_agents", "resource_agent")
    workflow.add_edge("resource_agent",   "gemini_reasoning")
    workflow.add_edge("gemini_reasoning", END)

    return workflow.compile()


farm_graph = build_graph()


def _make_initial_state(query: str, farmer: dict, db_history: list) -> AgentState:
    return {
        "query": query,
        "farmer_context": {
            "farmer_id":       str(farmer.get("id", "")),
            "name":            farmer.get("name", "Farmer"),
            "latitude":        farmer.get("latitude",      26.85),
            "longitude":       farmer.get("longitude",     80.91),
            "district":        farmer.get("district",      ""),
            "state":           farmer.get("state",         "Uttar Pradesh"),
            "land_area_acres": farmer.get("land_area_acres", 2.0),
            "soil_type":       farmer.get("soil_type",    "alluvial"),
            "irrigation":      farmer.get("irrigation",   "none"),
            "language":        farmer.get("language",     "hi"),
            "crop_history":    db_history,
        },
        "weather_data":    None,
        "crop_data":       None,
        "market_data":     None,
        "resource_data":   None,
        "memory_data":     None,
        "final_response":  None,
        "structured_plan": None,
        "errors":          [],
        "started_at":      datetime.utcnow().isoformat(),
        "completed_at":    None,
    }


async def run_farm_advisor(query: str, farmer: dict, db_history: list) -> AgentState:
    """Main entry point — runs the full multi-agent pipeline."""
    initial_state = _make_initial_state(query, farmer, db_history)
    result = await farm_graph.ainvoke(initial_state)
    return result


async def stream_farm_advisor(
    query: str, farmer: dict, db_history: list
) -> AsyncGenerator[str, None]:
    """Streaming version — yields Server-Sent Events."""
    yield f"data: {json.dumps({'type': 'status', 'message': '🌦️ Fetching weather data...'})}\n\n"

    state = _make_initial_state(query, farmer, db_history)

    state = await run_initial_agents(state)
    yield f"data: {json.dumps({'type': 'status', 'message': '📊 Checking market prices...'})}\n\n"

    state = await run_secondary_agents(state)
    yield f"data: {json.dumps({'type': 'status', 'message': '💧 Building resource plan...'})}\n\n"

    state = await run_resource_agent(state)
    yield f"data: {json.dumps({'type': 'status', 'message': '🤖 Gemini is writing your recommendation...'})}\n\n"

    ctx       = state["farmer_context"]
    weather   = state.get("weather_data",  {})
    crops     = state.get("crop_data",     {})
    market    = state.get("market_data",   {})
    resources = state.get("resource_data", {})
    memory    = state.get("memory_data",   {})

    system_prompt = """You are an expert agricultural advisor for Indian farmers.
You are helpful, practical, and speak in simple language.
When responding in Hindi, use clear simple Hindi mixed with common English farm terms.
Always be specific — give exact quantities, timing, and rupee amounts."""

    user_prompt = (
        f"Farmer query: \"{query}\"\n\n"
        f"Farmer: {ctx.get('name')}, {ctx.get('land_area_acres')} acres, "
        f"{ctx.get('soil_type')} soil, {ctx.get('state')}\n"
        f"Season: {weather.get('season')} | Temp: {weather.get('temperature_celsius')}°C | "
        f"Alerts: {weather.get('risk_alerts', [])}\n"
        f"Top crop: {(crops.get('recommended_crops') or [{}])[0].get('name', 'N/A')} "
        f"(confidence: {(crops.get('recommended_crops') or [{}])[0].get('confidence', 'N/A')})\n"
        f"Expected profit: ₹{resources.get('expected_profit_inr', 'N/A')} | "
        f"Cost: ₹{resources.get('estimated_cost_inr', 'N/A')}\n"
        f"Market risk: {market.get('market_risk', 'N/A')}\n"
        f"Past success: {memory.get('past_successful_crops', [])}\n\n"
        f"Write a complete, actionable recommendation in language: {ctx.get('language', 'hi')}.\n"
        f"Include: crop choice + reason, sowing schedule, costs/profits, risks, and next steps."
    )

    full_response = ""
    combined_prompt = system_prompt + "\n\n" + user_prompt
    model = genai.GenerativeModel(settings.GEMINI_MODEL)
    response = model.generate_content(
        combined_prompt,
        generation_config=genai.types.GenerationConfig(max_output_tokens=1500),
        stream=True
    )
    for chunk in response:
        if chunk.text:
            text = chunk.text
            full_response += text
            yield f"data: {json.dumps({'type': 'token', 'text': text})}\n\n"

    state["final_response"] = full_response
    state["completed_at"]   = datetime.utcnow().isoformat()

    yield f"data: {json.dumps({'type': 'done', 'state': {'weather': state['weather_data'], 'crops': state['crop_data'], 'market': state['market_data'], 'resources': state['resource_data']}})}\n\n"
