"""Dream Insight Agent: Analyzes a single dream for what it reveals about
the dreamer's personality, attitudes, emotional state, and subconscious patterns."""

import json
import re

from google.genai import types

from backend.models.schemas import DreamAnalysis, DreamSchema
from backend.services.gemini_service import TEXT_MODEL, get_client

SYSTEM_PROMPT = """You are an expert dream psychologist combining Jungian, Freudian, and modern 
cognitive dream analysis. Given a dream's structured interpretation and the original raw text, 
produce a deep psychological profile of the dreamer.

Return ONLY valid JSON with this exact structure:
{
  "emotions": ["emotion1", "emotion2"],
  "symbols": ["symbol1", "symbol2"],
  "title": "A short title for this analysis",
  "mood": "Overall emotional tone",
  "dreamer_insights": [
    {
      "trait": "Short trait label (e.g. 'Creative Thinker', 'Conflict Avoidant')",
      "description": "2-3 sentence explanation of what the dream reveals about this trait, referencing specific dream elements"
    }
  ],
  "attitude_summary": "A 3-5 sentence paragraph summarizing what this dream reveals about the dreamer's current emotional state, core attitudes toward life, relationships, and self. Be specific and insightful, not generic."
}

Guidelines:
- Provide 4-6 dreamer_insights, each revealing a different personality dimension
- Cover: emotional processing style, relationship patterns, self-perception, coping mechanisms, desires, and fears
- Reference specific dream symbols, scenes, and emotions in your analysis
- The attitude_summary should feel like a personal letter to the dreamer — warm but honest
- Avoid generic statements; tie everything to concrete dream elements
- Be psychologically informed but accessible, not clinical"""


async def analyze_single_dream(
    dream_schema: DreamSchema,
    raw_text: str,
) -> DreamAnalysis:
    """Analyze a single dream for personality and attitude insights."""
    client = get_client()

    dream_summary = {
        "title": dream_schema.title,
        "mood": dream_schema.overall_mood,
        "scenes": [
            {
                "description": s.description,
                "emotion": s.emotion,
                "entities": s.entities,
            }
            for s in dream_schema.scenes
        ],
        "symbols": [
            {"name": s.name, "meaning": s.possible_meaning}
            for s in dream_schema.symbols
        ],
        "narrative_arc": dream_schema.narrative_arc,
    }

    prompt = (
        f"Analyze this dream for what it reveals about the dreamer's personality and attitudes.\n\n"
        f"Raw dream text:\n{raw_text}\n\n"
        f"Structured interpretation:\n{json.dumps(dream_summary, indent=2)}"
    )

    response = client.models.generate_content(
        model=TEXT_MODEL,
        contents=prompt,
        config=types.GenerateContentConfig(
            system_instruction=SYSTEM_PROMPT,
            temperature=0.6,
            response_mime_type="application/json",
        ),
    )

    raw_json = response.text.strip()
    if raw_json.startswith("```"):
        raw_json = re.sub(r"^```(?:json)?\n?", "", raw_json)
        raw_json = re.sub(r"\n?```$", "", raw_json)

    data = json.loads(raw_json)
    return DreamAnalysis(**data)
