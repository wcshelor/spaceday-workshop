import { describe, it, expect, vi, beforeEach } from 'vitest'
import { render, screen, fireEvent, waitFor, within } from '@testing-library/react'
import App from '../src/app/App'
import * as api from '../src/api/client'
import { loadState, saveState } from '../src/state/storage'

// Mock API client with deterministic fixtures
vi.mock('../src/api/client', () => ({
  getBootstrap: vi.fn(() => Promise.resolve({
    dataset_id: 'test123',
    scoring_version: 'scoring-v1',
    calibration_version: 'calibration-v1',
    language_status: 'disabled',
    supported_methods: ['clap-v1','rhythm-v1','texture-v1','collaborative-v1'],
    filter_vocab: { style_families: ['pop_smooth','rock'] },
    collaborative: { supported_count: 2, supported_ids: ['id1','id2'] },
    score_help: 'How strong vs reference',
  })),
  searchSongs: vi.fn((params: any) => {
    if (params.ids) {
      const ids = (params.ids as string).split(',')
      return Promise.resolve({ items: ids.map(id=> ({recording_mbid:id, title:`Title ${id}`, artist:`Artist ${id}`, year: 2000, primary_style_family:'pop_smooth', is_editorial_anchor:false, style_families:[]})), total: ids.length })
    }
    return Promise.resolve({
      items: [
        {recording_mbid:'id1', title:'Song One With Very Long Title That Should Wrap Correctly Without Overflow', artist:'Artist One With Long Name', year: 1990, primary_style_family:'pop_smooth', is_editorial_anchor:true, style_families:['pop_smooth']},
        {recording_mbid:'id2', title:'Song Two', artist:'Artist Two', year: 1991, primary_style_family:'rock', is_editorial_anchor:false, style_families:['rock']},
        {recording_mbid:'id3', title:'Song Three', artist:'Artist Three', year: 1992, primary_style_family:'pop_smooth', is_editorial_anchor:false, style_families:['pop_smooth']},
      ], total: 3
    })
  }),
  postRecommendations: vi.fn((body:any) => {
    if (!body.seed_ids || body.seed_ids.length===0) return Promise.reject(new Error('Choose at least one song'))
    if (body.seed_ids.includes('unsupported')) return Promise.reject(new Error('No listener model'))
    const results = [1,2,3,4,5].map(n=> ({recording_mbid:`res${n}`, title:`Result ${n} With Long Title To Test Wrapping And Overflow Handling`, artist:`Result Artist ${n}`, year: 2000+n, primary_style_family:'pop_smooth', match_percentile: 90+n, base_score: 0.5, youtube_search_url:'https://youtube.com', spotify_search_url:'https://spotify.com'}))
    return Promise.resolve({run_id:`run_${body.seed_ids.join('_')}_${body.method}`, dataset_id:'test123', scoring_version:'scoring-v1', calibration_version:'calibration-v1', method: body.method, seed_ids_canonical: [...body.seed_ids].sort(), candidate_filter: body.candidate_filter||null, preferences_applied: body.preferences||null, results})
  }),
  postExplanations: vi.fn(()=> Promise.resolve({method:'clap-v1', base_score:0.5, per_seed_scores:{id1:0.6}, detail:{note:'test'}, note:'test'})),
  postDescriptions: vi.fn(()=> Promise.resolve({matches:[
    {id:'desc1', text:'warm acoustic guitar', category:'instruments', paraphrase_group:'g1'},
    {id:'desc2', text:'intimate vocals', category:'vocals', paraphrase_group:'g2'},
  ], note:'test'})),
  postTextSearch: vi.fn(()=> Promise.reject(new Error('text search unavailable: encoder disabled'))),
  getExamples: vi.fn(()=> Promise.resolve({version:'prompts-v1', items:[{id:'ex1', query:'warm acoustic guitar', category:'texture'}]})),
}))

const go = (name:string)=>fireEvent.click(screen.getByRole('button',{name:`${name}`,exact:true}))
const step = (label:string)=>fireEvent.click(screen.getByRole('button',{name:label,exact:true}))
async function chooseTwo() {
  const add=await screen.findAllByRole('button',{name:/^Add /})
  fireEvent.click(add[0]);fireEvent.click(add[1])
}
async function generate() {
  await waitFor(()=>expect(screen.getByRole('button',{name:'Find 5 recommendations'})).toBeEnabled())
  fireEvent.click(screen.getByRole('button',{name:'Find 5 recommendations'}))
  await screen.findByRole('heading',{name:/Result 1 With Long Title/})
}

describe('Shared song listening workshop',()=>{
  beforeEach(()=>{localStorage.clear();vi.clearAllMocks()})
  it('carries one active seed and the same pool through all methods; keeps reactions scoped to method',async()=>{
    render(<App/>);await chooseTwo()
    step('Musical features');await generate()
    expect(api.postRecommendations).toHaveBeenLastCalledWith({seed_ids:['id1'],method:'rhythm-v1',limit:5,candidate_filter:{collaborative_only:true}})
    fireEvent.change(screen.getByLabelText(/Enjoyment for/),{target:{value:'like'}})
    fireEvent.click(screen.getByRole('button',{name:'Reveal how this system matched it'}))
    await screen.findByRole('heading',{name:'Why this recommendation?'})
    expect(api.postExplanations).toHaveBeenLastCalledWith(expect.objectContaining({method:'rhythm-v1',seed_ids:['id1']}))
    step('Listener patterns');await generate()
    expect(api.postRecommendations).toHaveBeenLastCalledWith(expect.objectContaining({seed_ids:['id1'],method:'collaborative-v1',candidate_filter:{collaborative_only:true}}))
    expect(screen.getByLabelText(/Enjoyment for/)).toHaveValue('')
    expect(screen.queryByRole('heading',{name:'Why this recommendation?'})).not.toBeInTheDocument()
    step('CLAP sound');await generate()
    expect(api.postRecommendations).toHaveBeenLastCalledWith(expect.objectContaining({seed_ids:['id1'],method:'clap-v1',candidate_filter:{collaborative_only:true}}))
    step('Musical features')
    expect(screen.getByLabelText(/Enjoyment for/)).toHaveValue('like')
    expect(screen.getByRole('heading',{name:'Why this recommendation?'})).toBeInTheDocument()
    step('Compare')
    expect(screen.getAllByText(/Result 1 With Long Title/)).toHaveLength(3)
  })
  it('changing active song hides other seed results and restores them when returning',async()=>{
    render(<App/>);await chooseTwo();step('Musical features');await generate()
    fireEvent.change(screen.getByLabelText('Active starting song'),{target:{value:'id2'}})
    expect(screen.queryByRole('heading',{name:/Result 1/})).not.toBeInTheDocument()
    await generate()
    expect(api.postRecommendations).toHaveBeenLastCalledWith(expect.objectContaining({seed_ids:['id2']}))
    fireEvent.change(screen.getByLabelText('Active starting song'),{target:{value:'id1'}})
    expect(screen.getByRole('heading',{name:/Result 1/})).toBeInTheDocument()
  })
  it('unsupported song is kept in the set, blocks only listener generation, and is never substituted',async()=>{
    render(<App/>);const add=await screen.findAllByRole('button',{name:/^Add /});fireEvent.click(add[2]);step('Listener patterns')
    expect(screen.getByRole('button',{name:'Find 5 recommendations'})).toBeDisabled()
    expect(screen.getByText(/We won’t substitute/)).toBeInTheDocument()
    expect(api.postRecommendations).not.toHaveBeenCalled()
    step('CLAP sound');await generate()
    expect(api.postRecommendations).toHaveBeenLastCalledWith(expect.objectContaining({seed_ids:['id3']}))
  })
  it('survey supplies listening prompts without adding ranking preferences',async()=>{
    render(<App/>);await chooseTwo()
    fireEvent.change(screen.getByLabelText('What draws you into a song?'),{target:{value:'Rhythm'}})
    fireEvent.change(screen.getByLabelText('Artists or genres you usually enjoy'),{target:{value:'Soul'}})
    step('Musical features');expect(screen.getByText(/Your lens:/)).toHaveTextContent('rhythm');await generate()
    expect(vi.mocked(api.postRecommendations).mock.calls[0][0]).not.toHaveProperty('preferences')
    step('Compare');expect(screen.getByText(/Your usual listening: Soul/)).toBeInTheDocument()
  })
  it('catalogue checkmark removes songs and updates the active seed; selection survives filters and refresh',async()=>{
    const {unmount}=render(<App/>);await chooseTwo()
    const remove=screen.getByRole('button',{name:/Remove Song One.*by Artist One.*from working set/})
    expect(remove).toHaveTextContent('✓');expect(remove).toBeEnabled();fireEvent.click(remove)
    expect(screen.getByLabelText('Active starting song')).toHaveValue('id2')
    expect(screen.getByRole('button',{name:/Add Song One/})).toHaveTextContent('+')
    fireEvent.change(screen.getByLabelText('Search title or artist'),{target:{value:'Two'}})
    await waitFor(()=>expect(screen.getByRole('button',{name:/Remove Song Two by Artist Two/})).toHaveTextContent('✓'))
    await waitFor(()=>expect(JSON.parse(localStorage.getItem('spaceday-workshop:v1') || '{}').activeSeedId).toBe('id2'))
    unmount();render(<App/>);await screen.findByRole('button',{name:/Remove Song Two by Artist Two/})
    expect(screen.getByLabelText('Active starting song')).toHaveValue('id2')
  })
  it('keeps per-result notes while navigating and retains reactions after deterministic regeneration',async()=>{
    render(<App/>);await chooseTwo();step('Musical features');await generate()
    fireEvent.change(screen.getByLabelText(/Listening note for Result 1/),{target:{value:'Same pulse'}})
    go('Next recommendation');expect(screen.getByLabelText(/Listening note for Result 2/)).toHaveValue('')
    go('Previous recommendation');expect(screen.getByLabelText(/Listening note for Result 1/)).toHaveValue('Same pulse')
    go('Refresh recommendations')
    await waitFor(()=>expect(api.postRecommendations).toHaveBeenCalledTimes(2))
    expect(screen.getByLabelText(/Listening note for Result 1/)).toHaveValue('Same pulse')
  })
  it('retains description matching as an optional CLAP experiment without the retired live text search',async()=>{
    render(<App/>);await chooseTwo();step('CLAP sound')
    fireEvent.click(screen.getByText('Optional: explore CLAP with words'))
    expect((await screen.findAllByRole('button',{name:'fits'}))[0]).toBeInTheDocument()
    fireEvent.click(screen.getAllByRole('button',{name:'fits'})[0])
    expect(screen.getAllByRole('button',{name:'fits'})[0]).toHaveAttribute('aria-pressed','true')
    expect(screen.queryByLabelText('Your description')).not.toBeInTheDocument()
    expect(screen.queryByRole('button',{name:'Search with your description',exact:true})).not.toBeInTheDocument()
    step('Notes & export');expect(screen.getByRole('button',{name:'Download Markdown'})).toBeEnabled()
  })
  it('does not label older multi-seed runs as a controlled current comparison',async()=>{
    const initial=loadState();initial.myList=['id1','id2'];initial.activeSeedId='id1';initial.activeStage='compare'
    initial.runs=[{run_id:'old',method:'clap-v1',seeds:['id1','id2'],candidate_filter:{collaborative_only:true},preferences:null,results:[{recording_mbid:'oldresult',title:'Old recommendation'}],created_at:new Date().toISOString(),reactions:{},notes:'',dataset_id:'test123'}]
    saveState(initial);render(<App/>);await screen.findByText(/same candidate pool/)
    expect(screen.queryByText('Old recommendation')).not.toBeInTheDocument()
    step('Notes & export');expect(screen.getByText(/Saved experiments · 1/)).toBeInTheDocument()
  })
  it('shows recommendation failures and allows retry',async()=>{
    vi.mocked(api.postRecommendations).mockRejectedValueOnce(new Error('Server unavailable'))
    render(<App/>);await chooseTwo();step('Musical features')
    go('Find 5 recommendations');expect(await screen.findByRole('alert')).toHaveTextContent('Server unavailable')
    await generate()
  })
})
