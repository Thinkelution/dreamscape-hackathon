"""Analysis API endpoints — dream journal analysis and theme reports."""

import logging

from fastapi import APIRouter

from backend.agents.dream_analyst import analyze_dream_journal
from backend.services import firestore_service

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get("/analysis")
async def get_analysis(user_id: str = "anonymous"):
    """Get the latest theme analysis for a user's dream journal."""
    try:
        dreams = await firestore_service.list_dreams(user_id, limit=50)
        if not dreams:
            return {"analysis": None, "message": "No dreams to analyze"}

        dream_dicts = [d.model_dump(mode="json") for d in dreams]
        report = await analyze_dream_journal(dream_dicts, user_id)
        return {"analysis": report.model_dump(mode="json")}
    except Exception as e:
        logger.error(f"Analysis failed: {e}")
        return {"analysis": None, "error": str(e)}


@router.post("/analysis/refresh")
async def refresh_analysis(user_id: str = "anonymous"):
    """Trigger a fresh analysis of the user's dream journal."""
    try:
        dreams = await firestore_service.list_dreams(user_id, limit=50)
        if not dreams:
            return {"message": "No dreams to analyze", "analysis": None}

        dream_dicts = [d.model_dump(mode="json") for d in dreams]
        report = await analyze_dream_journal(dream_dicts, user_id)
        return {
            "message": "Analysis complete",
            "analysis": report.model_dump(mode="json"),
        }
    except Exception as e:
        logger.error(f"Analysis refresh failed: {e}")
        return {"error": str(e)}
