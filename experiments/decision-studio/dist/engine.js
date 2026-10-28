/* Owned local research adapter. No provider, account, storage or publishing access. */
(function (root) {
  'use strict';
  const cents = n => Math.round(n * 100);
  const finite = (n, lo, hi) => Number.isFinite(n) && n >= lo && n <= hi;
  const reasonText = {
    policy_review: 'Belge / politika incelemesi bekliyor', objective_not_supported: 'Seçilen optimizasyon hedefi desteklenmiyor',
    account_not_ready: 'Örnek hesap / satın alma erişimi hazır değil', asset_not_ready: 'Gerekli kreatif veya katalog eksik',
    forecast_missing: 'Bu koşullara bağlı güncel tahmin yok', below_platform_minimum: 'Toplam bütçe teknik minimumun altında',
    cap_below_useful_minimum: 'Faydalı tavan anlamlı test minimumundan düşük', score_below_threshold: 'Uzman uygunluk puanı eşik altında',
    owned_action: 'Ücretli medya dışında destekleyici aksiyon', portfolio_limit: 'Bu bütçede seçilen kanallara öncelik verildi',
    insufficient_budget: 'Kalan bütçe anlamlı bir testi karşılamıyor', geo_unverified: 'Bu ürünün seçilen yarıçapı uygulaması doğrulanmadı',
    audience_unverified: 'Asgari kitle doğrulaması eksik', stale_forecast: 'Örnek tahmin tarihinden farklı plan: yeniden tahmin gerekli',
    minimum_unverified: 'Teknik minimum / hesap para birimi doğrulanmadı'
  };
  function policy(input) {
    return input.communication === 'fundraising' || input.action === 'donate' || input.business === 'nonprofit_fundraising' ||
      ['fundraising','health','finance','political','children','alcohol_tobacco','gambling'].includes(input.risk) ||
      ['health_medical','finance_insurance','public_political','real_estate','recruitment','nonprofit_social_cause'].includes(input.sector) ||
      ['sale_promotion','public_issue','recruitment','reputation'].includes(input.communication);
  }
  function evaluate(input, data, simulation=null, liveFx=null) {
    if (!finite(input.budget,0,1000000) || !Number.isInteger(input.days) || !finite(input.days,1,365) ||
        !finite(input.value,0,100000000) || !finite(input.margin,0,100) || !finite(input.cpa,0,10000000) ||
        !Number.isInteger(input.capacity) || !finite(input.capacity,0,1000000) ||
        (input.geo === 'radius_local' && (!Number.isInteger(input.radius) || !finite(input.radius,1,800)))) {
      throw new Error('Bütçe, süre, yarıçap ve ekonomi alanlarını kontrol et.');
    }
    const total = cents(input.budget), blocked = policy(input);
    const interactive = input.fixture === 'interactive' && simulation?.kind === 'authored_simulation' && simulation.signature === JSON.stringify(input);
    // Only SC01 has forecast fixtures. Never rebind its observations to other audiences/regions/dates.
    const bound = input.fixture === 'demo' && input.goal === 'store_visits' && input.business === 'local_retail' &&
      input.audience === 'local_nearby' && input.sector === 'fashion_beauty_lifestyle' && input.geo === 'district_city' &&
      input.region.trim().toLocaleLowerCase('tr-TR') === 'istanbul, kadıköy' && input.days === 7 &&
      input.measurement === 'basic_utm' && input.start === '2026-10-27';
    const contextBound = bound || interactive;
    const usableFx = interactive && liveFx?.snapshot?.quality==='official_public' && ['tcmb','ecb'].includes(liveFx.snapshot.source) &&
      liveFx.snapshot.payload?.base==='USD' && liveFx.snapshot.payload?.quote==='TRY' &&
      Number.isFinite(liveFx.rate) && liveFx.rate>0 && Date.parse(liveFx.snapshot.expires_at)>Date.now();
    const exchangeRate = usableFx ? liveFx.rate : 49.7627;
    const profitCPA = Math.min(input.cpa, input.value * input.margin / 100);
    // Capacity and profitability are a SHARED portfolio cap, not counted once per channel.
    const businessCap = Math.min(total, Math.floor(input.capacity * input.days * profitCPA * 100));
    const rows = data.channels.map(channel => {
      const f = (interactive ? simulation.forecasts : data.forecasts).find(x => x.channelId === channel.id);
      const owned = channel.tier === 'non_paid_recommendation';
      const fx = channel.currency === 'USD' ? exchangeRate : 1;
      const platform = channel.id === 'spotify' ? null : Math.ceil(Math.max(channel.dailyMinimum * input.days,channel.lifetimeMinimum) * fx * 100);
      const reasons = [];
      if (owned) reasons.push('owned_action');
      if ((blocked || !f?.policyPass) && !owned) reasons.push('policy_review');
      if (!channel.objectives.includes(input.goal) && !owned) reasons.push('objective_not_supported');
      if (!f?.accountReady && !owned) reasons.push('account_not_ready');
      // Checking an asset box does not qualify a provider asset or invent a fixture.
      const assetReady = !!f?.assetReady && (!channel.assets.some(a => /^(vertical_video|horizontal_or_vertical_video|audio_or_video|vertical_video_or_ar)$/.test(a)) || input.video);
      if (!assetReady && !owned) reasons.push('asset_not_ready');
      if (channel.id === 'google_pmax_shopping' && (!input.catalog || !input.tracking)) reasons.push('asset_not_ready');
      if ((!contextBound || !f?.hasForecast) && !owned) reasons.push('forecast_missing');
      if (input.geo === 'radius_local' && !(interactive && f?.radiusSupported) && !owned) reasons.push('geo_unverified');
      if (channel.minimumAudience > 0 && !(interactive && f?.uniqueReach >= channel.minimumAudience) && !owned) reasons.push('audience_unverified');
      if (platform !== null && platform > total && !owned) reasons.push('below_platform_minimum');
      if (platform === null && !owned) reasons.push('minimum_unverified');
      let useful = 0;
      if (!owned && f) {
        const relevant = ['awareness','reach','video_views','engagement'].includes(input.goal) ? f.cpm * 10 :
          input.goal === 'traffic' ? f.cpc * 40 : Math.max(f.cpa * 8,f.cpc * 40,f.cpm * 10);
        useful = Math.ceil(Math.max((platform || 0)/100,f.baseUsefulMinimum,relevant) * 100);
      }
      const demand = contextBound && f?.hasForecast ? cents(f.potentialBudget) : null;
      const cap = owned ? 0 : demand === null ? null : Math.min(total,demand,businessCap);
      const budgetScore = platform !== null && total < platform ? 0 : total < useful ? 1 : total < useful * 1.5 ? 3 : 5;
      const dimensions = { objective:input.goal,business_model:input.business,audience:input.audience,sector:input.sector,
        geo:input.geo,creative:'static_image',measurement:input.measurement };
      const breakdown = data.weights.map(w => {
        const found = data.scoreRules.find(r => r.channelId === channel.id && r.dimension === w.dimension && r.value === dimensions[w.dimension]);
        const score = w.dimension === 'budget' ? budgetScore : (found?.score ?? 0);
        return {dimension:w.dimension,weight:w.weight,score,points:w.weight * score / 5};
      });
      const score = Math.round(breakdown.reduce((s,x) => s+x.points,0)*100)/100;
      if (cap !== null && cap < useful && !owned) reasons.push('cap_below_useful_minimum');
      if (score < 60 && !owned) reasons.push('score_below_threshold');
      return {channel,f,owned,platform,useful,cap,score,breakdown,reasons:[...new Set(reasons)],eligible:!owned && !reasons.length,amount:0};
    });
    const eligible = rows.filter(r => r.eligible).sort((a,b) => b.score-a.score || a.channel.id.localeCompare(b.channel.id));
    const mins = eligible.map(r => r.useful).sort((a,b)=>a-b);
    const median = mins.length ? (mins[Math.floor((mins.length-1)/2)]+mins[Math.floor(mins.length/2)])/2 : 0;
    let limit = median ? Math.max(1,Math.min(4,Math.floor(total/(median*1.5)))) : 0;
    // Reserve a demand-capture role only if both minima fit the shared cap.
    const capture = eligible.find(r => r.channel.type === 'paid_search');
    if (eligible.length > 1 && capture && eligible[0] !== capture && eligible[0].useful + capture.useful <= businessCap) limit = Math.max(limit,2);
    const selected = [];
    let remaining = businessCap;
    for (const row of eligible) {
      if (selected.length >= limit) {row.reasons.push('portfolio_limit');continue;}
      if (row.useful > remaining) {row.reasons.push('insufficient_budget');continue;}
      row.amount = row.useful; remaining -= row.amount; selected.push(row);
    }
    // Integer kuruş water filling, always capped. A deterministic final kuruş prevents drift.
    while (remaining > 0) {
      const open = selected.filter(r => r.amount < r.cap);
      if (!open.length) break;
      const weights = open.reduce((s,r) => s+r.score*r.score,0);
      const available = remaining;
      let assigned = 0;
      for (const r of open) {
        const add = Math.min(r.cap-r.amount,Math.floor(available*(r.score*r.score/weights)));
        r.amount += add; assigned += add;
      }
      if (!assigned) {open[0].amount++;assigned=1;}
      remaining -= assigned;
    }
    const allocated = rows.reduce((s,r)=>s+r.amount,0);
    return {version:data.version,createdAt:new Date().toISOString(),input:{...input},bound,interactive,blocked,total,businessCap,rows,
      allocated,unallocated:total-allocated,externalQuery:false,model:null,quality:interactive?'authored_simulation_NOT_market_data':'demo_illustrative',simulationVersion:interactive?simulation.version:null,
      fx:{rate:exchangeRate,source:usableFx?liveFx.snapshot.source:'research_example',source_as_of:usableFx?liveFx.snapshot.source_as_of:'2026-10-26',snapshot_id:usableFx?liveFx.snapshot.id:null,expires_at:usableFx?liveFx.snapshot.expires_at:null,indicative_only:true},publishable:false};
  }
  function manual(plan,id,amount) {
    const row = plan.rows.find(r=>r.channel.id===id);
    if (!row || !row.eligible || !Number.isSafeInteger(amount) || amount<0 || (amount>0 && (amount<row.useful || amount>row.cap)))
      throw new Error('Tutar, anlamlı test minimumu ile faydalı tavan arasında olmalı; kanalı kaldırmak için 0 yaz.');
    const other = plan.rows.reduce((s,r)=>s+(r===row?0:r.amount),0);
    if (other+amount>plan.businessCap) throw new Error('Toplam bütçe veya ortak işletme tavanı aşılır. Önce başka bir payı azalt.');
    row.amount=amount;plan.allocated=other+amount;plan.unallocated=plan.total-plan.allocated;plan.manual=true;
  }
  root.YaparoDecision = {evaluate,manual,reasonText};
})(typeof window === 'undefined' ? globalThis : window);
