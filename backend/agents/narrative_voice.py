"""Narrative Voice Agent: Generates ethereal narration audio using Google Cloud TTS."""

import os
import tempfile
from pathlib import Path

from google.cloud import texttospeech

from backend.services.storage_service import upload_file

VOICE_CONFIG = texttospeech.VoiceSelectionParams(
    language_code="en-US",
    name="en-US-Wavenet-D",
    ssml_gender=texttospeech.SsmlVoiceGender.MALE,
)

AUDIO_CONFIG = texttospeech.AudioConfig(
    audio_encoding=texttospeech.AudioEncoding.LINEAR16,
    speaking_rate=0.75,
    pitch=-2.0,
    effects_profile_id=["large-home-entertainment-class-device"],
)


def _get_tts_client() -> texttospeech.TextToSpeechClient:
    return texttospeech.TextToSpeechClient()


def _synthesize_text(client: texttospeech.TextToSpeechClient, text: str) -> bytes:
    """Synthesize a single text segment to WAV audio bytes."""
    synthesis_input = texttospeech.SynthesisInput(text=text)
    response = client.synthesize_speech(
        input=synthesis_input,
        voice=VOICE_CONFIG,
        audio_config=AUDIO_CONFIG,
    )
    return response.audio_content


async def generate_narration(
    dream_id: str,
    narration_texts: list[str],
) -> str | None:
    """Generate narration audio for all scenes, concatenated into a single WAV.

    Returns the GCS URI of the uploaded narration file, or a local path as fallback.
    """
    if not narration_texts:
        return None

    client = _get_tts_client()

    with tempfile.TemporaryDirectory() as tmpdir:
        segment_paths = []

        for i, text in enumerate(narration_texts):
            if not text.strip():
                continue

            audio_bytes = _synthesize_text(client, text)
            segment_path = os.path.join(tmpdir, f"segment_{i}.wav")
            with open(segment_path, "wb") as f:
                f.write(audio_bytes)
            segment_paths.append(segment_path)

        if not segment_paths:
            return None

        # If only one segment, use it directly
        if len(segment_paths) == 1:
            output_path = segment_paths[0]
        else:
            output_path = os.path.join(tmpdir, "narration.wav")
            _concatenate_wav_files(segment_paths, output_path)

        # Upload to GCS
        try:
            gcs_path = f"dreams/{dream_id}/narration.wav"
            uri = upload_file(output_path, gcs_path, "audio/wav")
            return uri
        except Exception:
            # Fallback: keep locally for video composition
            fallback = os.path.join(tempfile.gettempdir(), f"{dream_id}_narration.wav")
            Path(output_path).rename(fallback)
            return fallback


def _concatenate_wav_files(input_paths: list[str], output_path: str):
    """Concatenate WAV files using ffmpeg."""
    import subprocess

    list_file = output_path + ".txt"
    with open(list_file, "w") as f:
        for p in input_paths:
            f.write(f"file '{p}'\n")

    subprocess.run(
        [
            "ffmpeg", "-y",
            "-f", "concat",
            "-safe", "0",
            "-i", list_file,
            "-c", "copy",
            output_path,
        ],
        check=True,
        capture_output=True,
    )
    os.remove(list_file)
