import { RunSnapshot, WorkshopStage } from '../state/storage'

export const STAGES: {id: WorkshopStage; label: string; sub: string}[] = [
  {id:'choose', label:'Your songs', sub:'Build a working set'},
  {id:'features', label:'Musical features', sub:'Compare measurements'},
  {id:'listeners', label:'Listener patterns', sub:'Learn from people'},
  {id:'clap', label:'CLAP sound', sub:'Learn from audio'},
  {id:'compare', label:'Compare', sub:'What did you hear?'},
  {id:'notes', label:'Notes & export', sub:'Keep your discoveries'},
]
export const METHODS = {
  'rhythm-v1': {name:'Rhythm & movement', intro:'An explicit formula compares measured tempo, onset rate and danceability. No listener preferences are learned.', predict:'Will a similar pace also feel like a similar groove?', listen:'Listen for pulse, accents and movement. Do the songs make you want to move in the same way?', explain:'This formula ranks songs by distance between their rhythm measurements. Similar numbers can still produce different musical experiences.', miss:'A similar tempo does not capture lyrics, cultural context or your personal memories.'},
  'texture-v1': {name:'Sound & texture', intro:'An explicit formula compares timbral and spectral measurements of the recordings.', predict:'Could two different genres share a similar sound texture?', listen:'Listen for brightness, density and the character of the instruments. What sounds alike to you?', explain:'This formula gives equal weight to timbral and spectral distances. It compares sound measurements without learning listener tastes.', miss:'Averaged measurements can miss song structure and the moments that matter to you.'},
  'collaborative-v1': {name:'Listener patterns', intro:'A trained model learns patterns from real listeners’ song loves. It uses listener feedback, without hearing the audio.', predict:'Could songs belong together in someone’s taste even when they sound different?', listen:'Can you imagine enjoying these songs together? Separate an audible resemblance from a shared taste or association.', explain:'This model learned a shared preference space from ListenBrainz song loves. Nearby songs have related learned listener patterns; that does not establish a specific shared audience or an audible resemblance.', miss:'The available listeners and songs shape the model. Limited feedback leaves some songs outside its coverage.'},
  'clap-v1': {name:'CLAP sound', intro:'A trained audio–language model represents recordings as embeddings. Here, we compare audio embeddings to find nearby songs.', predict:'What connection might a learned audio representation find beyond simple measurements?', listen:'Listen for voice, instrumentation, atmosphere or production. Can you name a connection—or does the result feel unrelated?', explain:'These recordings are nearby in CLAP’s learned audio embedding space. Proximity alone cannot tell us which audible quality caused the match.', miss:'The model’s training shapes its representation. Its similarity score cannot tell whether you will enjoy a song.'},
}
export type Method = keyof typeof METHODS
export function methodForStage(stage: WorkshopStage, featureMethod: 'rhythm-v1'|'texture-v1'): Method | null {
  return stage === 'features' ? featureMethod : stage === 'listeners' ? 'collaborative-v1' : stage === 'clap' ? 'clap-v1' : null
}
export function matchesSetup(run: RunSnapshot, seed: string | null, shared: boolean, dataset: string | null) {
  return !!seed && run.seeds.length === 1 && run.seeds[0] === seed &&
    JSON.stringify(run.candidate_filter || null) === JSON.stringify(shared ? {collaborative_only:true} : null) &&
    (!run.preferences || Object.keys(run.preferences).length === 0) && run.dataset_id === dataset
}
