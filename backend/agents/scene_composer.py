"""Scene Composer Agent: Composes surrealist dream film from images + narration using FFmpeg.

Applies Ken Burns pan/zoom effects, text overlays, dissolve transitions,
and mixes narration audio into a final MP4."""

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
SCENE_DURATION = 8  # seconds per scene
FADE_DURATION = 1   # seconds for cross-dissolve


async def compose_dream_film(dream: DreamEntry) -> str | None:
    """Compose the final dream film MP4 from scene images and narration audio.

    Returns the GCS URI of the uploaded video, or a local path as fallback.
    """
    if not dream.dream_schema or not dream.dream_schema.scenes:
        return None

    scenes = dream.dream_schema.scenes
    has_images = any(s.image_url and not s.image_url.startswith("gs://") for s in scenes)

    with tempfile.TemporaryDirectory() as tmpdir:
        # Download / decode scene images
        image_paths = []
        for i, scene in enumerate(scenes):
            img_path = os.path.join(tmpdir, f"scene_{i}.png")
            if scene.image_url and scene.image_url.startswith("data:"):
                _save_base64_image(scene.image_url, img_path)
                image_paths.append(img_path)
            elif scene.image_url and scene.image_url.startswith("gs://"):
                try:
                    _download_gcs_image(scene.image_url, img_path)
                    image_paths.append(img_path)
                except Exception:
                    image_paths.append(_create_placeholder(img_path, scene.description))
            else:
                image_paths.append(_create_placeholder(img_path, scene.description))

        if not image_paths:
            return None

        # Ensure all images are the right resolution
        for path in image_paths:
            _resize_image(path, TARGET_WIDTH, TARGET_HEIGHT)

        # Build video with Ken Burns + dissolves
        video_path = os.path.join(tmpdir, "dream_film.mp4")
        _build_video_with_ffmpeg(image_paths, video_path, scenes)

        # Mix in narration audio if available
        narration_path = None
        if dream.generated_assets.narration_audio:
            audio_src = dream.generated_assets.narration_audio
            if audio_src.startswith("gs://"):
                narration_path = os.path.join(tmpdir, "narration.wav")
                try:
                    _download_gcs_file(audio_src, narration_path)
                except Exception:
                    narration_path = None
            elif os.path.exists(audio_src):
                narration_path = audio_src

        if narration_path and os.path.exists(narration_path):
            final_path = os.path.join(tmpdir, "dream_film_final.mp4")
            _mix_audio(video_path, narration_path, final_path)
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


def _build_video_with_ffmpeg(
    image_paths: list[str],
    output_path: str,
    scenes: list,
):
    """Build video from images with Ken Burns (slow zoom) and dissolve transitions."""
    n = len(image_paths)
    total_duration = n * SCENE_DURATION

    # Build a complex filter for Ken Burns zoom + crossfade between scenes
    inputs = []
    filter_parts = []

    for i, img_path in enumerate(image_paths):
        inputs.extend(["-loop", "1", "-t", str(SCENE_DURATION), "-i", img_path])

        # Ken Burns: slow zoom from 100% to 110% centered
        zoom_start = 1.0
        zoom_end = 1.1
        filter_parts.append(
            f"[{i}:v]scale={TARGET_WIDTH * 2}:{TARGET_HEIGHT * 2},"
            f"zoompan=z='min({zoom_end},pzoom+0.001)':"
            f"d={SCENE_DURATION * 25}:"
            f"x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':"
            f"s={TARGET_WIDTH}x{TARGET_HEIGHT}:fps=25,"
            f"setpts=PTS-STARTPTS,format=yuva420p[v{i}]"
        )

    # Apply crossfade transitions between consecutive scenes
    if n == 1:
        filter_complex = f"{filter_parts[0]}; [v0]format=yuv420p[outv]"
    else:
        xfade_parts = []
        prev = "v0"
        for i in range(1, n):
            out = f"xf{i}" if i < n - 1 else "outv"
            offset = i * SCENE_DURATION - FADE_DURATION * i
            xfade_parts.append(
                f"[{prev}][v{i}]xfade=transition=fade:duration={FADE_DURATION}:offset={offset}[{out}]"
            )
            prev = out

        filter_complex = "; ".join(filter_parts) + "; " + "; ".join(xfade_parts)

    cmd = [
        "ffmpeg", "-y",
        *inputs,
        "-filter_complex", filter_complex,
        "-map", "[outv]",
        "-c:v", "libx264",
        "-pix_fmt", "yuv420p",
        "-preset", "fast",
        "-crf", "23",
        "-movflags", "+faststart",
        output_path,
    ]

    subprocess.run(cmd, check=True, capture_output=True, timeout=120)


def _mix_audio(video_path: str, audio_path: str, output_path: str):
    """Mix narration audio into the video."""
    subprocess.run(
        [
            "ffmpeg", "-y",
            "-i", video_path,
            "-i", audio_path,
            "-c:v", "copy",
            "-c:a", "aac",
            "-b:a", "128k",
            "-shortest",
            output_path,
        ],
        check=True,
        capture_output=True,
        timeout=60,
    )


def _save_base64_image(data_uri: str, output_path: str):
    """Decode a base64 data URI and save as PNG."""
    import base64
    header, b64data = data_uri.split(",", 1)
    raw = base64.b64decode(b64data)
    img = Image.open(BytesIO(raw))
    img.save(output_path, "PNG")


def _create_placeholder(output_path: str, text: str) -> str:
    """Create a dark placeholder image with text for missing scenes."""
    img = Image.new("RGB", (TARGET_WIDTH, TARGET_HEIGHT), color=(20, 10, 40))
    img.save(output_path, "PNG")
    return output_path


def _resize_image(path: str, width: int, height: int):
    """Resize image to exact dimensions, cropping to fill."""
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


def _download_gcs_image(gcs_uri: str, local_path: str):
    """Download a file from GCS."""
    from google.cloud import storage
    bucket_name = gcs_uri.split("/")[2]
    blob_path = "/".join(gcs_uri.split("/")[3:])
    client = storage.Client()
    bucket = client.bucket(bucket_name)
    blob = bucket.blob(blob_path)
    blob.download_to_filename(local_path)


def _download_gcs_file(gcs_uri: str, local_path: str):
    """Download any file from GCS."""
    _download_gcs_image(gcs_uri, local_path)
