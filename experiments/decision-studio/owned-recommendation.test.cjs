const assert=require('node:assert/strict');
global.window=global;
require('./dist/data.js');require('./dist/engine.js');
const X=require('./dist/simulation.js');require('./dist/outcome-contract.js');
require('./dist/turkey-boundary.js');require('./dist/plan-geo.js');
const E=YaparoDecision,D=YaparoResearch,C=YaparoOutcomeContract;
const sample=(id='cafe',mode='paid')=>{const s=X.get(id).snapshot;s.answers.delivery_mode=mode;return s;};
const base={firstStage:sample(),budget:3000,days:7,start:'2026-11-15',geo:'nationwide',video:false,value:0,margin:0,cpa:0,capacity:0,economicsMode:'not_provided'};
const run=patch=>E.evaluateOwned({...base,...patch},D);
const plan=run({});
const noEconomicsMode=run({economicsMode:undefined,value:9000,margin:80,cpa:999,capacity:500});
assert.equal(noEconomicsMode.economicsProvided,false);assert.equal(noEconomicsMode.input.value,0);
assert.deepEqual(noEconomicsMode.rows.map(r=>r.amount),plan.rows.map(r=>r.amount));
assert.throws(()=>run({economicsMode:'ignore_limits'}));
assert(plan.allocated>0);assert.equal(plan.allocated+plan.unallocated,plan.total);
assert.equal(plan.analysis.signature,C.signature(base.firstStage));
assert.equal(plan.input.goal,'store_visits');assert.equal(plan.input.business,'owned_unspecified');assert.equal(plan.input.sector,'owned_unspecified');
assert.equal(plan.analysis.sourceBusiness,null);assert.equal(plan.analysis.sourceSector,null);
assert.equal(plan.publishable,false);assert.equal(plan.qualification.publishReady,false);assert.equal(plan.externalQuery,false);
for(const row of plan.rows){
  assert.equal(row.scoreBasis,'known_facts_only');
  assert(row.coverageWeight<=40);
  assert.equal(row.coverageWeight,row.breakdown.filter(b=>b.known).reduce((sum,b)=>sum+b.weight,0));
  for(const dim of ['business_model','sector','audience','measurement','creative']){
    const b=row.breakdown.find(b=>b.dimension===dim);assert.equal(b.known,false);assert.equal(b.score,null);assert.equal(b.points,0);
  }
  if(row.amount){assert(row.eligible);assert(row.amount>=row.useful);assert(row.amount<=row.cap);assert(row.channel.objectives.includes(plan.input.goal));}
}
// Hidden legacy controls cannot invent classification, intent or platform readiness.
const injected=run({goal:'awareness',communication:'other',action:'donate',risk:'health',business:'b2b_leadgen',sector:'food_hospitality',audience:'b2b_decision_makers',ownedAudience:'business',fixture:'demo',readiness:'all',measurement:'pixel_capi_crm',tracking:true,catalog:true});
assert.deepEqual(injected.rows.map(r=>r.amount),plan.rows.map(r=>r.amount));
assert.equal(injected.input.ownedAudience,'individuals');assert.equal(injected.input.measurement,'none');
assert.equal(injected.input.tracking,false);assert.equal(injected.input.catalog,false);
assert.equal(injected.analysis.risk,null);assert.equal(injected.input.risk,'not_declared');
const health=sample();health.answers.risk='health';
assert.equal(run({firstStage:health,risk:'normal'}).allocated,0);
const fundraising={version:'yaparo-first-stage-v1',intent:'fundraise',outcome:'understand',answers:{fundraise_organizer_type:'association',fundraise_organizer_name:'Sentetik dernek',fundraise_purpose:'education',fundraise_goal:'Sentetik bilgilendirme',delivery_mode:'paid',risk:'health'}};
const fa=C.analyze(fundraising);assert(fa.valid);assert(fa.risks.includes('fundraising'));assert(fa.risks.includes('health'));
assert.equal(run({firstStage:fundraising,risk:'normal'}).allocated,0);
for(const mode of ['organic','content_only','unsure'])assert.throws(()=>run({firstStage:sample('cafe',mode)}));
const email=sample();email.outcome='contact';delete email.answers.action_location_address;Object.assign(email.answers,{action_contact:'email',action_email:'sentetik@example.test'});
assert(C.analyze(email).valid);assert.equal(C.analyze(email).goal,null);assert.throws(()=>run({firstStage:email}),/eşleştirmesi/);
assert.throws(()=>run({firstStage:{...sample(),version:'unknown'}}));
assert.throws(()=>run({firstStage:{...sample(),outcome:'volunteer'}}));
for(const patch of [{budget:-1},{budget:NaN},{days:0},{days:366},{start:'2026-02-30'},{geo:'unknown'},{geo:'district_city',region:''},{geo:'radius_local',radius:80}])assert.throws(()=>run(patch));
const radius=run({geo:'radius_local',radius:80,geoCenter:{lat:41.005,lon:29.04,verified:true,untrusted:'drop'}});
assert.deepEqual(Object.keys(radius.input.geoCenter).sort(),['boundary','lat','lon','verified']);
assert.equal(radius.input.geoCenter.verified,false);
assert.throws(()=>run({geo:'radius_local',radius:80,geoCenter:{lat:48.8566,lon:2.3522}}));
assert.equal(run({economicsMode:'provided',capacity:0}).allocated,0);
assert.throws(()=>E.evaluate(plan.input,D,null,null,{analysis:plan.analysis}));
const b2b=run({firstStage:sample('saas')});assert.equal(b2b.input.ownedAudience,'business');assert.equal(b2b.input.goal,'lead_generation');
assert(b2b.analysis.known.some(f=>f.value==='İşletmeler'));
assert.notEqual(b2b.rows[0].f.cpc,plan.rows[0].f.cpc);
for(let budget=0;budget<=12000;budget+=499){const p=run({budget});assert.equal(p.allocated+p.unallocated,p.total);assert(p.allocated<=p.businessCap);assert.equal(p.publishable,false);}
console.log('Owned recommendation passed: bound first-stage facts, known-only coverage, no hidden classification/readiness overrides, risk/goal/geo gates and capped synthetic allocation.');
