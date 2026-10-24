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
  useEffect(()=> { setLangSong(activeSeed) }, [activeSeed])
  const descriptionRequest = useRef(0)
  const fetchDescriptions = async ()=>{
    const request = ++descriptionRequest.current
    if(!langSong) return
    setDescLoading(true); setDescriptionError(null)
    try{ const res = await api.postDescriptions({recording_mbid: langSong, categories: descCat? [descCat] : undefined, limit:8}); if (request === descriptionRequest.current) { setDescMatches(res.matches || []); setDescriptionNote(res.note || '') } }catch{ if(request === descriptionRequest.current) { setDescMatches([]); setDescriptionNote(''); setDescriptionError('Song description matching is unavailable. Please try again.') } } finally{ if(request === descriptionRequest.current) setDescLoading(false)}
  }
  useEffect(()=>{ setDescMatches([]); setDescriptionNote(''); setDescriptionError(null); setDescLoading(false); if(langSong) fetchDescriptions(); return ()=>{ descriptionRequest.current++ } }, [langSong, descCat])

  return (
        <div className="description-experiment" style={{marginTop:12}}>
          <section className="panel">
            <div className="eyebrow">Optional CLAP experiment</div>
            <h2>Matching descriptions</h2>
            <p className="muted" style={{fontSize:12}}>CLAP compares this song with a prepared bank of descriptions. Listen, then judge which phrases fit. A mismatch is useful.</p>
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
                  {(bootstrap?.description_categories || ['rhythm','vocals','instruments','texture','mood','atmosphere','combo','dynamics','production']).map((category: string)=><option key={category} value={category}>{category}</option>)}
                </select>
              </label>
            </div>
            {descriptionNote && <p className="help">{descriptionNote}</p>}
            {descriptionError && <div role="alert"><p>{descriptionError}</p><button className="btn-soft" onClick={fetchDescriptions}>Retry descriptions</button></div>}
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
              {langSong && descMatches.length===0 && !descLoading && !descriptionError && <p className="muted">No descriptions in this category.</p>}
            </div>

          </section>

        </div>
  )
}
