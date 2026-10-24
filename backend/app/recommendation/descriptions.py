"""Corpus-standardized description scores for the listening/discussion activity."""
import numpy as np

METHOD = "description-standardized-v1"
MIN_STD = 1e-8


def build_reference(audio_vectors, text_vectors):
    """Population statistics over the entire frozen catalogue, never a UI filter."""
    similarities = np.asarray(audio_vectors, dtype=np.float64) @ np.asarray(text_vectors, dtype=np.float64).T
    if similarities.ndim != 2 or not np.isfinite(similarities).all():
        raise ValueError("Invalid description reference similarities")
    means, stds = similarities.mean(axis=0), similarities.std(axis=0, ddof=0)
    if not np.any(stds > MIN_STD):
        raise ValueError("No descriptions vary across the catalogue")
    return means, stds


def standardized_scores(similarities, means, stds):
    """Zero-variance candidates have no discriminating evidence and are excluded."""
    similarities, means, stds = (np.asarray(v, dtype=np.float64) for v in (similarities, means, stds))
    if similarities.shape != means.shape or means.shape != stds.shape:
        raise ValueError("Description reference dimensions do not match")
    if not all(np.isfinite(v).all() for v in (similarities, means, stds)):
        raise ValueError("Non-finite description scores")
    return np.divide(similarities - means, stds,
                     out=np.full_like(similarities, -np.inf), where=stds > MIN_STD)
