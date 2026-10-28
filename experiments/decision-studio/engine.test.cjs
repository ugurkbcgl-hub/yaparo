const assert = require('node:assert/strict');
global.window = global;
require('./dist/data.js');require('./dist/engine.js');
const D=YaparoResearch,E=YaparoDecision;
const base={budget:3000,days:7,value:500,margin:40,cpa:100,capacity:20,goal:'store_visits',business:'local_retail',audience:'local_nearby',sector:'fashion_beauty_lifestyle',geo:'district_city',region:'İstanbul, Kadıköy',start:'2026-10-27',measurement:'basic_utm',fixture:'demo',communication:'product_service_intro',risk:'normal'};
const run=patch=>E.evaluate({...base,...patch},D);
const p=run({});
assert.equal(p.allocated,300000);assert.equal(p.rows.find(r=>r.channel.id==='meta_social').amount,180000);
assert.equal(p.rows.find(r=>r.channel.id==='google_search_maps').amount,120000);
for(const row of p.rows){const cached=D.demoCachedResults.find(r=>r.channelId===row.channel.id);assert.equal(row.score,Number(cached.score));}
assert.equal(p.rows.find(r=>r.channel.id==='tiktok').amount,0);
assert.equal(p.rows.find(r=>r.channel.id==='tiktok').platform,696678);
assert.equal(run({budget:10000}).unallocated,680000);
assert.equal(run({capacity:1}).allocated,0);
assert.equal(run({capacity:0}).allocated,0);
for(const patch of [{fixture:'unknown'},{region:'Ankara'},{start:'2026-10-28'},{days:8},{goal:'awareness'},{audience:'b2b_decision_makers'},{business:'b2b_leadgen'},{geo:'radius_local',radius:10},{measurement:'platform_pixel'}])assert.equal(run(patch).allocated,0,JSON.stringify(patch));
for(const patch of [{communication:'fundraising'},{risk:'health'},{sector:'finance_insurance'},{communication:'sale_promotion'},{communication:'public_issue'}])assert.equal(run(patch).allocated,0);
for(const patch of [{budget:NaN},{budget:-1},{days:2.5},{capacity:-2},{margin:101},{geo:'radius_local',radius:0}])assert.throws(()=>run(patch));
E.manual(p,'meta_social',100000);assert.equal(p.unallocated,80000);
assert.throws(()=>E.manual(p,'meta_social',99999));assert.throws(()=>E.manual(p,'tiktok',10000));
assert.throws(()=>E.manual(p,'meta_social',200001));assert.throws(()=>E.manual(p,'meta_social',200000));
assert.equal(run({}).rows.find(r=>r.channel.id==='meta_social').amount,180000);
for(let budget=0;budget<=12000;budget+=137){const q=run({budget});assert.equal(q.allocated+q.unallocated,q.total);assert(q.allocated<=q.businessCap);for(const r of q.rows){assert(Number.isSafeInteger(r.amount));assert(r.amount===0||(r.amount>=r.useful&&r.amount<=r.cap));if(r.owned)assert.equal(r.amount,0);}}
assert.deepEqual([D.questions.length,D.options.length,D.channels.length,D.scoreRules.length,D.weights.length,D.policyGates.length],[79,249,20,1460,8,16]);
assert.equal(D.weights.reduce((s,r)=>s+r.weight,0),100);
assert(D.branchRules.every(r=>!r.executable));assert.equal(p.externalQuery,false);assert.equal(p.publishable,false);
console.log('Decision-engine checks passed: exact research example, all20 scores, caps, blocked/unknown/stale context, manual edits and88 budget boundaries.');
