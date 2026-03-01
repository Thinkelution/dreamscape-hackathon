"""Narrative Voice Agent: Generates narration audio using Google Cloud TTS.

Supports configurable narrator gender and speaking style."""

import os
import subprocess
import tempfile
from pathlib import Path

from google.cloud import texttospeech

from backend.models.schemas import NarratorConfig
from backend.services.storage_service import upload_file

VOICE_MAP = {
    ("female", "calm"):      ("en-US-Neural2-F",  texttospeech.SsmlVoiceGender.FEMALE,  1.0,  -1.0),
    ("female", "warm"):      ("en-US-Neural2-C",  texttospeech.SsmlVoiceGender.FEMALE,  1.0,   0.0),
    ("female", "dramatic"):  ("en-US-Neural2-E",  texttospeech.SsmlVoiceGender.FEMALE,  0.95, -2.0),
    ("female", "youthful"):  ("en-US-Neural2-H",  texttospeech.SsmlVoiceGender.FEMALE,  1.05,  2.0),
    ("male", "calm"):        ("en-US-Neural2-D",  texttospeech.SsmlVoiceGender.MALE,    1.0,  -1.0),
    ("male", "warm"):        ("en-US-Neural2-A",  texttospeech.SsmlVoiceGender.MALE,    1.0,   0.0),
    ("male", "dramatic"):    ("en-US-Neural2-J",  texttospeech.SsmlVoiceGender.MALE,    0.95, -3.0),
    ("male", "youthful"):    ("en-US-Neural2-I",  texttospeech.SsmlVoiceGender.MALE,    1.05,  1.0),
}

DEFAULT_VOICE = ("en-US-Neural2-F", texttospeech.SsmlVoiceGender.FEMALE, 1.0, -1.0)


def _resolve_voice(config: NarratorConfig):
    key = (config.gender.lower(), config.style.lower())
    return VOICE_MAP.get(key, VOICE_MAP.get((config.gender.lower(), "calm"), DEFAULT_VOICE))


def _get_tts_client() -> texttospeech.TextToSpeechClient:
    return texttospeech.TextToSpeechClient()


def _synthesize_text(
    client: texttospeech.TextToSpeechClient,
    text: str,
    voice_name: str,
    ssml_gender: texttospeech.SsmlVoiceGender,
    speaking_rate: float,
    pitch: float,
) -> bytes:
    """Synthesize a single text segment to WAV audio bytes."""
    voice_config = texttospeech.VoiceSelectionParams(
        language_code="en-US",
        name=voice_name,
        ssml_gender=ssml_gender,
    )
    audio_config = texttospeech.AudioConfig(
        audio_encoding=texttospeech.AudioEncoding.LINEAR16,
        speaking_rate=speaking_rate,
        pitch=pitch,
        effects_profile_id=["large-home-entertainment-class-device"],
    )
    synthesis_input = texttospeech.SynthesisInput(text=text)
    response = client.synthesize_speech(
        input=synthesis_input, voice=voice_config, audio_config=audio_config,
    )
    return response.audio_content


async def generate_narration(
    dream_id: str,
    narration_texts: list[str],
    narrator_config: NarratorConfig | None = None,
) -> str | None:
    """Generate narration audio for all scenes, concatenated into a single WAV."""
    if not narration_texts:
        return None

    config = narrator_config or NarratorConfig()
    voice_name, ssml_gender, rate, pitch = _resolve_voice(config)

    client = _get_tts_client()

    with tempfile.TemporaryDirectory() as tmpdir:
        segment_paths = []

        for i, text in enumerate(narration_texts):
            if not text.strip():
                continue

            audio_bytes = _synthesize_text(client, text, voice_name, ssml_gender, rate, pitch)
            segment_path = os.path.join(tmpdir, f"segment_{i}.wav")
            with open(segment_path, "wb") as f:
                f.write(audio_bytes)
            segment_paths.append(segment_path)

        if not segment_paths:
            return None

        if len(segment_paths) == 1:
            output_path = segment_paths[0]
        else:
            output_path = os.path.join(tmpdir, "narration.wav")
            _concatenate_wav_files(segment_paths, output_path)

        try:
            gcs_path = f"dreams/{dream_id}/narration.wav"
            uri = upload_file(output_path, gcs_path, "audio/wav")
            return uri
        except Exception:
            fallback = os.path.join(tempfile.gettempdir(), f"{dream_id}_narration.wav")
            Path(output_path).rename(fallback)
            return fallback


def _concatenate_wav_files(input_paths: list[str], output_path: str):
    """Concatenate WAV files using ffmpeg."""
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
