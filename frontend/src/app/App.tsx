import { useEffect, useRef, useState } from 'react'
import * as api from '../api/client'
import { loadState, debouncedSave, saveState, exportJSON, exportMarkdown, RunSnapshot, WorkshopStage } from '../state/storage'
import { STAGES, METHODS, Method, methodForStage, matchesSetup } from './workshop'
import LanguageLab from './LanguageLab'

function ListenLinks({song}: {song:any}) {
  const query = encodeURIComponent(`${song.artist} ${song.title}`)
  return <div className="listen-links">
    <a className="primary-link" href={song.youtube_search_url || `https://www.youtube.com/results?search_query=${query}`} target="_blank" rel="noopener noreferrer">Listen on YouTube ↗</a>
    <a href={song.spotify_search_url || `https://open.spotify.com/search/${query}`} target="_blank" rel="noopener noreferrer">Spotify ↗</a>
  </div>
}

function Evidence({run, result, seedName}: {run:RunSnapshot; result:any; seedName:string}) {
  const [evidence, setEvidence] = useState<any>(null)
  const [error, setError] = useState(false)
  const [attempt, setAttempt] = useState(0)
  useEffect(()=> {
    let cancelled = false
    setEvidence(null); setError(false)
    api.postExplanations({seed_ids:run.seeds, method:run.method, result_id:result.recording_mbid, candidate_filter:run.candidate_filter, preferences:run.preferences})
      .then(data=>{if(!cancelled) setEvidence(data)})
      .catch(()=>{if(!cancelled) setError(true)})
    return ()=>{cancelled=true}
  }, [run.run_id, result.recording_mbid, attempt])
  const method = METHODS[run.method as Method]
  const seedValues = evidence?.detail?.seed_values?.[run.seeds[0]]
  const candidateValues = evidence?.detail?.candidate_values
  return <div className="evidence" aria-live="polite">
    <h3>Why this recommendation?</h3>
    <p>{method?.explain}</p>
    {error ? <p role="alert">The scoring evidence could not load. <button className="btn-soft" onClick={()=>setAttempt(a=>a+1)}>Retry explanation</button></p> : !evidence ? <p className="muted">Loading scoring evidence…</p> : <>
      {seedValues && candidateValues && <div className="table-scroll"><table><caption>Measured rhythm of {seedName} and this recommendation</caption><thead><tr><th>Measurement</th><th>Starting song</th><th>Recommendation</th></tr></thead><tbody>
        {Object.entries(candidateValues).map(([key,value])=><tr key={key}><th>{({'rhythm.bpm':'Tempo (BPM)', 'rhythm.onset_rate':'Onset rate', 'rhythm.danceability':'Danceability'} as Record<string,string>)[key] || key}</th><td>{Number(seedValues[key]).toFixed(2)}</td><td>{Number(value).toFixed(2)}</td></tr>)}
      </tbody></table></div>}
      {run.method === 'collaborative-v1' && typeof evidence.detail?.result_positive_listeners === 'number' && <p>This recording has {evidence.detail.result_positive_listeners} positive listener signals in the training data. This count alone does not explain the recommendation.</p>}
      <p className="help">Reference percentile: {result.match_percentile}%. This describes computed similarity relative to reference comparisons, not your chance of liking the song.</p>
      <details><summary>Inspect scoring details</summary><pre>{JSON.stringify(evidence,null,2)}</pre></details>
    </>}
    <p className="muted">What might it miss? {method?.miss}</p>
    <p><strong>Does that explanation fit what you heard?</strong> A mismatch is useful too.</p>
  </div>
}

export default function App() {
  const [state, setState] = useState(loadState)
  const [bootstrap, setBootstrap] = useState<any>(null)
  const [bootstrapError, setBootstrapError] = useState(false)
  const [songs, setSongs] = useState<any[]>([])
  const [songCache, setSongCache] = useState<Record<string,any>>({})
  const [total, setTotal] = useState(0)
  const [offset, setOffset] = useState(0)
  const [loadingSongs, setLoadingSongs] = useState(false)
  const [songError, setSongError] = useState('')
  const [supportedOnly, setSupportedOnly] = useState(true)
  const [recError, setRecError] = useState('')
  const [generating, setGenerating] = useState(false)
  const [resultIndex, setResultIndex] = useState(0)
  const [predictionDraft, setPredictionDraft] = useState<Record<string,string>>({})
  const songRequest = useRef(0)
  const sessionGeneration = useRef(0)
  const navRef = useRef<HTMLElement>(null)
  const stage = state.activeStage
  const seed = state.myList.includes(state.activeSeedId || '') ? state.activeSeedId : state.myList[0] || null
  const method = methodForStage(stage, state.featureMethod)
  const sharedPool = !!bootstrap?.supported_methods?.includes('collaborative-v1') && !!bootstrap?.collaborative?.supported_ids?.length
  const seedSupported = !!seed && !!bootstrap?.collaborative?.supported_ids?.includes(seed)
  const selectedSong = seed ? songCache[seed] : null
  const setupRuns = state.runs.filter(r=>matchesSetup(r, seed, sharedPool, bootstrap?.dataset_id || null))
  const run = method ? [...setupRuns].reverse().find(r=>r.method === method) : undefined
  const currentIndex = Math.min(resultIndex, Math.max(0,(run?.results.length || 1)-1))
  const result = run?.results[currentIndex]
  const reaction = result && run ? run.reactions[result.recording_mbid] || {revealed:false} : {revealed:false, like:'', connection:'', note:''}
  const methodInfo = method ? METHODS[method] : null
  const methodUnavailable = !!method && !!bootstrap && !bootstrap.supported_methods?.includes(method)
  const listenerBlocked = method === 'collaborative-v1' && !seedSupported
  const predictionKey = `${seed}:${method}`

  const fetchBootstrap = ()=>{
    setBootstrapError(false)
    api.getBootstrap().then(b=>{setBootstrap(b); setState(s=>({...s,dataset_id:b.dataset_id}))}).catch(()=>setBootstrapError(true))
  }
  useEffect(fetchBootstrap, [])
  useEffect(()=>{
    debouncedSave(state)
    const flush = ()=>saveState(state)
    window.addEventListener('pagehide',flush)
    return ()=>window.removeEventListener('pagehide',flush)
  },[state])
  useEffect(()=>{
    const nav = navRef.current
    const button = nav?.querySelector<HTMLElement>('[aria-current="step"]')
    if(nav && button) nav.scrollTo?.({left:button.offsetLeft - nav.offsetLeft,behavior:'auto'})
    setRecError(''); setResultIndex(0)
  },[stage, seed, method])
  useEffect(()=>{
    if(!state.myList.length) return
    let cancelled = false
    api.searchSongs({ids:state.myList.join(','),limit:5}).then(res=>{
      if(!cancelled) setSongCache(c=>({...Object.fromEntries(res.items.map((s:any)=>[s.recording_mbid,s])),...c}))
    }).catch(()=>{})
    return ()=>{cancelled=true}
  },[state.myList])

  const fetchSongs = async (nextOffset=0)=>{
    const request = ++songRequest.current
    setLoadingSongs(true); setSongError('')
    const {q,style,year_min,year_max} = state.browseFilters
    if(year_min && year_max && Number(year_min)>Number(year_max)) {
      setSongError('The starting year must be before the ending year.'); setLoadingSongs(false); return
    }
    try {
      const response = await api.searchSongs({offset:nextOffset,limit:30,...(q?{q}:{}),...(style?{style}:{}),...(year_min?{year_min}:{}),...(year_max?{year_max}:{}),...(supportedOnly && sharedPool?{collaborative_only:'true'}:{})})
      if(request!==songRequest.current) return
      setSongs(response.items); setTotal(response.total); setOffset(nextOffset)
      setSongCache(c=>({...c,...Object.fromEntries(response.items.map((s:any)=>[s.recording_mbid,s]))}))
    } catch { if(request===songRequest.current) setSongError('The song catalogue could not load. Try again.') }
    finally { if(request===songRequest.current) setLoadingSongs(false) }
  }
  useEffect(()=>{if(!bootstrap) return; fetchSongs(); return ()=>{songRequest.current++}},[state.browseFilters, supportedOnly, sharedPool, bootstrap])
  const setStage = (activeStage:WorkshopStage)=>setState(s=>({...s,activeStage}))
  const toggleSong = (id:string)=>{
    setState(s=>{
      const removing=s.myList.includes(id)
      if(!removing && s.myList.length>=5) return s
      const myList=removing?s.myList.filter(x=>x!==id):[...s.myList,id]
      return {...s,myList,activeSeedId:myList.includes(s.activeSeedId || '')?s.activeSeedId:myList[0] || null}
    })
  }
  const generate = async ()=>{
    if(!seed || !method || !bootstrap || listenerBlocked || methodUnavailable || generating) return
    const generation = sessionGeneration.current
    setGenerating(true); setRecError('')
    try {
      const response = await api.postRecommendations({seed_ids:[seed],method,limit:5,...(sharedPool?{candidate_filter:{collaborative_only:true}}:{})})
      if(generation!==sessionGeneration.current) return
      const snapshot:RunSnapshot={run_id:response.run_id,method:response.method,seeds:response.seed_ids_canonical,candidate_filter:response.candidate_filter,preferences:response.preferences_applied,results:response.results,created_at:new Date().toISOString(),reactions:{},notes:'',dataset_id:response.dataset_id,scoring_version:response.scoring_version,calibration_version:response.calibration_version,prediction:predictionDraft[predictionKey] || ''}
      setState(s=>{
        // Deterministic run IDs may repeat: keep existing reflections on regeneration.
        const previous=s.runs.find(r=>r.run_id===snapshot.run_id)
        return {...s,runs:[...s.runs.filter(r=>r.run_id!==snapshot.run_id),previous || snapshot].slice(-20)}
      })
      setResultIndex(0)
    } catch(e:any) {if(generation===sessionGeneration.current) setRecError(e.message || 'Recommendations could not load. Please try again.')}
    finally {if(generation===sessionGeneration.current) setGenerating(false)}
  }
  const updateReaction = (field:string,value:string|boolean)=>{
    if(!run || !result) return
    setState(s=>({...s,runs:s.runs.map(r=>r.run_id===run.run_id?{...r,reactions:{...r.reactions,[result.recording_mbid]:{...(r.reactions[result.recording_mbid] || {revealed:false}),[field]:value}}}:r)}))
  }
  const download = (format:'json'|'md')=>{
    const blob=new Blob([format==='json'?exportJSON(state):exportMarkdown(state)],{type:format==='json'?'application/json':'text/markdown'})
    const url=URL.createObjectURL(blob); const link=document.createElement('a')
    link.href=url; link.download=`workshop-export.${format}`; link.click(); URL.revokeObjectURL(url)
  }
  const reset = ()=>{
    if(!confirm('Start a new session? Export first if you want to keep your songs and reflections.')) return
    sessionGeneration.current++; setGenerating(false); setRecError(''); setPredictionDraft({})
    localStorage.removeItem('spaceday-workshop:v1')
    const fresh=loadState(); saveState(fresh); debouncedSave(fresh); setState(fresh)
  }
  const stageIndex=STAGES.findIndex(s=>s.id===stage)
  const focus=state.tasteSurvey.focus

  return <div className="app-shell">
    <header className="app-header">
      <div className="brand"><div className="eyebrow">SpaceDay · A listening experiment</div><h1>Same song. Different ways to discover.</h1><p>What does each system notice—and what do you notice with your ears?</p></div>
      <button className="btn-ghost" onClick={reset}>Start new session</button>
    </header>
    {bootstrapError && <p role="alert" className="notice">The workshop could not connect. <button className="btn-soft" onClick={fetchBootstrap}>Retry connection</button></p>}
    <nav className="stage-nav" aria-label="Workshop steps" ref={navRef}><div className="stage-list">
      {STAGES.map((s,i)=><button key={s.id} className="stage-btn" aria-label={s.label} aria-current={stage===s.id?'step':undefined} onClick={()=>setStage(s.id)}><span className="stage-num" aria-hidden="true">{i+1}</span><span><span className="stage-label">{s.label}</span><span className="stage-sub">{s.sub}</span></span></button>)}
    </div></nav>
    {state.myList.length>0 && <section className="working-set panel" aria-label="Your working set">
      <div><div className="eyebrow">Your working set · {state.myList.length}/5</div><p className="muted">One active starting song, carried across all three systems.</p></div>
      <label className="field"><span>Active starting song</span><select className="select" value={seed || ''} onChange={e=>setState(s=>({...s,activeSeedId:e.target.value}))}>
        {state.myList.map(id=><option key={id} value={id}>{songCache[id]?`${songCache[id].title} — ${songCache[id].artist}`:'Loading song…'}</option>)}
      </select></label>
      <p className="help">Changing the song starts a new comparison. Previous results and reflections stay saved.</p>
      {selectedSong && <ListenLinks song={selectedSong}/>}
      {bootstrap && !seedSupported && <p className="notice">This song has no listener-model coverage. Keep it for musical features and CLAP, or choose another from your set to compare all three.</p>}
    </section>}
    <main id="workshop-content">
      {stage==='choose' && <div className="main-grid">
        <section className="panel" aria-labelledby="choose-heading">
          <div className="eyebrow">Step 1 · Your songs</div><h2 id="choose-heading">Choose your starting songs</h2>
          <p>Pick 3–5 songs you know, or start with just one. You’ll explore one at a time across three recommendation systems.</p>
          <label className="field"><span>Search title or artist</span><input className="input" placeholder="Try an artist or a familiar song" value={state.browseFilters.q} onChange={e=>setState(s=>({...s,browseFilters:{...s.browseFilters,q:e.target.value}}))}/></label>
          {sharedPool && <label className="field-row"><input type="checkbox" checked={supportedOnly} onChange={e=>setSupportedOnly(e.target.checked)}/>Show songs that work with all three systems ({bootstrap.collaborative.supported_count})</label>}
          <details><summary>Browse by style or year</summary><div className="filters">
            <label className="field"><span>Style</span><select className="select" value={state.browseFilters.style} onChange={e=>setState(s=>({...s,browseFilters:{...s.browseFilters,style:e.target.value}}))}><option value="">All styles</option>{bootstrap?.filter_vocab?.style_families?.map((style:string)=><option key={style} value={style}>{style}</option>)}</select></label>
            {(['year_min','year_max'] as const).map((key,i)=><label className="field" key={key}><span>{i===0?'From year':'Through year'}</span><input className="input" type="number" inputMode="numeric" value={state.browseFilters[key]} onChange={e=>setState(s=>({...s,browseFilters:{...s.browseFilters,[key]:e.target.value}}))}/></label>)}
            <button className="btn-ghost" onClick={()=>setState(s=>({...s,browseFilters:{q:'',style:'',year_min:'',year_max:''}}))}>Clear filters</button>
          </div></details>
          {songError && <p role="alert">{songError} <button className="btn-soft" onClick={()=>fetchSongs()}>Retry catalogue</button></p>}
          <div className="catalogue-list" aria-busy={loadingSongs}>
            {loadingSongs?<p className="muted">Loading songs…</p>:songs.map(song=>{const added=state.myList.includes(song.recording_mbid); return <div key={song.recording_mbid} className="catalogue-item">
              <div className="meta"><div className="title">{song.title}</div><div className="artist">{song.artist}</div><div className="sub">{song.year} · {song.primary_style_family}{bootstrap?.collaborative?.supported_ids?.includes(song.recording_mbid)?' · Works with all three':sharedPool?' · No listener model':''}</div></div>
              <button className={`add-btn${added?' add-btn--added':''}`} disabled={!added && state.myList.length>=5} aria-label={`${added?'Remove':'Add'} ${song.title} by ${song.artist} ${added?'from':'to'} working set`} onClick={()=>toggleSong(song.recording_mbid)}><span aria-hidden="true">{added?'✓':'+'}</span></button>
            </div>})}
            {!loadingSongs && !songs.length && !songError && <p>No matches. Try another search or clear the filters.</p>}
          </div>
          <div className="pagination"><span className="muted">{total?`${offset+1}–${Math.min(offset+songs.length,total)} of ${total}`:'0 songs'} · Up to 5 in your set</span><button className="btn-soft" disabled={!offset || loadingSongs} onClick={()=>fetchSongs(Math.max(0,offset-30))}>Previous songs</button><button className="btn-soft" disabled={offset+songs.length>=total || loadingSongs} onClick={()=>fetchSongs(offset+30)}>More songs</button></div>
        </section>
        <div className="stack">
          <section className="panel"><h2>Your working set · {state.myList.length}/5</h2><p className="muted">Choose a starting song above. Your other picks are ready for another experiment.</p>
            {!state.myList.length?<p>No songs yet—add a familiar one from the catalogue.</p>:state.myList.map(id=><div className="set-item" key={id}><span>{songCache[id]?.title || 'Loading song…'}<small>{songCache[id]?.artist}{seed===id?' · Active starting song':''}</small></span><button className="btn-ghost" aria-label={`Remove ${songCache[id]?.title || 'song'} from working set`} onClick={()=>toggleSong(id)}>Remove</button></div>)}
          </section>
          <section className="panel"><div className="eyebrow">Optional · Your listening lens</div><h2>A little about your taste</h2><p className="muted">Skip any question. These answers personalize your reflection prompts; they do not change the recommendation rankings. Saved on this device.</p>
            <label className="field"><span>Artists or genres you usually enjoy</span><input className="input" maxLength={300} placeholder="Whatever comes to mind" value={state.tasteSurvey.favorites} onChange={e=>setState(s=>({...s,tasteSurvey:{...s.tasteSurvey,favorites:e.target.value}}))}/></label>
            <label className="field"><span>What draws you into a song?</span><select className="select" value={focus} onChange={e=>setState(s=>({...s,tasteSurvey:{...s.tasteSurvey,focus:e.target.value}}))}><option value="">No particular focus</option>{['Rhythm','Melody','Voice','Lyrics','Atmosphere','Instrumentation'].map(v=><option key={v}>{v}</option>)}</select></label>
            <label className="field"><span>What would you like to discover?</span><select className="select" value={state.tasteSurvey.discovery} onChange={e=>setState(s=>({...s,tasteSurvey:{...s.tasteSurvey,discovery:e.target.value}}))}><option value="">Either is welcome</option><option value="familiar">Something familiar</option><option value="unexpected">Something unexpected</option></select></label>
          </section>
          <section className="panel"><h3>Three ways to find the next song</h3><p>First, compare musical measurements. Then explore a model trained on listener preferences. Finally, try CLAP’s learned audio representations.</p><p className="muted">Both listener patterns and CLAP use trained models. Their training data and ideas of similarity differ.</p></section>
        </div>
      </div>}
      {method && methodInfo && <>
        <div className="main-grid method-layout">
          <section className="panel method-intro"><div className="eyebrow">Step {stageIndex+1} · {stage==='features'?'Explicit feature formulas':'A trained model'}</div><h2>{stage==='features'?'Compare musical features':methodInfo.name}</h2>
            <p>{methodInfo.intro}</p>
            {stage==='features' && <fieldset className="method-toggle"><legend>Try a feature formula</legend>{(['rhythm-v1','texture-v1'] as const).map(m=><button key={m} className="btn-soft" aria-pressed={state.featureMethod===m} onClick={()=>setState(s=>({...s,featureMethod:m}))}>{METHODS[m].name}</button>)}</fieldset>}
            <div className="learning-prompt"><div className="eyebrow">1 · Predict</div><p>{methodInfo.predict}</p><details><summary>Write a prediction (optional)</summary><div><label className="field"><span>Your prediction</span><textarea className="textarea" value={run?.prediction || predictionDraft[predictionKey] || ''} onChange={e=>{const value=e.target.value; setPredictionDraft(p=>({...p,[predictionKey]:value})); if(run) setState(s=>({...s,runs:s.runs.map(r=>r.run_id===run.run_id?{...r,prediction:value}:r)}))}} placeholder="What do you expect this system to find?"/></label></div></details></div>
            <p className="help">{sharedPool?`All three systems use the same eligible pool of ${bootstrap.collaborative.supported_count} songs, excluding the starting song.`:'Recommendations use the available catalogue, excluding the starting song.'} Your taste survey does not alter the rankings.</p>
            {!seed && <p className="notice">Choose a starting song in Your songs to begin.</p>}
            {listenerBlocked && seed && <p className="notice">The listener model needs more feedback than this song has. Choose a supported song from your working set, or return to Your songs and add one. We won’t substitute a different seed.</p>}
            {methodUnavailable && <p role="status">This method is not available on this server.</p>}
            {recError && <p role="alert">{recError}</p>}
            <button className="btn-primary generate-button" onClick={generate} disabled={!seed || !bootstrap || generating || listenerBlocked || methodUnavailable}>{generating?'Finding songs…':run?'Refresh recommendations':'Find 5 recommendations'}</button>
          </section>
          <section className="panel results-panel" aria-label="Recommendations">
            <div className="eyebrow">2 · Listen with your ears</div><h2>{run?'What connects these songs?':'Your listening experiment'}</h2><p>{methodInfo.listen}</p>
            {focus && <p className="listening-lens">Your lens: <strong>{focus.toLowerCase()}</strong>. Does this recommendation connect in the way you hoped?</p>}
            {!run?<div className="empty-state"><p>Keep your starting song in mind, then find recommendations from this system.</p><p className="muted">Listen before revealing the score and explanation. There is no correct reaction.</p></div>:!result?<p role="status">No recommendations are available for this setup. Try another starting song.</p>:<div className="carousel" tabIndex={0} aria-label="Recommendations carousel" aria-roledescription="carousel" onKeyDown={e=>{if(e.target!==e.currentTarget) return; if(e.key==='ArrowRight'){e.preventDefault();setResultIndex(i=>Math.min(run.results.length-1,i+1))} if(e.key==='ArrowLeft'){e.preventDefault();setResultIndex(i=>Math.max(0,i-1))}}}>
              <div className="indicator"><button className="btn-soft" aria-label="Previous recommendation" disabled={currentIndex===0} onClick={()=>setResultIndex(i=>Math.max(0,i-1))}>← Previous</button><span aria-live="polite">{currentIndex+1} / {run.results.length}</span><button className="btn-soft" aria-label="Next recommendation" disabled={currentIndex===run.results.length-1} onClick={()=>setResultIndex(i=>i+1)}>Next →</button></div>
              <article className="result-card"><h3 className="song-title">{result.title}</h3><p className="artist">{result.artist}</p><ListenLinks song={result}/><p className="inline-help">Links open searches in another tab. Choose the matching recording and return here.</p>
                <div className="learning-prompt"><div className="eyebrow">3 · Reflect</div><h3>Similarity and enjoyment can differ.</h3><div className="reaction-grid">
                  <label className="field"><span>Do you want to keep listening?</span><select className="select" aria-label={`Enjoyment for ${result.title}`} value={reaction.like || ''} onChange={e=>updateReaction('like',e.target.value)}><option value="">Your reaction (optional)</option><option value="like">Yes</option><option value="unsure">Unsure</option><option value="dislike">No</option></select></label>
                  <label className="field"><span>Can you hear a connection?</span><select className="select" aria-label={`Connection for ${result.title}`} value={reaction.connection || ''} onChange={e=>updateReaction('connection',e.target.value)}><option value="">Your reaction (optional)</option><option value="clear">A clear connection</option><option value="partly">Partly</option><option value="not">Hard to connect</option></select></label>
                </div><label className="field"><span>What did you hear?</span><textarea className="textarea" aria-label={`Listening note for ${result.title}`} value={reaction.note || ''} onChange={e=>updateReaction('note',e.target.value)} placeholder="A similar groove? A different voice? An unexpected connection?"/></label>
                {!reaction.revealed?<button className="btn-soft" onClick={()=>updateReaction('revealed',true)}>Reveal how this system matched it</button>:<Evidence run={run} result={result} seedName={selectedSong?.title || 'Starting song'}/>}
                {reaction.revealed && <p className="inline-help">You can revise your reaction after reading the explanation.</p>}
              </div></article>
            </div>}
          </section>
        </div>
        {stage==='clap' && <details className="language-extension"><summary>Optional: explore CLAP with words</summary><div><p>Continue beyond the controlled song comparison: try describing sound and judging prepared descriptions.</p><LanguageLab appState={state} setAppState={setState} bootstrap={bootstrap} songs={songs} songCache={songCache} activeSeed={seed}/></div></details>}
      </>}
      {stage==='compare' && <section className="panel"><div className="eyebrow">Step 5 · Compare</div><h2>Same starting song. What changed?</h2><p>These cards show results for your current starting song, with the same candidate pool and no taste reranking. Change the active song above to revisit another experiment.</p>
        <div className="comparison-grid">{(['rhythm-v1','texture-v1','collaborative-v1','clap-v1'] as Method[]).map(m=>{const saved=[...setupRuns].reverse().find(r=>r.method===m);return <section className="result-card" key={m}><h3>{METHODS[m].name}</h3>{!saved?<p className="muted">{m==='collaborative-v1' && !seedSupported?'Your starting song has no listener-model coverage.':'Try this method to add its recommendations.'}</p>:<><ol className="comparison-songs">{saved.results.map(r=><li key={r.recording_mbid}><strong>{r.title}</strong><span>{r.artist}</span><small>{saved.reactions[r.recording_mbid]?.like==='like'?'You wanted to keep listening. ':''}{saved.reactions[r.recording_mbid]?.connection==='clear'?'You heard a clear connection. ':''}{saved.reactions[r.recording_mbid]?.note}</small></li>)}</ol><p className="muted">{saved.notes}</p></>}
          <button className="btn-soft" onClick={()=>{if(m==='rhythm-v1'||m==='texture-v1')setState(s=>({...s,featureMethod:m,activeStage:'features'}));else setStage(m==='clap-v1'?'clap':'listeners')}}>Explore {METHODS[m].name}</button></section>})}</div>
        <div className="learning-prompt"><h3>Which system found a close match? Which found something you wanted to hear?</h3><p>Those can be different answers. What did each system seem to notice or miss?</p>{state.tasteSurvey.favorites && <p>Your usual listening: {state.tasteSurvey.favorites}. Did any system take you beyond it?</p>}{state.tasteSurvey.discovery && <p>You hoped for something {state.tasteSurvey.discovery}. Which method came closest to that?</p>}
          <label className="field"><span>Your takeaways</span><textarea className="textarea" value={state.notes} onChange={e=>setState(s=>({...s,notes:e.target.value}))} placeholder="What did the systems notice—and what did you notice?"/></label>
        </div>
      </section>}
      {stage==='notes' && <section className="panel"><div className="eyebrow">Step 6 · Keep your discoveries</div><h2>Your reflections</h2><p className="muted">Your working set, survey and reflections stay on this device. Download them before ending a shared-device session.</p><label className="field"><span>Session notes</span><textarea className="textarea" value={state.notes} onChange={e=>setState(s=>({...s,notes:e.target.value}))}/></label><div className="field-row"><button className="btn-primary" onClick={()=>download('md')}>Download Markdown</button><button className="btn-soft" onClick={()=>download('json')}>Download JSON</button></div>
        <h3>Saved experiments · {state.runs.length}</h3>{!state.runs.length && <p>No experiments yet. Your reflections will appear here after you try a method.</p>}
        {[...state.runs].reverse().map(r=><details key={r.run_id}><summary>{METHODS[r.method as Method]?.name || r.method} · {r.seeds.map(id=>songCache[id]?.title || id.slice(0,8)).join(', ')} · {new Date(r.created_at).toLocaleTimeString()}</summary><div>{r.prediction && <p>Prediction: {r.prediction}</p>}<label className="field"><span>Experiment reflection</span><textarea className="textarea" value={r.notes} onChange={e=>{const notes=e.target.value;setState(s=>({...s,runs:s.runs.map(x=>x.run_id===r.run_id?{...x,notes}:x)}))}}/></label>{r.results.map(result=>{const reaction=r.reactions[result.recording_mbid];return reaction?<p key={result.recording_mbid}><strong>{result.title}</strong> · Enjoyment: {reaction.like || 'unanswered'} · Connection: {reaction.connection || 'unanswered'}<br/>{reaction.note}</p>:null})}<p className="muted">{matchesSetup(r,seed,sharedPool,bootstrap?.dataset_id || null)?'Matches your current comparison setup.':'Saved from a different setup. Kept for your records.'}</p></div></details>)}
      </section>}
    </main>
    <div className="bottom-bar" role="toolbar" aria-label="Workshop navigation"><span className="muted">Step {stageIndex+1} of {STAGES.length}</span>{stageIndex>0 && <button className="btn-ghost secondary" onClick={()=>setStage(STAGES[stageIndex-1].id)}>Back</button>}{stageIndex<STAGES.length-1 && <button className="btn-primary primary" disabled={stage==='choose' && !seed} onClick={()=>setStage(STAGES[stageIndex+1].id)}>Next: {STAGES[stageIndex+1].label}</button>}</div>
    <footer>Listen, question, compare. A surprising recommendation can be as useful as a familiar one. Your work is saved on this device.</footer>
  </div>
}
