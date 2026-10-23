from __future__ import annotations

from typing import Literal, Optional
from pydantic import BaseModel, Field


class ErrorEnvelope(BaseModel):
    code: str
    message: str
    retryable: bool = False
    request_id: Optional[str] = None


class BootstrapResponse(BaseModel):
    dataset_id: str
    pipeline_version: str
    snapshot_date: str
    scoring_version: str
    calibration_version: str
    language_status: Literal["disabled", "prepared", "live", "unavailable"]
    language_encoder: Optional[str] = None
    supported_methods: list[str]
    collaborative: Optional[dict] = None
    filter_vocab: dict
    year_bounds: dict
    score_help: str
    attribution_links: dict


class SongPublic(BaseModel):
    recording_mbid: str
    title: str
    artist: str
    year: Optional[int]
    primary_style_family: Optional[str]
    style_families: list[str]
    familiarity_band: str
    is_editorial_anchor: bool
    tags: list[str]
    musicbrainz_url: str
    youtube_search_url: str
    spotify_search_url: str


class SongsResponse(BaseModel):
    total: int
    offset: int
    limit: int
    items: list[SongPublic]


class RecommendationRequest(BaseModel):
    seed_ids: list[str] = Field(..., min_length=1, max_length=5)
    method: Literal["rhythm-v1", "texture-v1", "clap-v1", "collaborative-v1"]
    limit: int = Field(default=5, ge=1, le=20)
    candidate_filter: Optional[dict] = None  # {style_family, year_min, year_max}
    preferences: Optional[dict] = None  # {instrumental, acoustic_electronic}
    scoring_version: Optional[str] = None
    dataset_id: Optional[str] = None


class RecommendationResultPublic(BaseModel):
    recording_mbid: str
    title: str
    artist: str
    year: Optional[int]
    primary_style_family: Optional[str]
    rank: int
    base_score: float
    match_percentile: float
    youtube_search_url: str
    spotify_search_url: str


class RecommendationResponse(BaseModel):
    run_id: str
    dataset_id: str
    scoring_version: str
    calibration_version: str
    method: str
    seed_ids_canonical: list[str]
    candidate_filter: Optional[dict] = None
    preferences_applied: Optional[dict] = None
    results: list[RecommendationResultPublic]


class ExplanationRequest(BaseModel):
    seed_ids: list[str]
    method: str
    result_id: str
    candidate_filter: Optional[dict] = None
    preferences: Optional[dict] = None
    scoring_version: Optional[str] = None


class TextSearchRequest(BaseModel):
    query: str = Field(..., min_length=1, max_length=500)
    limit: int = Field(default=5, ge=1, le=20)
    candidate_filter: Optional[dict] = None


class TextSearchResponse(BaseModel):
    query: str
    query_hash: str
    encoder_id: Optional[str]
    prompt_version: Optional[str]
    results: list[RecommendationResultPublic]
    calibration_note: str


class DescriptionMatchRequest(BaseModel):
    recording_mbid: str
    categories: Optional[list[str]] = None
    limit: int = Field(default=5, ge=1, le=20)


class ExampleItem(BaseModel):
    id: str
    query: str
    category: str
