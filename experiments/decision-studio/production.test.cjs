'use strict';
const assert=require('node:assert/strict');
const P=require('./dist/production.js');
const row=(id,amount=100)=>({channel:{id},amount,owned:false});
const build=(rows,patch={})=>P.build({mode:'paid',plan:{rows},organicPlatforms:[],videoAllowed:false,videoAvailable:false,...patch});
const search=build([row('google_search_maps'),row('meta_social',0)]);
assert.deepEqual(search.requirements.map(r=>r.medium),['text']);
assert.equal(search.ready,true);
assert.equal(search.publishable,false);
const core={id:'core-1',revision:2,title:'Yeni sezonu keşfet',angle:'Yeni sezon',message:'Özgün parçaları mağazada gör.',cta:'Mağazayı keşfet',kind:0,x:10,y:15};
const searchPreview=P.adapt(core,search.requirements);
assert.equal(searchPreview.length,1);
assert.equal(searchPreview[0].medium,'text');
assert.equal(searchPreview[0].destination,null);
assert.equal(Object.hasOwn(searchPreview[0],'caption'),false);
assert.equal(searchPreview[0].headlines.length,3);
const mixed=build([row('google_search_maps'),row('meta_social'),{...row('owned_crm'),owned:true}]);
assert.equal(mixed.requirements.length,2);
assert.deepEqual(new Set(P.adapt(core,mixed.requirements).map(r=>r.coreId)),new Set(['core-1']));
assert.ok(P.adapt(core,mixed.requirements).every(r=>r.coreRevision===2&&r.quality==='authored_demo'&&!r.publishable));
assert.notEqual(search.signature,mixed.signature);
assert.notEqual(search.signature,build([row('google_search_maps',200)]).signature);
assert.notEqual(search.signature,build([row('google_search_maps')],{videoAllowed:true}).signature);
const organic=P.build({mode:'organic',plan:{rows:[row('google_search_maps')]},organicPlatforms:['instagram','instagram','tiktok'],videoAllowed:false});
assert.equal(organic.requirements.length,2);
assert.ok(organic.requirements.every(r=>r.usage==='organic'));
assert.equal(organic.requirements.some(r=>r.channelId==='google_search_maps'),false);
assert.equal(organic.ready,false);
assert.equal(organic.requirements.find(r=>r.channelId==='tiktok').status,'blocked_material');
for(const id of ['tiktok','youtube','snapchat']){
  assert.equal(build([row(id)]).requirements[0].status,'blocked_material');
  const withMaterial=build([row(id)],{videoAllowed:true,videoAvailable:true});
  assert.equal(withMaterial.requirements[0].status,'production_pending');
  assert.equal(P.adapt(core,withMaterial.requirements).length,0);
}
assert.equal(build([row('unknown-product')]).ready,false);
assert.equal(build([row('unknown-product')]).requirements[0].status,'production_pending');
assert.equal(build([]).ready,false);
assert.equal(build([row('meta_social')]).requirements.length,1);
assert.equal(build([row('meta_social')],{videoAllowed:true,videoAvailable:true}).requirements.length,2);
assert.throws(()=>P.adapt({...core,revision:0},search.requirements));
assert.throws(()=>P.build({mode:'anything'}));
global.window={};require('./dist/data.js');
for(const channel of window.YaparoResearch.channels){
  const result=build([row(channel.id)]);
  if(channel.tier==='non_paid_recommendation')assert.equal(result.requirements.length,0);
  else assert.ok(result.requirements.length>0&&result.requirements.every(r=>r.purpose!=='Bu ürün için güvenilir üretim reçetesi yok'),channel.id);
}
console.log('Production contract passed: channel-specific requirements, Search-only text, organic bypass, material gates, core pins and recipe coverage.');
