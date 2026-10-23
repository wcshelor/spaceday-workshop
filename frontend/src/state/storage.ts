// Versioned local storage adapter
const KEY = 'spaceday-workshop:v1'
const VERSION = 2

export type WorkshopStage = 'choose' | 'listen' | 'reflect' | 'compare' | 'describe' | 'notes'

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
  // stage navigator (v2)
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
  activeStage: 'choose' as WorkshopStage,
  activeRunId: null,
  activeResultIndex: 0,
}

export function loadState(): AppState {
  try {
    const raw = localStorage.getItem(KEY)
    if (!raw) return {...defaultState}
    const parsed = JSON.parse(raw)
    if (parsed.version !== VERSION) {
      // migrate v1 -> v2: preserve everything, add stage defaults without clobbering runs
      if (parsed.version === 1) {
        return {
          ...defaultState,
          ...parsed,
          version: VERSION,
          activeStage: parsed.activeStage || 'choose',
          activeRunId: parsed.activeRunId || (parsed.runs?.[parsed.runs.length-1]?.run_id || null),
          activeResultIndex: typeof parsed.activeResultIndex === 'number' ? parsed.activeResultIndex : 0,
        }
      }
      return {...defaultState, ...parsed, version: VERSION}
    }
    return {...defaultState, ...parsed}
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
  let md = `# Workshop Session Export\n\nDataset: ${state.dataset_id || 'unknown'}\nMy List: ${state.myList.join(', ')}\n\n## Runs\n`
  for (const r of state.runs) {
    md += `\n### ${r.run_id} ${r.method} seeds ${r.seeds.join(', ')} at ${r.created_at}\n`
    md += `Preferences: ${JSON.stringify(r.preferences)}\nFilter: ${JSON.stringify(r.candidate_filter)}\n`
    if (r.scoring_version) md += `Model: ${r.scoring_version}\nCalibration: ${r.calibration_version || 'unknown'}\n`
    for (const res of r.results) {
      const react = r.reactions[res.recording_mbid] || {}
      md += `- ${res.artist} – ${res.title} (${res.match_percentile}% ) like:${react.like||''} conn:${react.connection||''} note:${react.note||''}\n`
    }
    if (r.notes) md += `Notes: ${r.notes}\n`
  }
  md += `\n## Text history\n`
  for (const t of state.textHistory) md += `- "${t.query}" at ${t.at} -> ${t.results.map((r:any)=>r.title).join(', ')}\n`
  md += `\n## Description judgments\n`
  for (const [k,v] of Object.entries(state.descriptionJudgments)) md += `- ${k}: ${v.fit} ${v.reason||''}\n`
  return md
}
