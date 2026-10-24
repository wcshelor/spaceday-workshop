// Versioned local storage adapter
const KEY = 'spaceday-workshop:v1'
const VERSION = 3

export type WorkshopStage = 'choose' | 'features' | 'listeners' | 'clap' | 'compare' | 'notes'

export type RunSnapshot = {
  run_id: string
  method: string
  seeds: string[]
  candidate_filter: any
  preferences: any
  results: any[]
  created_at: string
  reactions: Record<string, {like?: string, connection?: string, note?: string, revealed: boolean}>
  notes: string
  prediction?: string
  dataset_id: string
  scoring_version?: string
  calibration_version?: string
}

export type AppState = {
  version: number
  dataset_id: string | null
  myList: string[] // ordered mbids
  browseFilters: {q: string, style: string, year_min: string, year_max: string}
  candidateFilter: any | null
  preferencesDraft: any
  runs: RunSnapshot[]
  textHistory: {query: string, results: any[], at: string}[]
  descriptionJudgments: Record<string, {fit: string, reason?: string}>
  notes: string
  activeSeedId: string | null
  featureMethod: 'rhythm-v1' | 'texture-v1'
  tasteSurvey: { favorites: string; focus: string; discovery: string }
  // Workshop navigation
  activeStage: WorkshopStage
  activeRunId: string | null
  activeResultIndex: number
}

const defaultState: AppState = {
  version: VERSION,
  dataset_id: null,
  myList: [],
  browseFilters: {q:'', style:'', year_min:'', year_max:''},
  candidateFilter: null,
  preferencesDraft: {instrumental: null, acoustic_electronic: null},
  runs: [],
  textHistory: [],
  descriptionJudgments: {},
  notes: '',
  activeSeedId: null,
  featureMethod: 'rhythm-v1',
  tasteSurvey: {favorites:'', focus:'', discovery:''},
  activeStage: 'choose' as WorkshopStage,
  activeRunId: null,
  activeResultIndex: 0,
}

export function loadState(): AppState {
  try {
    const raw = localStorage.getItem(KEY)
    if (!raw) return {...defaultState}
    const parsed = JSON.parse(raw)
    const oldStage = parsed.activeStage
    const activeStage = oldStage === 'listen' || oldStage === 'reflect'
      ? (parsed.runs?.find((r: RunSnapshot)=>r.run_id === parsed.activeRunId)?.method === 'collaborative-v1' ? 'listeners' :
        parsed.runs?.find((r: RunSnapshot)=>r.run_id === parsed.activeRunId)?.method === 'clap-v1' ? 'clap' : 'features')
      : oldStage === 'describe' ? 'clap' : oldStage
    return {
      ...defaultState, ...parsed, version: VERSION,
      activeStage: ['choose','features','listeners','clap','compare','notes'].includes(activeStage) ? activeStage : 'choose',
      activeSeedId: parsed.myList?.includes(parsed.activeSeedId) ? parsed.activeSeedId : parsed.myList?.[0] || null,
      featureMethod: parsed.featureMethod === 'texture-v1' ? 'texture-v1' : 'rhythm-v1',
      tasteSurvey: {...defaultState.tasteSurvey, ...parsed.tasteSurvey},
    }
  } catch {
    return {...defaultState}
  }
}

export function saveState(s: AppState) {
  try {
    localStorage.setItem(KEY, JSON.stringify(s))
  } catch (e) {
    console.warn('storage quota', e)
    // fallback: try to prune runs
    const pruned = {...s, runs: s.runs.slice(-10)}
    try { localStorage.setItem(KEY, JSON.stringify(pruned)) } catch {}
  }
}

let debounceTimer: any = null
export function debouncedSave(s: AppState) {
  clearTimeout(debounceTimer)
  debounceTimer = setTimeout(()=> saveState(s), 300)
}

export function exportJSON(state: AppState) {
  return JSON.stringify(state, null, 2)
}
export function exportMarkdown(state: AppState) {
  let md = `# Workshop Session Export\n\nDataset: ${state.dataset_id || 'unknown'}\nWorking set: ${state.myList.join(', ')}\nActive song: ${state.activeSeedId || 'none'}\nListening survey (reflection only): ${JSON.stringify(state.tasteSurvey || {})}\n\n## Runs\n`
  for (const r of state.runs) {
    md += `\n### ${r.run_id} ${r.method} seeds ${r.seeds.join(', ')} at ${r.created_at}\n`
    md += `Preferences: ${JSON.stringify(r.preferences)}\nFilter: ${JSON.stringify(r.candidate_filter)}\n`
    if (r.scoring_version) md += `Model: ${r.scoring_version}\nCalibration: ${r.calibration_version || 'unknown'}\n`
    for (const res of r.results) {
      const react = r.reactions[res.recording_mbid] || {}
      md += `- ${res.artist} – ${res.title} (${res.match_percentile}% ) like:${react.like||''} conn:${react.connection||''} note:${react.note||''}\n`
    }
    if (r.prediction) md += `Prediction: ${r.prediction}\n`
    if (r.notes) md += `Notes: ${r.notes}\n`
  }
  md += `\n## Text history\n`
  for (const t of state.textHistory) md += `- "${t.query}" at ${t.at} -> ${t.results.map((r:any)=>r.title).join(', ')}\n`
  md += `\n## Description judgments\n`
  for (const [k,v] of Object.entries(state.descriptionJudgments)) md += `- ${k}: ${v.fit} ${v.reason||''}\n`
  md += `\n## Session notes\n${state.notes}\n`
  return md
}
