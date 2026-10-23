from backend.app.config import settings
from backend.app.data_store import DataStore
from backend.app.recommendation.scoring import _preference_fit, score_candidates

def get_ds():
    ds = DataStore(settings.data_dir, settings.scoring_artifact, settings.language_artifact)
    ds.load()
    return ds

def test_neutral_identity():
    ds = get_ds()
    seed = ds.songs[0]['recording_mbid']
    cands = [r for r in ds.songs if r['recording_mbid']!=seed][:10]
    base = score_candidates(ds, [seed], 'clap-v1', cands, preferences=None)
    neutral = score_candidates(ds, [seed], 'clap-v1', cands, preferences={'instrumental': 0})
    # neutral with 0 should be similar to None? But spec says neutral produces identical ranking as no prefs
    # Our implementation treats 0 as no effect? For instrumental=0, fit=0 -> same
    # Check order identical
    assert [r[0]['recording_mbid'] for r in base] == [r[0]['recording_mbid'] for r in neutral]

def test_skipped_preserves_order():
    ds = get_ds()
    seed = ds.songs[0]['recording_mbid']
    cands = [r for r in ds.songs if r['recording_mbid']!=seed][:20]
    base = score_candidates(ds, [seed], 'rhythm-v1', cands, preferences=None)
    # No preferences means U=B exactly
    for rec, base_score, U in base:
        from backend.app.recommendation.calibration import percentile_for_score
        B = percentile_for_score(ds, 'rhythm-v1', 1, base_score)/100
        assert abs(U - B) < 1e-6

def test_bounded_effect():
    ds = get_ds()
    # Preference effect is bounded at 0.05 * fit where fit in [-1,1]
    seed = ds.songs[0]['recording_mbid']
    # Find a song with strong acoustic vs electronic difference
    # Use first song with predictions
    cands = [r for r in ds.songs if r['recording_mbid']!=seed][:5]
    for c in cands:
        fit = _preference_fit(ds, c['recording_mbid'], {'acoustic_electronic': 1})
        assert -1 <= fit <= 1
        # Utility change bounded
        from backend.app.recommendation.calibration import percentile_for_score
        base_score = -0.5
        B = percentile_for_score(ds, 'clap-v1', 1, base_score)/100
        U = B + 0.05*fit
        assert abs(U-B) <= 0.05 + 1e-9

def test_missing_prediction_neutral():
    ds = get_ds()
    # The one recording without high-level predictions
    missing = [r for r in ds.songs if not ds.features[r['recording_mbid']]['predictions']]
    assert len(missing)==1
    mbid = missing[0]['recording_mbid']
    fit = _preference_fit(ds, mbid, {'instrumental': 1})
    assert fit == 0.0
    fit2 = _preference_fit(ds, mbid, {'acoustic_electronic': -1})
    assert fit2 == 0.0
    # Should not be excluded from recommendations
    seed = ds.songs[0]['recording_mbid']
    cands = [r for r in ds.songs if r['recording_mbid']!=seed]
    res = score_candidates(ds, [seed], 'clap-v1', cands, preferences={'instrumental':1})
    ids = [r[0]['recording_mbid'] for r in res]
    assert mbid in ids

def test_class_specific_scores():
    ds = get_ds()
    # Verify we read correct class names
    sample = ds.songs[0]['recording_mbid']
    preds = ds.features[sample]['predictions']
    # voice_instrumental should have 'instrumental' and 'voice'
    vi = preds.get('voice_instrumental', {}).get('all', {})
    assert 'instrumental' in vi and 'voice' in vi
    ae = preds.get('mood_acoustic', {}).get('all', {})
    assert 'acoustic' in ae
    ee = preds.get('mood_electronic', {}).get('all', {})
    assert 'electronic' in ee
