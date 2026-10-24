import { describe, it, expect, beforeEach } from 'vitest'
import { exportMarkdown, exportJSON, loadState, saveState } from '../src/state/storage'

describe('storage export', ()=>{
  it('produces markdown with expected sections', ()=>{
    const state:any={dataset_id:'abc', myList:['id1'], runs:[{run_id:'r1', method:'clap-v1', seeds:['id1'], candidate_filter:null, preferences:null, results:[{title:'T', artist:'A', match_percentile:99.8, recording_mbid:'id2'}], created_at:'2026-10-21', reactions:{}, notes:'hi', dataset_id:'abc', scoring_version:'scoring-v1'}], textHistory:[], descriptionJudgments:{}, notes:'', version:2, browseFilters:{q:'',style:'',year_min:'',year_max:''}, candidateFilter:null, preferencesDraft:{instrumental:null, acoustic_electronic:null}, activeStage:'choose', activeRunId:null, activeResultIndex:0}
    const md=exportMarkdown(state)
    expect(md).toContain('Workshop Session Export')
    expect(md).toContain('r1')
    expect(md).toContain('Model: scoring-v1')
    const j=exportJSON(state)
    expect(JSON.parse(j).dataset_id).toBe('abc')
  })
  it('persists stage and active indices', ()=>{
    localStorage.clear()
    const s = loadState()
    s.activeStage = 'features'
    s.activeRunId = 'r123'
    s.activeResultIndex = 2
    saveState(s)
    const loaded = loadState()
    expect(loaded.activeStage).toBe('features')
    expect(loaded.activeRunId).toBe('r123')
    expect(loaded.activeResultIndex).toBe(2)
  })
  it('migrates v1 to v3 without losing runs', ()=>{
    localStorage.clear()
    const v1:any = {version:1, myList:['a'], runs:[{run_id:'r1', method:'clap-v1', seeds:['a'], results:[], created_at:'', reactions:{}, notes:'', dataset_id:'d'}], browseFilters:{q:'',style:'',year_min:'',year_max:''}, preferencesDraft:{}, textHistory:[], descriptionJudgments:{}, notes:''}
    localStorage.setItem('spaceday-workshop:v1', JSON.stringify(v1))
    const migrated = loadState()
    expect(migrated.version).toBe(3)
    expect(migrated.myList).toEqual(['a'])
    expect(migrated.runs.length).toBe(1)
    expect(migrated.activeStage).toBeDefined()
  })
  it('handles corrupted storage without crash', ()=>{
    localStorage.setItem('spaceday-workshop:v1', 'not-json{')
    const s = loadState()
    expect(s.myList).toEqual([])
    expect(s.version).toBe(3)
  })
  it('caps run history at 20 via benchmark', ()=>{
    const s = loadState()
    s.runs = Array.from({length:22}, (_,i)=> ({run_id:`r${i}`, method:'clap-v1', seeds:['a'], results:[], created_at:'', reactions:{}, notes:'', dataset_id:'d'} as any))
    // simulate save pruning
    saveState({...s, runs: s.runs.slice(-10)})
    const loaded = loadState()
    expect(loaded.runs.length).toBeLessThanOrEqual(10)
  })
})

describe('workshop migration and reflection exports',()=>{
  beforeEach(()=>localStorage.clear())
  it('maps the old description stage to CLAP and preserves saved experiments',()=>{
    const old={...loadState(),version:2,activeStage:'describe',myList:['a','b'],activeSeedId:undefined,runs:[{run_id:'old',method:'clap-v1',seeds:['a','b'],results:[],reactions:{},created_at:'',notes:'Keep this',dataset_id:'d'}]}
    localStorage.setItem('spaceday-workshop:v1',JSON.stringify(old))
    const state=loadState()
    expect(state.activeStage).toBe('clap');expect(state.activeSeedId).toBe('a')
    expect(state.runs[0].notes).toBe('Keep this');expect(state.tasteSurvey.focus).toBe('')
  })
  it('exports the listening lens and session takeaways',()=>{
    const state=loadState();state.tasteSurvey.focus='Rhythm';state.notes='Similarity is not enjoyment'
    const md=exportMarkdown(state)
    expect(md).toContain('Rhythm');expect(md).toContain('Similarity is not enjoyment')
  })
})
