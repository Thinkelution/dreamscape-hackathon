"""Visual Director Agent: Generates narration text + surrealist scene images via
Gemini's interleaved output (text + image in a single response stream).

This is the CORE hackathon requirement — demonstrating native interleaved output."""

import base64
from io import BytesIO

from google.genai import types
from PIL import Image

from backend.models.schemas import DreamSchema, SceneSchema
from backend.services.gemini_service import INTERLEAVED_MODEL, get_client

SCENE_PROMPT_TEMPLATE = """You are a surrealist film director creating a dream sequence.

Dream title: {title}
Overall mood: {mood}
Color palette: {palette}

For the following scene, do TWO things:
1. Write a short, poetic narration (2-3 sentences) that a narrator would read over this scene in a dreamy, ethereal voice. The narration should evoke the emotion and atmosphere.
2. Generate a surrealist image of this scene. The image should be dreamlike, with soft focus, unusual perspectives, and the specified visual style.

Scene: {description}
Entities: {entities}
Emotion: {emotion}
Visual Style: {visual_style}

Write the narration first, then generate the image."""


async def generate_scene_visuals(
    dream: DreamSchema, scene: SceneSchema, scene_index: int
) -> tuple[str, bytes]:
    """Generate narration text and image for a single scene using interleaved output.

    Returns (narration_text, image_bytes).
    """
    client = get_client()

    prompt = SCENE_PROMPT_TEMPLATE.format(
        title=dream.title,
        mood=dream.overall_mood,
        palette=", ".join(dream.color_palette),
        description=scene.description,
        entities=", ".join(scene.entities),
        emotion=scene.emotion,
        visual_style=scene.visual_style,
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

    return narration_text.strip(), image_bytes


async def generate_all_visuals(
    dream: DreamSchema,
    progress_callback=None,
) -> list[tuple[str, bytes]]:
    """Generate visuals for all scenes in the dream.

    Returns list of (narration_text, image_bytes) tuples.
    """
    results = []

    for i, scene in enumerate(dream.scenes):
        narration, image_data = await generate_scene_visuals(dream, scene, i)
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


def image_bytes_to_base64(image_bytes: bytes) -> str:
    """Convert raw image bytes to a base64 data URI."""
    return f"data:image/png;base64,{base64.b64encode(image_bytes).decode()}"


def image_bytes_to_pil(image_bytes: bytes) -> Image.Image:
    """Convert raw image bytes to a PIL Image."""
    return Image.open(BytesIO(image_bytes))
