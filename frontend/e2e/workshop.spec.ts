import { test, expect } from '@playwright/test';

async function mockApi(page) {
  await page.route('**/api/bootstrap', async route => {
    await route.fulfill({ json: {
      dataset_id: 'test123',
      scoring_version: 'scoring-v1',
      calibration_version: 'calibration-v1',
      language_status: 'disabled',
      supported_methods: ['clap-v1','rhythm-v1','texture-v1','collaborative-v1'],
      filter_vocab: {style_families:['pop_smooth','rock']},
      collaborative: {supported_count:2, supported_ids:['id1','id2']},
      score_help: 'How strong vs reference',
      year_bounds: {min:1960,max:2022},
      attribution_links: {}
    }});
  });
  await page.route('**/api/songs**', async route => {
    const url = new URL(route.request().url());
    const ids = url.searchParams.get('ids');
    if (ids) {
      const list = ids.split(',').map(id=> ({recording_mbid:id, title:`Title ${id}`, artist:`Artist ${id}`, year:2000, primary_style_family:'pop_smooth', is_editorial_anchor:false, style_families:[], tags:[], musicbrainz_url:'', youtube_search_url:'https://youtube.com', spotify_search_url:'https://spotify.com'}));
      await route.fulfill({ json: {items:list, total:list.length, offset:0, limit:10}});
      return;
    }
    await route.fulfill({ json: {
      items:[
        {recording_mbid:'id1', title:'Song One With Very Long Title That Should Wrap Correctly Without Overflow On Narrow Screens', artist:'Artist One With Long Name That Also Wraps', year:1990, primary_style_family:'pop_smooth', is_editorial_anchor:true, style_families:['pop_smooth'], tags:[], musicbrainz_url:'', youtube_search_url:'https://youtube.com', spotify_search_url:'https://spotify.com'},
        {recording_mbid:'id2', title:'Song Two', artist:'Artist Two', year:1991, primary_style_family:'rock', is_editorial_anchor:false, style_families:['rock'], tags:[], musicbrainz_url:'', youtube_search_url:'https://youtube.com', spotify_search_url:'https://spotify.com'},
        {recording_mbid:'id3', title:'Song Three', artist:'Artist Three', year:1992, primary_style_family:'pop_smooth', is_editorial_anchor:false, style_families:['pop_smooth'], tags:[], musicbrainz_url:'', youtube_search_url:'https://youtube.com', spotify_search_url:'https://spotify.com'},
      ], total:3, offset:0, limit:30
    }});
  });
  await page.route('**/api/recommendations', async route => {
    const body = JSON.parse(route.request().postData() || '{}');
    if (!body.seed_ids || body.seed_ids.length===0) {
      await route.fulfill({ status:422, json:{detail:'Choose at least one song'}});
      return;
    }
    const results = [1,2,3,4,5].map(n=> ({recording_mbid:`res${n}`, title:`Result ${n} With Long Title To Test Wrapping And Overflow Handling On Mobile`, artist:`Result Artist ${n} With Long Name`, year:2000+n, primary_style_family:'pop_smooth', match_percentile:90+n, base_score:0.5, youtube_search_url:'https://youtube.com', spotify_search_url:'https://spotify.com'}));
    await route.fulfill({ json: {run_id:`run_${body.seed_ids.join('_')}_${body.method}`, dataset_id:'test123', scoring_version:'scoring-v1', calibration_version:'calibration-v1', method: body.method, seed_ids_canonical: [...body.seed_ids].sort(), candidate_filter: body.candidate_filter||null, preferences_applied: body.preferences||null, results }});
  });
  await page.route('**/api/explanations', async route => {
    await route.fulfill({ json: {method:'clap-v1', base_score:0.5, per_seed_scores:{id1:0.6}, detail:{note:'test evidence, not invented'}, note:'test'}});
  });
  await page.route('**/api/descriptions', async route => {
    await route.fulfill({ json: {matches:[
      {id:'desc1', text:'warm acoustic guitar with soft vocals', category:'instruments', paraphrase_group:'g1'},
      {id:'desc2', text:'intimate close-miked vocals', category:'vocals', paraphrase_group:'g2'},
    ], note:'test'}});
  });
  await page.route('**/api/text-search', async route => {
    await route.fulfill({ status:503, json:{detail:'text search unavailable: encoder disabled'}});
  });
  await page.route('**/api/examples', async route => {
    await route.fulfill({ json: {version:'prompts-v1', items:[{id:'ex1', query:'warm acoustic guitar', category:'texture'}]}});
  });
  await page.route('**/health/live', async route => { await route.fulfill({ json: {status:'ok'}}); });
}

test.beforeEach(async ({ page }) => {
  await mockApi(page);
});

async function step(page,label) {
  await page.getByRole('button',{name:label,exact:true}).click();
}
async function choose(page) {
  await page.goto('/');
  await page.getByRole('button',{name:/^Add Song One/}).click();
  await page.getByRole('button',{name:/^Add Song Two/}).click();
}
async function generate(page) {
  await page.getByRole('button',{name:'Find 5 recommendations',exact:true}).click();
  await expect(page.getByRole('heading',{name:/Result 1 With Long Title/})).toBeVisible();
}
async function noOverflow(page) {
  expect(await page.evaluate(()=>document.documentElement.scrollWidth<=document.documentElement.clientWidth+1)).toBeTruthy();
}

test('same seed and candidate pool across the three steps, with separate reactions',async({page})=>{
  const requests:any[]=[];
  page.on('request',r=>{if(r.url().endsWith('/api/recommendations')) requests.push(r.postDataJSON());});
  await choose(page);
  await page.getByRole('button',{name:'Next: Musical features'}).click();
  await generate(page);
  await page.getByLabel(/Enjoyment for/).selectOption('like');
  await page.getByRole('button',{name:'Reveal how this system matched it'}).click();
  await expect(page.getByRole('heading',{name:'Why this recommendation?'})).toBeVisible();
  await noOverflow(page);
  await page.getByRole('button',{name:'Next: Listener patterns'}).click();await generate(page);
  await expect(page.getByLabel(/Enjoyment for/)).toHaveValue('');
  await page.getByRole('button',{name:'Next: CLAP sound'}).click();await generate(page);
  expect(requests.map(r=>r.method)).toEqual(['rhythm-v1','collaborative-v1','clap-v1']);
  for(const r of requests) {expect(r.seed_ids).toEqual(['id1']);expect(r.candidate_filter).toEqual({collaborative_only:true});expect(r.preferences).toBeUndefined();}
  await step(page,'Musical features');
  await expect(page.getByLabel(/Enjoyment for/)).toHaveValue('like');
  await step(page,'Compare');
  await expect(page.getByText(/Result 1 With Long Title/)).toHaveCount(3);
  await noOverflow(page);
});

test('active seed changes and refresh preserve experiments without showing stale recommendations',async({page})=>{
  await choose(page);await step(page,'Musical features');await generate(page);
  await page.getByLabel(/Listening note for/).fill('A similar pulse');
  await page.getByLabel('Active starting song').selectOption('id2');
  await expect(page.getByRole('heading',{name:/Result 1/})).toHaveCount(0);
  await generate(page);
  await page.getByLabel('Active starting song').selectOption('id1');
  await expect(page.getByLabel(/Listening note for/)).toHaveValue('A similar pulse');
  await expect.poll(()=>page.evaluate(()=>JSON.parse(localStorage.getItem('spaceday-workshop:v1') || '{}').activeSeedId)).toBe('id1');
  await page.reload();
  await expect(page.getByLabel(/Listening note for/)).toHaveValue('A similar pulse');
});

test('unsupported songs are explained; selection checkmark removes and changes active song',async({page})=>{
  await choose(page);
  await page.getByRole('button',{name:/^Remove Song One.*by Artist One/}).click();
  await expect(page.getByLabel('Active starting song')).toHaveValue('id2');
  await page.getByRole('button',{name:/^Add Song Three/}).click();
  await page.getByLabel('Active starting song').selectOption('id3');
  await step(page,'Listener patterns');
  await expect(page.getByRole('button',{name:'Find 5 recommendations'})).toBeDisabled();
  await expect(page.getByText(/We won’t substitute/)).toBeVisible();
  await step(page,'CLAP sound');await generate(page);await noOverflow(page);
});

test('responsive layouts, listening survey, keyboard carousel and optional CLAP activity',async({page},testInfo)=>{
  await choose(page);
  await page.getByLabel('What draws you into a song?').selectOption('Rhythm');
  const initialViewport=page.viewportSize();
  for(const width of [320,768,1440]) { await page.setViewportSize({width,height:844}); await noOverflow(page); }
  await page.setViewportSize(initialViewport!);
  await noOverflow(page);
  await page.screenshot({path:testInfo.outputPath('choose.png'),fullPage:true});
  await step(page,'Musical features');await generate(page);
  await expect(page.getByText(/Your lens:/)).toContainText('rhythm');
  await page.getByLabel('Recommendations carousel').focus();await page.keyboard.press('ArrowRight');
  await expect(page.getByText('2 / 5',{exact:true})).toBeVisible();
  await page.keyboard.press('ArrowLeft');await expect(page.getByText('1 / 5',{exact:true})).toBeVisible();
  await noOverflow(page);
  await page.screenshot({path:testInfo.outputPath('features.png'),fullPage:true});
  await step(page,'CLAP sound');
  await page.getByText('Optional: explore CLAP with words',{exact:true}).click();
  await expect(page.getByRole('button',{name:'fits',exact:true}).first()).toBeVisible();
  await page.getByRole('button',{name:'fits',exact:true}).first().click();
  await page.getByLabel('Your description',{exact:true}).fill('a new sound');
  await page.getByRole('button',{name:'Search with your description',exact:true}).click();
  await expect(page.getByText(/Live search isn’t available/)).toBeVisible();
  await noOverflow(page);
  await step(page,'Notes & export');
  const download=page.waitForEvent('download');
  await page.getByRole('button',{name:'Download Markdown'}).click();
  expect((await download).suggestedFilename()).toBe('workshop-export.md');
});

test('real backend accepts one supported seed for all four formulas',async({page})=>{
  await page.unrouteAll({behavior:'wait'});
  const b=await page.request.get('/api/bootstrap');expect(b.ok()).toBeTruthy();
  const bootstrap=await b.json();const seed=bootstrap.collaborative.supported_ids[0];
  for(const method of ['rhythm-v1','texture-v1','collaborative-v1','clap-v1']) {
    const r=await page.request.post('/api/recommendations',{data:{seed_ids:[seed],method,limit:5,candidate_filter:{collaborative_only:true}}});
    expect(r.ok()).toBeTruthy();const data=await r.json();expect(data.results).toHaveLength(5);
    const e=await page.request.post('/api/explanations',{data:{seed_ids:[seed],method,result_id:data.results[0].recording_mbid,candidate_filter:{collaborative_only:true}}});
    expect(e.ok()).toBeTruthy();
  }
});
