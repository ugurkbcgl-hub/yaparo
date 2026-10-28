const assert = require('node:assert/strict');
const c = require('./dist/v2-data.js');
const f = require('./dist/v2-flow.js');
assert.equal(c.routes.length, 200);
assert.equal(f.resolve(c, 'wrong', 'purchase').route, null);
assert.equal(f.matches({op:'eval', value:'true'}, {}), false);
assert.equal(f.matches({op:'all', args:[]}, {}), false);
assert.equal(f.matches({op:'eq', field:'x'}, {}), false);
assert.equal(f.matches({op:'cross_border'}, {target_countries:['DE']}), false);
assert.equal(f.matches({op:'cross_border'}, {business_country:'TR',target_countries:['DE']}), true);
for (const r of c.routes) {
  const s = f.resolve(c, r.intent_id, r.outcome_id);
  assert.equal(s.route.route_id, r.route_id);
  assert.equal(new Set(s.questions.map(q=>q.field_id)).size, s.questions.length);
  assert.equal(f.assess(c, s).ready, false);
  assert.equal(f.outcomes(c, r.intent_id).length, 20);
}
let s = f.resolve(c, 'sell', 'purchase', {delivery_mode:'paid', offer_type:'discount',reference_price_evidence:'Synthetic', purchase_url:'https://example.test', checkout_location:'website', unknown:'discard'});
assert(s.modules.includes('paid_budget')); assert(s.modules.includes('economics'));
assert(s.questions.some(q=>q.field_id==='purchase_url')); assert(!Object.hasOwn(s.answers,'unknown'));
s = f.resolve(c, 'sell', 'purchase', {...s.answers, checkout_location:'store', offer_type:'regular',delivery_mode:'organic'});
assert(!s.modules.includes('paid_budget')); assert(!s.modules.includes('economics'));
assert(!Object.hasOwn(s.answers,'purchase_url')); assert(!Object.hasOwn(s.answers,'reference_price_evidence'));
const url = c.questions.find(q=>q.field_id==='landing_url');
for (const bad of ['javascript:alert(1)','https://user:secret@example.test','not a url','']) assert.equal(f.valid(url,bad,c),false);
assert(f.valid(url,'https://example.test/path',c));
assert(!f.valid(c.questions.find(q=>q.type==='geo_picker'), 'Istanbul', c));
assert(!f.valid(c.questions.find(q=>q.field_id==='industry'), 'invented', c));
for (const [field,value] of [['radius_km',-1],['radius_km',0],['media_budget',-1],['contribution_margin',101]]) assert(!f.valid(c.questions.find(q=>q.field_id===field),value,c));
assert.throws(()=>f.assess(c,s,'invented'));
const complete = {};
for (const q of f.resolve(c,'sell','purchase').questions.filter(q=>q.required_for==='brief')) {
  complete[q.field_id] = q.type === 'select' ? c.options.find(o=>o.option_set_id===q.option_set_id).value : 'Sentetik örnek';
}
assert.equal(f.assess(c,f.resolve(c,'sell','purchase',complete)).ready,true);
assert.equal(f.assess(c,f.resolve(c,'sell','purchase',complete),'plan').ready,false);
console.log('V2: 200 routes, conditional modules, pruning and fail-closed qualification passed.');
