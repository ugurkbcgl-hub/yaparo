/* Owned percentage controls for the existing authored plan. No eligibility inference or I/O. */
(function (root, factory) {
  'use strict';
  if (typeof module !== 'undefined' && module.exports && !root.YaparoDecision) require('./engine.js');
  const api = factory(root.YaparoDecision);
  if (typeof module !== 'undefined' && module.exports) module.exports = api;
  root.YaparoPlanSummary = api;
})(typeof window !== 'undefined' ? window : globalThis, function (E) {
  'use strict';
  const version = 'yaparo-plan-shares-v1';
  const integer = n => Number.isSafeInteger(n) && n >= 0;
  const sum = rows => rows.reduce((total, row) => total + row.amount, 0);
  function check(plan) {
    if (!E || typeof E.manual !== 'function' || !plan || !Array.isArray(plan.rows) ||
        plan.blocked !== false || plan.externalQuery !== false || plan.publishable !== false ||
        !['demo_illustrative','authored_simulation_NOT_market_data'].includes(plan.quality) ||
        !integer(plan.total) || plan.total > 100000000 || !integer(plan.businessCap) ||
        plan.businessCap > plan.total || !integer(plan.allocated) || !integer(plan.unallocated)) {
      throw new Error('Geçerli ve güncel bir yerel kanal planı gerekli.');
    }
    const ids = new Set();
    for (const row of plan.rows) {
      if (!row || typeof row.channel?.id !== 'string' || !row.channel.id || ids.has(row.channel.id) || !integer(row.amount)) {
        throw new Error('Kanal kayıtları doğrulanamadı.');
      }
      ids.add(row.channel.id);
      if (row.eligible === true && (row.owned || !integer(row.useful) || row.useful < 1 || !integer(row.cap) || row.cap < row.useful || row.cap > plan.businessCap)) {
        throw new Error('Kanal minimumu veya tavanı doğrulanamadı.');
      }
      if (row.amount && (row.eligible !== true || row.owned || row.amount < row.useful || row.amount > row.cap)) {
        throw new Error('Seçili kanalın tutarı sınırları karşılamıyor.');
      }
    }
    if (sum(plan.rows) !== plan.allocated || plan.allocated > plan.businessCap || plan.allocated + plan.unallocated !== plan.total) {
      throw new Error('Plan toplamları tutarlı değil.');
    }
  }
  function bounds(plan, id) {
    check(plan);
    const target = plan.rows.find(row => row.channel.id === id);
    if (!target || target.eligible !== true || target.owned) throw new Error('Bu kanal mevcut koşullarda bütçe alamıyor.');
    const others = plan.rows.filter(row => row !== target && row.amount > 0);
    const otherMin = others.reduce((total, row) => total + row.useful, 0);
    const maximum = Math.min(target.cap, plan.businessCap - otherMin);
    return {target, others, minimum:target.useful, maximum:Math.max(0, maximum)};
  }
  function limits(plan, id) {
    const b = bounds(plan, id), total = plan.total;
    return {minimum:b.minimum, maximum:b.maximum, minPercent:total ? b.minimum / total * 100 : 0,
      maxPercent:total ? b.maximum / total * 100 : 0, canAdd:b.maximum >= b.minimum};
  }
  function redistribute(plan, id, percent) {
    if (!Number.isFinite(percent) || percent < 0 || percent > 100) throw new Error('Kanal payı 0 ile 100 arasında olmalı.');
    const {target,others,minimum,maximum} = bounds(plan, id);
    if (percent > 0 && maximum < minimum) throw new Error('Bu kanalı eklemek için başka bir kanalı kaldır veya bütçeyi güncelle.');
    const requested = Math.round(plan.total * percent / 100);
    const desired = percent === 0 ? 0 : Math.max(minimum, Math.min(maximum, requested));
    // Keep the previous spend envelope where possible. Spare budget is used only
    // when the explicit new target plus other selected minima requires it.
    const otherMin = others.reduce((total, row) => total + row.useful, 0);
    const envelope = Math.min(plan.businessCap, Math.max(plan.allocated, desired + otherMin));
    const otherBudget = Math.min(envelope - desired,others.reduce((total,row)=>total+row.cap,0));
    const bounded = (row, scale) => Math.max(row.useful,Math.min(row.cap,Math.floor(row.amount*scale)));
    // Find the common proportional scale, clamped at each existing minimum/cap.
    // In particular, setting an unchanged share leaves the other shares unchanged.
    let low=0, high=others.length?Math.max(...others.map(row=>row.cap/row.amount))+1:0;
    for(let i=0;i<80;i++){
      const scale=(low+high)/2, total=others.reduce((s,row)=>s+bounded(row,scale),0);
      if(total<=otherBudget)low=scale;else high=scale;
    }
    const allocations = new Map(others.map(row=>[row.channel.id,bounded(row,low)]));
    let remaining=otherBudget-others.reduce((total,row)=>total+allocations.get(row.channel.id),0);
    const order=[...others].sort((a,b)=>a.channel.id.localeCompare(b.channel.id));
    while(remaining>0){
      const open=order.filter(row=>allocations.get(row.channel.id)<row.cap);
      if(!open.length)break;
      for(const row of open){if(!remaining)break;allocations.set(row.channel.id,allocations.get(row.channel.id)+1);remaining--;}
    }
    allocations.set(id,desired);
    // Validate all mutations on a separate trial. Reductions go first so the
    // established engine remains the authority for every amount and shared cap.
    const trial = {...plan,rows:plan.rows.map(row => ({...row}))};
    const changes = trial.rows.filter(row => allocations.has(row.channel.id) && allocations.get(row.channel.id) !== row.amount);
    for (const row of changes.filter(row => allocations.get(row.channel.id) < row.amount)) E.manual(trial,row.channel.id,allocations.get(row.channel.id));
    for (const row of changes.filter(row => allocations.get(row.channel.id) > row.amount)) E.manual(trial,row.channel.id,allocations.get(row.channel.id));
    check(trial);
    for (const row of plan.rows) row.amount = trial.rows.find(r => r.channel.id === row.channel.id).amount;
    plan.allocated = trial.allocated; plan.unallocated = trial.unallocated; plan.manual = true;
    return {requestedPercent:percent,appliedPercent:plan.total ? desired / plan.total * 100 : 0,amount:desired,
      allocated:plan.allocated,unallocated:plan.unallocated,limited:desired !== requested};
  }
  return Object.freeze({version,limits,redistribute,remove:(plan,id)=>redistribute(plan,id,0)});
});
