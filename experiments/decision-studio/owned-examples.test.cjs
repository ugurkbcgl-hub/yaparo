const assert=require('node:assert/strict');
const M=require('./dist/first-stage-bank.js'),X=require('./dist/simulation.js');
const expected={cafe:['promote','visit'],fashion:['promote','visit'],saas:['lead','lead_form'],home:['lead','call'],event:['event','register']};
assert.deepEqual(X.ids(),Object.keys(expected));
for(const id of X.ids()){
  const e=X.get(id),s=e.snapshot;
  assert.deepEqual([s.intent,s.outcome],expected[id]);
  assert.equal(e.origin,'authored_synthetic_example');
  assert.deepEqual(Object.keys(M.validate(s.intent,s.outcome,s.answers).errors),['delivery_mode'],id);
  assert.deepEqual(M.prune(s.intent,s.outcome,s.answers),s.answers,id);
  for(const mode of ['paid','organic','hybrid','content_only','unsure'])assert(M.validate(s.intent,s.outcome,{...s.answers,delivery_mode:mode}).valid,id+' '+mode);
  for(const key of ['delivery_mode','risk','budget','start','radius','business','sector','measurement','tracking'])assert(!Object.hasOwn(s.answers,key),id+' '+key);
  for(const [key,value]of Object.entries(s.answers)){
    if(key.endsWith('_url'))assert.equal(new URL(value).hostname,'ornek.example');
    assert(!key.endsWith('_start')&&!key.endsWith('_end'));
  }
  const subject=M.fields(s.intent,s.outcome,s.answers).find(f=>f.role==='subject');
  assert(s.answers[subject.id].startsWith('Sentetik '));
  s.answers[subject.id]='changed';assert.notEqual(X.get(id).snapshot.answers[subject.id],'changed');
}
for(const id of ['unknown','__proto__','constructor',null,{},1])assert.equal(X.get(id),null);
assert.notEqual(X.get('cafe').snapshot.answers.action_location_address,X.get('fashion').snapshot.answers.action_location_address);
assert(!Object.hasOwn(X.get('home').snapshot.answers,'action_url'));
assert(!Object.hasOwn(X.get('saas').snapshot.answers,'action_phone'));
console.log('Owned examples passed: five typed routes, usage remains explicit, synthetic endpoints, no planning/verification defaults and isolated copies.');
