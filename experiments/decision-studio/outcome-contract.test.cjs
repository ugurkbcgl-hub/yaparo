'use strict';
const assert=require('node:assert/strict');
const fs=require('node:fs');
const path=require('node:path');
const M=require('./dist/first-stage-bank.js');
const sourcePath=path.join(__dirname,'dist/data.js');
const sourceBefore=fs.readFileSync(sourcePath);
const C=require('./dist/outcome-contract.js');
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
    answers=M.prune(intent,outcome,answers);
    if(before===JSON.stringify(answers))break;
  }
  const check=M.validate(intent,outcome,answers);assert.equal(check.valid,true,JSON.stringify(check.errors));
  return {version:'yaparo-first-stage-v1',intent,outcome,answers};
}
let routes=0;
for(const intent of M.intents())for(const outcome of M.outcomes(intent.id)){
  const snapshot=fill(intent.id,outcome.id),original=structuredClone(snapshot),contract=C.resolve(snapshot);
  assert.equal(contract.valid,true,intent.id+'/'+outcome.id);
  assert.equal(contract.outcomeLabel,outcome.label);
  assert.equal(contract.action.id,intent.id+'/'+outcome.id);
  assert.ok(contract.action.cta);
  assert.ok(contract.kpi.id);
  assert.equal(contract.kpi.forecast,null);
  assert.equal(contract.policy.publishReady,false);
  assert.equal(contract.policy.platformQualified,false);
  assert.equal(contract.authorship.externalQuery,false);
  assert.equal(contract.binding.signature,C.signature(snapshot));
  assert.ok(Object.isFrozen(contract));assert.ok(Object.isFrozen(contract.binding.snapshot.answers));
  const cards=C.buildConcepts(snapshot,{revision:2,notes:'Sadece sentetik taslak'});
  assert.equal(cards.length,3);
  assert.equal(new Set(cards.map(c=>c.title+'|'+c.message)).size,3);
  assert.equal(new Set(cards.map(c=>c.angle)).size,3);
  for(const card of cards){
    assert.equal(card.cta,contract.action.cta);assert.equal(card.binding.signature,contract.binding.signature);assert.equal(card.outcomeSignature,contract.binding.signature);assert.equal(card.outcome,outcome.id);
    assert.equal(card.revision,2);assert.equal(card.provenance.externalQuery,false);assert.equal(card.provenance.model,null);
    assert.equal(card.provenance.fictional,true);assert.match(card.disclaimer,/yerel/);
    assert.ok(card.message.includes('Somut sentetik açıklama'),intent.id+'/'+outcome.id+' must keep literal typed answer');
    if(intent.id==='fundraise')assert.doesNotMatch(card.title+' '+card.message+' '+card.cta,/satın al|ürünleri|indirim|sipariş/i);
  }
  assert.deepEqual(snapshot,original);
  routes++;
}
assert.equal(routes,46);
for(const malformed of [null,[],{},'bad',{version:'future',intent:'sell',outcome:'purchase',answers:{}},{version:C.snapshotVersion,intent:'unknown',outcome:'purchase',answers:{}},{version:C.snapshotVersion,intent:'sell',outcome:'donate',answers:{}},{version:C.snapshotVersion,intent:'sell',outcome:'purchase',answers:[]}]){
  const result=C.resolve(malformed);assert.equal(result.valid,false);assert.equal(typeof result.binding.signature,'string');assert.equal(result.action,null);assert.equal(result.legacyProjection,null);assert.deepEqual(C.buildConcepts(malformed),[]);
}
const hidden=fill('fundraise','donate');hidden.answers.sell_name='Hidden commercial text';assert.equal(C.resolve(hidden).valid,false);
for(const intent of ['toString','constructor','__proto__',{},null])assert.equal(C.resolve({version:C.snapshotVersion,intent,outcome:'traffic',answers:{}}).valid,false);
const circular={};circular.self=circular;assert.equal(C.resolve(circular).valid,false);assert.equal(typeof C.resolve(undefined).binding.signature,'string');
const badUrl=fill('sell','traffic');badUrl.answers.action_url='javascript:alert(1)';assert.equal(C.resolve(badUrl).valid,false);
const future=fill('sell','traffic');future.version='yaparo-first-stage-v2';assert.equal(C.resolve(future).valid,false);
const snap=fill('fundraise','volunteer'),key=C.signature(snap);
const reordered={answers:Object.fromEntries(Object.entries(snap.answers).reverse()),outcome:snap.outcome,intent:snap.intent,version:snap.version};
assert.equal(C.signature(reordered),key,'object insertion order does not invalidate exact content binding');
snap.answers.action_volunteer_task='Kütüphanede kitapları düzenlemek';assert.notEqual(C.signature(snap),key);
const beforeContract=C.resolve(snap);snap.answers.action_volunteer_task='Yeni görev';assert.equal(beforeContract.binding.snapshot.answers.action_volunteer_task,'Kütüphanede kitapları düzenlemek');
assert.notEqual(C.buildConcepts(snap,{revision:1})[0].title,C.buildConcepts(snap,{revision:2})[0].title);
assert.throws(()=>{beforeContract.binding.snapshot.answers.action_volunteer_task='Mutasyon';},TypeError);
for(const outcome of ['donate','materials','volunteer'])assert.ok(C.resolve(fill('fundraise',outcome)).kpi.id.includes(({donate:'monetary',materials:'material',volunteer:'volunteer'})[outcome]));
assert.notEqual(C.resolve(fill('sell','purchase')).kpi.id,C.resolve(fill('sell','visit')).kpi.id);
assert.notEqual(C.resolve(fill('event','register')).kpi.id,C.resolve(fill('event','ticket')).kpi.id);
assert.notEqual(C.resolve(fill('announce','follow')).kpi.id,C.resolve(fill('announce','share')).kpi.id);
const subscription=C.resolve(fill('community','subscribe'));assert.equal(subscription.kpi.id,'started_subscriptions');assert.equal(subscription.kpi.secondary.id,'active_subscriptions');
const app=C.resolve(fill('promote','install',{action_app_platform:'both'}));assert.equal(app.kpi.id,'app_installs');assert.equal(app.kpi.secondary.id,'activated_app_users');assert.ok(app.destination.androidUrl);assert.ok(app.destination.iosUrl);
for(const method of ['whatsapp','social','email']){
  const result=C.resolve(fill('lead','message',{action_message_method:method}));
  assert.equal(result.destination.channel,method);assert.equal(result.destination.kind,'message');
  assert.equal(result.legacyProjection?.action||null,method==='whatsapp'?'message_whatsapp':null);
}
const place=C.resolve(fill('sell','purchase',{action_checkout:'store'}));assert.equal(place.kpi.id,'completed_purchases');assert.equal(place.destination.kind,'location');assert.equal(place.legacyProjection,null);
const missingForm=C.resolve(fill('lead','quote',{action_lead_method:'new'}));assert.equal(missingForm.destination.kind,'unresolved');assert.ok(missingForm.destination.missing.includes('form_not_created'));
const custom=C.resolve(fill('fundraise','donate',{action_donation_method:'other'}));assert.equal(custom.destination.kind,'unresolved');assert.equal(custom.policy.publishReady,false);
for(const [intent,outcome]of [['event','ticket'],['fundraise','materials'],['fundraise','volunteer'],['community','subscribe'],['community','join'],['announce','follow'],['reputation','share'],['lead','meeting']])assert.equal(C.resolve(fill(intent,outcome)).legacyProjection,null);
const content=C.resolve(fill('fundraise','materials',{delivery_mode:'content_only'}));assert.equal(content.usage.contentOnly,true);assert.equal(content.usage.resolved,true);assert.ok(content.requirements.some(r=>r.id==='independent_draft'));assert.ok(!content.requirements.some(r=>r.id==='channel_permissions'));
const unsure=C.resolve(fill('promote','understand',{delivery_mode:'unsure'}));assert.equal(unsure.usage.resolved,false);assert.ok(unsure.requirements.some(r=>r.id==='usage_choice'));
assert.deepEqual(fs.readFileSync(sourcePath),sourceBefore,'source dataset is untouched');
console.log('Owned outcome contract: all 46 routes, 138 distinct bound local concepts, exact destinations and fail-closed validation passed.');
