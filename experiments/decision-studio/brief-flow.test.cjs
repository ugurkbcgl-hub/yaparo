'use strict';
const assert=require('node:assert/strict');
const F=require('./dist/brief-flow.js');
global.window={};require('./dist/data.js');
const D=window.YaparoResearch;
const ids={communication:'S1_Q01',business:'S3_Q02',sector:'S3_Q03'};
for(const [kind,q] of Object.entries(ids)){
  const all=D.options.filter(o=>o.questionId===q).map(o=>o.value).sort();
  const grouped=F.families(kind).flatMap(g=>F.choices(kind,g.id,D).map(o=>o.value));
  assert.deepEqual([...grouped].sort(),all,`${kind}: every source option remains reachable`);
  assert.equal(new Set(grouped).size,grouped.length,`${kind}: no overlapping family`);
  for(const value of all)assert.ok(F.familyOf(kind,value));
}
assert.deepEqual(F.choices('communication','missing',D),[]);
assert.deepEqual(F.families('unknown'),[]);
assert.equal(F.familyOf('business','unknown'),null);
const values=(job,business,destination)=>F.actions(job,business,D,destination).map(o=>o.value);
const retail=values('product_service_intro','local_retail');
assert.ok(retail.includes('visit_store'));
assert.ok(!retail.includes('donate')&&!retail.includes('apply_job')&&!retail.includes('download_app'));
assert.deepEqual(values('recruitment','local_retail'),['visit_website','fill_form','apply_job']);
assert.deepEqual(values('fundraising','local_retail'),['understand','visit_website','donate']);
assert.ok(values('event','b2b_leadgen').includes('register_event'),'a business can organize an event');
assert.ok(!values('event','b2b_leadgen').includes('apply_job'));
assert.ok(values('product_service_intro','local_retail','own_website').includes('buy_online'),'explicit web destination must override shop shortlist');
assert.ok(!values('product_service_intro','local_retail','own_website').includes('visit_store'));
assert.deepEqual(values('product_service_intro','local_retail','bad-destination'),[]);
assert.deepEqual(values('unknown','local_retail'),[]);
assert.deepEqual(values('product_service_intro','unknown'),[]);
const reached=new Set();
for(const job of D.options.filter(o=>o.questionId==='S1_Q01')){
  for(const business of D.options.filter(o=>o.questionId==='S3_Q02')){
    const offered=values(job.value,business.value);
    assert.ok(offered.length>0&&offered.length<=5,`${job.value}/${business.value} stays short`);
    offered.forEach(v=>reached.add(v));
  }
}
assert.deepEqual([...reached].sort(),D.options.filter(o=>o.questionId==='S1_Q04').map(o=>o.value).sort(),'all 16 actions remain reachable in valid contexts');
const questions=[
  {id:'job',showWhen:{}},{id:'note',showWhen:{}},
  {id:'event',showWhen:{job:['event']}},
  {id:'date',showWhen:{event:['onsite']}},
  {id:'consent',showWhen:{date:['tomorrow']}}
];
const original={job:'event',note:'keep',event:'onsite',date:'tomorrow',consent:['yes'],unknown:'drop'};
const retained=F.pruneAnswers(original,questions,{job:'event'});
assert.deepEqual(retained,{job:'event',note:'keep',event:'onsite',date:'tomorrow',consent:['yes']});
const pruned=F.pruneAnswers(original,questions,{job:'announcement'});
assert.deepEqual(pruned,{job:'announcement',note:'keep'},'upstream override recursively removes hidden answers; latest parent and unrelated notes survive');
assert.deepEqual(original.consent,['yes'],'inputs are not mutated');
retained.consent.push('new');assert.deepEqual(original.consent,['yes']);
const dataQuestion=D.questions.find(q=>q.id==='S1_F02');
const actual=F.pruneAnswers({S1_F02:'yes'},[dataQuestion],{S1_Q01:'product_service_intro'});
assert.deepEqual(actual,{},'source fundraising branch clears outside fundraising');
console.log('Brief-flow checks passed: complete canonical coverage, context-bound shortlists, destination override and recursive hidden-answer removal.');
