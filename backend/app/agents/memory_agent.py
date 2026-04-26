from app.agents.state import AgentState, MemoryData
from app.core.config import settings

_pinecone_index = None


def get_pinecone_index():
    global _pinecone_index
    if _pinecone_index is None and settings.PINECONE_API_KEY:
        from pinecone import Pinecone
        pc = Pinecone(api_key=settings.PINECONE_API_KEY)
        if settings.PINECONE_INDEX not in [i.name for i in pc.list_indexes()]:
            pc.create_index(
                name  = settings.PINECONE_INDEX,
                dimension = 1536,
                metric    = "cosine",
                spec      = {"serverless": {"cloud": "aws", "region": "us-east-1"}},
            )
        _pinecone_index = pc.Index(settings.PINECONE_INDEX)
    return _pinecone_index


async def memory_agent(state: AgentState) -> AgentState:
    """
    Analyses farmer's crop history and retrieves personalized insights.
    Optionally uses Pinecone for similar-farmer recommendations.
    """
    ctx          = state["farmer_context"]
    crop_history = ctx.get("crop_history", [])

    past_successful = []
    past_failed     = []

    for record in crop_history:
        crop_name = record.get("crop_name", "")
        profit    = record.get("profit_inr", 0) or 0
        yield_kg  = record.get("yield_kg",   0) or 0

        if profit > 5000 or yield_kg > 800:
            past_successful.append(crop_name)
        elif profit < 0 or yield_kg < 200:
            past_failed.append(crop_name)

    tips = []
    if past_successful:
        tips.append(f"You have successfully grown {', '.join(set(past_successful))} before")
    if past_failed:
        tips.append(f"Avoid {', '.join(set(past_failed))} — they underperformed on your farm")
    if ctx.get("soil_type") == "alluvial":
        tips.append("Your alluvial soil is excellent for most crops — you have a soil advantage")
    if ctx.get("irrigation") == "drip":
        tips.append("Your drip irrigation allows growing water-intensive crops efficiently")
    if (ctx.get("land_area_acres") or 0) < 2:
        tips.append("For small farms, focus on high-value crops like vegetables or spices")

    similar_insights = "No similar-farmer data yet — insights will improve over time"

    try:
        index = get_pinecone_index()
        if index:
            import openai
            oai = openai.OpenAI()
            query_text = (
                f"Farmer in {ctx.get('state')} with {ctx.get('soil_type')} soil "
                f"asking: {state['query']}"
            )
            emb_resp = oai.embeddings.create(input=query_text, model="text-embedding-3-small")
            query_vector = emb_resp.data[0].embedding

            results = index.query(
                vector=query_vector, top_k=3, include_metadata=True,
                filter={"state": ctx.get("state", "")},
            )

            if results["matches"]:
                insights = [m["metadata"].get("insight", "") for m in results["matches"]]
                similar_insights = " | ".join(insights[:3])

    except Exception:
        pass

    memory_data: MemoryData = {
        "past_successful_crops":   list(set(past_successful)),
        "past_failed_crops":       list(set(past_failed)),
        "personalized_tips":       tips,
        "similar_farmer_insights": similar_insights,
    }

    return {**state, "memory_data": memory_data}


async def save_to_memory(state: AgentState, recommendation_id: str):
    """Save recommendation to Pinecone for future similar-farmer matching."""
    try:
        index = get_pinecone_index()
        if not index:
            return

        import openai
        oai = openai.OpenAI()
        ctx = state["farmer_context"]

        summary = (
            f"{ctx.get('state')} farmer, {ctx.get('soil_type')} soil, "
            f"query: {state['query'][:100]}, "
            f"top crop: {(state.get('crop_data', {}).get('recommended_crops') or [{}])[0].get('name', 'N/A')}"
        )

        emb_resp = oai.embeddings.create(input=summary, model="text-embedding-3-small")
        vector   = emb_resp.data[0].embedding

        index.upsert(vectors=[{
            "id": recommendation_id,
            "values": vector,
            "metadata": {
                "state":   ctx.get("state", ""),
                "soil":    ctx.get("soil_type", ""),
                "season":  state.get("weather_data", {}).get("season", ""),
                "insight": state.get("final_response", "")[:500],
            },
        }])
    except Exception:
        pass
