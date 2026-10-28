/* Compact owned planning view. Local synthetic proposals only. */
(function () {
  'use strict';
  if(location.pathname==='/legacy.html')return;
  const $=id=>document.getElementById(id), studio=window.YaparoStudio;
  const money=n=>new Intl.NumberFormat('tr-TR',{style:'currency',currency:'TRY',maximumFractionDigits:2}).format(n/100);
  const node=(tag,text,cls)=>{const n=document.createElement(tag);if(text!==undefined)n.textContent=text;if(cls)n.className=cls;return n;};
  const button=(text,fn,cls='text-button')=>{const b=node('button',text,cls);b.type='button';b.addEventListener('click',fn);return b;};
  const banner=document.querySelector('.demo-banner p'),originalBanner=banner.textContent;
  const snap=()=>studio.getSnapshot(), brief=()=>snap().firstStage, usage=()=>brief()?.answers.delivery_mode;
  const paid=()=>['paid','hybrid'].includes(usage());
  const summary=()=>brief()?window.YaparoFirstStage.summary(brief().intent,brief().outcome,brief().answers):[];
  let lastBrief='', lastPair='', lastAudience='', lastPlan=null;
  document.body.classList.add('owned-planning');
  const form=$('plan-form'), controls=$('plan-controls'), results=$('plan-results');
  const heading=$('step-1').querySelector('.section-heading h1'), lead=$('step-1').querySelector('.lead');
  const briefPanel=node('section',undefined,'plan-brief');briefPanel.id='plan-brief-summary';
  const briefTitle=node('h2'), briefLine=node('p'), audienceLine=node('p');
  const edit=button('Değiştir',()=>studio.go(0));briefPanel.append(briefTitle,briefLine,audienceLine,edit);
  const answers=node('details'), answersTitle=node('summary','İlk aşamadaki bilgilerin');answers.append(answersTitle);const answerList=node('dl');answers.append(answerList);briefPanel.append(answers);
  form.prepend(briefPanel);
  const bounds=node('section',undefined,'plan-card');bounds.id='plan-bounds';bounds.append(node('h2','Planın sınırları'),node('p','Yalnız eksik bilgileri tamamla. Tercihlerin değişirse dağılımı yeniden öneririz.','plan-muted'));
  const fields=node('div',undefined,'plan-fields');bounds.append(fields);controls.prepend(bounds);
  function moveField(id,label,parent=fields){const control=$(id), box=node('div',undefined,'plan-field'), title=node('label',label);title.htmlFor=id;box.append(title,control);parent.append(box);return box;}
  const geoBox=moveField('geo-mode','Nerede?');
  const empty=node('option','Bölgeni seç');empty.value='';$('geo-mode').prepend(empty);$('geo-mode').value='';
  const regionBox=moveField('region','Şehir / bölge');$('region').value='';$('region').placeholder='Örn. Ankara, Çankaya';regionBox.append(node('small','Bu bölge bir plan notudur; gerçek platform hedeflemesi ayrıca doğrulanır.'));
  const audienceBox=moveField('audience','Kime ulaşalım?');
  const audienceEmpty=node('option','Kitleyi seç');audienceEmpty.value='';$('audience').prepend(audienceEmpty);$('audience').value='';
  const audienceLabels={b2c_new:'Yeni müşteriler',b2c_existing:'Mevcut müşteriler',b2b_decision_makers:'İşletmelerde karar verenler',professionals_job_seekers:'Profesyoneller / iş arayanlar',young_18_24:'18–24 yaş yetişkinler',parents_families:'Ebeveynler / aileler',high_intent_searchers:'İlgili konuda arama yapanlar',local_nearby:'Yakındaki kişiler',broad_mass:'Genel kitle'};
  for(const option of $('audience').options)if(audienceLabels[option.value])option.textContent=audienceLabels[option.value];
  const budgetBox=moveField('budget','Toplam reklam bütçesi (TL)');$('budget').value='';$('budget').min='1';$('budget').placeholder='Ayırmak istediğin toplam tutar';
  const presets=node('div',undefined,'plan-presets');for(const amount of [1000,3000,5000])presets.append(button(`${amount.toLocaleString('tr-TR')} TL`,()=>{$('budget').value=amount;$('budget').dispatchEvent(new Event('input',{bubbles:true}));}));budgetBox.append(presets,node('small','Yalnız medya bütçesi. İçerik üretimi ve hizmet bedeli ayrıca gösterilir; bu demoda hesaplanmaz.'));
  const startBox=moveField('start','Yayın başlangıcı');$('start').value='';
  const endBox=node('div',undefined,'plan-field'),endLabel=node('label','Yayın bitişi'),end=node('input');end.id='plan-end';end.type='date';end.required=true;endLabel.htmlFor=end.id;endBox.append(endLabel,end);fields.append(endBox);
  const datesNote=node('p',undefined,'plan-muted');datesNote.id='plan-date-note';bounds.append(datesNote);
  const radiusSection=node('section',undefined,'plan-map-section');radiusSection.id='plan-radius-section';bounds.append(radiusSection);
  $('radius-field').removeAttribute('id');
  const radiusField=moveField('radius','Konumun çevresi (km)',radiusSection);radiusField.id='radius-field';$('radius').value='';$('radius').min='1';$('radius').max='800';$('radius').required=true;
  const mapRoot=node('div');mapRoot.id='plan-map';radiusSection.append(mapRoot);
  const coords=node('div',undefined,'plan-coordinates');
  for(const [id,label,min,max] of [['plan-latitude','Enlem',35,43],['plan-longitude','Boylam',25,45]]){const box=node('div'),l=node('label',label),input=node('input');input.id=id;input.type='number';input.step='0.00001';input.min=min;input.max=max;l.htmlFor=id;box.append(l,input);coords.append(box);}
  const precise=node('details');precise.id='plan-coordinate-details';precise.append(node('summary','Hassas konum için koordinat gir'),coords);radiusSection.append(precise,node('p','Harita seçimi yaklaşık konumdur; hassas merkez için koordinat girebilirsin. Daire Türkiye kara sınırıyla kesilir; gerçek platform hedeflemesi doğrulanmış sayılmaz.','plan-muted'));bounds.append(radiusSection);
  const geoView=window.YaparoPlanGeo.mount(mapRoot,{onSelect:({lat,lon})=>{$('plan-latitude').value=lat;$('plan-longitude').value=lon;updateMap();studio.planChanged();updateFooter();}});
  const advanced=node('details',undefined,'plan-card plan-advanced');advanced.id='plan-advanced';advanced.append(node('summary','Öneri için ek bilgiler'));controls.append(advanced);
  advanced.append($('owned-plan-context'));
  const refineAudience=node('div');refineAudience.id='plan-audience-refinement';refineAudience.append(node('h3','Kitleyi daha ayrıntılı seç'),audienceBox);advanced.append(refineAudience);
  advanced.append(moveField('measurement','Ölçüm hazırlığı',node('div')));
  const economics=$('plan-controls').querySelector('.economics');economics.querySelector('summary').textContent='İş ekonomisi · isteğe bağlı';
  const economicsChoice=node('label',undefined,'check-label'),economicsCheck=node('input');economicsCheck.id='plan-economics-enabled';economicsCheck.type='checkbox';economicsChoice.append(economicsCheck,document.createTextNode('Kapasite ve kârlılık sınırı eklemek istiyorum'));
  economics.querySelector('.details-inner').prepend(economicsChoice);advanced.append(economics);
  const simulation=node('details');simulation.id='plan-simulation';simulation.append(node('summary','Demo varsayımları ve kaynak bilgisi'),node('p','Kanal hesabı, maliyetler ve erişim sayıları hazırlanmış örneklerdir. Gerçek hesap bağlantısı veya sonuç garantisi yok.','plan-muted'));
  simulation.append(moveField('fixture','Örnek veri',node('div')),moveField('demo-readiness','Örnek hesap hazırlığı',node('div')));
  if($('source-panel'))simulation.append($('source-panel'));
  advanced.append(simulation);
  // Keep source controls for compatibility, but only expose relevant fields above.
  const sourceControls=node('div');sourceControls.hidden=true;sourceControls.id='plan-source-controls';
  for(const child of [...controls.children])if(child!==bounds&&child!==advanced)sourceControls.append(child);
  controls.replaceChildren(bounds,advanced,sourceControls);
  $('goal').disabled=true;
  $('duration').required=false;
  const productionDetails=node('details',undefined,'plan-card plan-production-details');productionDetails.append(node('summary','İçerik ve yayın hazırlığı'));
  productionDetails.append($('material-controls'),$('plan-production'),$('owned-outcome-summary'));form.append(productionDetails);
  $('owned-plan-note').hidden=true;
  const toolbar=results.querySelector('.decision-toolbar');toolbar.querySelector('strong').textContent='Bütçeni uygun kanallara paylaştıralım.';toolbar.querySelector('p').textContent='Yerel demo · gerçek erişim veya satış tahmini değil.';
  $('recommend').textContent='Dağılım öner';toolbar.append(node('small','Yeniden öneri, elle değiştirdiğin payları güncel seçimlere göre sıfırlar.'));
  const footer=form.querySelector('.form-footer');footer.classList.add('plan-footer');const footerSummary=node('p');footerSummary.id='plan-footer-summary';footer.prepend(footerSummary);form.append(footer);
  footer.querySelector('button[type="submit"]').textContent='İçeriklere devam et ↗';
  function roleAudience(){const s=brief();if(!s)return '';const f=window.YaparoFirstStage.fields(s.intent,s.outcome,s.answers).find(f=>f.role==='audience');return f?summary().find(r=>r.label===f.label)?.value||'':'';}
  function updateMap(){const selection={lat:Number($('plan-latitude').value),lon:Number($('plan-longitude').value),radius:Number($('radius').value)};return geoView.update($('plan-latitude').value&&$('plan-longitude').value&&$('radius').value?selection:null);}
  function syncDates(){end.min=$('start').value;const start=Date.parse($('start').value),finish=Date.parse(end.value);end.setCustomValidity(Number.isFinite(start)&&Number.isFinite(finish)&&finish<start?'Bitiş başlangıçtan önce olamaz.':'');const days=Math.round((finish-start)/86400000)+1;$('duration').value=Number.isInteger(days)&&days>0?days:'';end.max=$('start').value?new Date(start+364*86400000).toISOString().slice(0,10):'';}
  function updateFooter(){const stale=snap().stale;results.querySelector('.channel-section-heading h2').textContent=stale&&lastPlan?'Önceki dağılım · yeniden öner':'Planında yer alanlar';if(stale)for(const control of form.querySelectorAll('#recommended input,#other-channels input'))control.disabled=true;const date=$('start').value&&end.value?`${$('start').value} – ${end.value}`:'Tarih seçilmedi';const budget=paid()&&$('budget').value?money(Math.round(Number($('budget').value)*100)):paid()?'Bütçe seçilmedi':'Medya bütçesi yok';if(!paid()){footerSummary.textContent=usage()==='content_only'?'Kanaldan bağımsız içerik · medya bütçesi yok':usage()==='unsure'?'Önce kullanım yolunu seç.':'Kendi hesaplarında paylaşım · medya bütçesi yok';return;}footerSummary.textContent=`${budget} · ${$('geo-mode').value==='country'?'Türkiye geneli':$('geo-mode').value==='radius'&&$('plan-latitude').value?`${$('radius').value} km · seçilen konum`:$('region').value||'Bölge seçilmedi'} · ${paid()?date:'Ücretli kanal seçimi yok'}${lastPlan&&!snap().stale?' · '+lastPlan.rows.filter(r=>r.amount>0).length+' kanal':''}`;}
  function configure(){
    const isPaid=paid(),mode=usage(),commerce=['promote','sell','lead'].includes(brief()?.intent);
    heading.textContent=isPaid?'Bütçen, bölgen, doğru kanallar.':mode==='content_only'?'İçeriğinin biçimini seç.':'Nerede paylaşmak istiyorsun?';
    lead.textContent=isPaid?'İsteğini biliyoruz. Planın sınırlarını belirle; payları birlikte netleştirelim.':'İsteğin korundu. Yalnız bu kullanım için gerekli seçimlerle devam et.';
    controls.hidden=!isPaid;results.hidden=!isPaid;bounds.hidden=!isPaid;advanced.hidden=!isPaid;
    for(const c of controls.querySelectorAll('input,select,textarea'))c.disabled=!isPaid;
    $('goal').disabled=true;
    for(const id of ['region','radius','budget','start'])$(id).required=isPaid;
    end.required=isPaid;
    regionBox.hidden=$('geo-mode').value==='country'||$('geo-mode').value==='radius';$('region').disabled=!isPaid||regionBox.hidden;
    $('region').required=isPaid&&!regionBox.hidden;
    radiusSection.hidden=!isPaid||$('geo-mode').value!=='radius';
    for(const c of radiusSection.querySelectorAll('input'))c.disabled=radiusSection.hidden;
    for(const id of ['plan-latitude','plan-longitude'])$(id).required=false;
    economics.hidden=!isPaid||!commerce;
    for(const id of ['order-value','margin','cpa','capacity']){$(id).disabled=!isPaid||!commerce||!economicsCheck.checked;$(id).required=isPaid&&commerce&&economicsCheck.checked;}
    $('fixture').disabled=!isPaid;$('demo-readiness').disabled=!isPaid;
    const audience=roleAudience();audienceLine.textContent=audience?`Kitle: ${audience}`:'';audienceLine.hidden=!audience;
    $('audience').required=isPaid&&!audience;
    if(!audience)fields.insertBefore(audienceBox,budgetBox);else refineAudience.append(audienceBox);
    const c=window.YaparoOutcomeContract.resolve(brief());$('owned-plan-context').hidden=!isPaid||!c.legacyProjection;
    productionDetails.hidden=mode==='unsure';
    $('organic-controls').hidden=!['organic','hybrid'].includes(mode);
    $('owned-content-formats').hidden=mode!=='content_only';
    $('owned-plan-note').hidden=true;updateMap();syncDates();updateFooter();
  }
  function prefill(b){
    const signature=window.YaparoOutcomeContract.signature(b.firstStage);
    if(signature!==lastBrief){const first=!lastBrief,pair=b.firstStage.intent+'/'+b.firstStage.outcome;if(!first){if(pair!==lastPair||lastAudience!==roleAudience())$('audience').value='';if(pair!==lastPair){economicsCheck.checked=false;for(const id of ['order-value','margin','cpa','capacity'])$(id).value='';}}lastPair=pair;lastAudience=roleAudience();lastBrief=signature;lastPlan=null;if(first){for(const id of ['budget','region','radius','plan-latitude','plan-longitude','start','plan-end','duration','audience','order-value','margin','cpa','capacity'])$(id).value='';$('geo-mode').value='';$('measurement').value='none';economicsCheck.checked=false;}
      const a=b.firstStage.answers;
      if(b.firstStage.intent==='sell'&&a.sell_timing==='range'&&!$('start').value&&!end.value){$('start').value=a.sell_start||'';end.value=a.sell_end||'';}
      datesNote.textContent=a.event_start?`Etkinlik tarihi: ${a.event_start}${a.event_end?' – '+a.event_end:''}. Reklamın yayın aralığını ayrıca seç.`:'';
    }
    const c=b.outcomeContract||window.YaparoOutcomeContract.resolve(b.firstStage);briefTitle.textContent=c.intentLabel||'İsteğin';briefLine.textContent=c.outcomeLabel||'';
    answerList.replaceChildren();for(const row of b.firstStageSummary||[])answerList.append(node('dt',row.label),node('dd',row.value));
    configure();
  }
  function issue(){
    if(!paid())return '';
    if(!$('geo-mode').value)return 'Önce reklamın bölgesini seç.';
    if($('geo-mode').value!=='country'&&$('geo-mode').value!=='radius'&&!$('region').value.trim())return 'Şehir veya bölgeyi yaz.';
    if($('geo-mode').value==='radius'){const map=updateMap();if(!map?.valid)return 'Türkiye içinde bir konum ve 1–800 km arasında bir mesafe seç.';}
    if(!$('budget').value||!$('budget').checkValidity())return 'Toplam reklam bütçeni belirt.';
    syncDates();if(!$('start').value||!end.value||!end.checkValidity()||!$('duration').value)return 'Geçerli bir yayın başlangıcı ve bitişi seç (en fazla 365 gün).';
    if(!roleAudience()&&!$('audience').value)return 'Ulaşmak istediğin kitleyi seç.';
    return '';
  }
  function inputPatch(){const isEconomics=paid()&&!economics.hidden&&economicsCheck.checked;return {economicsMode:isEconomics?'provided':'not_provided',...(isEconomics?{}:{value:0,margin:0,cpa:0,capacity:0}),audience:$('audience').value||'owned_declared',...(paid()&&$('geo-mode').value==='radius'?{region:'Haritada seçilen konum',geoCenter:{lat:Number($('plan-latitude').value),lon:Number($('plan-longitude').value),boundary:window.YaparoPlanGeo.version||'pinned-turkey',verified:false}}:{})};}
  function share(plan,row,value){try{const result=studio.changeShare(row.channel.id,Number(value));$('decision-status').textContent=result.limited?'Pay, kanalın test minimumu veya bütçe sınırında tutuldu. Diğer paylar dengelendi.':'Paylar güncellendi. Diğer seçili kanallar orantılı dengelendi; yeniden öneri elle yaptığın değişikliği sıfırlar.';updateFooter();}catch(error){$('decision-status').textContent=error.message;renderPlan(plan);}}
  function renderPlan(plan){
    lastPlan=plan;const stats=$('plan-summary');stats.replaceChildren();for(const [label,amount] of [['Toplam',plan.total],['Kanallara ayrılan',plan.allocated],['Ayrılmayan',plan.unallocated]]){const box=node('div',undefined,'summary-stat');box.append(node('span',label),node('strong',money(amount)));stats.append(box);}
    const upper=$('recommended'),lower=$('other-channels');upper.replaceChildren();lower.replaceChildren();
    const groups={};for(const [key,label] of [['paid','Diğer reklam kanalları'],['managed','Partner / yönetilen kanallar'],['owned','Medya bütçesi dışındaki yollar']]){const section=node('section',undefined,'catalog-group');section.append(node('h3',label));lower.append(section);groups[key]=section;}
    for(const row of [...plan.rows].sort((a,b)=>b.amount-a.amount||b.score-a.score)){
      const article=node('article',undefined,row.amount?'compact-channel':'compact-other');article.dataset.channel=row.channel.id;
      const check=node('input');check.type='checkbox';check.checked=row.amount>0;check.disabled=!row.eligible||snap().stale;check.setAttribute('aria-label',`${row.channel.name} seç`);check.addEventListener('change',()=>{if(check.checked){const limits=window.YaparoPlanSummary.limits(plan,row.channel.id);share(plan,row,limits.minPercent);}else share(plan,row,0);});
      const name=node('strong',row.channel.name), info=button('ⓘ',()=>studio.guideChannel(row.channel.id),'book-button');info.setAttribute('aria-label',`${row.channel.name} neden ve koşullar`);article.append(check,name);
      if(row.amount){
        const input=node('input');input.type='number';input.required=true;input.min='0';input.max='100';input.step='0.01';input.value=(row.amount/plan.total*100).toFixed(2);input.setAttribute('aria-label',`${row.channel.name} payı yüzde`);input.disabled=snap().stale;input.addEventListener('change',()=>{if(!input.value.trim()||!input.checkValidity()){$('decision-status').textContent='0–100 arasında bir yüzde yaz.';input.value=(row.amount/plan.total*100).toFixed(2);return;}share(plan,row,input.value);});
        const slider=node('input');slider.type='range';slider.min='0';slider.max='100';slider.step='0.01';slider.value=input.value;slider.disabled=snap().stale;slider.setAttribute('aria-label',`${row.channel.name} payını ayarla`);slider.addEventListener('input',()=>{try{
          const preview=structuredClone(plan);window.YaparoPlanSummary.redistribute(preview,row.channel.id,Number(slider.value));
          for(const candidate of preview.rows){
            const current=upper.querySelector(`[data-channel="${candidate.channel.id}"]`);if(!current)continue;
            const value=(candidate.amount/preview.total*100).toFixed(2);current.querySelector('input[type=number]').value=value;
            if(candidate.channel.id!==row.channel.id)current.querySelector('input[type=range]').value=value;
            current.querySelector('.compact-amount').textContent=money(candidate.amount);
          }
          const reserve=upper.querySelector('.plan-reserve');if(reserve)reserve.textContent=`Önizleme · ayrılmayan pay: %${(preview.total?preview.unallocated/preview.total*100:0).toLocaleString('tr-TR',{maximumFractionDigits:2})} · ${money(preview.unallocated)}. Bıraktığında uygulanır.`;
        }catch(error){$('decision-status').textContent=error.message;}});slider.addEventListener('change',()=>share(plan,row,slider.value));slider.addEventListener('pointercancel',()=>renderPlan(plan));
        const pct=node('label',undefined,'compact-percent');pct.append(input,document.createTextNode('%'));
        article.append(pct,slider,node('span',money(row.amount),'compact-amount'),info);
        const detail=node('details');detail.append(node('summary','Örnek sonuç / neden'),node('p',`Başarı göstergesi: ${window.YaparoOutcomeContract.resolve(brief()).kpi.label}. Bu sonuç için doğrulanmış tahmin yok.`, 'plan-muted'));
        if(plan.interactive){const clicks=row.f.cpc>0?Math.floor(row.amount/100/row.f.cpc):0;detail.append(node('p',`${Math.floor(clicks*.7).toLocaleString('tr-TR')}–${Math.floor(clicks*1.3).toLocaleString('tr-TR')} örnek tıklama · hazırlanmış demo hesabı; beklenen hedef sonucu veya tekil kişi sayısı değildir.`,'plan-muted'));}
        article.append(detail);upper.append(article);
      }else{article.append(info);const detail=node('details');detail.append(node('summary',row.eligible?'Pay ekleyebilirsin':row.owned?'Bütçe dışı':'Neden seçilemiyor?'),node('p',row.reasons.map(r=>window.YaparoDecision.reasonText[r]).join(' · ')||'Bu bütçede başka kanallara öncelik verildi.'));article.append(detail);groups[row.owned?'owned':/managed|partner|creator/.test(row.channel.purchase)?'managed':'paid'].append(article);}
    }
    if(!plan.allocated)upper.append(node('p',plan.blocked?'Gerekli belge / politika değerlendirmesi tamamlanmadı; bütçe dağıtılmadı.':'Bu koşullarda pay ayırabileceğimiz kanal yok. Diğer kanallardaki gerekçeleri inceleyebilirsin.','empty-state'));
    const reserve=node('p',`Ayrılmayan pay: %${(plan.total?plan.unallocated/plan.total*100:0).toLocaleString('tr-TR',{maximumFractionDigits:2})} · ${money(plan.unallocated)}. Bütçenin tamamını dağıtmak zorunda değilsin. Yüzdeler yuvarlanır.`,'plan-reserve');upper.append(reserve);
    $('why-plan').replaceChildren(node('strong','Bu dağılım neden böyle?'),node('p',plan.blocked?'Belge ve politika koşulları bütçe önerisinden önce gelir.':`${window.YaparoOutcomeContract.resolve(brief()).outcomeLabel} hedefini, bölgeyi, süreyi ve örnek kanal koşullarını birlikte değerlendirdik. Yalnız test minimumu ve tavanı karşılayan kanallara pay ayrıldı.`),node('small',`Hazırlanmış yerel demo · gerçek AI / platform tahmini değil.${plan.economicsProvided?' Kullanıcının girdiği ekonomi sınırı uygulandı.':' Kapasite ve kârlılık verisi girilmedi; işletme getirisi değerlendirilmedi.'}`));updateFooter();
  }
  function renderReview({root,brief:b,creative,plan,production,adaptations,artwork}){
    const panel=node('section',undefined,'plan-card review-compact'),dl=node('dl');panel.append(node('h2','Çalışmanın kısa özeti'));
    const c=b.outcomeContract;for(const [label,value] of [['Amaç',c.intentLabel],['Beklenen adım',c.outcomeLabel],['İçerik',`${creative.title} · ${creative.cta}`],['Başarı göstergesi',`${c.kpi.label} · gerçek ölçüm bağlı değil`],['Yönlendirme',[c.destination.url,c.destination.phone,c.destination.email,c.destination.address,c.destination.mapUrl,c.destination.androidUrl,c.destination.iosUrl].filter(Boolean).join(' · ')||'İlk aşamadaki yöntem; yayın öncesi doğrulanmalı'],['Medya bütçesi',plan?`${money(plan.total)} · ${money(plan.unallocated)} ayrılmadı`:'Medya bütçesi yok'],['Kanal dağılımı',plan?plan.rows.filter(r=>r.amount).map(r=>`${r.channel.name} %${(r.amount/plan.total*100).toLocaleString('tr-TR',{maximumFractionDigits:2})}`).join(' · '):usage()==='content_only'?'Kanaldan bağımsız içerik': 'Kendi hesaplarında paylaşım'],['Yayın aralığı',plan?`${plan.input.start} · ${plan.input.days} gün`:'Ücretli yayın planı yok']])dl.append(node('dt',label),node('dd',value));panel.append(dl);root.append(panel);
    const all=node('details',undefined,'plan-card');all.id='review-all-answers';all.append(node('summary','Tüm yanıtların ve hazırlık ayrıntıları'));const list=node('dl');for(const row of b.firstStageSummary)list.append(node('dt',row.label),node('dd',row.value));all.append(list);for(const req of c.requirements)all.append(node('p',req.label));for(const req of production.requirements)all.append(node('p',`${req.placement} · ${req.label}`));root.append(all);
    if(production.requirements.some(r=>r.medium==='image'))root.append(artwork(creative));
    root.append(node('p',`${adaptations?.length||0} yerel içerik taslağı. Gerçek AI, ölçüm, fiyatlandırma ve yayın bağlantıları açılmadı.`,'plan-muted'));
  }
  for(const id of ['geo-mode','plan-latitude','plan-longitude','radius','plan-economics-enabled'])$(id).addEventListener('change',configure);
  for(const id of ['start','plan-end'])$(id).addEventListener('input',syncDates);
  form.addEventListener('input',()=>{syncDates();updateMap();updateFooter();});
  form.addEventListener('change',()=>{syncDates();updateMap();updateFooter();});
  studio.attachPlanUI({prefill,configure,issue,sourceReady:()=>paid()&&!issue()&&!!$('business').value&&!!$('sector').value&&!!window.YaparoOutcomeContract.resolve(brief()).legacyProjection,revealIssue(){if(paid()&&window.YaparoOutcomeContract.resolve(brief()).legacyProjection)advanced.open=true;},inputPatch,renderPlan,renderReview,onStep(step){banner.textContent=step===1?'Yerel demo · gerçek AI, reklam tahmini veya yayın yapılmaz. Yalnız sentetik örnek kullan; yenileme çalışmayı sıfırlar.':originalBanner;if(step===1){configure();if(lastPlan)renderPlan(lastPlan);}}});
  configure();
})();
