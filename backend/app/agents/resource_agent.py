from app.agents.state import AgentState, ResourceData


FERTILIZER_GUIDE = {
    "Wheat":        {"N": 60, "P": 30, "K": 20, "urea_bags": 3},
    "Rice (Paddy)": {"N": 80, "P": 40, "K": 40, "urea_bags": 4},
    "Maize":        {"N": 70, "P": 35, "K": 25, "urea_bags": 3},
    "Cotton":       {"N": 50, "P": 25, "K": 50, "urea_bags": 2},
    "Soybean":      {"N": 20, "P": 60, "K": 20, "urea_bags": 1},
    "Mustard":      {"N": 40, "P": 30, "K": 20, "urea_bags": 2},
    "Chickpea":     {"N": 15, "P": 45, "K": 20, "urea_bags": 1},
    "Groundnut":    {"N": 25, "P": 50, "K": 25, "urea_bags": 1},
    "Sugarcane":    {"N": 150,"P": 60, "K": 80, "urea_bags": 7},
    "Jowar":        {"N": 40, "P": 20, "K": 20, "urea_bags": 2},
    "Bajra":        {"N": 40, "P": 20, "K": 20, "urea_bags": 2},
    "Pulses":       {"N": 15, "P": 40, "K": 20, "urea_bags": 1},
    "default":      {"N": 50, "P": 30, "K": 25, "urea_bags": 2},
}

IRRIGATION_GUIDE = {
    "drip":      "Drip: 2 litres/plant/day. Schedule: every alternate day, 6–8 AM",
    "flood":     "Flood: irrigate every 10–15 days, maintain 5cm standing water",
    "sprinkler": "Sprinkler: 30 min session, every 3 days, early morning",
    "none":      "Rainfed: no supplemental irrigation, ensure good field drainage",
}

COSTS_PER_ACRE = {
    "Wheat":        {"seeds": 1200, "labour": 3500, "pesticide": 800,  "misc": 500},
    "Rice (Paddy)": {"seeds": 800,  "labour": 5000, "pesticide": 1200, "misc": 600},
    "Maize":        {"seeds": 1500, "labour": 3000, "pesticide": 700,  "misc": 400},
    "Cotton":       {"seeds": 1800, "labour": 6000, "pesticide": 2500, "misc": 800},
    "Soybean":      {"seeds": 2200, "labour": 2500, "pesticide": 600,  "misc": 400},
    "Mustard":      {"seeds": 600,  "labour": 2000, "pesticide": 500,  "misc": 300},
    "Chickpea":     {"seeds": 1400, "labour": 2000, "pesticide": 400,  "misc": 300},
    "Groundnut":    {"seeds": 3500, "labour": 4000, "pesticide": 800,  "misc": 500},
    "default":      {"seeds": 1200, "labour": 3000, "pesticide": 700,  "misc": 400},
}

FERTILIZER_COST_PER_KG = {"N": 18, "P": 45, "K": 25}


async def resource_agent(state: AgentState) -> AgentState:
    """
    Calculates fertilizer plan, irrigation schedule, input costs, and expected profit.
    """
    ctx         = state["farmer_context"]
    crop_data   = state.get("crop_data", {})
    market_data = state.get("market_data", {})

    area_acres = ctx.get("land_area_acres", 2.0) or 2.0
    irrigation = ctx.get("irrigation", "none")
    top_crop   = (crop_data.get("recommended_crops") or [{}])[0]
    crop_name  = top_crop.get("name", "Wheat")

    fert    = FERTILIZER_GUIDE.get(crop_name, FERTILIZER_GUIDE["default"])
    total_N = fert["N"] * area_acres
    total_P = fert["P"] * area_acres
    total_K = fert["K"] * area_acres

    fertilizer_plan = {
        "nitrogen_kg":    round(total_N),
        "phosphorus_kg":  round(total_P),
        "potassium_kg":   round(total_K),
        "urea_bags_50kg": round(fert["urea_bags"] * area_acres),
        "dap_bags_50kg":  round((total_P / 23) * 0.5),
        "mop_bags_50kg":  round((total_K / 50) * 0.6),
        "schedule": (
            "Basal dose (50%): at sowing. "
            "Top dress (30%): 21 days after. "
            "Final (20%): 42 days after sowing."
        ),
    }

    irrigation_schedule = IRRIGATION_GUIDE.get(irrigation, IRRIGATION_GUIDE["none"])

    costs     = COSTS_PER_ACRE.get(crop_name, COSTS_PER_ACRE["default"])
    fert_cost = (total_N * FERTILIZER_COST_PER_KG["N"] +
                 total_P * FERTILIZER_COST_PER_KG["P"] +
                 total_K * FERTILIZER_COST_PER_KG["K"])

    total_cost = sum(v * area_acres for v in costs.values()) + fert_cost

    yield_kg   = top_crop.get("expected_yield_kg", 1400) * area_acres
    price_data = next(
        (p for p in market_data.get("price_forecasts", []) if p["crop"] == crop_name),
        {"predicted_price_inr": 2000}
    )
    revenue = (yield_kg / 100) * price_data["predicted_price_inr"]
    profit  = revenue - total_cost

    resource_data: ResourceData = {
        "fertilizer_plan":     fertilizer_plan,
        "irrigation_schedule": irrigation_schedule,
        "estimated_cost_inr":  round(total_cost),
        "expected_profit_inr": round(profit),
    }

    return {**state, "resource_data": resource_data}
