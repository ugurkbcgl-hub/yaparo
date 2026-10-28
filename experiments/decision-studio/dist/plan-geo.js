/* Owned offline planning preview. Pinned Natural Earth land geometry is approximate;
   it is not official border data or evidence of a platform's targeting capability. */
(function (root, factory) {
  'use strict';
  const node = typeof module !== 'undefined' && module.exports;
  const api = factory(node ? require('./vendor/polygon-clipping-0.15.7.js') : root.polygonClipping,
    root.YaparoTurkey || root.window?.YaparoTurkey);
  if (node) module.exports = api;
  root.YaparoPlanGeo = api;
})(typeof globalThis !== 'undefined' ? globalThis : this, function (clipping, boundary) {
  'use strict';
  const version = 'yaparo-plan-geo-v1';
  const country = boundary?.geometry?.coordinates;
  const EARTH = 6371.0088, NS = 'http://www.w3.org/2000/svg';
  const radians = degrees => degrees * Math.PI / 180;
  const degrees = angle => angle * 180 / Math.PI;
  const finite = n => typeof n === 'number' && Number.isFinite(n);
  const provenance = Object.freeze({source:boundary?.source || null,sourceSha256:boundary?.sourceSha256 || null,
    license:boundary?.license || null,approximate:true,officialBoundary:false,externalQuery:false,platformVerified:false});

  function inRing(point, ring) {
    let contained = false;
    for (let i=0,j=ring.length-1;i<ring.length;j=i++) {
      const [x,y]=point,[ax,ay]=ring[j],[bx,by]=ring[i];
      const cross=(x-ax)*(by-ay)-(y-ay)*(bx-ax);
      if(Math.abs(cross)<1e-9 && x>=Math.min(ax,bx)-1e-9 && x<=Math.max(ax,bx)+1e-9 && y>=Math.min(ay,by)-1e-9 && y<=Math.max(ay,by)+1e-9)return true;
      if((by>y)!==(ay>y) && x<(ax-bx)*(y-by)/(ay-by)+bx)contained=!contained;
    }
    return contained;
  }
  function inside(point) {
    return Array.isArray(country) && Array.isArray(point) && point.length===2 && point.every(finite) &&
      country.some(poly=>inRing(point,poly[0])&&!poly.slice(1).some(hole=>inRing(point,hole)));
  }
  function ringArea(ring) {
    let result=0;
    for(let i=0;i<ring.length-1;i++)result+=radians(ring[i+1][0]-ring[i][0])*(2+Math.sin(radians(ring[i][1]))+Math.sin(radians(ring[i+1][1])));
    return Math.abs(result)*EARTH*EARTH/2;
  }
  function area(polygons) {
    return polygons.reduce((sum,poly)=>sum+Math.max(0,ringArea(poly[0])-poly.slice(1).reduce((holes,hole)=>holes+ringArea(hole),0)),0);
  }
  function circle(lat,lon,radius) {
    const ring=[],distance=radius/EARTH,a=radians(lat),b=radians(lon);
    for(let i=0;i<256;i++) {
      const bearing=2*Math.PI*i/256;
      const phi=Math.asin(Math.sin(a)*Math.cos(distance)+Math.cos(a)*Math.sin(distance)*Math.cos(bearing));
      const lambda=b+Math.atan2(Math.sin(bearing)*Math.sin(distance)*Math.cos(a),Math.cos(distance)-Math.sin(a)*Math.sin(phi));
      ring.push([degrees(lambda),degrees(phi)]);
    }
    ring.push([...ring[0]]);return [ring];
  }
  function calculate(selection) {
    const invalid = error => ({version,valid:false,error,geometry:null,areaKm2:null,rawAreaKm2:null,label:'Konum seçilmedi',clipped:true,verified:false,provenance});
    if(!country||!clipping?.intersection)return invalid('Yerel Türkiye harita verisi hazır değil.');
    if(!selection || !finite(selection.lat)||!finite(selection.lon)||!Number.isInteger(selection.radius)||selection.radius<1||selection.radius>800)
      return invalid('Türkiye içinden bir merkez ve 1–800 km arasında tam sayı bir mesafe seç.');
    const {lat,lon,radius}=selection;
    if(!inside([lon,lat]))return invalid('Merkez Türkiye kara sınırları içinde olmalı.');
    try {
      const raw=circle(lat,lon,radius),coordinates=clipping.intersection(country,raw);
      if(!coordinates.length)return invalid('Bu merkez için Türkiye içinde bir kapsama alanı hesaplanamadı.');
      return {version,valid:true,error:'',lat,lon,radius,
        geometry:{type:'MultiPolygon',coordinates},areaKm2:area(coordinates),rawAreaKm2:area([raw]),
        label:`${lat.toFixed(5)}° K, ${lon.toFixed(5)}° D · ${radius} km · Türkiye içinde`,
        clipped:true,verified:false,provenance};
    }catch{return invalid('Konum önizlemesi hesaplanamadı; merkezi veya mesafeyi yeniden seç.');}
  }
  const project=([lon,lat])=>[(lon-25.5)*600/19.5,(42.5-lat)*260/7];
  const unproject=([x,y])=>[x*19.5/600+25.5,42.5-y*7/260];
  function path(polygons) {
    return polygons.map(poly=>poly.map(ring=>ring.map((point,i)=>`${i?'L':'M'}${project(point).map(n=>n.toFixed(3)).join(',')}`).join(' ')+'Z').join(' ')).join(' ');
  }
  function mount(root,{onSelect}={}) {
    if(!root?.ownerDocument)throw new TypeError('Harita için bir ekran alanı gerekli.');
    const document=root.ownerDocument;
    const svgNode=(name,attributes={})=>{const n=document.createElementNS(NS,name);for(const [key,value]of Object.entries(attributes))n.setAttribute(key,String(value));return n;};
    const svg=svgNode('svg',{viewBox:'0 0 600 260',preserveAspectRatio:'xMidYMid meet',role:'img','aria-label':'Türkiye konum önizlemesi. Haritadan veya koordinat alanlarından merkez seçilebilir.'});
    svg.style.width='100%';svg.style.display='block';svg.style.cursor='crosshair';
    const base=svgNode('path',{d:country?path(country):'',fill:'#e7eeed',stroke:'#9eb6b0','stroke-width':1,'fill-rule':'evenodd'});
    const coverage=svgNode('path',{fill:'#257d6a','fill-opacity':0.35,stroke:'#247461','stroke-width':1,'fill-rule':'evenodd'});
    const pin=svgNode('circle',{r:4,fill:'#155b4f',stroke:'#fff','stroke-width':1.5});pin.style.display='none';
    const status=document.createElement('p');status.className='plan-map-status';status.setAttribute('role','status');status.setAttribute('aria-live','polite');
    svg.append(base,coverage,pin);root.replaceChildren(svg,status);
    let destroyed=false,current=null;
    function update(selection) {
      const result=calculate(selection);current=result.valid?result:null;
      coverage.setAttribute('d',current?path(current.geometry.coordinates):'');pin.style.display=current?'':'none';
      if(current){const [x,y]=project([current.lon,current.lat]);pin.setAttribute('cx',x);pin.setAttribute('cy',y);}
      status.textContent=current?`${current.label}. Deniz ve komşu ülke alanları kapsama alınmaz. Bu bir plan önizlemesidir; gerçek platform hedeflemesi doğrulanmadı.`:
        selection?result.error:'Haritadan bir merkez seç veya koordinatlarını gir. Otomatik konum alınmaz.';
      return result;
    }
    function choose(event) {
      if(destroyed||!finite(event.clientX)||!finite(event.clientY))return;
      const matrix=svg.getScreenCTM();if(!matrix)return;
      const point=svg.createSVGPoint();point.x=event.clientX;point.y=event.clientY;
      const local=point.matrixTransform(matrix.inverse()),[lon,lat]=unproject([local.x,local.y]);
      const selection={lat:Math.round(lat*100000)/100000,lon:Math.round(lon*100000)/100000};
      if(!inside([selection.lon,selection.lat])){status.textContent='Türkiye kara sınırları içinde bir merkez seç.';return;}
      if(typeof onSelect==='function')onSelect(selection);
    }
    svg.addEventListener('click',choose);update(null);
    return {update,destroy(){destroyed=true;svg.removeEventListener('click',choose);root.replaceChildren();}};
  }
  return Object.freeze({version,calculate,inside,mount,provenance});
});
