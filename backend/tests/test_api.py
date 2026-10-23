from fastapi.testclient import TestClient
from backend.app.main import app

def get_client():
    return TestClient(app)

def test_bootstrap():
    with TestClient(app) as c:
        r=c.get('/api/bootstrap')
        assert r.status_code==200
        j=r.json()
        assert 'dataset_id' in j
        assert 'score_help' in j
        assert 'W' not in j.get('score_help','') or 'chance you will like' in j['score_help']

def test_songs_validation():
    with TestClient(app) as c:
        r=c.get('/api/songs?year_min=2020&year_max=2010')
        assert r.status_code==422
        r=c.get('/api/songs?offset=0&limit=5')
        assert r.status_code==200
        assert 'total' in r.json()
        # check public fields only, no embeddings
        item=r.json()['items'][0]
        assert 'recording_mbid' in item
        assert 'clap_embeddings' not in str(item)
        assert 'embedding_index' not in item
        # diacritic tolerant search: Björk vs Bjork
        r=c.get('/api/songs?q=Bjork&limit=5')
        assert r.status_code==200
        # should find Björk entries
        if r.json()['total']>0:
            assert any('Bj' in x['artist'] for x in r.json()['items'])

def test_recommendation_validation():
    with TestClient(app) as c:
        r=c.get('/api/songs?limit=1')
        sid=r.json()['items'][0]['recording_mbid']
        # duplicate seeds
        r=c.post('/api/recommendations', json={'seed_ids':[sid,sid], 'method':'clap-v1'})
        assert r.status_code==422
        # empty
        r=c.post('/api/recommendations', json={'seed_ids':[], 'method':'clap-v1'})
        assert r.status_code==422
        # unknown id
        r=c.post('/api/recommendations', json={'seed_ids':['00000000-0000-0000-0000-000000000000'], 'method':'clap-v1'})
        assert r.status_code==404
        # invalid method
        r=c.post('/api/recommendations', json={'seed_ids':[sid], 'method':'invalid'})
        assert r.status_code==422
        # limit bounds
        r=c.post('/api/recommendations', json={'seed_ids':[sid], 'method':'clap-v1', 'limit': 100})
        assert r.status_code==422

def test_private_data_isolation():
    with TestClient(app) as c:
        r=c.get('/api/songs?limit=1')
        item=r.json()['items'][0]
        assert 'lowlevel' not in str(item).lower()
        assert 'mfcc' not in str(item).lower()
        # try to fetch embedding file via static
        r=c.get('/data/workshop/clap_embeddings.f32')
        assert r.status_code==404
        r=c.get('/api/bootstrap')
        assert 'clap_embeddings' not in r.text

def test_deterministic():
    with TestClient(app) as c:
        r=c.get('/api/songs?limit=2')
        sids=[x['recording_mbid'] for x in r.json()['items']]
        r1=c.post('/api/recommendations', json={'seed_ids':[sids[0]], 'method':'rhythm-v1', 'limit':5})
        r2=c.post('/api/recommendations', json={'seed_ids':[sids[0]], 'method':'rhythm-v1', 'limit':5})
        assert r1.json()['results'] == r2.json()['results']
        # seed order permuted
        r3=c.post('/api/recommendations', json={'seed_ids':[sids[1], sids[0]], 'method':'clap-v1', 'limit':5})
        r4=c.post('/api/recommendations', json={'seed_ids':[sids[0], sids[1]], 'method':'clap-v1', 'limit':5})
        assert r3.json()['results'] == r4.json()['results']
        assert r3.json()['run_id'] == r4.json()['run_id']

def test_explanations_recompute():
    with TestClient(app) as c:
        r=c.get('/api/songs?limit=1')
        sid=r.json()['items'][0]['recording_mbid']
        rec=c.post('/api/recommendations', json={'seed_ids':[sid], 'method':'clap-v1', 'limit':1})
        res_id=rec.json()['results'][0]['recording_mbid']
        e1=c.post('/api/explanations', json={'seed_ids':[sid], 'method':'clap-v1', 'result_id':res_id})
        assert e1.status_code==200
        # forged client scores have no effect – we don't accept scores, so just ensure recomputed base_score matches earlier
        base = rec.json()['results'][0]['base_score']
        exp_base = e1.json()['base_score']
        assert abs(base - exp_base) < 1e-6

def test_text_search_bounds():
    with TestClient(app) as c:
        r=c.post('/api/text-search', json={'query':'', 'limit':5})
        assert r.status_code==422
        r=c.post('/api/text-search', json={'query':'a'*501, 'limit':5})
        assert r.status_code==422

def test_health():
    with TestClient(app) as c:
        assert c.get('/health/live').status_code==200
        r=c.get('/health/ready')
        assert r.status_code in [200,503]
        if r.status_code==200:
            assert r.json()['status']=='ready'
