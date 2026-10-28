'use strict';
const assert=require('node:assert/strict');
const fs=require('node:fs');
const path=require('node:path');
const crypto=require('node:crypto');
global.window={};
require('./dist/turkey-boundary.js');
const G=require('./dist/plan-geo.js');
const root=path.join(__dirname,'dist');
const hashes={
  'turkey-boundary.js':'2c74f7c7e56d986a731aac3b9da2635aad4e617bab3491c0528b537014e47cde',
  'vendor/polygon-clipping-0.15.7.js':'7f8619e84a86ce8dd400c9b50430e9c8cf8f26027b19eeb479f109f5c1a9d688'
};
for(const [file,expected]of Object.entries(hashes)) {
  const content=fs.readFileSync(path.join(root,file));
  assert.equal(crypto.createHash('sha256').update(content).digest('hex'),expected);
  assert.deepEqual(content,fs.readFileSync(path.join(__dirname,'../unified-journey/dist',file)));
}
const ankara={lat:39.9179,lon:32.8627,radius:1};
for(const bad of [null,{},[],{...ankara,lat:''},{...ankara,lat:NaN},{...ankara,lon:Infinity},
  {...ankara,lat:'39.9179'},{...ankara,radius:0},{...ankara,radius:801},
  {...ankara,radius:1.5},{...ankara,radius:'80'},{...ankara,radius:undefined},
  {...ankara,lat:51.5074,lon:-0.1278},{...ankara,lat:36,lon:32}]) {
  const r=G.calculate(bad);assert.equal(r.valid,false);assert.equal(r.geometry,null);assert.equal(r.areaKm2,null);assert.equal(r.verified,false);
}
assert.equal(G.inside([32.8627,39.9179]),true);
assert.equal(G.inside([0,0]),false);
assert.equal(G.inside([32.8627,'39.9179']),false);
assert.equal(G.inside([32.8627,39.9179,1]),false);
const small=G.calculate(ankara);
assert.equal(small.valid,true);assert.equal(small.geometry.type,'MultiPolygon');
assert.ok(small.areaKm2>3.13&&small.areaKm2<3.15);
assert.ok(Math.abs(small.areaKm2-small.rawAreaKm2)<1e-7);
assert.match(small.label,/1 km/);assert.equal(small.verified,false);
assert.equal(small.provenance.externalQuery,false);assert.equal(small.provenance.officialBoundary,false);
assert.equal(small.provenance.platformVerified,false);
const cases=[ankara,{...ankara,radius:800},{lat:41.677,lon:26.5558,radius:80},
  {lat:38.4189,lon:27.1287,radius:50},{lat:36.2,lon:36.16,radius:80}];
for(const point of cases) {
  const r=G.calculate(point);assert.equal(r.valid,true,JSON.stringify(point));
  assert.ok(r.geometry.coordinates.length>0);assert.ok(r.areaKm2>0);
  assert.ok(r.areaKm2<=r.rawAreaKm2+1e-6);
  for(const polygon of r.geometry.coordinates)for(const ring of polygon) {
    assert.deepEqual(ring[0],ring.at(-1));
    for(const point of ring)assert.equal(G.inside(point),true,'Clipped vertex is outside pinned Turkey geometry');
  }
}
const border=G.calculate(cases[2]);assert.ok(border.areaKm2<border.rawAreaKm2*.7);
const broad=G.calculate(cases[1]);assert.equal(broad.geometry.coordinates.length,6);
assert.deepEqual(G.calculate(ankara),small);
const mutable=G.calculate(ankara);mutable.geometry.coordinates[0][0][0][0]=0;
assert.deepEqual(G.calculate(ankara),small,'Separate calculations must not share mutable output geometry');
assert.equal(G.calculate(ankara).lat,ankara.lat);
assert.throws(()=>G.mount(null),TypeError);
console.log('Offline planning geo passed: exact pinned assets, 1–800 km validation, Turkey land clipping, border/coast limits and independent output geometry.');
