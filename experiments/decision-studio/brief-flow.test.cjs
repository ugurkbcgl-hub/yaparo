'use strict';
const assert=require('node:assert/strict');
const F=require('./dist/brief-flow.js');
global.window={};require('./dist/data.js');
const D=window.YaparoResearch;
// The initial response remains authoritative as later business details change.
assert.deepEqual(F.intentActions('fundraising'),['donate','understand','visit_website']);
assert.ok(!F.intentActions('fundraising').includes('buy_online'));
assert.ok(F.intentActions('sale_promotion').includes('remember'));
assert.ok(F.intentActions('product_service_intro').includes('visit_store'));
assert.ok(F.intentActions('product_service_intro').includes('fill_form'));
assert.deepEqual(F.intentActions('unsure'),[]);
assert.deepEqual(F.intentActions('__other__'),[]);
assert.deepEqual(F.destinations('buy_online',D).map(o=>o.value),['own_website']);
assert.deepEqual(F.destinations('visit_store',D).map(o=>o.value),['physical_store']);
assert.ok(!F.destinations('call',D).some(o=>o.value==='marketplace'));
const originalSourceOptions=JSON.stringify(D.options);
assert.deepEqual(F.destinations('unknown',D),[]);
assert.deepEqual(F.destinations('',D),[]);
assert.deepEqual(F.destinations('visit_website',D).map(o=>o.value),['own_website']);
assert.deepEqual(F.destinations('register_event',D).map(o=>o.value),['lead_form','own_website','physical_store']);
assert.deepEqual(F.destinations('apply_job',D).map(o=>o.value),['lead_form','own_website','whatsapp_phone']);
assert.equal(F.destinations('follow_engage',D)[0].value,'social_profile');
assert.equal(F.destinations('follow_engage',D)[0].owned,true);
assert.ok(F.destinations('remember',D).some(o=>o.value==='none'&&o.owned===true));
assert.equal(JSON.stringify(D.options),originalSourceOptions,'owned route extensions never change source rows');
assert.equal(F.destinationApplies('event','register_event',D),true);
assert.equal(F.destinationApplies('recruitment','apply_job',D),true);
assert.equal(F.destinationApplies('education','follow_engage',D),true);
assert.equal(F.destinationApplies('fundraising','visit_website',D),true);
assert.equal(F.destinationApplies('fundraising','donate',D),false,'donation does not silently require a website');
assert.equal(F.destinationApplies('unknown','visit_website',D),false);
assert.equal(F.destinationApplies('fundraising','apply_job',D),false,'incompatible purpose/action fails closed');
for(const type of ['own_website','marketplace','lead_form','app','social_profile']){
  assert.deepEqual(F.destinationFields(type,'visit_website').map(field=>field.key),['url']);
  assert.equal(F.destinationFields(type,'visit_website')[0].required,true);
  assert.deepEqual(F.validateDestination(type,{url:'https://ornek.example/kampanya?source=demo'},'visit_website'),{});
  assert.deepEqual(F.validateDestination(type,{url:'http://ornek.example/'},'visit_website'),{});
  for(const url of ['', 'javascript:alert(1)','data:text/html,test','ftp://ornek.example/','https://user:pass@ornek.example/','https://ornek.example/a b','https://ornek.example/\nnext','https://ornek.example/\u007f','https:\\ornek.example/','https://ornek.example/'+'x'.repeat(2048)]){
    assert.ok(F.validateDestination(type,{url},'visit_website').url,`${type}: reject malformed/unsafe URL`);
  }
}
assert.match(F.destinationFields('whatsapp_phone','call')[0].label,/Aranacak/);
assert.match(F.destinationFields('whatsapp_phone','message_whatsapp')[0].label,/WhatsApp/);
assert.deepEqual(F.validateDestination('whatsapp_phone',{phone:'+90 (555) 000-00-00'},'call'),{});
for(const phone of ['','123','+1234567890123456','+90 call 5550000000','90+5550000000','+90\n5550000000'])assert.ok(F.validateDestination('whatsapp_phone',{phone},'call').phone);
assert.deepEqual(F.validateDestination('physical_store',{address:'Örnek Mahallesi, Örnek Sokak No: 1'},'visit_store'),{});
assert.deepEqual(F.validateDestination('physical_store',{mapUrl:'https://harita.example/konum'},'visit_store'),{});
assert.ok(F.validateDestination('physical_store',{},'visit_store').address);
assert.ok(F.validateDestination('physical_store',{address:'Kısa'},'visit_store').address);
assert.ok(F.validateDestination('physical_store',{address:'x'.repeat(401)},'visit_store').address);
assert.ok(F.validateDestination('physical_store',{mapUrl:'javascript:alert(1)'},'visit_store').mapUrl);
assert.ok(F.validateDestination('own_website',{url:{value:'https://ornek.example/'}},'visit_website').url);
assert.ok(F.validateDestination('own_website',{url:'https://ornek.example/',phone:'5550000000'},'visit_website')._form);
for(const type of ['none','__other__']){
  assert.deepEqual(F.destinationFields(type,'remember'),[]);
  assert.deepEqual(F.validateDestination(type,{},'remember'),{});
  assert.ok(F.validateDestination(type,{url:'https://old.example/'},'remember')._form,'no stale hidden details admitted');
}
assert.deepEqual(F.destinationFields('unknown','remember'),[]);
assert.ok(F.validateDestination('unknown',{},'remember')._form);
assert.ok(F.validateDestination('own_website',[],'visit_website')._form);
for(const comm of D.options.filter(o=>o.questionId==='S1_Q01'&&o.value!=='unsure')){
  assert.ok(F.intentActions(comm.value).length);
  for(const value of F.intentActions(comm.value))assert.ok(D.options.some(o=>o.questionId==='S1_Q04'&&o.value===value));
}
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
assert.equal(F.version,'yaparo-brief-flow-v3');
const businesses=job=>F.businesses(job,D).map(o=>o.value);
assert.equal(businesses('product_service_intro').length,9);
assert.ok(!businesses('product_service_intro').includes('nonprofit_fundraising'));
assert.ok(!businesses('sale_promotion').includes('employer_recruitment'));
assert.equal(businesses('recruitment').length,6);
assert.ok(businesses('recruitment').includes('employer_recruitment'));
assert.equal(businesses('fundraising').length,5);
assert.ok(businesses('fundraising').includes('nonprofit_fundraising'));
assert.equal(businesses('event').length,11,'an event does not force event-only business model');
assert.ok(businesses('event').includes('local_retail'));
assert.ok(businesses('event').includes('b2b_leadgen'));
assert.deepEqual(F.businesses('unknown',D),[]);
assert.deepEqual(F.businesses('custom:business',D),[]);
assert.deepEqual(F.sectors('unknown','local_retail',D),[]);
assert.deepEqual(F.sectors('product_service_intro','custom:business',D),[]);
const retailSectors=F.sectors('product_service_intro','local_retail',D).map(o=>o.value);
assert.equal(retailSectors.length,6);
assert.ok(!retailSectors.includes('public_political')&&!retailSectors.includes('recruitment'));
assert.ok(retailSectors.includes('other'));
const serviceSectors=F.sectors('product_service_intro','local_service',D).map(o=>o.value);
assert.ok(serviceSectors.includes('local_home_services')&&!serviceSectors.includes('industrial_b2b'));
const availableBusinesses=new Set(),availableSectors=new Set();
for(const job of D.options.filter(o=>o.questionId==='S1_Q01')){
  for(const business of F.businesses(job.value,D)){
    availableBusinesses.add(business.value);
    const offered=F.sectors(job.value,business.value,D);
    assert.ok(offered.length>0&&offered.length<18,`${business.value}: sector shortlist is narrowed`);
    assert.equal(new Set(offered.map(o=>o.value)).size,offered.length);
    offered.forEach(o=>availableSectors.add(o.value));
  }
}
assert.deepEqual([...availableBusinesses].sort(),D.options.filter(o=>o.questionId==='S3_Q02').map(o=>o.value).sort(),'all business values still have a path');
assert.deepEqual([...availableSectors].sort(),D.options.filter(o=>o.questionId==='S3_Q03').map(o=>o.value).sort(),'all sector values still have a valid path');
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
