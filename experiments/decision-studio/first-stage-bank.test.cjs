'use strict';
const assert = require('node:assert/strict');
const F = require('./dist/first-stage-bank.js');
const design = require('../../docs/product/first-stage-question-bank.json');
function sample(field) {
  if (field.type === 'select') return field.options[0].value;
  if (field.type === 'multiselect') return [field.options[0].value];
  if (field.type === 'number') return Math.max(field.min || 0, 1);
  if (field.type === 'date') return '2026-11-15';
  if (field.type === 'time') return field.id.endsWith('_end') ? '11:00' : '10:00';
  if (field.type === 'url') return 'https://ornek.example/sentetik';
  if (field.type === 'tel') return '+90 (555) 000-00-00';
  if (field.type === 'email') return 'sentetik@example.test';
  return 'Somut sentetik açıklama';
}
function fill(intent,outcome,overrides={}) {
  let answers={...overrides};
  for(let step=0;step<20;step++) {
    const before=JSON.stringify(answers);
    for(const field of F.fields(intent,outcome,answers))if(!Object.hasOwn(answers,field.id))answers[field.id]=sample(field);
    answers=F.prune(intent,outcome,answers);
    if(before===JSON.stringify(answers))break;
  }
  return answers;
}
function has(intent,outcome,answers,id) {return F.fields(intent,outcome,answers).some(f=>f.id===id);}
function error(intent,outcome,answers,id) {assert(F.validate(intent,outcome,answers).errors[id],`expected ${id} error`);}

assert.equal(F.intents().length,9);
assert.deepEqual(F.intents(),design.banks.map(b=>({id:b.id,label:b.answer})), 'all accepted purpose banks retained');
for(const bank of design.banks)assert.deepEqual(F.outcomes(bank.id).map(o=>o.label),bank.outcomes, `${bank.id}: every designed response retained`);
let routes=0;
for(const intent of F.intents()) {
  assert(F.outcomes(intent.id).length>0);
  for(const outcome of F.outcomes(intent.id)) {
    routes++;
    const answers=fill(intent.id,outcome.id), result=F.validate(intent.id,outcome.id,answers);
    assert.equal(result.valid,true,JSON.stringify({intent:intent.id,outcome:outcome.id,errors:result.errors}));
    assert.equal(new Set(F.fields(intent.id,outcome.id,answers).map(f=>f.id)).size,F.fields(intent.id,outcome.id,answers).length);
    assert.equal(F.validate(intent.id,outcome.id,{}).valid,false,'blank brief cannot pass');
    const original=JSON.stringify(answers);F.summary(intent.id,outcome.id,answers);F.validate(intent.id,outcome.id,answers);
    assert.equal(JSON.stringify(answers),original,'consumer input stays unchanged');
    assert(F.summary(intent.id,outcome.id,answers).length>0);
  }
}
assert(routes>=40);
assert.deepEqual(F.fields('fundraise','purchase',{}),[]);
assert.deepEqual(F.prune('not-an-intent','donate',{fundraise_goal:'x'}),{});
assert(F.validate('fundraise','purchase',{}).errors._route);
assert.deepEqual(F.outcomes('unknown'),[]);

// Each bank owns its questions; commercial/job/donation facts do not bleed across.
for(const outcome of F.outcomes('fundraise')) {
  const fields=F.fields('fundraise',outcome.id,fill('fundraise',outcome.id));
  assert(!fields.some(f=>/^(sell_|hire_|promote_|lead_)/.test(f.id)));
  assert(!fields.some(f=>f.options?.some(o=>/ürün sunuyorum|mağazamdan|B2B/i.test(o.label))));
}
for(const intent of F.intents().filter(i=>i.id!=='fundraise'))for(const outcome of F.outcomes(intent.id))assert(!F.fields(intent.id,outcome.id,fill(intent.id,outcome.id)).some(f=>f.id.startsWith('fundraise_')));

// Donation money, in-kind and volunteering are distinct and prune hidden money.
let cash=fill('fundraise','donate',{fundraise_target_status:'set',fundraise_target:1000,fundraise_currency:'TRY'});
assert(has('fundraise','donate',cash,'fundraise_target'));
assert(has('fundraise','donate',cash,'fundraise_permit'));
const volunteer=F.prune('fundraise','volunteer',{...cash,action_volunteer_task:'Paketleme'});
assert(!Object.hasOwn(volunteer,'fundraise_target'));
assert(!Object.hasOwn(volunteer,'fundraise_currency'));
assert(!Object.hasOwn(volunteer,'action_donation_method'));
assert(has('fundraise','volunteer',volunteer,'action_volunteer_task'));
assert(!has('fundraise','volunteer',volunteer,'fundraise_permit'));
for(const route of ['understand','traffic','share']) {
  const pruned=F.prune('fundraise',route,cash);
  assert(!Object.hasOwn(pruned,'fundraise_target'));
  assert(!Object.hasOwn(pruned,'action_donation_method'));
  assert(!has('fundraise',route,pruned,'fundraise_permit'));
}
const materials=fill('fundraise','materials',{action_delivery:'dropoff',action_material_quantity:0});
assert.equal(F.validate('fundraise','materials',materials).valid,true,'zero optional quantity preserved');
assert(has('fundraise','materials',materials,'action_material_unit'));
assert(!has('fundraise','materials',materials,'fundraise_currency'));

// Method change removes endpoints and their descendants until visibility converges.
let sale=fill('sell','purchase',{action_checkout:'website',action_url:'https://ornek.example/urun'});
sale=F.prune('sell','purchase',{...sale,action_checkout:'store'});
assert(!Object.hasOwn(sale,'action_url'));
assert(has('sell','purchase',sale,'action_location_address'));
sale=F.prune('sell','purchase',{...sale,action_checkout:'message',action_message_method:'email',action_email:'test@example.test'});
sale=F.prune('sell','purchase',{...sale,action_checkout:'phone'});
assert(!Object.hasOwn(sale,'action_message_method'));
assert(!Object.hasOwn(sale,'action_email'));
assert(!Object.hasOwn(sale,'action_location_address'));
assert(has('sell','purchase',sale,'action_phone'));

// Manual Other is meaningful and typed, and cannot survive returning to an enum.
let manual={...fill('promote','remember',{promote_kind:'other'}),promote_kind_other:'   '};
error('promote','remember',manual,'promote_kind_other');
manual={...manual,promote_kind_other:'   Özgün proje   '};
assert.equal(F.validate('promote','remember',manual).answers.promote_kind_other,'Özgün proje');
manual=F.prune('promote','remember',{...manual,promote_kind:'brand'});
assert(!Object.hasOwn(manual,'promote_kind_other'));

// URL syntax and userinfo, phone/email, numeric types and actual calendar dates.
const traffic=fill('promote','traffic');
for(const url of ['javascript:alert(1)','data:text/html,test','ftp://example.test','https:example.test','https://user:secret@example.test','https://example.test/a b','https://example.test/\nnext','https:\\example.test'])error('promote','traffic',{...traffic,action_url:url},'action_url');
assert.equal(F.validate('promote','traffic',{...traffic,action_url:'https://example.test/path?x=1'}).valid,true);
const call=fill('lead','call');
for(const phone of ['12','+90ABC12345','90+5550000000','555\n0000000','1234567890123456'])error('lead','call',{...call,action_phone:phone},'action_phone');
const apply=fill('hire','apply',{action_apply_method:'email'});
for(const email of ['not-an-email','a@','a\n@example.test','a@b'])error('hire','apply',{...apply,action_email:email},'action_email');
const event=fill('event','register',{event_timing:'range',event_start:'2026-11-10',event_end:'2026-11-11'});
error('event','register',{...event,event_start:'2026-02-30'},'event_start');
error('event','register',{...event,event_end:'2026-11-09'},'event_end');
assert.equal(F.validate('event','register',{...event,event_start:'2028-02-29',event_end:'2028-03-01'}).valid,true);
error('event','register',{...event,event_capacity_status:'known',event_capacity:-1},'event_capacity');
error('event','register',{...event,event_capacity_status:'known',event_capacity:1.5},'event_capacity');
error('event','register',{...event,event_capacity_status:'known',event_capacity:'10'},'event_capacity');
error('event','register',{...event,event_capacity_status:'known',event_capacity:Infinity},'event_capacity');
const online=fill('event','register',{event_mode:'online',event_online_method:'invite'});
assert(!has('event','register',online,'event_location_address'));
error('event','visit',{...online},'event_mode');
assert(!Object.hasOwn(F.prune('event','register',{...event,event_mode:'online'}),'event_location_address'));

const hire=fill('hire','apply',{hire_model:'remote',hire_qualifications:['none']});
assert(!has('hire','apply',hire,'hire_location_address'));
assert(!has('hire','apply',hire,'hire_experience'));
error('hire','apply',{...hire,hire_qualifications:['none','experience']},'hire_qualifications');
error('hire','apply',{...hire,hire_qualifications:['none',{}]},'hire_qualifications');
const mapped=fill('promote','visit');delete mapped.action_location_address;
assert.equal(F.validate('promote','visit',mapped).valid,true,'map-only location accepted');
delete mapped.action_location_map_url;error('promote','visit',mapped,'action_location_address');

const discount=fill('sell','purchase',{sell_offer:'discount',sell_show_price:'yes',sell_regular_price:100,sell_price:90});
assert.equal(F.validate('sell','purchase',discount).valid,true);
error('sell','purchase',{...discount,sell_price:110},'sell_price');
const nonprofitLiteral='<img src=x onerror=alert(1)>';
assert(F.summary('fundraise','understand',fill('fundraise','understand',{fundraise_goal:nonprofitLiteral})).some(r=>r.value===nonprofitLiteral),'summary remains literal; renderer owns escaping');
const fields=F.fields('sell','purchase',{});fields[0].options[0].label='tampered';
assert.notEqual(F.fields('sell','purchase',{})[0].options[0].label,'tampered','schema copies do not mutate internal definitions');
const unknown=F.prune('promote','remember',{...fill('promote','remember'),not_a_field:'discard',promote_name:{html:'invalid'}});
assert(!Object.hasOwn(unknown,'not_a_field'));
error('promote','remember',unknown,'promote_name');
assert(!F.fields('fundraise','donate',{}).some(f=>/iban/i.test(f.id)));
assert.equal(F.prune('hire','apply',{risk:'health',fundraise_goal:'discard'}).risk,'health','shared risk declaration not relabelled or discarded');
const ended=F.prune('hire','apply',{...hire,hire_deadline_status:'unknown',hire_deadline:'2026-11-01'});
assert(!Object.hasOwn(ended,'hire_deadline'));
const summaryZero=F.summary('fundraise','materials',materials);
assert(summaryZero.some(row=>row.label==='Hedef adet veya miktar'&&row.value==='0'));
console.log(`First-stage bank checks passed: ${F.intents().length} purpose banks, ${routes} compatible routes, typed branches, pruning and validation.`);
