from __future__ import annotations

import uuid
from datetime import datetime
from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field


class DreamStatus(str, Enum):
    PENDING = "pending"
    INTERPRETING = "interpreting"
    GENERATING_VISUALS = "generating_visuals"
    GENERATING_NARRATION = "generating_narration"
    COMPOSING_VIDEO = "composing_video"
    ANALYZING = "analyzing"
    COMPLETE = "complete"
    FAILED = "failed"


class DreamerProfile(BaseModel):
    gender: str = "unspecified"
    age_range: str = "adult"
    ethnicity: str = "unspecified"


class NarratorConfig(BaseModel):
    gender: str = "female"
    style: str = "calm"


class SymbolSchema(BaseModel):
    name: str
    possible_meaning: str
    frequency: int = 1


class SceneSchema(BaseModel):
    description: str
    entities: list[str] = []
    emotion: str = ""
    visual_style: str = ""
    transition_to: str = "dissolve"
    narration_text: Optional[str] = None
    image_url: Optional[str] = None


class DreamSchema(BaseModel):
    title: str
    scenes: list[SceneSchema]
    overall_mood: str
    symbols: list[SymbolSchema] = []
    narrative_arc: str = ""
    color_palette: list[str] = []


class GeneratedAssets(BaseModel):
    scene_images: list[str] = []
    narration_audio: Optional[str] = None
    ambient_audio: Optional[str] = None
    final_video: Optional[str] = None


class DreamerInsight(BaseModel):
    trait: str
    description: str


class DreamAnalysis(BaseModel):
    emotions: list[str] = []
    symbols: list[str] = []
    title: str = ""
    mood: str = ""
    dreamer_insights: list[DreamerInsight] = []
    attitude_summary: str = ""


class DreamEntry(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str = "anonymous"
    raw_text: str
    art_style: str = "anime"
    dreamer_profile: DreamerProfile = Field(default_factory=DreamerProfile)
    narrator_config: NarratorConfig = Field(default_factory=NarratorConfig)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    dream_schema: Optional[DreamSchema] = None
    generated_assets: GeneratedAssets = Field(default_factory=GeneratedAssets)
    analysis: Optional[DreamAnalysis] = None
    status: DreamStatus = DreamStatus.PENDING


class DreamCreateRequest(BaseModel):
    text: str
    user_id: str = "anonymous"
    art_style: str = "anime"
    dreamer_profile: DreamerProfile = Field(default_factory=DreamerProfile)
    narrator_config: NarratorConfig = Field(default_factory=NarratorConfig)


class RecurringSymbol(BaseModel):
    symbol: str
    count: int
    dream_ids: list[str] = []
    interpretation: str = ""


class EmotionalPattern(BaseModel):
    pattern: str
    frequency: str = ""
    correlation: str = ""


class DreamConnection(BaseModel):
    dream_id_1: str
    dream_id_2: str
    shared_elements: list[str] = []
    insight: str = ""


class ThemeReport(BaseModel):
    user_id: str = "anonymous"
    analyzed_at: datetime = Field(default_factory=datetime.utcnow)
    total_dreams: int = 0
    recurring_symbols: list[RecurringSymbol] = []
    emotional_patterns: list[EmotionalPattern] = []
    connections: list[DreamConnection] = []
