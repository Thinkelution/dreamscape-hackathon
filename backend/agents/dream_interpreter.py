"""Dream Interpreter Agent: Parses messy dream text into structured DreamSchema JSON."""

import json
import re

from google.genai import types

from backend.models.schemas import DreamSchema
from backend.services.gemini_service import TEXT_MODEL, get_client

SYSTEM_PROMPT = """You are a dream analyst and creative storyteller. Given a raw, messy dream 
description, extract a structured cinematic interpretation.

Return ONLY valid JSON with this exact structure:
{
  "title": "A poetic, evocative title for this dream",
  "scenes": [
    {
      "description": "Vivid description of what happens in this scene",
      "entities": ["entity1", "entity2"],
      "emotion": "The dominant emotion",
      "visual_style": "Cinematic visual direction (lighting, color, mood)",
      "transition_to": "dissolve|morph|cut|fade"
    }
  ],
  "overall_mood": "surreal|nightmarish|ethereal|nostalgic|anxious|joyful|melancholic",
  "symbols": [
    {
      "name": "symbol_name",
      "possible_meaning": "Psychological interpretation",
      "frequency": 1
    }
  ],
  "narrative_arc": "One-sentence description of the dream's emotional journey",
  "color_palette": ["#hex1", "#hex2", "#hex3", "#hex4"]
}

Rules:
- Extract 2-5 scenes from the dream
- Each scene should be cinematically described for image generation
- Visual style should be specific enough to guide surrealist image creation
- Color palette should match the dream's mood (4-6 hex colors)
- Symbols should include psychological dream interpretation
- Be creative with the title — make it poetic and memorable"""


async def interpret_dream(raw_text: str) -> DreamSchema:
    """Parse raw dream text into a structured DreamSchema."""
    client = get_client()

    response = client.models.generate_content(
        model=TEXT_MODEL,
        contents=f"Interpret this dream and return structured JSON:\n\n{raw_text}",
        config=types.GenerateContentConfig(
            system_instruction=SYSTEM_PROMPT,
            temperature=0.7,
            response_mime_type="application/json",
        ),
    )

    raw_json = response.text.strip()
    # Strip markdown fences if present
    if raw_json.startswith("```"):
        raw_json = re.sub(r"^```(?:json)?\n?", "", raw_json)
        raw_json = re.sub(r"\n?```$", "", raw_json)

    data = json.loads(raw_json)
    return DreamSchema(**data)
