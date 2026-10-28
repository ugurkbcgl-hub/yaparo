const assert=require('node:assert/strict');
global.window=global;
require('./dist/data.js');require('./dist/engine.js');
const H=require('./dist/plan-summary.js');
const base={budget:3000,days:7,value:500,margin:40,cpa:100,capacity:20,goal:'store_visits',business:'local_retail',audience:'local_nearby',sector:'fashion_beauty_lifestyle',geo:'district_city',region:'İstanbul, Kadıköy',start:'2026-10-27',measurement:'basic_utm',fixture:'demo',communication:'product_service_intro',risk:'normal'};
const make=patch=>YaparoDecision.evaluate({...base,...patch},YaparoResearch);
const invariant=p=>{assert.equal(p.allocated+p.unallocated,p.total);assert(p.allocated<=p.businessCap);assert.equal(p.rows.reduce((s,r)=>s+r.amount,0),p.allocated);for(const r of p.rows){assert(Number.isSafeInteger(r.amount));assert(r.amount===0||(r.eligible&&!r.owned&&r.amount>=r.useful&&r.amount<=r.cap));}};
let p=make();
assert.deepEqual(H.limits(p,'meta_social'),{minimum:100000,maximum:180000,minPercent:100000/300000*100,maxPercent:60,canAdd:true});
let result=H.redistribute(p,'meta_social',50);
assert.equal(result.amount,150000);assert.equal(p.rows.find(r=>r.channel.id==='google_search_maps').amount,120000);assert.equal(p.unallocated,30000);invariant(p);
result=H.redistribute(p,'meta_social',90);assert.equal(result.amount,180000);assert(result.limited);assert.equal(p.rows.find(r=>r.channel.id==='google_search_maps').amount,120000);invariant(p);
result=H.redistribute(p,'meta_social',1);assert.equal(result.amount,100000);assert(result.limited);invariant(p);
H.remove(p,'meta_social');assert.equal(p.rows.find(r=>r.channel.id==='meta_social').amount,0);assert(p.unallocated>0);invariant(p);
H.redistribute(p,'meta_social',50);assert.equal(p.rows.find(r=>r.channel.id==='meta_social').amount,150000);invariant(p);
// An existing unallocated reserve is not silently spent by a smaller explicit share.
p=make({budget:10000});const previous=p.allocated;H.redistribute(p,'meta_social',15);assert(p.allocated<=previous);assert(p.unallocated>=680000);invariant(p);
// No outside eligible/owned or omitted row gets automatically selected.
for(const id of ['tiktok','not_a_channel','owned_crm']){p=make();const before=JSON.stringify(p);assert.throws(()=>H.redistribute(p,id,10));assert.equal(JSON.stringify(p),before);}
for(const patch of [{budget:0},{communication:'fundraising'}]){p=make(patch);const before=JSON.stringify(p);assert.throws(()=>H.redistribute(p,'meta_social',50));assert.equal(JSON.stringify(p),before);}
for(const value of [NaN,Infinity,-1,100.1,'10',null,undefined]){p=make();const before=JSON.stringify(p);assert.throws(()=>H.redistribute(p,'meta_social',value));assert.equal(JSON.stringify(p),before);}
for(const mutate of [p=>p.blocked=true,p=>p.externalQuery=true,p=>p.publishable=true,p=>p.allocated++,p=>p.unallocated++,p=>p.businessCap=-1,p=>p.rows.push(p.rows[0]),p=>p.rows[0].amount=.1,p=>p.quality='real_forecast']){p=make();mutate(p);const before=JSON.stringify(p);assert.throws(()=>H.redistribute(p,'meta_social',50));assert.equal(JSON.stringify(p),before);}
// A tight shared cap cannot add a row by weakening another selected minimum.
p=make();p.businessCap=200000;for(const r of p.rows){if(r.eligible){r.cap=Math.min(r.cap,200000);r.amount=0;}}p.rows.find(r=>r.channel.id==='meta_social').amount=100000;p.allocated=100000;p.unallocated=200000;invariant(p);
assert.equal(H.limits(p,'google_search_maps').canAdd,false);const tightBefore=JSON.stringify(p);assert.throws(()=>H.redistribute(p,'google_search_maps',50));assert.equal(JSON.stringify(p),tightBefore);
p.businessCap=220000;H.redistribute(p,'google_search_maps',50);invariant(p);assert.equal(p.allocated,220000);assert.equal(p.unallocated,80000);
// Three uncapped selected channels preserve their existing ratio; unchanged share is a no-op.
p={blocked:false,externalQuery:false,publishable:false,quality:'authored_simulation_NOT_market_data',total:100000,businessCap:100000,allocated:100000,unallocated:0,rows:[['a',50000],['b',30000],['c',20000]].map(([id,amount])=>({channel:{id},eligible:true,owned:false,amount,useful:10000,cap:100000}))};
H.redistribute(p,'a',50);assert.deepEqual(p.rows.map(r=>r.amount),[50000,30000,20000]);
H.redistribute(p,'a',40);assert.deepEqual(p.rows.map(r=>r.amount),[40000,36000,24000]);invariant(p);
H.redistribute(p,'a',80);assert.deepEqual(p.rows.map(r=>r.amount),[80000,10000,10000]);invariant(p);
// Repeated decimal-percentage changes retain exact integer totals, caps and minima.
for(let budget=2000;budget<=12000;budget+=137){p=make({budget});const row=p.rows.find(r=>r.channel.id==='meta_social');if(!row.eligible)continue;for(const share of [0,1,12.345,25,33.333,50,66.667,99.99,100,0]){try{H.redistribute(p,'meta_social',share);}catch(error){assert.match(error.message,/başka bir kanalı/);}invariant(p);}}
console.log('Plan shares passed: exact cents, selected-only proportional rebalance, minima/caps/shared cap, reserve, explicit removal and atomic refusal.');
