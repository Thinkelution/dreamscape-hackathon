"""Dream API endpoints — submit dreams, track progress, retrieve results."""

import asyncio
import logging
import traceback

from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from backend.agents.dream_interpreter import interpret_dream
from backend.agents.visual_director import (
    generate_all_visuals,
    image_bytes_to_base64,
)
from backend.models.schemas import (
    DreamCreateRequest,
    DreamEntry,
    DreamStatus,
)
from backend.services import firestore_service, storage_service

logger = logging.getLogger(__name__)

router = APIRouter()

# In-memory progress tracking for WebSocket clients
_dream_progress: dict[str, list[dict]] = {}
_dream_results: dict[str, dict] = {}


@router.post("/dreams")
async def create_dream(request: DreamCreateRequest):
    """Submit a new dream for processing through the full pipeline."""
    dream = DreamEntry(raw_text=request.text, user_id=request.user_id)

    try:
        await firestore_service.save_dream(dream)
    except Exception as e:
        logger.warning(f"Firestore save failed (continuing in-memory): {e}")

    _dream_progress[dream.id] = []

    asyncio.create_task(_run_pipeline(dream))

    return {
        "dream_id": dream.id,
        "status": dream.status.value,
        "message": "Dream submitted. Connect to WebSocket or poll status for updates.",
    }


async def _run_pipeline(dream: DreamEntry):
    """Run the full dream-to-film pipeline."""
    try:
        # Phase 1: Interpret
        await _update_status(dream, DreamStatus.INTERPRETING)
        dream_schema = await interpret_dream(dream.raw_text)
        dream.dream_schema = dream_schema
        await _emit_progress(dream.id, "interpretation_complete", {
            "title": dream_schema.title,
            "scenes_count": len(dream_schema.scenes),
            "mood": dream_schema.overall_mood,
            "symbols": [s.name for s in dream_schema.symbols],
        })

        # Phase 2: Generate visuals (INTERLEAVED OUTPUT — core hackathon feature)
        await _update_status(dream, DreamStatus.GENERATING_VISUALS)
        scene_results = await generate_all_visuals(
            dream_schema,
            progress_callback=lambda event, data: _emit_progress(dream.id, event, data),
        )

        scene_images = []
        scene_narrations = []
        for i, (narration, image_bytes) in enumerate(scene_results):
            dream_schema.scenes[i].narration_text = narration

            if image_bytes:
                # Always store base64 for API response (browser-displayable)
                b64 = image_bytes_to_base64(image_bytes)
                dream_schema.scenes[i].image_url = b64
                scene_images.append(b64)

                # Also upload to GCS for persistence (non-blocking)
                try:
                    gcs_path = f"dreams/{dream.id}/scene_{i}.png"
                    storage_service.upload_bytes(image_bytes, gcs_path, "image/png")
                except Exception as e:
                    logger.warning(f"GCS upload failed for scene {i}: {e}")

            scene_narrations.append(narration)

        dream.generated_assets.scene_images = scene_images
        dream.dream_schema = dream_schema

        # Phase 3: Narration (TTS)
        await _update_status(dream, DreamStatus.GENERATING_NARRATION)
        try:
            from backend.agents.narrative_voice import generate_narration
            audio_path = await generate_narration(dream.id, scene_narrations)
            if audio_path:
                dream.generated_assets.narration_audio = audio_path
                await _emit_progress(dream.id, "narration_ready", {"audio_url": audio_path})
        except Exception as e:
            logger.warning(f"TTS generation failed (continuing without audio): {e}")

        # Phase 4: Video composition
        await _update_status(dream, DreamStatus.COMPOSING_VIDEO)
        try:
            from backend.agents.scene_composer import compose_dream_film
            video_path = await compose_dream_film(dream)
            if video_path:
                dream.generated_assets.final_video = video_path
                await _emit_progress(dream.id, "video_complete", {"video_url": video_path})
        except Exception as e:
            logger.warning(f"Video composition failed (continuing without video): {e}")

        # Convert gs:// URIs to public HTTPS URLs for browser access
        if dream.generated_assets.narration_audio:
            dream.generated_assets.narration_audio = _to_public_url(
                dream.generated_assets.narration_audio
            )
        if dream.generated_assets.final_video:
            dream.generated_assets.final_video = _to_public_url(
                dream.generated_assets.final_video
            )

        # Done
        await _update_status(dream, DreamStatus.COMPLETE)
        _dream_results[dream.id] = dream.model_dump(mode="json")

        await _emit_progress(dream.id, "pipeline_complete", {
            "dream_id": dream.id,
            "title": dream_schema.title,
        })

    except Exception as e:
        logger.error(f"Pipeline failed for dream {dream.id}: {e}\n{traceback.format_exc()}")
        await _update_status(dream, DreamStatus.FAILED)
        await _emit_progress(dream.id, "pipeline_error", {"error": str(e)})


def _to_public_url(uri: str) -> str:
    """Convert gs:// URI to a public HTTPS URL."""
    if uri.startswith("gs://"):
        return uri.replace("gs://", "https://storage.googleapis.com/", 1)
    return uri


async def _update_status(dream: DreamEntry, status: DreamStatus):
    dream.status = status
    try:
        await firestore_service.update_dream_status(dream.id, status)
    except Exception:
        pass


async def _emit_progress(dream_id: str, event: str, data: dict):
    if dream_id not in _dream_progress:
        _dream_progress[dream_id] = []
    _dream_progress[dream_id].append({"event": event, "data": data})


@router.get("/dreams")
async def list_dreams(user_id: str = "anonymous"):
    """List all dreams for a user."""
    try:
        dreams = await firestore_service.list_dreams(user_id)
        return {"dreams": [d.model_dump(mode="json") for d in dreams]}
    except Exception:
        results = [v for v in _dream_results.values() if v.get("user_id") == user_id]
        return {"dreams": results}


@router.get("/dreams/{dream_id}")
async def get_dream(dream_id: str):
    """Get a single dream with all assets."""
    if dream_id in _dream_results:
        return _dream_results[dream_id]

    try:
        dream = await firestore_service.get_dream(dream_id)
        if dream:
            return dream.model_dump(mode="json")
    except Exception:
        pass

    return {"error": "Dream not found", "dream_id": dream_id}


@router.get("/dreams/{dream_id}/status")
async def get_dream_status(dream_id: str):
    """Poll generation status and progress events."""
    progress = _dream_progress.get(dream_id, [])
    result = _dream_results.get(dream_id)

    status = "pending"
    if result:
        status = result.get("status", "complete")
    elif progress:
        last_event = progress[-1]["event"]
        if last_event == "pipeline_error":
            status = "failed"
        elif last_event == "pipeline_complete":
            status = "complete"
        else:
            status = "processing"

    return {
        "dream_id": dream_id,
        "status": status,
        "progress": progress,
    }


@router.delete("/dreams/{dream_id}")
async def delete_dream(dream_id: str):
    """Delete a dream entry and its assets."""
    try:
        await firestore_service.delete_dream(dream_id)
    except Exception:
        pass

    _dream_progress.pop(dream_id, None)
    _dream_results.pop(dream_id, None)

    return {"deleted": dream_id}


@router.websocket("/dreams/{dream_id}/stream")
async def dream_stream(websocket: WebSocket, dream_id: str):
    """WebSocket endpoint for real-time progress updates."""
    await websocket.accept()

    last_index = 0
    try:
        while True:
            progress = _dream_progress.get(dream_id, [])
            if len(progress) > last_index:
                for event in progress[last_index:]:
                    await websocket.send_json(event)
                last_index = len(progress)

                if progress[-1]["event"] in ("pipeline_complete", "pipeline_error"):
                    break

            await asyncio.sleep(0.5)
    except WebSocketDisconnect:
        pass
    finally:
        try:
            await websocket.close()
        except Exception:
            pass
