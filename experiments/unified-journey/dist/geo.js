"use strict";
window.YaparoGeo = (() => {
  const el = id => document.getElementById(id);
  const country = window.YaparoTurkey.geometry.coordinates;
  const options = window.YaparoChannels;
  const decisions = new Map(), shares = new Map(), shareErrors = new Set(), views = new Map();
  let selectionKey = "";
  const groupViews = new Map();
  let groupMode = null;
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
  // Largest-remainder apportionment keeps both percent basis points and kuruş exact.
  function apportion(total, ids, weight) {
    if (!ids.length) return new Map();
    let sum = ids.reduce((n,id)=>n+weight(id),0);
    const equal = sum===0;
    if(equal)sum=ids.length;
    const rows=ids.map((id,index)=>{const exact=total*(equal?1:weight(id))/sum;return {id,index,value:Math.floor(exact),fraction:exact-Math.floor(exact)};});
    let rest=total-rows.reduce((n,row)=>n+row.value,0);
    for(const row of [...rows].sort((a,b)=>b.fraction-a.fraction||a.index-b.index)) {if(rest<=0)break;row.value++;rest--;}
    return new Map(rows.map(row=>[row.id,row.value]));
  }
  function reconcile(ids) {
    const key=ids.join('|');if(key===selectionKey)return;
    const old=selectionKey?selectionKey.split('|'):[];
    const added=ids.filter(id=>!old.includes(id)),retained=ids.filter(id=>old.includes(id));
    let next;
    if(!retained.length)next=apportion(10000,ids,()=>1);
    else if(!added.length)next=apportion(10000,ids,id=>shares.get(id)||0);
    else {
      const newcomers=apportion(Math.round(10000*added.length/ids.length),added,()=>1);
      const remaining=10000-[...newcomers.values()].reduce((a,b)=>a+b,0);
      next=new Map([...newcomers,...apportion(remaining,retained,id=>shares.get(id)||0)]);
    }
    shares.clear();for(const [id,value]of next)shares.set(id,value);
    shareErrors.clear();selectionKey=key;
  }
  function setShare(id,raw) {
    const view=views.get(id),number=Number(raw);
    if(raw.trim()===''||!/^\d{1,3}(?:[.,]\d{1,2})?$/.test(raw)||!Number.isFinite(number)||number<0||number>100) {
      shareErrors.add(id);view.number.setCustomValidity('0–100 arasında, en fazla iki ondalıklı yüzde gir.');view.number.setAttribute('aria-invalid','true');update();changed();return;
    }
    const others=selectionKey.split('|').filter(other=>other!==id);
    if(!others.length)return;
    const target=Math.round(number*100);
    shares.set(id,target);
    for(const [other,value]of apportion(10000-target,others,other=>shares.get(other)||0))shares.set(other,value);
    shareErrors.delete(id);view.number.setCustomValidity('');view.number.removeAttribute('aria-invalid');
    update();changed();
  }
  function calculate(geo) {
    const budget=Number(el('budget').value),valid=Number.isInteger(budget)&&budget>=100&&budget<=1000000;
    const rows=options.map(channel=>({...channel,...support(channel,geo)}));
    for(const row of rows)row.selected=row.eligible&&decisions.get(row.id)!==false;
    const selected=rows.filter(row=>row.selected),ids=selected.map(row=>row.id);
    // Editing a coordinate is not an instruction to reset the last valid mixture.
    if(geo)reconcile(ids);
    const validShares=shareErrors.size===0;
    const cents=valid&&geo&&validShares?budget*100:0;
    const amounts=apportion(cents,ids,id=>shares.get(id)||0),assumption=assumptions();
    for(const row of rows) {
      row.share=row.selected?(shares.get(row.id)||0)/100:0;
      row.amountCents=amounts.get(row.id)||0;row.impressions=null;row.clicks=null;
      if(row.selected&&cents&&assumption) {
        const theoretical=row.amountCents/100/assumption.cpm*1000;
        const capacity=geo.areaKm2==null?Infinity:geo.areaKm2*assumption.density*assumption.frequency*row.share/100;
        row.impressions=Math.min(theoretical,capacity);row.clicks=row.impressions*assumption.ctr/100;
      }
    }
    return {rows,valid:valid&&Boolean(geo)&&ids.length>0&&Boolean(assumption)&&validShares,budget,assumption,validShares};
  }
  function changed(){document.dispatchEvent(new Event('yaparo-geography-change'));}
  function booklet(row) {
    const dialog=el('channel-guide');el('channel-guide-title').textContent=row.name;
    const content=el('channel-guide-content');content.replaceChildren();
    const entries=[['Reklam alanı',row.detail],['Konum durumu',row.why],['Erişim ve koşullar',row.route],['Pay ve sonuç',row.selected?`%${row.share.toFixed(2)} · ${money(row.amountCents/100)} senaryo bütçesi`:'Bu seçimde bütçe ayrılmıyor'],['Yüzde nasıl değişir?','Bir kanalın yüzdesini değiştirdiğinde kalan pay diğer seçili kanallara mevcut oranlarıyla dağılır. Oranları sıfırsa eşit bölünür. Tek kanal seçiliyse payı %100 kalır.'],['Hesabın sınırları','Gösterim/tıklama gerçek platform tahmini değildir. Ortak örnek varsayımlar kullanılır; sektör, içerik biçimi, hesap izinleri, envanter ve gerçek performans doğrulanmadı. Türkiye sınırında kesmenin gerçek platformda uygulanması ayrıca bekliyor.']];
    for(const [heading,text]of entries){const h=document.createElement('h3'),p=document.createElement('p');h.textContent=heading;p.textContent=text;content.append(h,p);}
    const source=document.createElement('a');source.href=row.source;source.target='_blank';source.rel='noreferrer noopener';source.textContent='Resmî koşulları incele ↗';content.append(source);dialog.showModal();
  }
  function buildChannels() {
    if(views.size)return;
    const container=el('geo-channels');container.replaceChildren();
    const groups=[['local','Konum çevresine uygun','Belgelenen yarıçap adayları'],['wide','Ülke / geniş alan adayları','Kesin yarıçap koşulları ayrıca doğrulanmalı'],['unknown','Konum koşulları doğrulama bekleyenler','Bilinmiyor, desteklemiyor anlamına gelmez']];
    const bodies=new Map();
    for(const [id,title,description]of groups){const section=document.createElement('details');section.className='channel-group';section.dataset.group=id;const heading=document.createElement('summary'),hint=document.createElement('p'),body=document.createElement('div');const size=options.filter(c=>(c.radius?'local':c.country?'wide':'unknown')===id).length;heading.textContent=`${title} · ${size}`;hint.textContent=description;hint.className='hint';section.append(heading,hint,body);bodies.set(id,body);groupViews.set(id,section);container.append(section);}
    for(const channel of options) {
      const section=document.createElement('section');section.className='channel-line';section.dataset.channel=channel.id;
      const head=document.createElement('div');head.className='channel-line-heading';
      const label=document.createElement('label');label.className='channel-select';
      const checkbox=document.createElement('input');checkbox.type='checkbox';checkbox.setAttribute('aria-label',`${channel.name} kanalını seç`);
      checkbox.addEventListener('change',()=>{decisions.set(channel.id,checkbox.checked);update();changed();});
      const name=document.createElement('strong');name.textContent=channel.name;label.append(checkbox,name);
      const book=document.createElement('button');book.type='button';book.className='channel-book';book.innerHTML='<svg viewBox="0 0 24 24" width="19" height="19" aria-hidden="true"><path d="M12 5C8 2 4 2 2 3v15c3-1 6-1 10 2 4-3 7-3 10-2V3c-2-1-6-1-10 2Zm0 0v15" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linejoin="round"/></svg>';book.title='Kanal rehberi';book.setAttribute('aria-label',`${channel.name} kanal rehberi`);book.addEventListener('click',()=>booklet(current.rows.find(row=>row.id===channel.id)));
      head.append(label,book);
      const bar=document.createElement('div');bar.className='channel-percent-bar';
      const numberLabel=document.createElement('label');numberLabel.className='percent-entry';
      const number=document.createElement('input');number.type='number';number.min='0';number.max='100';number.step='0.01';number.inputMode='decimal';number.setAttribute('aria-label',`${channel.name} bütçe yüzdesi`);const symbol=document.createElement('span');symbol.textContent='%';numberLabel.append(number,symbol);
      const range=document.createElement('input');range.type='range';range.min='0';range.max='100';range.step='0.01';range.setAttribute('aria-label',`${channel.name} pay çubuğu`);
      number.addEventListener('input',()=>setShare(channel.id,number.value));
      number.addEventListener('blur',()=>{if(!shareErrors.has(channel.id))number.value=((shares.get(channel.id)||0)/100).toFixed(2);});
      range.addEventListener('input',()=>{shareErrors.delete(channel.id);number.setCustomValidity('');number.removeAttribute('aria-invalid');setShare(channel.id,range.value);});
      bar.append(numberLabel,range);
      const details=document.createElement('details');details.className='channel-inline-details';
      const summary=document.createElement('summary');summary.textContent='Özet ve açıklama';const estimate=document.createElement('p'),reason=document.createElement('p');details.append(summary,estimate,reason);
      section.append(head,bar,details);
      bodies.get(channel.radius?'local':channel.country?'wide':'unknown').append(section);
      views.set(channel.id,{section,checkbox,number,range,estimate,reason});
    }
  }
  function renderChannels(result) {
    buildChannels();
    const mode=el('geo-mode').value;
    if(mode!==groupMode){groupViews.get('local').open=true;groupViews.get('wide').open=mode==='country';groupViews.get('unknown').open=false;groupMode=mode;}
    const selectedCount=result.rows.filter(row=>row.selected).length;
    for(const row of result.rows) {
      const view=views.get(row.id);view.section.classList.toggle('channel-disabled',!row.eligible);view.checkbox.checked=row.selected;view.checkbox.disabled=!row.eligible;
      const disabled=!row.selected||selectedCount===1;
      view.number.disabled=view.range.disabled=disabled;
      if(!shareErrors.has(row.id)) {view.number.setCustomValidity('');view.number.removeAttribute('aria-invalid');if(document.activeElement!==view.number)view.number.value=row.share.toFixed(2);}
      if(document.activeElement!==view.range)view.range.value=row.share;
      view.range.style.setProperty('--share',`${row.share}%`);
      view.estimate.textContent=row.selected?`Senaryo bütçesi ${money(row.amountCents/100)} · ${row.impressions==null?'Geçerli alan/varsayım bekleniyor':`≈${count(row.impressions)} gösterim · ≈${count(row.clicks)} tıklama`}`:'%0 bütçe · Bu seçim için senaryo hesabı yok';
      view.reason.textContent=`${row.why} ${row.route}`;
    }
    const allocated=result.rows.reduce((n,row)=>n+row.amountCents,0),totalImpressions=result.rows.reduce((n,row)=>n+(row.impressions||0),0),totalClicks=result.rows.reduce((n,row)=>n+(row.clicks||0),0);
    el('google').value=result.rows.find(row=>row.id==='google').share;
    el('allocation-money').textContent=`Dağıtılan ${money(allocated/100)} · Kalan ${money(Math.max(0,(Number.isFinite(result.budget)?result.budget:0)*100-allocated)/100)} · Günlük ${money(allocated/100/Math.max(1,Number(el('duration').value)||1))}`;
    el('geo-total').textContent=!result.validShares?'Yüzdeyi 0–100 arasında, en fazla iki ondalıkla gir. Geçerli paylar bekleniyor.':allocated?`Toplam %100 · ${selectedCount} seçili kanal`:'Toplam %0 · Seçili uygun kanal yok veya alanlar geçersiz';
    el('scenario-totals').textContent=result.valid?`Senaryo: ≈${count(totalImpressions)} gösterim · ≈${count(totalClicks)} tıklama`:'Hesap için geçerli konum, bütçe, yüzdeler, varsayımlar ve en az bir uygun kanal seç.';
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
    el('allocation-reason').textContent='Kanalları seç, yüzdeyi yaz veya çubuğu sürükle. Diğer seçili paylar otomatik dengelenir; toplam %100 kalır. Kitap simgesi kanal rehberini açar. Hiçbir kanal bağlı değildir.';
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
