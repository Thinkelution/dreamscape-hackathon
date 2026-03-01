"""Dream Analyst Agent: Analyzes recurring symbols, emotional patterns, and
cross-dream connections across a user's dream journal."""

import json
import re

from google.genai import types

from backend.models.schemas import ThemeReport
from backend.services.gemini_service import TEXT_MODEL, get_client

SYSTEM_PROMPT = """You are a dream psychologist and pattern analyst. Given a collection of 
dream interpretations, identify recurring symbols, emotional patterns, and meaningful 
connections between dreams.

Return ONLY valid JSON with this exact structure:
{
  "total_dreams": <number>,
  "recurring_symbols": [
    {
      "symbol": "symbol name",
      "count": <number of dreams it appears in>,
      "dream_ids": ["id1", "id2"],
      "interpretation": "Psychological meaning of this recurring symbol"
    }
  ],
  "emotional_patterns": [
    {
      "pattern": "Description of the emotional pattern",
      "frequency": "How often it occurs",
      "correlation": "What it might correlate with"
    }
  ],
  "connections": [
    {
      "dream_id_1": "id1",
      "dream_id_2": "id2",
      "shared_elements": ["element1", "element2"],
      "insight": "What this connection might mean"
    }
  ]
}

Provide deep, thoughtful psychological analysis. Look for patterns across time,
recurring archetypes, and emotional threads that connect different dreams."""


async def analyze_dream_journal(
    dreams: list[dict],
    user_id: str = "anonymous",
) -> ThemeReport:
    """Analyze a collection of dreams for patterns and recurring themes."""
    if not dreams:
        return ThemeReport(user_id=user_id, total_dreams=0)

    client = get_client()

    dream_summaries = []
    for d in dreams:
        schema = d.get("dream_schema", {})
        summary = {
            "id": d.get("id", "unknown"),
            "title": schema.get("title", "Untitled"),
            "mood": schema.get("overall_mood", "unknown"),
            "symbols": [s.get("name", "") for s in schema.get("symbols", [])],
            "scenes": len(schema.get("scenes", [])),
            "narrative_arc": schema.get("narrative_arc", ""),
        }
        dream_summaries.append(summary)

    response = client.models.generate_content(
        model=TEXT_MODEL,
        contents=f"Analyze these {len(dream_summaries)} dreams for recurring patterns:\n\n"
                 f"{json.dumps(dream_summaries, indent=2)}",
        config=types.GenerateContentConfig(
            system_instruction=SYSTEM_PROMPT,
            temperature=0.5,
            response_mime_type="application/json",
        ),
    )

    raw_json = response.text.strip()
    if raw_json.startswith("```"):
        raw_json = re.sub(r"^```(?:json)?\n?", "", raw_json)
        raw_json = re.sub(r"\n?```$", "", raw_json)

    data = json.loads(raw_json)
    return ThemeReport(user_id=user_id, **data)
