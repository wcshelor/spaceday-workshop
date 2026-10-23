import { useEffect, useState, useRef, useMemo } from 'react'
import * as api from '../api/client'
import { loadState, debouncedSave, exportJSON, exportMarkdown, AppState, RunSnapshot, WorkshopStage } from '../state/storage'

function describeCandidatePool(filter: any) {
  if (!filter) return 'full collection'
  const parts = [filter?.collaborative_only ? 'shared listener-model catalogue' : null, filter?.style_family, filter?.year_min && `from ${filter.year_min}`, filter?.year_max && `through ${filter.year_max}`].filter(Boolean)
  return parts.length ? parts.join(' · ') : 'full collection'
}

const STAGES: {id: WorkshopStage, label: string, sub: string}[] = [
  {id:'choose', label:'Choose', sub:'Pick one you know'},
  {id:'listen', label:'Listen', sub:'Generate & listen'},
  {id:'reflect', label:'Reflect', sub:'Reveal & react'},
  {id:'compare', label:'Compare', sub:'Methods & runs'},
  {id:'describe', label:'Describe', sub:'Words → music'},
  {id:'notes', label:'Notes', sub:'Export & save'},
]

export default function App() {
  const [bootstrap, setBootstrap] = useState<any>(null)
  const [health, setHealth] = useState('checking')
  const [appState, setAppState] = useState<AppState>(()=>loadState())
  const [songs, setSongs] = useState<any[]>([])
  const [total, setTotal] = useState(0)
  const [loadingSongs, setLoadingSongs] = useState(false)
  const [songError, setSongError] = useState<string| null>(null)
  const [selectedMethod, setSelectedMethod] = useState<'rhythm-v1'|'texture-v1'|'clap-v1'|'collaborative-v1'>('clap-v1')
  const [sharedPool, setSharedPool] = useState(false)
  const [candidateStyle, setCandidateStyle] = useState('')
  const [candidateYearMin, setCandidateYearMin] = useState('')
  const [candidateYearMax, setCandidateYearMax] = useState('')
  const [recError, setRecError] = useState<string|null>(null)
  const [recLoading, setRecLoading] = useState(false)
  const [explanations, setExplanations] = useState<Record<string, any>>({})
  const [compareIds, setCompareIds] = useState<string[]>([])
  const [langSong, setLangSong] = useState<string | null>(null)
  const [descCat, setDescCat] = useState<string>('')
  const [descMatches, setDescMatches] = useState<any[]>([])
  const [descLoading, setDescLoading] = useState(false)
  const [textQuery, setTextQuery] = useState('')
  const [textResults, setTextResults] = useState<any[]>([])
  const [textError, setTextError] = useState<string|null>(null)
  const [examples, setExamples] = useState<any[]>([])
  const requestIdRef = useRef(0)
  const [songCache, setSongCache] = useState<Record<string,any>>({})

  const activeStage: WorkshopStage = appState.activeStage || 'choose'
  const setStage = (s: WorkshopStage) => setAppState(prev => ({...prev, activeStage: s}))

  // bootstrap and health
  useEffect(()=>{
    fetch('/health/live').then(r=>r.json()).then(j=>setHealth(j.status)).catch(()=>setHealth('offline'))
    api.getBootstrap().then(b=>{
      setBootstrap(b)
      setAppState(s=>({...s, dataset_id: b.dataset_id}))
      if (b.supported_methods?.includes('collaborative-v1')) {
        // keep selectedMethod as is, no auto switch
      }
    }).catch(()=>{})
    api.getExamples().then(e=> setExamples(e.items || [])).catch(()=>{})
  }, [])

  // persist
  useEffect(()=>{ debouncedSave(appState) }, [appState])

  // song cache
  useEffect(()=>{ setSongCache(prev=>({...prev, ...Object.fromEntries(songs.map(s=>[s.recording_mbid,s]))})) }, [songs])
  useEffect(()=>{
    if (!appState.myList.length) return
    let cancelled=false
    api.searchSongs({ids: appState.myList.join(','), limit: 5} as any).then(res=>{
      if (!cancelled) setSongCache(prev=>({...prev, ...Object.fromEntries(res.items.map((s:any)=>[s.recording_mbid,s]))}))
    }).catch(()=>{})
    return ()=>{cancelled=true}
  }, [appState.myList])

  const myListResolved = useMemo(()=> appState.myList.map(id=> songCache[id] || {recording_mbid:id, title: id.slice(0,8), artist: 'loading', year: null}), [appState.myList, songCache])

  // fetch songs
  const fetchSongs = async (offset=0)=>{
    setLoadingSongs(true); setSongError(null)
    const reqId = ++requestIdRef.current
    try {
      const params: any = {offset, limit: 30}
      if (selectedMethod === 'collaborative-v1') params.collaborative_only = 'true'
      if (appState.browseFilters.q) params.q = appState.browseFilters.q
      if (appState.browseFilters.style) params.style = appState.browseFilters.style
      if (appState.browseFilters.year_min) params.year_min = appState.browseFilters.year_min
      if (appState.browseFilters.year_max) params.year_max = appState.browseFilters.year_max
      if (appState.browseFilters.year_min && appState.browseFilters.year_max && Number(appState.browseFilters.year_min) > Number(appState.browseFilters.year_max)) {
        setSongError('Invalid year range — check min and max')
        setLoadingSongs(false); return
      }
      const res = await api.searchSongs(params)
      if (reqId !== requestIdRef.current) return
      setSongs(res.items); setTotal(res.total)
    } catch(e:any){ setSongError(e.message) } finally { setLoadingSongs(false) }
  }
  useEffect(()=>{ fetchSongs(0) }, [appState.browseFilters, selectedMethod])

  const addToList = (mbid:string)=>{
    if (appState.myList.includes(mbid)) return
    if (appState.myList.length>=5) { setRecError('My List holds up to 5 songs — remove one first'); return}
    setAppState(s=>({...s, myList: [...s.myList, mbid]}))
    setRecError(null)
  }
  const removeFromList = (mbid:string)=> setAppState(s=>({...s, myList: s.myList.filter(id=>id!==mbid)}))

  const latestRun = useMemo(()=>{
    if (appState.activeRunId) return appState.runs.find(r=>r.run_id===appState.activeRunId) || appState.runs[appState.runs.length-1] || null
    return appState.runs[appState.runs.length-1] || null
  }, [appState.runs, appState.activeRunId])
  const activeResultIndex = Math.min(appState.activeResultIndex || 0, Math.max(0, (latestRun?.results?.length || 1)-1))
  const setActiveResult = (idx:number) => setAppState(s=>({...s, activeResultIndex: idx}))
  const setActiveRun = (id:string) => setAppState(s=>({...s, activeRunId: id, activeResultIndex: 0}))

  const generate = async ()=>{
    if (appState.myList.length===0) { setRecError('Choose at least one song first — start with one you know'); return}
    if (selectedMethod === 'collaborative-v1' && bootstrap?.collaborative?.supported_ids && appState.myList.some(id=>!bootstrap.collaborative.supported_ids.includes(id))) {
      setRecError('Remove songs marked “No listener model” — collaborative needs supported songs only.'); return
    }
    setRecLoading(true); setRecError(null)
    const pref:any={}; let hasPref=false
    if (appState.preferencesDraft.instrumental==='instrumental') { pref.instrumental=1; hasPref=true}
    else if (appState.preferencesDraft.instrumental==='vocal') { pref.instrumental=-1; hasPref=true}
    if (appState.preferencesDraft.acoustic_electronic==='acoustic') { pref.acoustic_electronic=-1; hasPref=true}
    else if (appState.preferencesDraft.acoustic_electronic==='electronic') { pref.acoustic_electronic=1; hasPref=true}
    const body:any={seed_ids: appState.myList, method: selectedMethod, limit:5}
    if (candidateStyle || candidateYearMin || candidateYearMax || sharedPool || selectedMethod==='collaborative-v1') {
      body.candidate_filter={}
      if(candidateStyle) body.candidate_filter.style_family=candidateStyle
      if(candidateYearMin) body.candidate_filter.year_min=Number(candidateYearMin)
      if(candidateYearMax) body.candidate_filter.year_max=Number(candidateYearMax)
      if(sharedPool || selectedMethod==='collaborative-v1') body.candidate_filter.collaborative_only=true
      if(candidateYearMin && candidateYearMax && Number(candidateYearMin)>Number(candidateYearMax)){ setRecError('Invalid candidate year range'); setRecLoading(false); return}
      if(Object.keys(body.candidate_filter).length===0) delete body.candidate_filter
    }
    if(hasPref) body.preferences=pref
    try{
      const res = await api.postRecommendations(body)
      const snapshot: RunSnapshot = {
        run_id: res.run_id, method: res.method, seeds: res.seed_ids_canonical, candidate_filter: res.candidate_filter, preferences: res.preferences_applied,
        results: res.results, created_at: new Date().toISOString(), reactions: {}, notes: '', dataset_id: res.dataset_id,
        scoring_version: res.scoring_version, calibration_version: res.calibration_version,
      }
      let newRuns = [...appState.runs, snapshot]
      if(newRuns.length>20){ // alert but not blocking
        newRuns=newRuns.slice(-20)
      }
      setAppState(s=>({...s, runs: newRuns, activeRunId: snapshot.run_id, activeResultIndex: 0, activeStage: 'listen'}))
      // ensure listen stage visible
    }catch(e:any){ setRecError(e.message)} finally{ setRecLoading(false)}
  }

  const reveal = async (runId:string, resultId:string)=>{
    const run = appState.runs.find(r=>r.run_id===runId); if(!run) return
    setAppState(s=>({...s, runs: s.runs.map(r=> r.run_id===runId ? {...r, reactions: {...r.reactions, [resultId]: {...(r.reactions[resultId]||{}), revealed:true}}} : r)}))
    try{ const exp = await api.postExplanations({seed_ids: run.seeds, method: run.method, result_id: resultId, candidate_filter: run.candidate_filter, preferences: run.preferences}); setExplanations(e=>({...e, [resultId]: exp})) }catch{}
  }
  const updateReaction = (runId:string, mbid:string, field:string, value:string)=>{
    setAppState(s=>({...s, runs: s.runs.map(r=> r.run_id===runId ? {...r, reactions: {...r.reactions, [mbid]: {...(r.reactions[mbid]||{revealed:false}), [field]: value}}} : r)}))
  }

  const fetchDescriptions = async ()=>{
    if(!langSong) return
    setDescLoading(true)
    try{ const res = await api.postDescriptions({recording_mbid: langSong, categories: descCat? [descCat] : undefined, limit:8}); setDescMatches(res.matches || []) }catch{ setDescMatches([])} finally{ setDescLoading(false)}
  }
  useEffect(()=>{ if(langSong) fetchDescriptions() }, [langSong, descCat])

  const doTextSearch = async (q?:string)=>{
    const query = q ?? textQuery
    if(!query.trim()) { setTextError('Enter a description first'); return}
    if(query.trim().length>500){ setTextError('Query too long — keep under 500 characters'); return}
    setTextError(null)
    try{
      const res = await api.postTextSearch({query: query.trim(), limit:5})
      setTextResults(res.results || [])
      setAppState(s=>({...s, textHistory: [...s.textHistory, {query, results: res.results, at: new Date().toISOString()}].slice(-20)}))
      setAppState(s=>({...s, activeStage: 'describe'}))
    }catch(e:any){
      if(e.message.includes('unavailable') || e.message.includes('disabled') || e.message.includes('503')){
        setTextError('Live search isn’t available — showing prepared examples below')
      } else setTextError(e.message)
    }
  }

  const handleNewSession = ()=>{
    if(confirm('Start a new session? This clears local reflections. Consider exporting first.')){
      localStorage.removeItem('spaceday-workshop:v1')
      const fresh = {...loadState(), dataset_id: bootstrap?.dataset_id||null, myList:[], runs:[], textHistory:[], descriptionJudgments:{}, notes:'', activeStage: 'choose' as WorkshopStage, activeRunId: null, activeResultIndex: 0}
      // use direct save to avoid debounce race
      localStorage.setItem('spaceday-workshop:v1', JSON.stringify(fresh))
      setAppState(fresh)
    }
  }

  const compareRuns = compareIds.map(id=> appState.runs.find(r=>r.run_id===id)).filter(Boolean) as RunSnapshot[]

  // keyboard handler for carousel
  const onCarouselKey = (e: React.KeyboardEvent)=>{
    if(!latestRun) return
    if(e.key==='ArrowLeft') { e.preventDefault(); setActiveResult(Math.max(0, activeResultIndex-1)) }
    if(e.key==='ArrowRight') { e.preventDefault(); setActiveResult(Math.min(latestRun.results.length-1, activeResultIndex+1)) }
  }

  return (
    <div className="app-shell">
      <header className="app-header">
        <div className="brand">
          <h1>Music Recommendation Workshop</h1>
          <p>Choose a familiar song → listen → reflect. Your work stays on this device.</p>
        </div>
        <div className="header-actions">
          <span className="health-badge" aria-live="polite">health: {health} · {bootstrap?.dataset_id ? bootstrap.dataset_id.slice(0,6) : '…'}</span>
          <button className="btn-ghost" onClick={handleNewSession}>Start new session</button>
          <button className="btn-ghost" onClick={()=>{const j=exportJSON(appState); const blob=new Blob([j],{type:'application/json'}); const url=URL.createObjectURL(blob); const a=document.createElement('a'); a.href=url; a.download='workshop-export.json'; a.click(); URL.revokeObjectURL(url)}}>Export JSON</button>
          <button className="btn-ghost" onClick={()=>{const md=exportMarkdown(appState); const blob=new Blob([md],{type:'text/markdown'}); const url=URL.createObjectURL(blob); const a=document.createElement('a'); a.href=url; a.download='workshop-export.md'; a.click(); URL.revokeObjectURL(url)}}>Export Markdown</button>
        </div>
      </header>

      <nav className="stage-nav" aria-label="Workshop stages">
        <div className="stage-list" role="tablist">
          {STAGES.map(s=>(
            <button key={s.id} role="tab" aria-selected={activeStage===s.id} aria-current={activeStage===s.id ? 'step' : undefined} className="stage-btn" onClick={()=>setStage(s.id)}>
              <span className="stage-num" aria-hidden>{STAGES.indexOf(s)+1}</span>
              <span className="stage-label">{s.label}</span>
              <span className="stage-sub">{s.sub}</span>
            </button>
          ))}
        </div>
      </nav>

      {/* CHOOSE */}
      {activeStage==='choose' && (
        <div className="main-grid" style={{marginTop:12}}>
          <section className="panel" aria-labelledby="choose-heading">
            <div className="eyebrow">Step 1 · Choose</div>
            <h2 id="choose-heading">Search for a familiar song</h2>
            <p className="muted">Start with one you know. You can add up to 5. Filters are secondary — they only change browsing.</p>
            <div className="search-row" style={{marginTop:8}}>
              <input className="input" aria-label="Search title or artist" placeholder="Search title or artist (e.g., ABBA)" value={appState.browseFilters.q} onChange={e=> setAppState(s=>({...s, browseFilters:{...s.browseFilters, q:e.target.value}}))} />
              <button className="btn-soft" style={{minWidth:84}} onClick={()=>fetchSongs(0)}>Search</button>
            </div>
            <div className="filters" style={{marginTop:10}}>
              <label className="field"><span className="muted" style={{fontSize:12}}>Style (browsing only)</span>
                <select className="select" aria-label="Filter by style" value={appState.browseFilters.style} onChange={e=> setAppState(s=>({...s, browseFilters:{...s.browseFilters, style:e.target.value}}))}>
                  <option value="">All styles</option>
                  {bootstrap?.filter_vocab?.style_families?.map((s:string)=> <option key={s} value={s}>{s}</option>)}
                </select>
              </label>
              <label className="field"><span className="muted" style={{fontSize:12}}>Year min</span><input className="input" aria-label="Year min" placeholder="1960" type="number" inputMode="numeric" value={appState.browseFilters.year_min} onChange={e=> setAppState(s=>({...s, browseFilters:{...s.browseFilters, year_min:e.target.value}}))} /></label>
              <label className="field"><span className="muted" style={{fontSize:12}}>Year max</span><input className="input" aria-label="Year max" placeholder="2022" type="number" inputMode="numeric" value={appState.browseFilters.year_max} onChange={e=> setAppState(s=>({...s, browseFilters:{...s.browseFilters, year_max:e.target.value}}))} /></label>
              <button className="btn-ghost" onClick={()=>setAppState(s=>({...s, browseFilters:{q:'',style:'',year_min:'',year_max:''}}))} style={{alignSelf:'end'}}>Clear</button>
            </div>
            {selectedMethod==='collaborative-v1' && <p role="status" className="help">Showing the {bootstrap?.collaborative?.supported_count || 0} songs with enough listener feedback. This model learns shared tastes, not audio.</p>}
            {songError && <p role="alert" style={{color:'#ff6b6b', fontSize:13, margin:'8px 0 0'}}>{songError}</p>}
            <div className="catalogue-list" style={{marginTop:12, maxHeight: 380, overflowY:'auto'}}>
              {loadingSongs && <p style={{padding:12}} className="muted">Loading…</p>}
              {!loadingSongs && songs.map(s=>(
                <div key={s.recording_mbid} className="catalogue-item">
                  <div className="meta">
                    <div className="title no-overflow">{s.title} <span className="artist">— {s.artist}</span></div>
                    <div className="sub">{s.year || '—'} · {s.primary_style_family || '—'} {s.is_editorial_anchor ? '· Familiar starting point' : ''}</div>
                  </div>
                  <button aria-label={`Add ${s.title} by ${s.artist} to My List`} disabled={appState.myList.includes(s.recording_mbid)} onClick={()=>addToList(s.recording_mbid)} className="add-btn">Add</button>
                </div>
              ))}
              {!loadingSongs && songs.length===0 && <p style={{padding:12}} className="muted">No matches — try a different search or clear filters.</p>}
            </div>
            <p className="muted" style={{fontSize:12, marginTop:6}}>Showing {songs.length} of {total}</p>
          </section>

          <div className="stack">
            <section className="panel" aria-labelledby="mylist-heading">
              <div className="eyebrow">Your selection</div>
              <h2 id="mylist-heading">My List · {appState.myList.length}/5</h2>
              <p className="muted" style={{fontSize:12}}>Your picks stay even when filters change. Remove is easy.</p>
              {myListResolved.length===0 ? <p className="muted">No songs yet — add one above.</p> : (
                <div className="chip-list" style={{marginTop:8}}>
                  {myListResolved.map(r=>(
                    <span key={r.recording_mbid} className="chip">
                      <span>{r.title} — {r.artist}{selectedMethod==='collaborative-v1' && bootstrap?.collaborative?.supported_ids && !bootstrap.collaborative.supported_ids.includes(r.recording_mbid) && <em style={{marginLeft:6, color:'#ffb86b', fontStyle:'normal', fontSize:11}}>No listener model</em>}</span>
                      <button aria-label={`Remove ${r.title}`} onClick={()=>removeFromList(r.recording_mbid)}>×</button>
                    </span>
                  ))}
                </div>
              )}
              <div style={{display:'flex', gap:8, marginTop:12}}>
                <button className="btn-soft" onClick={()=>setStage('listen')} disabled={appState.myList.length===0} style={{flex:1}}>Continue → Listen</button>
              </div>
            </section>

            <section className="panel">
              <h3>How this works</h3>
              <p className="muted" style={{fontSize:13}}>You’ll pick a method, generate 5, then focus on one at a time. Keep genre/year and evidence hidden until you’ve listened.</p>
              <p className="help">Match score = how strong the computed similarity is vs reference comparisons — not the chance you’ll like it.</p>
            </section>
          </div>
        </div>
      )}

      {/* LISTEN */}
      {activeStage==='listen' && (
        <div className="main-grid" style={{marginTop:12}}>
          <section className="panel" aria-labelledby="listen-heading">
            <div className="eyebrow">Step 2 · Listen</div>
            <h2 id="listen-heading">Choose a method and generate</h2>
            <p className="muted">One clear action: Generate. Keep the same seeds when you want a fair comparison.</p>

            <div className="field" style={{marginTop:10}}>
              <label className="muted" style={{fontSize:12}}>Recommendation method</label>
              <select className="select" aria-label="Recommendation method" value={selectedMethod} onChange={e=>{setSelectedMethod(e.target.value as any); if(e.target.value==='collaborative-v1') setSharedPool(true)}}>
                <option value="clap-v1">Audio–language embeddings (CLAP)</option>
                <option value="rhythm-v1">Rhythm and movement</option>
                <option value="texture-v1">Sound and texture</option>
                {bootstrap?.supported_methods?.includes('collaborative-v1') && <option value="collaborative-v1">Listener patterns (small AI model)</option>}
              </select>
              <details style={{marginTop:8}}>
                <summary>What each method listens to</summary>
                <div className="muted" style={{fontSize:12}}>
                  <p><b>Rhythm:</b> tempo/onset/danceability — rhythm/activity similarity.</p>
                  <p><b>Texture:</b> timbre (MFCC) + spectral — production/texture similarity.</p>
                  <p><b>CLAP:</b> audio embedding proximity.</p>
                  <p><b>Listener patterns:</b> shared tastes learned from real loves — 32 factors, no audio (182 supported songs).</p>
                </div>
              </details>
            </div>

            <details style={{marginTop:10}}>
              <summary>Restrict recommendations (optional)</summary>
              <div>
                <p className="muted" style={{fontSize:12}}>Default is full collection (minus your seeds). Use this only when you mean to.</p>
                {bootstrap?.collaborative && <label className="field-row" style={{marginBottom:8}}><input type="checkbox" checked={sharedPool || selectedMethod==='collaborative-v1'} disabled={selectedMethod==='collaborative-v1'} onChange={e=>setSharedPool(e.target.checked)} /> <span style={{fontSize:13}}>Use shared supported pool for fair comparison ({bootstrap.collaborative.supported_count} songs)</span></label>}
                <div style={{display:'grid', gridTemplateColumns:'1fr 1fr 1fr', gap:8}}>
                  <label className="field"><span className="muted" style={{fontSize:12}}>Style</span>
                    <select className="select" aria-label="Restrict by style" value={candidateStyle} onChange={e=>setCandidateStyle(e.target.value)}>
                      <option value="">All styles</option>
                      {bootstrap?.filter_vocab?.style_families?.map((s:string)=> <option key={s} value={s}>{s}</option>)}
                    </select>
                  </label>
                  <label className="field"><span className="muted" style={{fontSize:12}}>From year</span><input className="input" placeholder="1960" type="number" inputMode="numeric" value={candidateYearMin} onChange={e=>setCandidateYearMin(e.target.value)} /></label>
                  <label className="field"><span className="muted" style={{fontSize:12}}>Through year</span><input className="input" placeholder="2022" type="number" inputMode="numeric" value={candidateYearMax} onChange={e=>setCandidateYearMax(e.target.value)} /></label>
                </div>
                {(candidateStyle||candidateYearMin||candidateYearMax) && <p className="help">Active pool: {describeCandidatePool({style_family: candidateStyle, year_min: candidateYearMin, year_max: candidateYearMax})}</p>}
              </div>
            </details>

            <details style={{marginTop:10}}>
              <summary>Taste nudge (optional, skippable)</summary>
              <div style={{display:'grid', gap:10}}>
                <label className="field"><span className="muted" style={{fontSize:12}}>Instrumental vs vocal</span>
                  <select className="select" value={appState.preferencesDraft.instrumental || ''} onChange={e=> setAppState(s=>({...s, preferencesDraft:{...s.preferencesDraft, instrumental:e.target.value||null}}))}>
                    <option value="">No nudge</option><option value="instrumental">Prefer instrumental</option><option value="vocal">Prefer vocal</option>
                  </select>
                </label>
                <label className="field"><span className="muted" style={{fontSize:12}}>Acoustic vs electronic</span>
                  <select className="select" value={appState.preferencesDraft.acoustic_electronic || ''} onChange={e=> setAppState(s=>({...s, preferencesDraft:{...s.preferencesDraft, acoustic_electronic:e.target.value||null}}))}>
                    <option value="">No nudge</option><option value="acoustic">Prefer acoustic</option><option value="electronic">Prefer electronic</option>
                  </select>
                </label>
                <p className="inline-help">Skipped = exact base order. Nudge reranks by a small bounded amount.</p>
              </div>
            </details>

            {recError && <p role="alert" style={{color:'#ff6b6b', fontSize:13, marginTop:10}}>{recError}</p>}
            {bootstrap && <p className="help">Dataset {bootstrap.dataset_id?.slice(0,8)} · {bootstrap.scoring_version} · Calibration {bootstrap.calibration_version}</p>}
          </section>

          <section className="panel" aria-labelledby="results-heading">
            <div className="eyebrow">Your results</div>
            <h2 id="results-heading">{latestRun ? `Results — ${latestRun.method==='collaborative-v1' ? 'Listener patterns' : latestRun.method}` : 'Results will appear here'}</h2>
            {!latestRun ? (
              <p className="muted">Add a song on Choose, then Generate. Your seeds stay when you change methods — that keeps comparisons fair.</p>
            ) : (
              <div className="carousel" onKeyDown={onCarouselKey} tabIndex={0} aria-label="Recommendations carousel" aria-roledescription="carousel">
                <div className="indicator">
                  <span className="muted" style={{fontSize:12}}>{latestRun.seeds.map(id=> (songCache[id]?.title || id.slice(0,6))).join(', ')} · {describeCandidatePool(latestRun.candidate_filter)}</span>
                  <span className="muted" style={{fontSize:12}}>{activeResultIndex+1} / {latestRun.results.length}</span>
                </div>
                <div className="dots" aria-hidden>
                  {latestRun.results.map((_:any,i:number)=> <span key={i} className="dot" aria-current={i===activeResultIndex ? 'true' : 'false'} />)}
                </div>

                {(() => {
                  const r = latestRun.results[activeResultIndex]
                  if (!r) return null
                  const react = latestRun.reactions[r.recording_mbid] || {revealed:false}
                  const isRevealed = !!react.revealed
                  return (
                    <div className="result-card">
                      <div className="topline">
                        <div className="song-title no-overflow">{r.title} <span style={{fontWeight:400, color:'var(--muted)'}}>— {r.artist} {r.year ? `· ${r.year}` : ''}</span></div>
                        <span className="score" aria-label={`Match score ${r.match_percentile} percent`}>{r.match_percentile}%</span>
                      </div>
                      <p className="help" style={{margin:'8px 0 0'}}>How strong the computed similarity is vs reference comparisons — not the chance you’ll like it.</p>
                      {!isRevealed ? (
                        <p className="muted" style={{fontSize:12, marginTop:6}}>You’ll see genre/year and evidence only after you’ve listened.</p>
                      ) : (
                        <p className="muted" style={{fontSize:12, marginTop:6}}>Revealed. External links are searches, not verified exact recordings.</p>
                      )}
                      <div className="listen-links">
                        <a className="primary-link" href={r.youtube_search_url} target="_blank" rel="noopener noreferrer">YouTube search ↗</a>
                        <a href={r.spotify_search_url} target="_blank" rel="noopener noreferrer">Spotify search ↗</a>
                      </div>
                      <div className="reveal-bar">
                        {!isRevealed ? (
                          <button className="btn-primary" style={{flex:1}} onClick={()=>reveal(latestRun.run_id, r.recording_mbid)}>I’ve listened</button>
                        ) : (
                          <span className="muted" style={{fontSize:12, color:'var(--accent-2)'}}>✓ Marked as listened — self-report, not proof</span>
                        )}
                      </div>
                      {!isRevealed && (
                        <fieldset style={{marginTop:12, border:'1px solid var(--border)', borderRadius:12, padding:12}}>
                          <legend style={{fontSize:12, padding:'0 6px'}}>Before reveal — optional</legend>
                          <div style={{display:'grid', gap:10}}>
                            <label className="field"><span className="muted" style={{fontSize:12}}>Enjoyment</span>
                              <select className="select" aria-label={`Enjoyment for ${r.title}`} value={react.like||''} onChange={e=>updateReaction(latestRun.run_id, r.recording_mbid,'like',e.target.value)}>
                                <option value="">—</option><option value="like">Like</option><option value="unsure">Unsure</option><option value="dislike">Dislike</option>
                              </select>
                            </label>
                            <label className="field"><span className="muted" style={{fontSize:12}}>Connection</span>
                              <select className="select" aria-label={`Connection for ${r.title}`} value={react.connection||''} onChange={e=>updateReaction(latestRun.run_id, r.recording_mbid,'connection',e.target.value)}>
                                <option value="">—</option><option value="clear">Clear</option><option value="partly">Partly</option><option value="not">Not clear</option>
                              </select>
                            </label>
                          </div>
                        </fieldset>
                      )}
                      {isRevealed && (
                        <div style={{marginTop:10, display:'grid', gap:10}}>
                          <label className="field"><span className="muted" style={{fontSize:12}}>Note — what stayed similar?</span>
                            <input className="input" aria-label={`Note for ${r.title}`} value={react.note||''} onChange={e=>updateReaction(latestRun.run_id, r.recording_mbid,'note',e.target.value)} placeholder="Rhythm, voice, instruments, mood, production…" />
                          </label>
                          {explanations[r.recording_mbid] ? (
                            <details open>
                              <summary>Evidence (readable, expand technical)</summary>
                              <div style={{fontSize:13, lineHeight:1.5}}>
                                {latestRun.method==='collaborative-v1' ? (
                                  <>
                                    <p>This model learned shared tastes from real listeners’ loves. Result: {explanations[r.recording_mbid].detail.result_positive_listeners} listeners. No audio was used — an artist or audience may drive the link.</p>
                                    <details><summary>Technical</summary><pre>{JSON.stringify(explanations[r.recording_mbid].detail,null,2)}</pre></details>
                                  </>
                                ) : (
                                  <>
                                    <p>Base score {explanations[r.recording_mbid].base_score?.toFixed(3)} · Per-seed similarities shown below. Similarity is arithmetic — not proof it caused enjoyment.</p>
                                    <pre>{JSON.stringify(explanations[r.recording_mbid],null,2)}</pre>
                                  </>
                                )}
                              </div>
                            </details>
                          ) : <p className="muted" style={{fontSize:12}}>Loading evidence…</p>}
                        </div>
                      )}
                    </div>
                  )
                })()}

                <div style={{display:'flex', gap:8}}>
                  <button className="btn-soft" style={{flex:1}} onClick={()=>setActiveResult(Math.max(0, activeResultIndex-1))} disabled={activeResultIndex===0} aria-label="Previous recommendation">‹ Previous</button>
                  <button className="btn-soft" style={{flex:1}} onClick={()=>setActiveResult(Math.min((latestRun.results.length-1), activeResultIndex+1))} disabled={activeResultIndex===latestRun.results.length-1} aria-label="Next recommendation">Next ›</button>
                </div>
                <p className="inline-help">Tip: Use ← → keys. All 5 remain reachable — this view just focuses you on one at a time.</p>
                <label className="field"><span className="muted" style={{fontSize:12}}>Run notes</span>
                  <textarea className="textarea" aria-label="Run notes" value={latestRun.notes} onChange={e=> setAppState(s=>({...s, runs: s.runs.map(r=> r.run_id===latestRun.run_id ? {...r, notes:e.target.value}: r)}))} placeholder="What surprised you?" rows={2} />
                </label>
                <div style={{display:'flex', gap:8, flexWrap:'wrap'}}>
                  <button className="btn-ghost" onClick={()=>setStage('reflect')}>Go to Reflect →</button>
                  <button className="btn-ghost" onClick={()=>setStage('compare')}>Compare runs</button>
                </div>
              </div>
            )}
          </section>
        </div>
      )}

      {/* REFLECT */}
      {activeStage==='reflect' && (
        <div className="main-grid" style={{marginTop:12}}>
          <section className="panel">
            <div className="eyebrow">Step 3 · Reflect</div>
            <h2>Reflect on what you heard</h2>
            {!latestRun ? <p className="muted">Generate results on Listen first.</p> : (
              <div style={{display:'grid', gap:10}}>
                {latestRun.results.map(r=>{
                  const react = latestRun.reactions[r.recording_mbid] || {revealed:false}
                  return (
                    <div key={r.recording_mbid} className="result-card" style={{padding:12}}>
                      <div className="topline"><b className="no-overflow">{r.title} — {r.artist}</b><span className="score">{r.match_percentile}%</span></div>
                      <div style={{fontSize:12, marginTop:6}} className="muted">{r.year ? `${r.year} · ` : ''}{react.revealed ? 'Revealed' : 'Not yet revealed'}</div>
                      <div style={{display:'grid', gridTemplateColumns:'1fr 1fr', gap:8, marginTop:8}}>
                        <label className="field"><span className="muted" style={{fontSize:11}}>Enjoyment</span>
                          <select className="select" value={react.like||''} onChange={e=>updateReaction(latestRun.run_id, r.recording_mbid,'like',e.target.value)} aria-label={`Enjoyment ${r.title}`}>
                            <option value="">—</option><option value="like">Like</option><option value="unsure">Unsure</option><option value="dislike">Dislike</option>
                          </select>
                        </label>
                        <label className="field"><span className="muted" style={{fontSize:11}}>Connection</span>
                          <select className="select" value={react.connection||''} onChange={e=>updateReaction(latestRun.run_id, r.recording_mbid,'connection',e.target.value)} aria-label={`Connection ${r.title}`}>
                            <option value="">—</option><option value="clear">Clear</option><option value="partly">Partly</option><option value="not">Not clear</option>
                          </select>
                        </label>
                      </div>
                      {react.revealed && <p className="inline-help" style={{marginTop:6}}>✓ Self-report — not proof of listening</p>}
                    </div>
                  )
                })}
                <div style={{display:'flex', gap:8}}>
                  <button className="btn-soft" onClick={()=>setStage('listen')}>Back to Listen</button>
                  <button className="btn-ghost" onClick={()=>setStage('compare')}>Compare</button>
                </div>
              </div>
            )}
          </section>
          <section className="panel">
            <h3>Prompts</h3>
            <ul className="muted" style={{fontSize:13, paddingLeft:18, margin:0, display:'grid', gap:6}}>
              <li>What stayed similar — rhythm, voice, instruments, mood, production?</li>
              <li>Can you hear the connection even if you dislike it?</li>
              <li>Which result surprised you?</li>
            </ul>
            {latestRun && <textarea className="textarea" style={{marginTop:12}} aria-label="Overall reflection" value={latestRun.notes} onChange={e=> setAppState(s=>({...s, runs: s.runs.map(r=> r.run_id===latestRun.run_id ? {...r, notes:e.target.value}: r)}))} placeholder="Overall reflection for this run…" />}
          </section>
        </div>
      )}

      {/* COMPARE */}
      {activeStage==='compare' && (
        <div style={{marginTop:12, display:'grid', gap:12}}>
          <section className="panel">
            <div className="eyebrow">Step 4 · Compare</div>
            <h2>Preserve setup, compare methods</h2>
            <p className="muted">Changing methods keeps your seeds and previous runs. Pick two runs to compare — same seeds/filter/prefs + different method = fair.</p>
            {appState.runs.length===0 ? <p className="muted">No runs yet — generate on Listen.</p> : (
              <>
                <div className="chip-list" aria-label="Choose runs to compare">
                  {appState.runs.map(r=>(
                    <label key={r.run_id} className="chip" style={{background: compareIds.includes(r.run_id) ? 'var(--accent-soft)' : 'var(--surface-2)'}}>
                      <input type="checkbox" checked={compareIds.includes(r.run_id)} onChange={e=> setCompareIds(ids=> e.target.checked ? [...ids, r.run_id].slice(-2) : ids.filter(id=>id!==r.run_id))} aria-label={`Select run ${r.method} ${r.run_id.slice(0,6)}`} /> {r.method} · {r.run_id.slice(0,6)} · {new Date(r.created_at).toLocaleTimeString()}
                    </label>
                  ))}
                </div>
                {compareRuns.length===2 && (()=>{ const [a,b]=compareRuns; const sameSeeds=JSON.stringify(a.seeds)===JSON.stringify(b.seeds); const sameFilter=JSON.stringify(a.candidate_filter)===JSON.stringify(b.candidate_filter); const samePref=JSON.stringify(a.preferences)===JSON.stringify(b.preferences); const controlled=sameSeeds&&sameFilter&&samePref&&a.method!==b.method; return (
                  <div className="evidence" style={{marginTop:12}}>
                    <p style={{marginTop:0}}><b>Controlled:</b> {controlled ? 'Yes — same seeds/filter/prefs, different method' : 'No — inputs differ'}</p>
                    <p className="muted" style={{fontSize:12}}>Differing: {[!sameSeeds&&'seeds', a.method!==b.method&&'method', !sameFilter&&'filter', !samePref&&'preferences'].filter(Boolean).join(', ')||'none'}</p>
                    <div className="compare-grid" style={{marginTop:10}}>
                      {compareRuns.map(r=>(
                        <div key={r.run_id} className="result-card" onClick={()=>setActiveRun(r.run_id)} role="button" tabIndex={0} onKeyDown={e=> e.key==='Enter' && setActiveRun(r.run_id)} aria-label={`Make ${r.method} active`}>
                          <div style={{fontWeight:800}}>{r.method} · {r.run_id.slice(0,6)}</div>
                          <div className="muted" style={{fontSize:12}}>{r.seeds.map(id=>songCache[id]?.title||id.slice(0,6)).join(', ')}</div>
                          {r.results.slice(0,5).map(res=> <div key={res.recording_mbid} style={{display:'flex', justifyContent:'space-between', gap:8, padding:'6px 0', borderBottom:'1px solid var(--border)', fontSize:13}}><span className="no-overflow">{res.title} — {res.artist}</span><span className="score" style={{fontSize:11, padding:'3px 7px'}}>{res.match_percentile}%</span></div>)}
                          <p className="inline-help">Tap to make active and revisit on Listen →</p>
                        </div>
                      ))}
                    </div>
                  </div>
                )})()}
                {appState.runs.length>0 && (
                  <div style={{marginTop:12, display:'grid', gap:8}}>
                    {appState.runs.slice(-5).reverse().map(r=>(
                      <div key={r.run_id} className="panel" style={{padding:10, background:'var(--bg)'}}>
                        <div style={{display:'flex', justifyContent:'space-between', gap:8, alignItems:'center'}}>
                          <b>{r.method}</b><span className="muted" style={{fontSize:12}}>{new Date(r.created_at).toLocaleTimeString()}</span>
                        </div>
                        <div className="muted" style={{fontSize:12}}>{r.seeds.map(id=>songCache[id]?.title||id.slice(0,6)).join(', ')} · {describeCandidatePool(r.candidate_filter)}</div>
                        <button className="btn-ghost" style={{marginTop:8, width:'100%'}} onClick={()=>setActiveRun(r.run_id)}>Make active</button>
                      </div>
                    ))}
                  </div>
                )}
              </>
            )}
          </section>
        </div>
      )}

      {/* DESCRIBE */}
      {activeStage==='describe' && (
        <div className="main-grid" style={{marginTop:12}}>
          <section className="panel">
            <div className="eyebrow">Step 5 · Describe</div>
            <h2>Matching descriptions</h2>
            <p className="muted" style={{fontSize:12}}>From a prepared bank — not a unique decoding. A mismatch is useful.</p>
            <div style={{display:'grid', gap:8, marginTop:8}}>
              <label className="field"><span className="muted" style={{fontSize:12}}>Song</span>
                <select className="select" aria-label="Choose song for descriptions" value={langSong||''} onChange={e=>setLangSong(e.target.value)}>
                  <option value="">— Select from My List or catalogue —</option>
                  {appState.myList.map(id=> { const s=songCache[id]; return <option key={id} value={id}>{s ? `${s.title} — ${s.artist}` : id}</option> })}
                  {songs.slice(0,30).map(s=> <option key={s.recording_mbid} value={s.recording_mbid}>{s.title} — {s.artist}</option>)}
                </select>
              </label>
              <label className="field"><span className="muted" style={{fontSize:12}}>Category</span>
                <select className="select" aria-label="Filter descriptions by category" value={descCat} onChange={e=>setDescCat(e.target.value)}>
                  <option value="">All categories</option>
                  <option value="rhythm">rhythm</option><option value="vocals">vocals</option><option value="instruments">instruments</option><option value="texture">texture</option><option value="mood">mood</option><option value="atmosphere">atmosphere</option><option value="combo">combo</option>
                </select>
              </label>
            </div>
            {descLoading && <p className="muted">Loading…</p>}
            <div style={{marginTop:10, display:'grid', gap:8}}>
              {descMatches.map(m=>{ const j=appState.descriptionJudgments[m.id]; return (
                <div key={m.id} className="result-card" style={{padding:10}}>
                  <div style={{display:'flex', justifyContent:'space-between', gap:8, alignItems:'flex-start'}}>
                    <span className="no-overflow" style={{fontSize:13, flex:1}}>{m.text}</span>
                    <span style={{fontSize:11, border:'1px solid var(--border)', padding:'2px 6px', borderRadius:999, color:'var(--muted)', flexShrink:0}}>{m.category}</span>
                  </div>
                  <div style={{display:'flex', gap:6, marginTop:8, flexWrap:'wrap'}}>
                    {(['fits','partly','misses'] as const).map(v=>(
                      <button key={v} className="btn-ghost" aria-pressed={j?.fit===v} style={{minHeight:36, padding:'0 10px', fontSize:12, background: j?.fit===v ? 'var(--accent)' : 'var(--surface-2)', color: j?.fit===v ? '#0c1220' : 'var(--text)', borderColor: j?.fit===v ? 'var(--accent)' : 'var(--border)'}} onClick={()=> setAppState(s=>({...s, descriptionJudgments:{...s.descriptionJudgments, [m.id]:{fit:v, reason: s.descriptionJudgments[m.id]?.reason}}}))}>{v}</button>
                    ))}
                    <input className="input" aria-label={`Reason for ${m.id}`} placeholder="why?" value={j?.reason||''} onChange={e=> setAppState(s=>({...s, descriptionJudgments:{...s.descriptionJudgments, [m.id]:{fit: j?.fit || 'fits', reason:e.target.value}}}))} style={{flex:'1 1 140px', minHeight:36}} />
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
            {bootstrap?.language_status==='disabled' && <p className="help">Live search is disabled (see docs/MODEL_SETUP.md). Prepared examples still work.</p>}
            {bootstrap?.language_status==='prepared' && <p className="help">Prepared mode — example results shown; live retrieval pending ONNX.</p>}
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
                  <button className="btn-ghost" style={{minHeight:32, padding:'0 10px', fontSize:11}} onClick={()=>{setTextQuery(h.query); doTextSearch(h.query)}}>Reuse</button>
                </div>
              ))}
            </div>
          </section>

          <aside className="panel">
            <div className="eyebrow">Prepared examples</div>
            <h3>Try without live retrieval</h3>
            <p className="muted" style={{fontSize:12}}>If live search is down, these work. They are <b>prepared</b>, not your query’s results.</p>
            {examples.map(ex=>(
              <div key={ex.id} className="result-card" style={{padding:10, background:'var(--bg)', marginTop:8}}>
                <div className="muted" style={{fontSize:11}}>{ex.category}</div>
                <div style={{fontSize:13, fontWeight:700}}>{ex.query}</div>
                <button className="btn-soft" style={{marginTop:8, width:'100%'}} onClick={()=>{setTextQuery(ex.query); doTextSearch(ex.query)}}>Try this example</button>
              </div>
            ))}
            {!examples.length && <p className="muted" style={{fontSize:12}}>No examples.</p>}
            <p className="inline-help" style={{marginTop:10}}>Capability: {bootstrap?.language_status || 'unknown'} · {bootstrap?.prompt_version || 'prompts-v1'}</p>
          </aside>
        </div>
      )}

      {/* NOTES */}
      {activeStage==='notes' && (
        <div className="main-grid" style={{marginTop:12}}>
          <section className="panel">
            <div className="eyebrow">Step 6 · Notes</div>
            <h2>Your reflections</h2>
            <p className="muted">Saved on this device only. Copy or download for discussion.</p>
            {appState.runs.length===0 ? <p className="muted">No runs yet — your notes will appear here after you generate.</p> : appState.runs.slice(-3).reverse().map(r=>(
              <div key={r.run_id} className="result-card" style={{padding:10, background:'var(--bg)', marginTop:8}}>
                <div style={{fontWeight:800, fontSize:13}}>{r.method} · {new Date(r.created_at).toLocaleString()}</div>
                <div className="muted" style={{fontSize:12}}>{r.seeds.map(id=>songCache[id]?.title||id.slice(0,6)).join(', ')}</div>
                <textarea className="textarea" aria-label={`Notes for ${r.run_id}`} value={r.notes} onChange={e=> setAppState(s=>({...s, runs: s.runs.map(x=> x.run_id===r.run_id ? {...x, notes:e.target.value}: x)}))} placeholder="What surprised you for this run?" style={{marginTop:8}} />
                <div style={{fontSize:12, marginTop:6}} className="muted">Reactions: {Object.entries(r.reactions).filter(([,v])=>v.like||v.connection).map(([id,v])=>`${songCache[id]?.title||id.slice(0,6)} ${v.like||''} ${v.connection||''}`).join(' · ') || 'none yet'}</div>
              </div>
            ))}
            <label className="field" style={{marginTop:12}}><span className="muted" style={{fontSize:12}}>Session notes</span>
              <textarea className="textarea" aria-label="Session notes" value={appState.notes} onChange={e=> setAppState(s=>({...s, notes:e.target.value}))} placeholder="Overall takeaways…" />
            </label>
          </section>
          <section className="panel">
            <h3>Export</h3>
            <p className="muted" style={{fontSize:12}}>Exports keep the same seeds, setup, and reflections you see.</p>
            <div style={{display:'grid', gap:8, marginTop:8}}>
              <button className="btn-primary" onClick={()=>{const j=exportJSON(appState); const blob=new Blob([j],{type:'application/json'}); const url=URL.createObjectURL(blob); const a=document.createElement('a'); a.href=url; a.download='workshop-export.json'; a.click(); URL.revokeObjectURL(url)}}>Download JSON</button>
              <button className="btn-soft" onClick={()=>{const md=exportMarkdown(appState); const blob=new Blob([md],{type:'text/markdown'}); const url=URL.createObjectURL(blob); const a=document.createElement('a'); a.href=url; a.download='workshop-export.md'; a.click(); URL.revokeObjectURL(url)}}>Download Markdown</button>
            </div>
            <p className="help">On a shared device, export before “Start new session”.</p>
            <details style={{marginTop:10}}>
              <summary>What’s saved?</summary>
              <div className="muted" style={{fontSize:12}}>My List order, browse filters, candidate pool, preferences draft, runs + per-result reactions/revealed, text history, description judgments, notes, versions. Seed-order permutations keep the same fingerprint.</div>
            </details>
          </section>
        </div>
      )}

      <div className="bottom-bar" role="toolbar" aria-label="Primary actions">
        {activeStage==='choose' && <button className="btn-primary primary" disabled={appState.myList.length===0} onClick={()=>setStage('listen')}>Continue to Listen · {appState.myList.length}/5</button>}
        {activeStage==='listen' && <button className="btn-primary primary" onClick={generate} disabled={recLoading || appState.myList.length===0}>{recLoading? 'Generating…' : 'Generate 5 recommendations'}</button>}
        {activeStage==='reflect' && <><button className="btn-ghost secondary" onClick={()=>setStage('listen')}>Back to Listen</button><button className="btn-primary primary" onClick={()=>setStage('compare')}>Compare runs</button></>}
        {activeStage==='compare' && <><button className="btn-ghost secondary" onClick={()=>setStage('reflect')}>Back to Reflect</button><button className="btn-primary primary" onClick={()=>setStage('describe')}>Go to Describe</button></>}
        {activeStage==='describe' && <><button className="btn-ghost secondary" onClick={()=>setStage('compare')}>Back to Compare</button><button className="btn-primary primary" onClick={()=>setStage('notes')}>To Notes & Export</button></>}
        {activeStage==='notes' && <><button className="btn-ghost secondary" onClick={()=>setStage('describe')}>Back to Describe</button><button className="btn-primary primary" onClick={()=>window.scrollTo({top:0, behavior:'smooth'})}>Top</button></>}
      </div>

      <footer style={{marginTop:18, fontSize:11, color:'var(--muted)', borderTop:'1px solid var(--border)', paddingTop:10, paddingBottom: 8}}>
        Workshop · Dataset {bootstrap?.dataset_id?.slice(0,8)} · Scoring {bootstrap?.scoring_version} · Language {bootstrap?.language_status} · <span style={{fontSize:11}}>Match % = reference percentile, not enjoyment odds. Links are searches. “I’ve listened” is self-report.</span>
      </footer>
    </div>
  )
}
