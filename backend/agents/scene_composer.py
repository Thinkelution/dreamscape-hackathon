"""Scene Composer Agent: Composes surrealist dream film from images + narration using FFmpeg.

Uses crossfade transitions between scene images with audio mixing.
Video duration is driven by narration audio length when available."""

import base64
import json
import os
import subprocess
import tempfile
from io import BytesIO
from pathlib import Path

from PIL import Image

from backend.models.schemas import DreamEntry
from backend.services.storage_service import upload_file

TARGET_WIDTH = 1280
TARGET_HEIGHT = 720
DEFAULT_SCENE_DURATION = 8
FADE_DURATION = 1


def _get_audio_duration(audio_path: str) -> float:
    """Get audio duration in seconds using ffprobe."""
    try:
        result = subprocess.run(
            [
                "ffprobe", "-v", "quiet",
                "-print_format", "json",
                "-show_format",
                audio_path,
            ],
            capture_output=True, text=True, timeout=10,
        )
        info = json.loads(result.stdout)
        return float(info["format"]["duration"])
    except Exception:
        return 0


async def compose_dream_film(dream: DreamEntry) -> str | None:
    """Compose the final dream film MP4 from scene images and narration audio."""
    if not dream.dream_schema or not dream.dream_schema.scenes:
        return None

    scenes = dream.dream_schema.scenes

    with tempfile.TemporaryDirectory() as tmpdir:
        image_paths = []
        for i, scene in enumerate(scenes):
            img_path = os.path.join(tmpdir, f"scene_{i}.png")
            if scene.image_url and scene.image_url.startswith("data:"):
                _save_base64_image(scene.image_url, img_path)
            else:
                _create_placeholder(img_path, scene.description)
            _resize_image(img_path, TARGET_WIDTH, TARGET_HEIGHT)
            image_paths.append(img_path)

        if not image_paths:
            return None

        # Resolve narration audio to a local file
        local_audio = None
        if dream.generated_assets.narration_audio:
            audio_src = dream.generated_assets.narration_audio
            if audio_src.startswith("https://"):
                local_audio = os.path.join(tmpdir, "narration.wav")
                try:
                    _download_url(audio_src, local_audio)
                except Exception:
                    local_audio = None
            elif audio_src.startswith("gs://"):
                local_audio = os.path.join(tmpdir, "narration.wav")
                try:
                    _download_gcs_file(audio_src, local_audio)
                except Exception:
                    local_audio = None
            elif os.path.exists(audio_src):
                local_audio = audio_src

        # Calculate per-scene duration: fit to audio length if available
        scene_duration = DEFAULT_SCENE_DURATION
        if local_audio and os.path.exists(local_audio):
            audio_dur = _get_audio_duration(local_audio)
            if audio_dur > 0:
                n = len(image_paths)
                # Total video needs to be >= audio duration + a small buffer
                total_fades = (n - 1) * FADE_DURATION if n > 1 else 0
                scene_duration = max(
                    DEFAULT_SCENE_DURATION,
                    (audio_dur + total_fades + 2) / n,
                )

        video_path = os.path.join(tmpdir, "dream_film.mp4")
        _build_video(image_paths, video_path, scene_duration)

        # Mix in narration audio
        if local_audio and os.path.exists(local_audio):
            final_path = os.path.join(tmpdir, "dream_film_final.mp4")
            _mix_audio(video_path, local_audio, final_path)
            video_path = final_path

        # Upload to GCS
        try:
            gcs_path = f"dreams/{dream.id}/dream_film.mp4"
            uri = upload_file(video_path, gcs_path, "video/mp4")
            return uri
        except Exception:
            fallback = os.path.join(tempfile.gettempdir(), f"{dream.id}_dream_film.mp4")
            Path(video_path).rename(fallback)
            return fallback


def _build_video(image_paths: list[str], output_path: str, scene_duration: float):
    """Build video from images with crossfade transitions."""
    n = len(image_paths)
    dur = str(int(scene_duration))

    if n == 1:
        subprocess.run(
            [
                "ffmpeg", "-y",
                "-loop", "1", "-t", dur,
                "-i", image_paths[0],
                "-c:v", "libx264", "-pix_fmt", "yuv420p",
                "-vf", f"scale={TARGET_WIDTH}:{TARGET_HEIGHT}",
                "-preset", "ultrafast", "-crf", "28",
                "-movflags", "+faststart",
                output_path,
            ],
            check=True, capture_output=True, timeout=30,
        )
        return

    inputs = []
    for img_path in image_paths:
        inputs.extend(["-loop", "1", "-t", dur, "-i", img_path])

    # Build xfade filter chain
    if n == 2:
        offset = scene_duration - FADE_DURATION
        filter_complex = (
            f"[0:v][1:v]xfade=transition=fade:duration={FADE_DURATION}"
            f":offset={offset},format=yuv420p[outv]"
        )
    else:
        parts = []
        prev = "0:v"
        for i in range(1, n):
            offset = i * scene_duration - i * FADE_DURATION
            out_label = "outv" if i == n - 1 else f"xf{i}"
            parts.append(
                f"[{prev}][{i}:v]xfade=transition=fade"
                f":duration={FADE_DURATION}:offset={offset}[{out_label}]"
            )
            prev = out_label
        filter_complex = "; ".join(parts)

    cmd = [
        "ffmpeg", "-y",
        *inputs,
        "-filter_complex", filter_complex,
        "-map", "[outv]",
        "-c:v", "libx264", "-pix_fmt", "yuv420p",
        "-preset", "ultrafast", "-crf", "28",
        "-movflags", "+faststart",
        output_path,
    ]

    subprocess.run(cmd, check=True, capture_output=True, timeout=120)


def _mix_audio(video_path: str, audio_path: str, output_path: str):
    """Mix narration audio into the video. Audio determines final duration."""
    subprocess.run(
        [
            "ffmpeg", "-y",
            "-i", video_path, "-i", audio_path,
            "-c:v", "copy", "-c:a", "aac", "-b:a", "128k",
            output_path,
        ],
        check=True, capture_output=True, timeout=30,
    )


def _save_base64_image(data_uri: str, output_path: str):
    _, b64data = data_uri.split(",", 1)
    raw = base64.b64decode(b64data)
    img = Image.open(BytesIO(raw))
    img.save(output_path, "PNG")


def _create_placeholder(output_path: str, text: str) -> str:
    img = Image.new("RGB", (TARGET_WIDTH, TARGET_HEIGHT), color=(20, 10, 40))
    img.save(output_path, "PNG")
    return output_path


def _resize_image(path: str, width: int, height: int):
    img = Image.open(path)
    img_ratio = img.width / img.height
    target_ratio = width / height

    if img_ratio > target_ratio:
        new_height = height
        new_width = int(height * img_ratio)
    else:
        new_width = width
        new_height = int(width / img_ratio)

    img = img.resize((new_width, new_height), Image.LANCZOS)
    left = (new_width - width) // 2
    top = (new_height - height) // 2
    img = img.crop((left, top, left + width, top + height))
    img.save(path, "PNG")


def _download_gcs_file(gcs_uri: str, local_path: str):
    from google.cloud import storage
    bucket_name = gcs_uri.split("/")[2]
    blob_path = "/".join(gcs_uri.split("/")[3:])
    client = storage.Client()
    bucket = client.bucket(bucket_name)
    blob = bucket.blob(blob_path)
    blob.download_to_filename(local_path)


def _download_url(url: str, local_path: str):
    """Download a file from an HTTPS URL."""
    import urllib.request
    urllib.request.urlretrieve(url, local_path)
