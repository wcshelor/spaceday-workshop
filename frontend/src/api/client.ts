export type Song = {
  recording_mbid: string
  title: string
  artist: string
  year: number | null
  primary_style_family: string | null
  style_families: string[]
  familiarity_band: string
  is_editorial_anchor: boolean
  tags: string[]
  musicbrainz_url: string
  youtube_search_url: string
  spotify_search_url: string
}

export async function getBootstrap() {
  const r = await fetch('/api/bootstrap')
  if (!r.ok) throw new Error('bootstrap failed')
  return r.json()
}
export async function searchSongs(params: Record<string,string|number>) {
  const qs = new URLSearchParams(params as any).toString()
  const r = await fetch(`/api/songs?${qs}`)
  if (!r.ok) throw new Error('songs failed')
  return r.json()
}
export async function postRecommendations(body: any) {
  const r = await fetch('/api/recommendations', {method:'POST', headers:{'Content-Type':'application/json'}, body: JSON.stringify(body)})
  if (!r.ok) {
    const e = await r.json().catch(()=>({detail: r.statusText}))
    throw new Error(e.detail || 'recommendation failed')
  }
  return r.json()
}
export async function postExplanations(body: any) {
  const r = await fetch('/api/explanations', {method:'POST', headers:{'Content-Type':'application/json'}, body: JSON.stringify(body)})
  if (!r.ok) throw new Error('explanation failed')
  return r.json()
}
export async function postDescriptions(body: any) {
  const r = await fetch('/api/descriptions', {method:'POST', headers:{'Content-Type':'application/json'}, body: JSON.stringify(body)})
  if (!r.ok) throw new Error('descriptions failed')
  return r.json()
}
export async function postTextSearch(body: any) {
  const r = await fetch('/api/text-search', {method:'POST', headers:{'Content-Type':'application/json'}, body: JSON.stringify(body)})
  if (!r.ok) {
    const e = await r.json().catch(()=>({detail: r.statusText}))
    throw new Error(e.detail || 'text search failed')
  }
  return r.json()
}
export async function getExamples() {
  const r = await fetch('/api/examples')
  if (!r.ok) throw new Error('examples failed')
  return r.json()
}
