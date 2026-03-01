"""Firestore service for dream entry CRUD operations."""

import os
from datetime import datetime
from typing import Optional

from google.cloud import firestore

from backend.models.schemas import DreamEntry, DreamStatus

_db: Optional[firestore.AsyncClient] = None

COLLECTION = "dreams"


def get_db() -> firestore.AsyncClient:
    global _db
    if _db is None:
        project = os.environ.get("GCP_PROJECT_ID", "dreamscape-hackathon")
        _db = firestore.AsyncClient(project=project)
    return _db


async def save_dream(dream: DreamEntry) -> DreamEntry:
    db = get_db()
    doc_ref = db.collection(COLLECTION).document(dream.id)
    await doc_ref.set(dream.model_dump(mode="json"))
    return dream


async def get_dream(dream_id: str) -> Optional[DreamEntry]:
    db = get_db()
    doc = await db.collection(COLLECTION).document(dream_id).get()
    if doc.exists:
        return DreamEntry(**doc.to_dict())
    return None


async def update_dream_status(dream_id: str, status: DreamStatus, **extra_fields):
    db = get_db()
    update_data = {"status": status.value}
    update_data.update(extra_fields)
    await db.collection(COLLECTION).document(dream_id).update(update_data)


async def update_dream(dream_id: str, data: dict):
    db = get_db()
    await db.collection(COLLECTION).document(dream_id).update(data)


async def list_dreams(user_id: str = "anonymous", limit: int = 20) -> list[DreamEntry]:
    db = get_db()
    query = (
        db.collection(COLLECTION)
        .where("user_id", "==", user_id)
        .order_by("created_at", direction=firestore.Query.DESCENDING)
        .limit(limit)
    )
    docs = []
    async for doc in query.stream():
        docs.append(DreamEntry(**doc.to_dict()))
    return docs


async def delete_dream(dream_id: str):
    db = get_db()
    await db.collection(COLLECTION).document(dream_id).delete()
