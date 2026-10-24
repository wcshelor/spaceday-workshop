import { useState, useEffect, useRef, Dispatch, SetStateAction } from 'react'
import * as api from '../api/client'
import { AppState } from '../state/storage'

export default function LanguageLab({appState, setAppState, bootstrap, songs, songCache, activeSeed}: {
  appState: AppState; setAppState: Dispatch<SetStateAction<AppState>>; bootstrap: any;
  songs: any[]; songCache: Record<string, any>; activeSeed: string | null;
}) {
  const [langSong, setLangSong] = useState<string | null>(activeSeed)
  const [descCat, setDescCat] = useState('')
  const [descMatches, setDescMatches] = useState<any[]>([])
  const [descriptionNote, setDescriptionNote] = useState('')
  const [descLoading, setDescLoading] = useState(false)
  const [descriptionError, setDescriptionError] = useState<string | null>(null)
  const [textQuery, setTextQuery] = useState('')
  const [textResults, setTextResults] = useState<any[]>([])
  const [textError, setTextError] = useState<string | null>(null)
  const [examples, setExamples] = useState<any[]>([])
  useEffect(()=> { api.getExamples().then(e=>setExamples(e.items || [])).catch(()=>{}) }, [])
  useEffect(()=> { setLangSong(activeSeed) }, [activeSeed])
  const descriptionRequest = useRef(0)
  const fetchDescriptions = async ()=>{
    const request = ++descriptionRequest.current
    if(!langSong) return
    setDescLoading(true); setDescriptionError(null)
    try{ const res = await api.postDescriptions({recording_mbid: langSong, categories: descCat? [descCat] : undefined, limit:8}); if (request === descriptionRequest.current) { setDescMatches(res.matches || []); setDescriptionNote(res.note || '') } }catch{ if(request === descriptionRequest.current) { setDescMatches([]); setDescriptionError('Descriptions could not load. Please try again.') } } finally{ if(request === descriptionRequest.current) setDescLoading(false)}
  }
  useEffect(()=>{ setDescMatches([]); setDescriptionNote(''); if(langSong) fetchDescriptions(); return ()=>{ descriptionRequest.current++ } }, [langSong, descCat])

  const doTextSearch = async (q?:string)=>{
    const query = q ?? textQuery
    if(!query.trim()) { setTextError('Enter a description first'); return}
    if(query.trim().length>500){ setTextError('Query too long — keep under 500 characters'); return}
    setTextError(null); setTextResults([])
    try{
      const res = await api.postTextSearch({query: query.trim(), limit:5})
      setTextResults(res.results || [])
      setAppState(s=>({...s, textHistory: [...s.textHistory, {query, results: res.results, at: new Date().toISOString()}].slice(-20)}))

    }catch(e:any){
      if(e.message.includes('unavailable') || e.message.includes('disabled') || e.message.includes('503')){
        setTextError('Live search isn’t available here. You can still explore the prepared description bank above.')
      } else setTextError(e.message)
    }
  }

  return (
        <div className="main-grid" style={{marginTop:12}}>
          <section className="panel">
            <div className="eyebrow">Optional CLAP experiment</div>
            <h2>Matching descriptions</h2>
            <p className="muted" style={{fontSize:12}}>From a prepared bank — not a unique decoding. A mismatch is useful.</p>
            <div style={{display:'grid', gap:8, marginTop:8}}>
              <label className="field"><span className="muted" style={{fontSize:12}}>Song</span>
                <select className="select" aria-label="Choose song for descriptions" value={langSong||''} onChange={e=>setLangSong(e.target.value)}>
                  <option value="">— Select a song —</option>
                  {appState.myList.map(id=> { const s=songCache[id]; return <option key={id} value={id}>{s ? `${s.title} — ${s.artist}` : id}</option> })}
                  {songs.filter(s=>!appState.myList.includes(s.recording_mbid)).slice(0,30).map(s=> <option key={s.recording_mbid} value={s.recording_mbid}>{s.title} — {s.artist}</option>)}
                </select>
              </label>
              <label className="field"><span className="muted" style={{fontSize:12}}>Category</span>
                <select className="select" aria-label="Filter descriptions by category" value={descCat} onChange={e=>setDescCat(e.target.value)}>
                  <option value="">All categories</option>
                  <option value="rhythm">rhythm</option><option value="vocals">vocals</option><option value="instruments">instruments</option><option value="texture">texture</option><option value="mood">mood</option><option value="atmosphere">atmosphere</option><option value="combo">combo</option>
                </select>
              </label>
            </div>
            {descriptionNote && <p className="help">{descriptionNote}</p>}
            {descriptionError && <p role="alert">{descriptionError}</p>}
            {descLoading && <p className="muted">Loading…</p>}
            <div style={{marginTop:10, display:'grid', gap:8}}>
              {descMatches.map(m=>{ const judgmentKey=`${langSong}:${m.id}`; const j=appState.descriptionJudgments[judgmentKey]; return (
                <div key={m.id} className="result-card" style={{padding:10}}>
                  <div style={{display:'flex', justifyContent:'space-between', gap:8, alignItems:'flex-start'}}>
                    <span className="no-overflow" style={{fontSize:13, flex:1}}>{m.text}</span>
                    <span style={{fontSize:11, border:'1px solid var(--border)', padding:'2px 6px', borderRadius:999, color:'var(--muted)', flexShrink:0}}>{m.category}</span>
                  </div>
                  <div style={{display:'flex', gap:6, marginTop:8, flexWrap:'wrap'}}>
                    {(['fits','partly','misses'] as const).map(v=>(
                      <button key={v} className="btn-ghost" aria-pressed={j?.fit===v} style={{minHeight:44, padding:'0 10px', fontSize:12, background: j?.fit===v ? 'var(--accent)' : 'var(--surface-2)', color: j?.fit===v ? '#0c1220' : 'var(--text)', borderColor: j?.fit===v ? 'var(--accent)' : 'var(--border)'}} onClick={()=> setAppState(s=>({...s, descriptionJudgments:{...s.descriptionJudgments, [judgmentKey]:{fit:v, reason: s.descriptionJudgments[judgmentKey]?.reason}}}))}>{v}</button>
                    ))}
                    <input className="input" aria-label={`Reason for ${m.id}`} placeholder="why?" value={j?.reason||''} onChange={e=> setAppState(s=>({...s, descriptionJudgments:{...s.descriptionJudgments, [judgmentKey]:{fit: j?.fit || 'fits', reason:e.target.value}}}))} style={{flex:'1 1 140px', minHeight:44}} />
                  </div>
                </div>
              )})}
              {langSong && descMatches.length===0 && !descLoading && <p className="muted">No descriptions in this category.</p>}
            </div>

            <h3 style={{marginTop:18}}>Describe what you like</h3>
            <p className="muted" style={{fontSize:12}}>Then change one aspect (e.g., intimate → distant) and compare.</p>
            <div className="search-row" style={{marginTop:8}}>
              <input className="input" aria-label="Your description" value={textQuery} onChange={e=>setTextQuery(e.target.value)} placeholder="e.g., warm acoustic guitar with soft vocals" />
              <button className="btn-primary" onClick={()=>doTextSearch()} aria-label="Search with your description">Search</button>
            </div>
            {textError && <p role="alert" style={{color:'#ff6b6b', fontSize:12, marginTop:6}}>{textError}</p>}
            {bootstrap?.language_status==='disabled' && <p className="help">Live text search is unavailable here. The prepared description bank above is a separate experiment.</p>}
            {bootstrap?.language_status==='prepared' && <p className="help">Prepared descriptions are available; live text retrieval is unavailable.</p>}
            <div style={{marginTop:10, display:'grid', gap:8}}>
              {textResults.map(r=>(
                <div key={r.recording_mbid} className="result-card" style={{padding:10}}>
                  <div style={{display:'flex', justifyContent:'space-between', gap:8}}><b className="no-overflow">{r.title} — {r.artist}</b><span className="score">{r.match_percentile}%</span></div>
                  <div className="listen-links"><a className="primary-link" href={r.youtube_search_url} target="_blank" rel="noopener noreferrer">YouTube search ↗</a><a href={r.spotify_search_url} target="_blank" rel="noopener noreferrer">Spotify search ↗</a></div>
                </div>
              ))}
            </div>
            <div style={{marginTop:12}}>
              <h4 style={{margin:'0 0 6px', fontSize:13}}>Query history</h4>
              {appState.textHistory.length===0 ? <p className="muted" style={{fontSize:12}}>No queries yet.</p> : appState.textHistory.slice(-5).reverse().map((h,i)=>(
                <div key={i} className="panel" style={{padding:8, background:'var(--bg)', display:'flex', gap:8, alignItems:'center', justifyContent:'space-between'}}>
                  <span className="no-overflow" style={{fontSize:12}}><b>{h.query}</b> <span className="muted">{new Date(h.at).toLocaleTimeString()}</span></span>
                  <button className="btn-ghost" style={{minHeight:44, padding:'0 10px', fontSize:11}} onClick={()=>{setTextQuery(h.query); doTextSearch(h.query)}}>Reuse</button>
                </div>
              ))}
            </div>
          </section>

          <aside className="panel">
            <div className="eyebrow">Example prompts</div>
            <h3>Ideas for describing sound</h3>
            <p className="muted" style={{fontSize:12}}>These are example phrases, not precomputed recommendations. Searching requires live text retrieval.</p>
            {examples.map(ex=>(
              <div key={ex.id} className="result-card" style={{padding:10, background:'var(--bg)', marginTop:8}}>
                <div className="muted" style={{fontSize:11}}>{ex.category}</div>
                <div style={{fontSize:13, fontWeight:700}}>{ex.query}</div>
                <button className="btn-soft" style={{marginTop:8, width:'100%'}} onClick={()=>{setTextQuery(ex.query); doTextSearch(ex.query)}}>Use this prompt</button>
              </div>
            ))}
            {!examples.length && <p className="muted" style={{fontSize:12}}>No examples.</p>}
            <p className="inline-help" style={{marginTop:10}}>Capability: {bootstrap?.language_status || 'unknown'} · {bootstrap?.prompt_version || 'prompts-v1'}</p>
          </aside>
        </div>
  )
}
