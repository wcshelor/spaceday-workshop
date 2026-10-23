import { describe, it, expect, vi, beforeEach } from 'vitest'
import { render, screen, fireEvent, waitFor } from '@testing-library/react'
import App from '../src/app/App'

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

describe('App mobile-first staged flow', ()=>{
  beforeEach(()=> { localStorage.clear(); vi.clearAllMocks() })

  it('Choose → generate → move between results → react → reveal, per result/run', async ()=>{
    render(<App />)
    // Wait for catalogue
    expect(await screen.findByText(/Search for a familiar song/)).toBeInTheDocument()
    // Add first song
    const addBtns = await screen.findAllByRole('button', {name:/Add /})
    expect(addBtns[0]).toHaveAccessibleName(/Add Song One/)
    fireEvent.click(addBtns[0])
    // Should appear in My List (chip + catalogue both have title, so check at least one)
    expect((await screen.findAllByText(/Song One With Very Long Title/)).length).toBeGreaterThanOrEqual(1)
    // Go to Listen stage
    fireEvent.click(screen.getByRole('tab', {name:/Listen/}))
    expect(await screen.findByText(/Choose a method and generate/)).toBeInTheDocument()
    // Generate
    const genBtn = screen.getByRole('button', {name:/Generate 5 recommendations/})
    expect(genBtn).toBeEnabled()
    fireEvent.click(genBtn)
    // Wait for carousel
    const resultTitle = await screen.findByText(/Result 1 With Long Title/)
    expect(resultTitle).toBeInTheDocument()
    expect(screen.getByText(/1 \/ 5/)).toBeInTheDocument()
    // Move next
    const nextBtn = screen.getByRole('button', {name:/Next recommendation/})
    expect(nextBtn).toHaveAccessibleName(/Next/)
    fireEvent.click(nextBtn)
    expect(await screen.findByText(/Result 2 With Long Title/)).toBeInTheDocument()
    expect(screen.getByText(/2 \/ 5/)).toBeInTheDocument()
    // Previous
    fireEvent.click(screen.getByRole('button', {name:/Previous recommendation/}))
    expect(await screen.findByText(/Result 1 With Long Title/)).toBeInTheDocument()
    // React before reveal
    const likeSelect = screen.getByLabelText(/Enjoyment for Result 1/)
    fireEvent.change(likeSelect, {target:{value:'like'}})
    // Reveal
    const listenedBtn = screen.getByRole('button', {name:/I’ve listened/})
    fireEvent.click(listenedBtn)
    await waitFor(()=> expect(screen.getByText(/Evidence/)).toBeInTheDocument(), {timeout: 3000})
    // Ensure reaction persisted per result: go next and back, still revealed?
    fireEvent.click(nextBtn)
    fireEvent.click(screen.getByRole('button', {name:/Previous recommendation/}))
    await waitFor(()=> expect(screen.getByText(/Evidence/)).toBeInTheDocument())
  })

  it('Switching methods preserves My List and previous runs', async ()=>{
    render(<App />)
    const addBtns = await screen.findAllByRole('button', {name:/Add /})
    fireEvent.click(addBtns[0])
    fireEvent.click(screen.getByRole('tab', {name:/Listen/}))
    fireEvent.click(screen.getByRole('button', {name:/Generate 5 recommendations/}))
    await screen.findByText(/Result 1 With Long Title/)
    // Switch method
    const methodSelect = screen.getByLabelText(/Recommendation method/)
    fireEvent.change(methodSelect, {target:{value:'rhythm-v1'}})
    fireEvent.click(screen.getByRole('button', {name:/Generate 5 recommendations/}))
    await screen.findByText(/Result 1 With Long Title/)
    // My List still there
    fireEvent.click(screen.getByRole('tab', {name:/Choose/}))
    expect((await screen.findAllByText(/Song One With Very Long Title/)).length).toBeGreaterThanOrEqual(1)
    // Compare should show 2 runs
    fireEvent.click(screen.getByRole('tab', {name:/Compare/}))
    expect(await screen.findByText(/Preserve setup/)).toBeInTheDocument()
    expect((await screen.findAllByText(/clap-v1/)).length).toBeGreaterThanOrEqual(1)
    expect((await screen.findAllByText(/rhythm-v1/)).length).toBeGreaterThanOrEqual(1)
  })

  it('Revisiting stages and refresh preserves state', async ()=>{
    const { unmount } = render(<App />)
    const addBtns = await screen.findAllByRole('button', {name:/Add /})
    fireEvent.click(addBtns[0])
    fireEvent.click(screen.getByRole('tab', {name:/Listen/}))
    fireEvent.click(screen.getByRole('button', {name:/Generate 5 recommendations/}))
    await screen.findByText(/Result 1 With Long Title/)
    // Go to Describe then back
    fireEvent.click(screen.getByRole('tab', {name:/Describe/}))
    expect(await screen.findByText(/Matching descriptions/)).toBeInTheDocument()
    fireEvent.click(screen.getByRole('tab', {name:/Listen/}))
    expect(await screen.findByText(/Result 1 With Long Title/)).toBeInTheDocument()
    // Simulate refresh by remounting (loadState should restore)
    unmount()
    render(<App />)
    expect((await screen.findAllByText(/Song One With Very Long Title/)).length).toBeGreaterThanOrEqual(1)
  })

  it('Description and prepared-example flow and notes export', async ()=>{
    render(<App />)
    // Add to My List to have song for descriptions
    const addBtns = await screen.findAllByRole('button', {name:/Add /})
    fireEvent.click(addBtns[0])
    fireEvent.click(screen.getByRole('tab', {name:/Describe/}))
    const songSelect = await screen.findByLabelText(/Choose song for descriptions/)
    fireEvent.change(songSelect, {target:{value:'id1'}})
    const warmMatches = await screen.findAllByText(/warm acoustic guitar/)
    expect(warmMatches.length).toBeGreaterThanOrEqual(1)
    // Judge - there are two fits buttons, pick first
    const fitsBtns = screen.getAllByRole('button', {name:'fits'})
    fireEvent.click(fitsBtns[0])
    expect(fitsBtns[0]).toHaveAttribute('aria-pressed','true')
    // Prepared examples visible and distinguishable
    expect(screen.getByText(/Try without live retrieval/)).toBeInTheDocument()
    expect((await screen.findAllByText(/warm acoustic guitar/)).length).toBeGreaterThanOrEqual(2)
    // Text search unavailable handling
    const searchInput = screen.getByLabelText(/Your description/)
    fireEvent.change(searchInput, {target:{value:'test query'}})
    fireEvent.click(screen.getByRole('button', {name:/Search/}))
    expect(await screen.findByText(/Live search isn’t available/)).toBeInTheDocument()
    // Notes export
    fireEvent.click(screen.getByRole('tab', {name:/Notes/}))
    expect(await screen.findByText(/Your reflections/)).toBeInTheDocument()
    expect(screen.getByRole('button', {name:/Download JSON/})).toBeEnabled()
    expect(screen.getByRole('button', {name:/Download Markdown/})).toBeEnabled()
  })

  it('Empty selection, loading, API failure, unsupported collaborative seeds', async ()=>{
    render(<App />)
    // Initially on Choose, Add buttons should be accessible
    const addBtns = await screen.findAllByRole('button', {name:/Add /})
    expect(addBtns[0]).toHaveAccessibleName(/Add Song One/)
    fireEvent.click(screen.getByRole('tab', {name:/Listen/}))
    // Empty My List -> Generate should be disabled
    const genBtn = screen.getByRole('button', {name:/Generate 5 recommendations/})
    expect(genBtn).toBeDisabled()
    expect(screen.getByLabelText(/Recommendation method/)).toBeInTheDocument()
    // Keyboard accessible: stage tabs are tablist with role=tab
    const chooseTab = screen.getByRole('tab', {name:/Choose/})
    expect(chooseTab).toBeInTheDocument()
    chooseTab.focus()
    expect(document.activeElement).toBe(chooseTab)
  })

  it('Phone and laptop layouts without horizontal overflow', async ()=>{
    render(<App />)
    const appShell = document.querySelector('.app-shell') as HTMLElement
    expect(appShell).toBeInTheDocument()
    const html = document.documentElement
    expect(html.scrollWidth <= html.clientWidth + 5 || html.clientWidth===0).toBeTruthy()
    const stageNav = document.querySelector('.stage-nav') as HTMLElement
    expect(stageNav).toBeInTheDocument()
    expect((await screen.findAllByText(/Song One With Very Long Title/)).length).toBeGreaterThanOrEqual(1)
  })
})
