"""Visual Director Agent: Generates narration text + surrealist scene images via
Gemini's interleaved output (text + image in a single response stream).

This is the CORE hackathon requirement — demonstrating native interleaved output."""

import base64
import re
from io import BytesIO

from google.genai import types
from PIL import Image

from backend.models.schemas import DreamerProfile, DreamSchema, SceneSchema
from backend.services.gemini_service import INTERLEAVED_MODEL, get_client

ART_STYLE_INSTRUCTIONS = {
    "anime": "in a beautiful Japanese anime art style (Studio Ghibli / Makoto Shinkai inspired), with vibrant colors, expressive lighting, and painterly detail",
    "realistic": "in a photorealistic style with cinematic lighting, natural textures, and high detail as if captured by a professional camera",
    "watercolor": "in a soft watercolor painting style with flowing pigments, wet-on-wet blending, gentle edges, and translucent layered washes",
    "oil-painting": "in a rich oil painting style with thick impasto brushstrokes, deep saturated colors, and dramatic chiaroscuro lighting",
    "pixel-art": "in a retro pixel art style with a limited color palette, clean dithering, and nostalgic 16-bit charm",
    "cyberpunk": "in a neon-drenched cyberpunk style with glowing holographics, rain-slicked surfaces, and high-tech dystopian atmosphere",
    "fantasy": "in an epic high-fantasy illustration style with magical luminescence, mythical creatures, and otherworldly landscapes",
}

SCENE_PROMPT_TEMPLATE = """You are a surrealist film director creating a dream sequence.

Dream title: {title}
Overall mood: {mood}
Color palette: {palette}
{dreamer_context}
For the following scene, do TWO things in order:

FIRST — Write 2-3 sentences of poetic narration that a voice actor will read aloud over this scene. Write ONLY the narration words themselves. Do NOT include any labels, headings, or prefixes like "Narration:" — just the raw spoken text. The tone should be dreamy and ethereal.

SECOND — Generate an image of this scene {art_style_instruction}. The image should be dreamlike, with unusual perspectives and evocative atmosphere.{dreamer_visual_note}

Scene: {description}
Entities: {entities}
Emotion: {emotion}"""


def _build_dreamer_context(profile: DreamerProfile) -> tuple[str, str]:
    """Build prompt fragments from the dreamer profile."""
    parts = []
    visual_parts = []

    if profile.gender and profile.gender != "unspecified":
        parts.append(f"gender: {profile.gender}")
    if profile.age_range and profile.age_range != "unspecified":
        parts.append(f"age: {profile.age_range}")
    if profile.ethnicity and profile.ethnicity != "unspecified":
        parts.append(f"ethnicity: {profile.ethnicity}")

    if not parts:
        return "", ""

    context = f"Dreamer profile: {', '.join(parts)}\n"
    visual_note = (
        f" When the dreamer appears as a character in the scene, depict them as a "
        f"{' '.join(parts)} person."
    )
    return context, visual_note


async def generate_scene_visuals(
    dream: DreamSchema,
    scene: SceneSchema,
    scene_index: int,
    art_style: str = "anime",
    dreamer_profile: DreamerProfile | None = None,
) -> tuple[str, bytes]:
    """Generate narration text and image for a single scene using interleaved output."""
    client = get_client()

    art_instruction = ART_STYLE_INSTRUCTIONS.get(
        art_style, ART_STYLE_INSTRUCTIONS["anime"]
    )

    dreamer_context = ""
    dreamer_visual_note = ""
    if dreamer_profile:
        dreamer_context, dreamer_visual_note = _build_dreamer_context(dreamer_profile)

    prompt = SCENE_PROMPT_TEMPLATE.format(
        title=dream.title,
        mood=dream.overall_mood,
        palette=", ".join(dream.color_palette),
        description=scene.description,
        entities=", ".join(scene.entities),
        emotion=scene.emotion,
        art_style_instruction=art_instruction,
        dreamer_context=dreamer_context,
        dreamer_visual_note=dreamer_visual_note,
    )

    response = client.models.generate_content(
        model=INTERLEAVED_MODEL,
        contents=prompt,
        config=types.GenerateContentConfig(
            response_modalities=["TEXT", "IMAGE"],
            temperature=0.9,
        ),
    )

    narration_text = ""
    image_bytes = b""

    for part in response.candidates[0].content.parts:
        if part.text:
            narration_text += part.text
        elif part.inline_data:
            image_bytes = part.inline_data.data

    if not narration_text:
        narration_text = f"In this dream, {scene.description.lower()}"

    narration_text = _clean_narration(narration_text.strip())
    return narration_text, image_bytes


async def generate_all_visuals(
    dream: DreamSchema,
    art_style: str = "anime",
    dreamer_profile: DreamerProfile | None = None,
    progress_callback=None,
) -> list[tuple[str, bytes]]:
    """Generate visuals for all scenes in the dream."""
    results = []

    for i, scene in enumerate(dream.scenes):
        narration, image_data = await generate_scene_visuals(
            dream, scene, i, art_style, dreamer_profile
        )
        results.append((narration, image_data))

        if progress_callback:
            await progress_callback(
                event="scene_image_generated",
                data={
                    "scene_index": i,
                    "total_scenes": len(dream.scenes),
                    "narration": narration,
                    "has_image": len(image_data) > 0,
                },
            )

    return results


def _clean_narration(text: str) -> str:
    """Strip labels, headings, and markdown from narration text."""
    text = re.sub(
        r"^[\s*#]*(?:Scene\s*\d+\s*)?(?:Narration|Voiceover|Narrator)\s*:?\s*[\s*]*",
        "", text, flags=re.IGNORECASE,
    )
    text = re.sub(r"\*{1,}", "", text)
    text = re.sub(r"^#+\s*", "", text, flags=re.MULTILINE)
    return text.strip()


def image_bytes_to_base64(image_bytes: bytes) -> str:
    """Convert raw image bytes to a base64 data URI."""
    return f"data:image/png;base64,{base64.b64encode(image_bytes).decode()}"


def image_bytes_to_pil(image_bytes: bytes) -> Image.Image:
    """Convert raw image bytes to a PIL Image."""
    return Image.open(BytesIO(image_bytes))
