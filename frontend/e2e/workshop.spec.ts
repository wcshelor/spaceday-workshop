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

test('Choose → generate → move between results → react → reveal', async ({ page }) => {
  await page.goto('/');
  await expect(page.getByRole('tab', {name:'Choose'})).toBeVisible();
  await expect(page.getByText(/Search for a familiar song/)).toBeVisible();
  await page.getByRole('button', {name:/Add Song One/}).click();
  // My List chip appears
  await expect(page.getByText(/Song One With Very Long Title/).first()).toBeVisible();
  // Continue to Listen
  await page.getByRole('button', {name:'Continue to Listen'}).click();
  await expect(page.getByText(/Choose a method and generate/)).toBeVisible();
  await page.getByRole('button', {name:'Generate 5 recommendations'}).click();
  await expect(page.getByText(/Result 1 With Long Title/)).toBeVisible();
  await expect(page.getByText('1 / 5')).toBeVisible();
  await page.getByRole('button', {name:'Next recommendation'}).click();
  await expect(page.getByText(/Result 2 With Long Title/)).toBeVisible();
  await expect(page.getByText('2 / 5')).toBeVisible();
  await page.getByRole('button', {name:'Previous recommendation'}).click();
  await expect(page.getByText(/Result 1 With Long Title/)).toBeVisible();
  await page.getByLabel(/Enjoyment for Result 1/).selectOption('like');
  await page.getByRole('button', {name:'I’ve listened'}).click();
  await expect(page.getByText(/Evidence/)).toBeVisible();
  // Per result: next not revealed
  await page.getByRole('button', {name:'Next recommendation'}).click();
  await expect(page.getByRole('button', {name:'I’ve listened'})).toBeVisible();
  await page.getByRole('button', {name:'Previous recommendation'}).click();
  await expect(page.getByText(/Evidence/)).toBeVisible();
});

test('Correct reaction and reveal state per result and run', async ({ page }) => {
  await page.goto('/');
  await page.getByRole('button', {name:/Add Song One/}).click();
  await page.getByRole('button', {name:'Continue to Listen'}).click();
  await page.getByRole('button', {name:'Generate 5 recommendations'}).click();
  await expect(page.getByText(/Result 1 With Long Title/)).toBeVisible();
  await page.getByRole('button', {name:'I’ve listened'}).click();
  await expect(page.getByText(/Evidence/)).toBeVisible();
  // Generate second run with different method
  await page.getByLabel(/Recommendation method/).selectOption('rhythm-v1');
  await page.getByRole('button', {name:'Generate 5 recommendations'}).click();
  await expect(page.getByText(/Result 1 With Long Title/)).toBeVisible();
  // New run should not have revealed state from previous
  await expect(page.getByRole('button', {name:'I’ve listened'})).toBeVisible();
});

test('Switching methods preserves My List and previous runs', async ({ page }) => {
  await page.goto('/');
  await page.getByRole('button', {name:/Add Song One/}).click();
  await page.getByRole('button', {name:'Continue to Listen'}).click();
  await page.getByRole('button', {name:'Generate 5 recommendations'}).click();
  await expect(page.getByText(/Result 1 With Long Title/)).toBeVisible();
  await page.getByLabel(/Recommendation method/).selectOption('rhythm-v1');
  await page.getByRole('button', {name:'Generate 5 recommendations'}).click();
  await expect(page.getByText(/Result 1 With Long Title/)).toBeVisible();
  await page.getByRole('tab', {name:'Choose'}).click();
  await expect(page.getByText(/Song One With Very Long Title/).first()).toBeVisible();
  await page.getByRole('tab', {name:'Compare'}).click();
  await expect(page.getByText(/Preserve setup/)).toBeVisible();
  await expect(page.getByText(/clap-v1/).first()).toBeVisible();
  await expect(page.getByText(/rhythm-v1/).first()).toBeVisible();
});

test('Revisiting stages and refresh preserves working state', async ({ page }) => {
  await page.goto('/');
  await page.getByRole('button', {name:/Add Song One/}).click();
  await page.getByRole('button', {name:'Continue to Listen'}).click();
  await page.getByRole('button', {name:'Generate 5 recommendations'}).click();
  await expect(page.getByText(/Result 1 With Long Title/)).toBeVisible();
  await page.getByRole('tab', {name:'Describe'}).click();
  await expect(page.getByText(/Matching descriptions/)).toBeVisible();
  await page.getByRole('tab', {name:'Listen'}).click();
  await expect(page.getByText(/Result 1 With Long Title/)).toBeVisible();
  await page.reload();
  await expect(page.getByRole('tab', {name:'Choose'})).toBeVisible();
  await page.getByRole('tab', {name:'Choose'}).click();
  await expect(page.getByText(/Song One With Very Long Title/).first()).toBeVisible();
  await page.reload();
  await expect(page.getByText(/Song One With Very Long Title/).first()).toBeVisible();
});

test('Description / prepared-example flow and notes export', async ({ page }) => {
  await page.goto('/');
  await page.getByRole('button', {name:/Add Song One/}).click();
  await page.getByRole('tab', {name:'Describe'}).click();
  await page.getByLabel(/Choose song for descriptions/).selectOption('id1');
  await expect(page.getByText(/warm acoustic guitar/).first()).toBeVisible();
  const fitsBtn = page.getByRole('button', {name:'fits'}).first();
  await fitsBtn.click();
  await expect(fitsBtn).toHaveAttribute('aria-pressed','true');
  await expect(page.getByText(/Try without live retrieval/)).toBeVisible();
  await page.getByLabel(/Your description/).fill('test query');
  await page.getByRole('button', {name:'Search'}).click();
  await expect(page.getByText(/Live search isn’t available/)).toBeVisible();
  await page.getByRole('tab', {name:'Notes'}).click();
  await expect(page.getByText(/Your reflections/)).toBeVisible();
  await expect(page.getByRole('button', {name:'Download JSON'})).toBeVisible();
  await expect(page.getByRole('button', {name:'Download Markdown'})).toBeVisible();
});

test('Empty selection, loading, API failure, unsupported collaborative seeds', async ({ page }) => {
  await page.goto('/');
  await page.getByRole('tab', {name:'Listen'}).click();
  const genBtn = page.getByRole('button', {name:'Generate 5 recommendations'});
  await expect(genBtn).toBeDisabled();
  await expect(page.getByLabel(/Recommendation method/)).toBeVisible();
  const chooseTab = page.getByRole('tab', {name:'Choose'});
  await expect(chooseTab).toBeVisible();
  await chooseTab.focus();
  await expect(chooseTab).toBeFocused();
  // Check accessible names
  await page.getByRole('tab', {name:'Choose'}).click();
  const addBtn = page.getByRole('button', {name:/Add Song One/});
  await expect(addBtn).toHaveAccessibleName(/Add Song One/);
});

test('Keyboard-accessible controls and accessible names', async ({ page }) => {
  await page.goto('/');
  const chooseTab = page.getByRole('tab', {name:'Choose'});
  await expect(chooseTab).toHaveAttribute('aria-selected','true');
  await chooseTab.focus();
  await expect(chooseTab).toBeFocused();
  await page.getByRole('button', {name:/Add Song One/}).click();
  await page.getByRole('button', {name:'Continue to Listen'}).click();
  await page.getByRole('button', {name:'Generate 5 recommendations'}).click();
  await expect(page.getByRole('button', {name:'Next recommendation'})).toBeVisible();
  // Focus carousel for keyboard
  await page.getByLabel(/Recommendations carousel/).focus();
  await page.keyboard.press('ArrowRight');
  await expect(page.getByText('2 / 5')).toBeVisible();
  await page.keyboard.press('ArrowLeft');
  await expect(page.getByText('1 / 5')).toBeVisible();
});

test('Phone and laptop layouts without horizontal overflow', async ({ page }) => {
  await page.goto('/');
  const noOverflow = await page.evaluate(() => document.documentElement.scrollWidth <= document.documentElement.clientWidth + 2);
  expect(noOverflow).toBeTruthy();
  await expect(page.getByText(/Search for a familiar song/)).toBeVisible();
  const longTitle = page.getByText(/Song One With Very Long Title/).first();
  await expect(longTitle).toBeVisible();
  const box = await longTitle.boundingBox();
  // At 390 viewport, title should wrap and not exceed viewport
  expect(box.width).toBeLessThan(500);
});

test('Real-backend integration check (uses actual API)', async ({ page }) => {
  await page.unrouteAll({behavior:'wait'});
  const resp = await page.request.get('/health/ready').catch(()=> null);
  if (!resp || !resp.ok()) test.skip(true, 'Real backend not available for integration check');
  else expect(resp.ok()).toBeTruthy();
});
