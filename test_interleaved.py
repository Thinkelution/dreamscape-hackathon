"""
Test: Verify Gemini interleaved output (text + image) works with your API key.
Run: pip install google-genai Pillow && python test_interleaved.py
"""
import os
from google import genai
from google.genai import types
from PIL import Image
from io import BytesIO

API_KEY = os.environ.get("GOOGLE_API_KEY", "")
if not API_KEY:
    raise RuntimeError("Set GOOGLE_API_KEY environment variable first")
client = genai.Client(api_key=API_KEY)

print("Testing interleaved output (text + image in one response)...")
print("-" * 60)

MODELS_TO_TRY = [
    "gemini-2.0-flash-exp-image-generation",
    "gemini-2.0-flash",
]

response = None
used_model = None

for model_name in MODELS_TO_TRY:
    print(f"Trying model: {model_name}")
    try:
        response = client.models.generate_content(
            model=model_name,
            contents="Describe a surreal dreamscape scene where a giant clock melts "
                     "over a floating island, then generate an image of this scene.",
            config=types.GenerateContentConfig(
                response_modalities=["TEXT", "IMAGE"],
                temperature=0.9,
            ),
        )
        used_model = model_name
        print(f"  -> Success with {model_name}")
        break
    except Exception as e:
        print(f"  -> Failed: {e}")
        continue

try:
    if response is None:
        raise Exception("All models failed")

    text_parts = 0
    image_parts = 0

    for part in response.candidates[0].content.parts:
        if part.text:
            text_parts += 1
            print(f"[TEXT PART {text_parts}]")
            print(part.text[:200])
            print()
        elif part.inline_data:
            image_parts += 1
            print(f"[IMAGE PART {image_parts}] mime_type: {part.inline_data.mime_type}")
            img = Image.open(BytesIO(part.inline_data.data))
            img.save(f"test_dream_scene_{image_parts}.png")
            print(f"  -> Saved as test_dream_scene_{image_parts}.png ({img.size[0]}x{img.size[1]})")

    print()
    print("-" * 60)
    print(f"RESULTS: {text_parts} text parts, {image_parts} image parts")

    if text_parts > 0 and image_parts > 0:
        print("  INTERLEAVED OUTPUT WORKS -- You are good to go!")
    elif text_parts > 0 and image_parts == 0:
        print("  TEXT ONLY -- Image generation not available on this model/key.")
        print("  Try model='gemini-2.0-flash-exp' or check Imagen access.")
    else:
        print("  UNEXPECTED -- Check the raw response above.")

except Exception as e:
    print(f"  ERROR: {e}")
    print()
    print("Troubleshooting:")
    print("  1. Is your API key valid? Test at aistudio.google.com")
    print("  2. Is 'gemini-2.0-flash-exp' available? Try 'gemini-2.0-flash'")
    print("  3. Check if interleaved output is enabled for your region")
