'use strict';
// Offline synthetic differential corpus. Never used by the application runtime.
const assert = require('node:assert/strict');
const crypto = require('node:crypto');
const fs = require('node:fs');
const path = require('node:path');
const M = require('./dist/first-stage-bank.js');
const C = require('./dist/outcome-contract.js');

const target = path.join(__dirname, 'server-bank-fixtures.json');
const sha = text => crypto.createHash('sha256').update(text).digest('hex');
function canonical(value) {
  if (Array.isArray(value)) return '[' + value.map(canonical).join(',') + ']';
  if (value && typeof value === 'object') return '{' + Object.keys(value).sort().map(key => JSON.stringify(key) + ':' + canonical(value[key])).join(',') + '}';
  return JSON.stringify(value);
}
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
function fill(intent, outcome, initial = {}) {
  let answers = structuredClone(initial);
  for (let n = 0; n < 30; n++) {
    const before = canonical(answers);
    for (const field of M.fields(intent, outcome, answers)) {
      if (answers[field.id] === undefined) answers[field.id] = sample(field);
    }
    answers = M.prune(intent, outcome, answers);
    if (before === canonical(answers)) return {version: C.snapshotVersion, intent, outcome, answers};
  }
  throw new Error('Synthetic fixture did not converge.');
}
function fieldSpec(field) {
  return {
    id: field.id, label: field.label, type: field.type, required: field.required,
    max_length: field.maxLength || 600, minimum: field.min ?? 0,
    maximum: field.max ?? 1e12, integer: field.step === 1,
    options: (field.options || []).map(option => [option.value, option.label]),
    role: field.role || null
  };
}
const field_specs = {};
const cases = [];
const seen = new Set();
function add(snapshot, name) {
  const key = canonical(snapshot);
  if (seen.has(key)) return false;
  seen.add(key);
  const {intent, outcome, answers} = snapshot;
  const checked = M.validate(intent, outcome, answers);
  const refs = M.fields(intent, outcome, checked.answers).map(field => {
    const spec = fieldSpec(field), hash = sha(canonical(spec));
    field_specs[hash] = spec;
    return hash;
  });
  const resolved = C.resolve(snapshot), analysis = C.analyze(snapshot);
  const analysisKeys = ['valid', 'intent', 'outcome', 'subject', 'identity', 'message', 'audienceLabel', 'ownedAudience', 'delivery', 'goal', 'communication', 'action', 'risk', 'riskDeclared', 'risks'];
  cases.push({
    name, snapshot, field_refs: refs,
    expected: {valid: checked.valid, error_keys: Object.keys(checked.errors).sort(), answers: checked.answers},
    resolved: {valid: resolved.valid, error_keys: Object.keys(resolved.errors).sort(), destination: resolved.destination, kpi: resolved.kpi, usage: resolved.usage, legacyProjection: resolved.legacyProjection},
    analysis: Object.fromEntries(analysisKeys.map(key => [key, analysis[key]]))
  });
  return true;
}
const bases = [];
for (const intent of M.intents()) for (const outcome of M.outcomes(intent.id)) {
  const snapshot = fill(intent.id, outcome.id);
  assert(M.validate(intent.id, outcome.id, snapshot.answers).valid);
  add(snapshot, intent.id + '/' + outcome.id + ':base');
  bases.push(snapshot);
}
assert.equal(bases.length, 46);

// Cover each enum transition once per purpose. This reaches conditional Other,
// messaging, price/date/location and multiselect detail fields without generating
// the exponential Cartesian product of unrelated answers. Route bases remain46.
const queue = bases.slice();
const transitions = new Set();
for (let cursor = 0; cursor < queue.length; cursor++) {
  assert(cases.length < 1400, 'Unexpected fixture growth; review exploration.');
  const snapshot = queue[cursor];
  for (const field of M.fields(snapshot.intent, snapshot.outcome, snapshot.answers)) {
    if (!['select', 'multiselect'].includes(field.type)) continue;
    for (const option of field.options) {
      const transition = snapshot.intent + '/' + field.id + '/' + option.value;
      if (transitions.has(transition)) continue;
      transitions.add(transition);
      const value = field.type === 'multiselect' ? [option.value] : option.value;
      const candidate = fill(snapshot.intent, snapshot.outcome, {...snapshot.answers, [field.id]: value});
      if (add(candidate, snapshot.intent + '/' + snapshot.outcome + ':' + field.id + '=' + option.value)) queue.push(candidate);
    }
  }
}

function mutate(base, changes, name, remove = []) {
  const snapshot = structuredClone(base);
  Object.assign(snapshot.answers, changes);
  for (const key of remove) delete snapshot.answers[key];
  add(snapshot, name);
}
const route = (intent, outcome) => bases.find(s => s.intent === intent && s.outcome === outcome);
const traffic = route('promote', 'traffic');
for (const url of ['javascript:alert(1)', 'https://user:pass@ornek.example/', 'https://ornek.example/a b', 'https:\\ornek.example/', 'https://ornek.example/\n']) {
  mutate(traffic, {action_url: url}, 'invalid-url:' + JSON.stringify(url));
}
mutate(traffic, {}, 'missing-required-url', ['action_url']);
mutate(traffic, {retired_business: 'clinic', accountReady: true}, 'hidden-authority-fields');
mutate(traffic, {promote_name: '  Somut sentetik açıklama  '}, 'trim-literal');
mutate(traffic, {promote_name: '😀'.repeat(81)}, 'utf16-length-overflow');
mutate(traffic, {promote_name: '😀'.repeat(80)}, 'utf16-length-boundary');
mutate(traffic, {}, 'missing-risk-remains-undeclared', ['risk']);
mutate(traffic, {delivery_mode: 'hybrid'}, 'actual-hybrid-delivery');
mutate(traffic, {risk: 'fundraising'}, 'explicit-fundraising-risk');
const ranged = fill('event', 'register', {event_timing: 'range'});
for (const date of ['2026-02-30', '1899-12-31', '2201-01-01', '2026-1-01']) {
  mutate(ranged, {event_start: date}, 'invalid-date:' + date);
}
mutate(ranged, {event_start: '2026-11-20', event_end: '2026-11-15'}, 'reversed-date-range');
mutate(fill('event', 'visit', {event_mode: 'online'}), {}, 'online-event-cannot-visit');
mutate(fill('event', 'register'), {}, 'location-missing', ['event_location_address', 'event_location_map_url']);
const discount = fill('sell', 'purchase', {sell_offer: 'discount', sell_show_price: 'yes'});
mutate(discount, {sell_price: 200, sell_regular_price: 100}, 'discount-above-old-price');
mutate(discount, {sell_price: -1}, 'negative-price');
mutate(discount, {sell_price: '10'}, 'numeric-string-refuses');
const quantity = fill('sell', 'purchase', {sell_conditions: 'quantity'});
mutate(quantity, {sell_min_quantity: 1.5}, 'fractional-integer-quantity');
const hire = route('hire', 'apply');
mutate(hire, {hire_qualifications: ['none', 'experience']}, 'hire-conflicting-qualification');
mutate(hire, {hire_qualifications: ['experience', 'experience']}, 'hire-duplicate-multiselect');
mutate(hire, {hire_qualifications: ['invented']}, 'hire-invalid-multiselect');
const hours = fill('announce', 'understand', {announce_kind: 'hours'});
mutate(hours, {announce_hours_start: '18:00', announce_hours_end: '08:00', announce_overnight: 'no'}, 'overnight-required');
mutate(hours, {announce_hours_start: '18:00', announce_hours_end: '08:00', announce_overnight: 'yes'}, 'overnight-allowed');
mutate(hours, {announce_hours_start: '24:00'}, 'invalid-time');
mutate(route('lead', 'call'), {action_phone: '123'}, 'short-phone');
mutate(route('lead', 'call'), {action_phone: '+90abc5550000000'}, 'invalid-phone');
mutate(fill('lead', 'lead_form', {action_lead_method: 'email'}), {action_email: 'x@y'}, 'invalid-email');
mutate(fill('fundraise', 'donate'), {risk: 'health'}, 'fundraising-health-retained');
mutate(fill('fundraise', 'materials'), {action_material_quantity: 0}, 'material-zero-unit-still-required');

// Outcome-sensitive branches that intentionally share a selector ID are sampled
// separately: paid price fields must disappear on non-enrolment community paths.
for (const outcome of M.outcomes('community')) {
  add(fill('community', outcome.id, {community_fee: 'paid', community_kind: 'course', community_mode: 'online'}), 'community/' + outcome.id + ':outcome-sensitive-price');
}

const sources = Object.fromEntries(['dist/first-stage-bank.js', 'dist/outcome-contract.js'].map(name => [name, sha(fs.readFileSync(path.join(__dirname, name), 'utf8').replace(/\r\n/g, '\n'))]));
const result = {
  schema: 'yaparo-server-bank-fixtures-v1', hash_normalization: 'utf8_lf', sources,
  coverage: {base_routes: bases.length, enum_transitions: transitions.size, cases: cases.length, field_specs: Object.keys(field_specs).length, exhaustive_combinations: false},
  field_specs, cases
};
const output = JSON.stringify(result) + '\n';
assert(Buffer.byteLength(output) <= 1_500_000, 'Corpus exceeds reviewed size bound.');
if (process.argv.includes('--check')) {
  assert.equal(fs.readFileSync(target, 'utf8').replace(/\r\n/g, '\n'), output, 'Bank fixture drift; review and regenerate.');
} else fs.writeFileSync(target, output, 'utf8');
console.log(JSON.stringify({...result.coverage, bytes: Buffer.byteLength(output), checked: process.argv.includes('--check')}));
