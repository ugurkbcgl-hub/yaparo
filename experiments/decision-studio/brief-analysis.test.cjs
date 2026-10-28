'use strict';
const assert=require('node:assert/strict');
const fs=require('node:fs');
const path=require('node:path');
const M=require('./dist/first-stage-bank.js'),C=require('./dist/outcome-contract.js');
const sourcePath=path.join(__dirname,'dist/data.js'),sourceBefore=fs.readFileSync(sourcePath);
function sample(f){
  if(f.type==='select')return f.options[0].value;
  if(f.type==='multiselect')return [f.options[0].value];
  if(f.type==='number')return Math.max(f.min||0,1);
  if(f.type==='date')return '2026-11-15';
  if(f.type==='time')return f.id.endsWith('_end')?'11:00':'10:00';
  if(f.type==='url')return 'https://ornek.example/sentetik';
  if(f.type==='tel')return '+90 (555) 000-00-00';
  if(f.type==='email')return 'sentetik@example.test';
  return 'Somut sentetik açıklama';
}
function fill(intent,outcome,overrides={}){
  let answers={...overrides};
  for(let n=0;n<20;n++){
    const before=JSON.stringify(answers);
    for(const f of M.fields(intent,outcome,answers))if(answers[f.id]===undefined)answers[f.id]=sample(f);
    answers=M.prune(intent,outcome,answers);if(before===JSON.stringify(answers))break;
  }
  const check=M.validate(intent,outcome,answers);assert(check.valid,JSON.stringify(check.errors));
  return {version:'yaparo-first-stage-v1',intent,outcome,answers};
}
let routes=0;
for(const intent of M.intents())for(const outcome of M.outcomes(intent.id)){
  const snapshot=fill(intent.id,outcome.id),original=structuredClone(snapshot),a=C.analyze(snapshot),c=C.resolve(snapshot);
  assert(a.valid,intent.id+'/'+outcome.id);assert.equal(a.version,'yaparo-owned-brief-analysis-v1');
  assert.equal(a.signature,C.signature(snapshot));assert.equal(a.binding.signature,a.signature);
  assert.equal(a.intent,intent.id);assert.equal(a.outcome,outcome.id);
  assert.equal(a.goal,c.legacyProjection?.goal||null);assert.equal(a.action,c.legacyProjection?.action||null);
  assert.deepEqual(a.scoringDimensions,c.legacyProjection?{objective:c.legacyProjection.goal}:{});
  assert.equal(a.sourceBusiness,null);assert.equal(a.sourceSector,null);assert.equal(a.sourceAudience,null);
  assert.equal(a.externalQuery,false);assert.equal(a.model,null);
  assert.equal(a.policy.status,'not_evaluated');assert.equal(a.policy.publishReady,false);assert.equal(a.policy.platformQualified,false);
  assert(a.known.length>=2);assert(a.known.every(f=>f.source==='first_stage'&&f.verified===false));
  for(const id of ['business_model','sector','source_audience','account_permissions','measurement','platform_forecast'])assert(a.unknown.some(item=>item.id===id));
  assert.ok(Object.isFrozen(a));assert.ok(Object.isFrozen(a.known));assert.ok(Object.isFrozen(a.binding.snapshot.answers));
  assert.deepEqual(snapshot,original);routes++;
}
assert.equal(routes,46);
for(const malformed of [undefined,null,[],{},'bad',{version:'future',intent:'promote',outcome:'traffic',answers:{}},{version:C.snapshotVersion,intent:'promote',outcome:'donate',answers:{}}]){
  const a=C.analyze(malformed);assert.equal(a.valid,false);assert.equal(a.goal,null);assert.equal(a.action,null);assert.equal(a.communication,null);assert.deepEqual(a.known,[]);assert.deepEqual(a.scoringDimensions,{});assert.equal(typeof a.signature,'string');assert.equal(a.policy.publishReady,false);
}
const unknownField=fill('promote','traffic');unknownField.answers.sector='health_medical';assert.equal(C.analyze(unknownField).valid,false);
const noRisk=fill('promote','understand',{promote_name:'Sentetik klinik finans ve çocuk hizmeti'});delete noRisk.answers.risk;
const plain=C.analyze(noRisk);assert.equal(plain.valid,true);assert.equal(plain.risk,null);assert.equal(plain.riskDeclared,null);assert.deepEqual(plain.risks,[]);assert.equal(plain.sourceSector,null);assert(plain.unknown.some(row=>row.id==='declared_risk'));
for(const risk of ['normal','health','finance','political','children','alcohol_tobacco','gambling']){
  const a=C.analyze(fill('promote','traffic',{risk}));assert.equal(a.risk,risk);assert.equal(a.riskDeclared,risk);assert(a.risks.includes(risk));assert.equal(a.policy.status,'not_evaluated');
}
const fundraiser=C.analyze(fill('fundraise','donate',{risk:'health'}));assert.equal(fundraiser.risk,'fundraising');assert.equal(fundraiser.riskDeclared,'health');assert.deepEqual(fundraiser.risks,['fundraising','health']);
const b2b=C.analyze(fill('lead','lead_form',{lead_audience:'business',lead_audience_detail:'small'}));assert.equal(b2b.ownedAudience,'business');assert.equal(b2b.audienceLabel,'İşletmeler');assert.equal(b2b.sourceAudience,null);
const custom=C.analyze(fill('promote','traffic',{promote_kind:'other',promote_kind_other:'Sentetik özgün alan'}));assert(custom.known.some(row=>row.value==='Sentetik özgün alan'));assert.equal(custom.sourceBusiness,null);
const snap=fill('promote','understand'),before=C.analyze(snap);snap.answers.promote_name='Yeni sentetik konu';assert.notEqual(C.analyze(snap).signature,before.signature);snap.answers.action_message='Yeni sentetik mesaj';assert.notEqual(C.analyze(snap).signature,before.signature);
assert.throws(()=>{before.known[0].value='changed';},TypeError);
assert.equal(before.binding.snapshot.answers.promote_name,'Somut sentetik açıklama');
for(const pair of [['fundraise','volunteer'],['community','register'],['promote','contact']]){
  const overrides=pair[1]==='contact'?{action_contact:'email'}:{};
  const a=C.analyze(fill(...pair,overrides));assert.equal(a.goal,null);assert.deepEqual(a.scoringDimensions,{});assert(a.unknown.some(row=>row.id==='paid_outcome'));
}
assert(fs.readFileSync(sourcePath).equals(sourceBefore));
console.log('Owned brief analysis passed: 46 exact routes, bound declared facts, no taxonomy/risk guesses, retained risks, immutable output and no readiness/forecast approval.');
