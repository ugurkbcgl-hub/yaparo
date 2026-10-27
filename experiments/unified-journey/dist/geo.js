"use strict";
window.YaparoGeo = (() => {
  const el = id => document.getElementById(id);
  const country = window.YaparoTurkey.geometry.coordinates;
  const options = window.YaparoChannels;
  const decisions = new Map(), priorities = new Map();
  const EARTH = 6371.0088;
  const presets = {istanbul:[41.005,29.04],ankara:[39.9179,32.8627],izmir:[38.4189,27.1287]};
  const money = n => new Intl.NumberFormat('tr-TR',{style:'currency',currency:'TRY',maximumFractionDigits:2}).format(n);
  const count = n => new Intl.NumberFormat('tr-TR',{maximumFractionDigits:0}).format(Math.floor(n));
  const radians = d => d * Math.PI / 180;
  const degrees = d => d * 180 / Math.PI;
  let cached = null, current = null;

  function inRing(point, ring) {
    let inside = false;
    for(let i=0,j=ring.length-1;i<ring.length;j=i++) {
      const [x,y]=point,[ax,ay]=ring[j],[bx,by]=ring[i];
      const cross=(x-ax)*(by-ay)-(y-ay)*(bx-ax);
      if(Math.abs(cross)<1e-9 && x>=Math.min(ax,bx)-1e-9 && x<=Math.max(ax,bx)+1e-9 && y>=Math.min(ay,by)-1e-9 && y<=Math.max(ay,by)+1e-9) return true;
      if((by>y)!==(ay>y) && x<(ax-bx)*(y-by)/(ay-by)+bx) inside=!inside;
    }
    return inside;
  }
  function inside(point, polygons=country) {
    return polygons.some(poly=>inRing(point,poly[0]) && !poly.slice(1).some(hole=>inRing(point,hole)));
  }
  function ringArea(ring) {
    let area=0;
    for(let i=0;i<ring.length-1;i++) {
      area+=radians(ring[i+1][0]-ring[i][0])*(2+Math.sin(radians(ring[i][1]))+Math.sin(radians(ring[i+1][1])));
    }
    return Math.abs(area)*EARTH*EARTH/2;
  }
  function area(polygons) {
    return polygons.reduce((sum,poly)=>sum+Math.max(0,ringArea(poly[0])-poly.slice(1).reduce((n,h)=>n+ringArea(h),0)),0);
  }
  function circle(lat,lon,radius) {
    const ring=[],d=radius/EARTH,a=radians(lat),b=radians(lon);
    for(let i=0;i<256;i++) {
      const bearing=2*Math.PI*i/256;
      const phi=Math.asin(Math.sin(a)*Math.cos(d)+Math.cos(a)*Math.sin(d)*Math.cos(bearing));
      const lambda=b+Math.atan2(Math.sin(bearing)*Math.sin(d)*Math.cos(a),Math.cos(d)-Math.sin(a)*Math.sin(phi));
      ring.push([degrees(lambda),degrees(phi)]);
    }
    ring.push([...ring[0]]); return [ring];
  }
  function geometry(lat,lon,radius) {
    const key=[lat,lon,radius].join('|');
    if(cached?.key===key) return cached;
    const raw=circle(lat,lon,radius);
    const clipped=window.polygonClipping.intersection(country,raw);
    if(!clipped.length) return null;
    cached={key,polygons:clipped,areaKm2:area(clipped),rawAreaKm2:area([raw]),raw};
    return cached;
  }
  function read() {
    const mode=el('geo-mode').value;
    if(mode==='country') return {mode,label:'Türkiye geneli',areaKm2:area(country),polygons:country};
    if(mode==='area') {
      const name=el('region').value.trim();
      return name.length>=2?{mode,label:`Türkiye içinde: ${name} (sınır çözümü bekliyor)`,areaKm2:null,polygons:[]}:null;
    }
    if(mode!=='radius') return null;
    const lat=Number(el('latitude').value),lon=Number(el('longitude').value),radius=Number(el('radius-number').value);
    if(!Number.isFinite(lat)||!Number.isFinite(lon)||!Number.isInteger(radius)||radius<1||radius>800||!inside([lon,lat])) return null;
    try {
      const clipped=geometry(lat,lon,radius);
      if(!clipped) return null;
      return {mode,lat,lon,radiusKm:radius,...clipped,label:`${lat.toFixed(5)}° K, ${lon.toFixed(5)}° D · ${radius} km ∩ Türkiye`};
    } catch { return null; }
  }
  const project=point=>[(point[0]-25.5)*600/19.5,(42.5-point[1])*260/7];
  function path(polygons) {
    return polygons.map(poly=>poly.map(ring=>ring.map((p,i)=>`${i?'L':'M'}${project(p).map(v=>v.toFixed(3)).join(',')}`).join(' ')+'Z').join(' ')).join(' ');
  }
  function draw(geo) {
    el('geo-country').setAttribute('d',path(country));
    el('geo-coverage').setAttribute('d',geo?.mode==='radius'||geo?.mode==='country'?path(geo.polygons):'');
    el('geo-circle-path').setAttribute('d',geo?.mode==='radius'?path([geo.raw]):'');
    el('geo-pin').style.display=geo?.mode==='radius'?'':'none';
    if(geo?.mode==='radius') {
      const [x,y]=project([geo.lon,geo.lat]);el('geo-pin').setAttribute('cx',x);el('geo-pin').setAttribute('cy',y);
    }
    el('geo-area-result').textContent=geo?.areaKm2!=null
      ? `Türkiye içinde kalan yaklaşık alan: ${count(geo.areaKm2)} km²${geo.mode==='radius'?` · Çemberin içeride kalan oranı: %${Math.round(100*geo.areaKm2/geo.rawAreaKm2)}`:''}. Deniz ve komşu ülke alanları plana dahil edilmez.`
      : 'Bölge adı için sınır çözümü henüz yok; alan ve yoğunluk hesabı yapılmaz.';
  }
  function support(channel,geo) {
    if(!geo) return {eligible:false,why:'Geçerli bir Türkiye konumu bekleniyor.'};
    if(geo.mode==='radius') {
      if(!channel.radius) return {eligible:false,why:channel.radiusMax&&geo.radiusKm>channel.radiusMax?`Seçilen ${geo.radiusKm} km, belgeli ${channel.radiusMax} km üst sınırını aşıyor.`:'Bu hassasiyette Türkiye yarıçap koşulları tam doğrulanmadı.'};
      if(geo.radiusKm<channel.radius[0]||geo.radiusKm>channel.radius[1]) return {eligible:false,why:`Yarıçap desteği ${channel.radius[0]}–${channel.radius[1]} km ile sınırlı.`};
      return {eligible:true,why:'Yarıçap türü belgeli. Türkiye kesişiminin gerçek platformda uygulanması ayrıca bekliyor.'};
    }
    if(channel[geo.mode]!==true) return {eligible:false,why:'Bu konum türü için Türkiye koşulları doğrulama bekliyor; destek yok demek değildir.'};
    return {eligible:true,why:'Coğrafi tür için plan adayı. Hesap, format ve gerçek hedef kimliği doğrulaması bekliyor.'};
  }
  function assumptions() {
    const cpm=Number(el('scenario-cpm').value),ctr=Number(el('scenario-ctr').value),density=Number(el('scenario-density').value),frequency=Number(el('scenario-frequency').value);
    if(!Number.isFinite(cpm)||cpm<1||cpm>10000||!Number.isFinite(ctr)||ctr<0||ctr>20||!Number.isFinite(density)||density<1||density>1000000||!Number.isFinite(frequency)||frequency<1||frequency>20) return null;
    return {cpm,ctr,density,frequency};
  }
  function calculate(geo) {
    const budget=Number(el('budget').value),valid=Number.isInteger(budget)&&budget>=100&&budget<=1000000;
    const rows=options.map(channel=>({...channel,...support(channel,geo)}));
    for(const row of rows) row.selected=row.eligible && decisions.get(row.id)!==false;
    const selected=rows.filter(row=>row.selected),weight=selected.reduce((n,row)=>n+(priorities.get(row.id)||1),0);
    let cents=valid&&geo?budget*100:0,remaining=cents;
    const assumption=assumptions();
    for(const row of rows) {
      row.amountCents=0;row.share=0;row.impressions=null;row.clicks=null;
      if(row.selected&&cents) {
        row.amountCents=row===selected[selected.length-1]?remaining:Math.floor(cents*(priorities.get(row.id)||1)/weight);
        remaining-=row.amountCents;row.share=row.amountCents/cents*100;
        if(assumption) {
          const theoretical=row.amountCents/100/assumption.cpm*1000;
          const capacity=geo.areaKm2==null?Infinity:geo.areaKm2*assumption.density*assumption.frequency*row.share/100;
          row.impressions=Math.min(theoretical,capacity);row.clicks=row.impressions*assumption.ctr/100;
        }
      }
    }
    return {rows,valid:valid&&Boolean(geo)&&selected.length>0&&Boolean(assumption),budget,assumption};
  }
  function changed() {document.dispatchEvent(new Event('yaparo-geography-change'));}
  function renderChannels(result) {
    const container=el('geo-channels');container.replaceChildren();
    for(const row of result.rows) {
      const section=document.createElement('section');section.className=`geo-channel ${row.selected?'geo-eligible':'geo-excluded'}`;section.dataset.channel=row.id;
      const label=document.createElement('label');label.className='channel-select';
      const checkbox=document.createElement('input');checkbox.type='checkbox';checkbox.checked=row.selected;checkbox.disabled=!row.eligible;checkbox.setAttribute('aria-label',`${row.name} kanalını seç`);
      checkbox.addEventListener('change',()=>{decisions.set(row.id,checkbox.checked);update();changed();});
      const name=document.createElement('strong');name.textContent=row.name;label.append(checkbox,name);
      const share=document.createElement('span');share.textContent=`%${row.share.toFixed(1)}`;
      const detail=document.createElement('p');detail.textContent=row.detail;
      const reason=document.createElement('p');reason.textContent=`${row.why} ${row.route}`;
      section.append(label,share,detail,reason);
      if(row.selected) {
        const preference=document.createElement('label');preference.textContent='Bütçe önceliği (1–10)';preference.className='channel-priority';
        const input=document.createElement('select');input.setAttribute('aria-label',`${row.name} bütçe önceliği`);
        for(let i=1;i<=10;i++){const option=document.createElement('option');option.value=i;option.textContent=i;input.append(option);}
        input.value=priorities.get(row.id)||1;input.addEventListener('change',()=>{priorities.set(row.id,Number(input.value));update();changed();});preference.append(input);section.append(preference);
      }
      const summary=document.createElement('p');summary.className='channel-estimate';
      summary.textContent=row.selected?`Senaryo bütçesi ${money(row.amountCents/100)} · ${row.impressions==null?'Varsayımlar geçersiz, hesap yok':`≈${count(row.impressions)} gösterim · ≈${count(row.clicks)} tıklama`}`:'%0 bütçe · Bu konum için senaryo hesabı yapılmaz';
      section.append(summary);
      const source=document.createElement('a');source.href=row.source;source.target='_blank';source.rel='noreferrer noopener';source.textContent='Koşulları ve kaynağı incele';section.append(source);container.append(section);
    }
    const allocated=result.rows.reduce((n,row)=>n+row.amountCents,0);
    const totalImpressions=result.rows.reduce((n,row)=>n+(row.impressions||0),0),totalClicks=result.rows.reduce((n,row)=>n+(row.clicks||0),0);
    el('google').value=result.rows.find(row=>row.id==='google').share;
    el('allocation-money').textContent=`Senaryoda dağıtılan ${money(allocated/100)} · Dağıtılmayan ${money(Math.max(0,(Number.isFinite(result.budget)?result.budget:0)*100-allocated)/100)} · Günlük ${money(allocated/100/Math.max(1,Number(el("duration").value)||1))}`;
    el('geo-total').textContent=allocated?`Toplam %100 · ${result.rows.filter(row=>row.selected).length} seçili coğrafi aday`:'Toplam %0 · Seçili uygun kanal yok veya alanlar geçersiz';
    el('scenario-totals').textContent=result.valid?`Örnek toplam: ≈${count(totalImpressions)} gösterim · ≈${count(totalClicks)} tıklama. Tekil kişi, satış veya garanti değildir.`:'Hesap için geçerli konum, bütçe, varsayımlar ve en az bir uygun kanal seç.';
  }
  function update() {
    const mode=el('geo-mode').value,radius=mode==='radius';
    el('geo-area').hidden=mode!=='area';el('geo-radius').hidden=!radius;
    el('region').disabled=mode!=='area';el('region').required=mode==='area';
    for(const id of ['latitude','longitude','radius-number','radius-range']){el(id).disabled=!radius;el(id).required=radius;}
    el('geo-center').disabled=!radius;
    const geo=read();current=calculate(geo);
    el('geo-status').textContent=geo?`${geo.label} · Yalnız Türkiye içinde kalan alan hedeflenir (taslak).`:'Konum geçersiz. Merkez Türkiye kara alanında ve yarıçap 1–800 km tam sayı olmalı; otomatik taşıma/genişletme yok.';
    el('radius-label').textContent=radius&&geo?`${geo.radiusKm} km`:'';
    if(radius&&geo)el('radius-range').value=geo.radiusKm;
    el('allocation-reason').textContent='Konum koşuluna uygun coğrafi adaylar önerilir. İstemediğin kanalı kapat; seçtiklerinin bütçe önceliğini ayarla. Başlangıç eşit paydır, performans sıralaması değildir. Hiçbir kanal bağlı veya yayına hazır değildir.';
    draw(geo);renderChannels(current);return geo;
  }
  for(const id of ['geo-mode','region','radius-number','scenario-cpm','scenario-ctr','scenario-density','scenario-frequency'])el(id).addEventListener(id==='geo-mode'?'change':'input',()=>{update();changed();});
  for(const id of ['latitude','longitude'])el(id).addEventListener('input',()=>{el('geo-center').value='custom';update();changed();});
  el('radius-range').addEventListener('input',()=>{el('radius-number').value=el('radius-range').value;update();changed();});
  el('geo-center').addEventListener('change',()=>{const p=presets[el('geo-center').value];if(p){el('latitude').value=p[0];el('longitude').value=p[1];}update();changed();});
  el('geo-map').addEventListener('click',event=>{
    if(el('geo-mode').value!=='radius')return;
    const rect=el('geo-map').getBoundingClientRect();el('longitude').value=(25.5+(event.clientX-rect.left)/rect.width*19.5).toFixed(6);el('latitude').value=(42.5-(event.clientY-rect.top)/rect.height*7).toFixed(6);el('geo-center').value='custom';update();changed();
  });
  return Object.freeze({update,inside,geometry,snapshot(){
    const geo=update();if(!geo||!current.valid)return null;
    return {...geo,checked:'2026-10-27',country:'TR',boundarySource:window.YaparoTurkey.source,operationalBoundaryVerified:false,
      assumptions:current.assumption,channels:current.rows.filter(row=>row.selected).map(({id,name,share,amountCents,impressions,clicks})=>({id,name,share,amountCents,impressions,clicks})),
      exclusions:current.rows.filter(row=>!row.selected).map(row=>`${row.name}: ${row.eligible?'Kullanıcı seçmedi':row.why}`).join(' · ')};
  }});
})();
