/* Authored, context-sensitive demo responses. No LLM or platform forecast call. */
(function(root){
  'use strict';
  const version='yaparo-authored-demo-v1';
  const norm=s=>String(s||'').toLocaleLowerCase('tr-TR').normalize('NFD').replace(/[\u0300-\u036f]/g,'').replace(/ı/g,'i');
  const hash=s=>{let h=2166136261;for(const c of s)h=Math.imul(h^c.charCodeAt(0),16777619);return (h>>>0).toString(16);};
  const profiles={
    cafe:{name:'Kafe / yeme içme',sector:'food_hospitality',business:'local_retail',action:'visit_store',audience:'local_nearby',goal:'store_visits',theme:'coffee',noun:'kahve',
      titles:[['İyi kahvenin küçük hikâyesi.','Bir fincan için zaman ayır.','Mahallende yeni bir mola.'],['Çekirdekten fincana bir yolculuk.','Günün en güzel küçük arası.','Kahve bahanesiyle tanışalım.'],['Her yudumda bir ayrıntı.','Birlikte geçirilen zamana.','Yeni favorinle tanış.']],
      messages:['Kahveni seç, hazırlık anının küçük hikâyesine ortak ol.','Günün koşuşturmasına kısa bir ara. Bir fincan, biraz sohbet, sana ait bir an.','Bildiğin sokakta yeni bir kahve molası. Yolun düşerse tanışalım.']},
    fashion:{name:'Butik / tasarım',sector:'fashion_beauty_lifestyle',business:'local_retail',action:'visit_store',audience:'local_nearby',goal:'store_visits',theme:'fashion',noun:'tasarım',
      titles:[['Detaylarda kendi stilini bul.','Kendin gibi hissettiğin an.','Yeni bir tarza yer aç.'],['Her parçanın bir hikâyesi var.','Gününe kendi rengini kat.','Bu kez farklı bir şey dene.'],['Özenle seçilmiş bir dokunuş.','Senin ritmin. Senin stilin.','Yakınında keşfedilmeyi bekliyor.']],
      messages:['Bir parçayı sana ait kılan küçük ayrıntıları yakından keşfet.','Bir renk, bir doku, kendin gibi hissettiğin bir stil.','Yeni bir parçayla başlayan bir hikâye. Koleksiyona birlikte bakalım.']},
    saas:{name:'B2B yazılım',sector:'technology_saas',business:'b2b_leadgen',action:'fill_form',audience:'b2b_decision_makers',goal:'lead_generation',theme:'software',noun:'yazılım',
      titles:[['İş akışına daha açık bir bakış.','Ekibin için daha sakin bir gün.','Birlikte nasıl çalışır, görelim.'],['Dağınık işleri tek yerde düşün.','Aynı hedefe, aynı ekranda.','Kısa bir tanışmayla başlayalım.'],['Süreci gör. Sonraki adımı bil.','İş birliğine yeni bir alan.','Sana uygun akışı keşfet.']],
      messages:['Görevlerini tek yerde gör. Ekibinle bir sonraki adımı birlikte planla.','Kim, hangi işin neresinde? Ekipçe aynı akışa bakabileceğin bir çalışma alanı.','Ekibinin iş akışını konuşalım. Ürünün sana nasıl uyabileceğini birlikte inceleyelim.']},
    home:{name:'Yerel hizmet',sector:'local_home_services',business:'local_service',action:'call',audience:'local_nearby',goal:'calls_messages',theme:'home',noun:'hizmet',
      titles:[['Evin için özenli bir başlangıç.','İçin rahat etsin.','Önce ihtiyacını konuşalım.'],['Küçük detaylara dikkat eden hizmet.','Yaşam alanına yeni bir nefes.','Yakınındaki çözümle tanış.'],['Nasıl çalıştığımızı yakından gör.','Evine zaman ayır.','Bir soruyla başlayabiliriz.']],
      messages:['İhtiyacını anlat; yapılacak işi ve kapsamını birlikte netleştirelim.','Evinde ilgilenmek istediğin işler için ilk adımı bir görüşmeyle at.','Bulunduğun bölgeyi ve ihtiyacını paylaş. Sana uygun hizmeti birlikte konuşalım.']},
    event:{name:'Atölye / etkinlik',sector:'entertainment_events',business:'event',communication:'event',action:'register_event',audience:'b2c_new',goal:'event_registration',theme:'event',noun:'atölye',
      titles:[['Bir fikri birlikte şekillendirelim.','Birlikte üretmenin güzel hâli.','Merakına bir yer ayır.'],['Deneyerek öğrenilen bir hikâye.','Yeni insanlarla, yeni bir an.','Takviminde yeni bir deneyim.'],['İlk dokunuşla başlayan keşif.','Günün sonunda elinde bir hikâye.','Bu davet merak edenlere.']],
      messages:['Merakını yanında getir. Yeni bir deneyimin parçası ol.','Yeni insanlarla tanış, birlikte üretmenin ritmini keşfet.','Katılım biçimini ve etkinlik ayrıntılarını incele; sana uygun deneyimi seç.']},
    general:{name:'Genel çalışma',sector:'other',business:'local_service',action:'visit_website',audience:'b2c_new',goal:'traffic',theme:'product',noun:'fikrin',
      titles:[['Fikrinin farkını görünür kıl.','Günlük hayatta bir karşılığı var.','Yeni bir bakışla tanış.'],['Ayrıntıda başlayan bir hikâye.','Sana yakın bir düşünce.','Merak ettiğin yerden başla.'],['Bir fikre daha yakından bak.','Bir an. Bir dokunuş.','Sonraki adımı birlikte atalım.']],
      messages:['İhtiyacından başlayan bir düşünce. Ayrıntılarına birlikte bakalım.','Günlük hayatında yer açmak istediğin yeni bir deneyimle tanış.','Merak ettiğin ayrıntıları keşfet. Sana uygun bir sonraki adımı seç.']}
  };
  function profile(brief){const t=norm(brief.description);if(/kahve|kafe|restoran|yemek|pastane/.test(t))return profiles.cafe;if(/yazilim|saas|crm|uygulama|ekip.*takip/.test(t))return profiles.saas;if(/atolye|etkinlik|konser|seramik.*ders/.test(t))return profiles.event;if(/tesisat|temizlik|usta|tadilat|tamir/.test(t))return profiles.home;if(/butik|moda|koleksiyon|giyim|takı|tasarim/.test(t))return profiles.fashion;return Object.values(profiles).find(p=>p.sector===brief.sector)||profiles.general;}
  const ctas={visit_store:'Mağazayı keşfet',visit_website:'Ayrıntıları incele',buy_online:'Ürünleri incele',buy_marketplace:'Mağazaya göz at',message_whatsapp:'WhatsApp’tan bilgi al',call:'Detayları konuşalım',fill_form:'Bilgi iste',book_appointment:'Randevu seçeneklerini sor',register_event:'Katılım ayrıntılarını gör',download_app:'Uygulamayı tanı',apply_job:'Pozisyonu incele',donate:'Resmî bilgileri incele',join_membership:'Katılım koşullarını gör',follow_engage:'Hikâyeye katıl',understand:'Daha fazla bilgi al',remember:'Hikâyeyi keşfet'};
  function cards(brief,batch,variation=0){const p=profile(brief),round=(batch-1+variation)%p.titles.length;
    return p.titles[round].map((title,i)=>({id:`${hash(JSON.stringify(brief))}-${batch}-${variation}-${i}`,kind:i,angle:['Ürünün hikâyesi','Bir anın hissi','Merak uyandıran davet'][i],hook:['Somut ayrıntı','Günlük hayat anı','Keşif daveti'][i],title,
      message:[brief.message||p.messages[0],p.messages[1],p.messages[2]][i],cta:ctas[brief.action]||'Ayrıntıları keşfet',tone:['Sade ve güven veren','Sıcak ve samimi','Canlı ve merak uyandıran'][i],
      format:'static_image',proof:'Kullanıcı notu; bağımsız kanıt yok',claims:[],channelAffinity:i===0?'Talep yakalama + ürün keşfi':'Talep yaratma + görsel keşif',x:10,y:14,revision:1,edits:[],theme:p.theme,
      context:{subject:brief.description,audience:brief.audience,identity:brief.identity,communication:brief.communication,action:brief.action,branch:structuredClone(brief.branch)},provenance:{kind:'authored_demo_response',version,externalQuery:false,model:null},briefLine:brief.description.slice(0,180)}));
  }
  function alternative(card,brief){const next=cards(brief,1,card.revision)[card.kind];return {title:next.title,message:next.message,cta:next.cta,theme:next.theme};}
  const shapes={
    coffee:'<ellipse cx="210" cy="353" rx="120" ry="22" fill="#142f3420"/><path d="M120 195h170l-15 132q-70 42-140 0z" fill="#fff7e9"/><path d="M288 214q91-4 49 68l-55 7" fill="none" stroke="#fff7e9" stroke-width="21"/><ellipse cx="205" cy="196" rx="85" ry="21" fill="#654332"/><path d="M180 153q-20-24 5-49m41 49q-20-24 5-49" fill="none" stroke="#fff" stroke-width="5" opacity=".65"/>',
    fashion:'<ellipse cx="210" cy="362" rx="110" ry="16" fill="#142f3420"/><path d="M155 146l-66 50 32 47 32-22v132h122V221l32 22 32-47-66-50-35 20h-49z" fill="#fff4da"/><path d="M186 153q23 37 50 0" fill="none" stroke="#bb795e" stroke-width="9"/><path d="M167 225h94" stroke="#c29d79" stroke-width="3" opacity=".4"/>',
    software:'<rect x="65" y="155" width="285" height="190" rx="15" fill="#f7f9ff"/><rect x="78" y="170" width="60" height="160" rx="7" fill="#cad5e7"/><path d="M91 190h33m-33 21h24m-24 21h28" stroke="#7186a7" stroke-width="5"/><rect x="155" y="183" width="174" height="33" rx="5" fill="#5674e1"/><rect x="155" y="233" width="75" height="80" rx="6" fill="#e5d4b6"/><rect x="244" y="233" width="85" height="80" rx="6" fill="#a9cbb7"/>',
    home:'<ellipse cx="210" cy="362" rx="120" ry="18" fill="#142f3420"/><path d="M91 227l115-91 119 91" fill="none" stroke="#fff8e9" stroke-width="23" stroke-linecap="round"/><path d="M113 225v123h187V225L207 155z" fill="#fff8e9"/><rect x="184" y="266" width="44" height="82" rx="3" fill="#a5bea9"/><rect x="136" y="242" width="30" height="35" rx="3" fill="#d0a47f"/><rect x="245" y="242" width="30" height="35" rx="3" fill="#d0a47f"/>',
    event:'<ellipse cx="210" cy="355" rx="130" ry="25" fill="#142f3420"/><path d="M100 313q0-130 100-106 100-26 107 106z" fill="#fff3db"/><ellipse cx="204" cy="310" rx="104" ry="29" fill="#d49a78"/><path d="M148 254q60-41 113 0m-100 25q42-26 85 0" fill="none" stroke="#eed7bb" stroke-width="6"/><path d="M288 122l-26 108" stroke="#fff" stroke-width="14" stroke-linecap="round"/>',
    product:'<ellipse cx="210" cy="360" rx="110" ry="20" fill="#142f3420"/><path d="M125 192l85-42 85 42v127l-85 40-85-40z" fill="#f7e7c7"/><path d="M125 192l85 43 85-43m-85 43v124" fill="none" stroke="#ba9368" stroke-width="3"/><path d="M167 171l87 43v55" fill="none" stroke="#fff9eb" stroke-width="23"/>'
  };
  function illustration(theme){return `<svg viewBox="0 0 400 400" aria-hidden="true" xmlns="http://www.w3.org/2000/svg">${shapes[theme]||shapes.product}</svg>`;}
  function forecast(input,data){
    const days=input.days/7, local=input.geo==='radius_local'?Math.min(5,Math.max(.12,input.radius/10)):input.geo==='nationwide'?7:1;
    const b2b=['b2b_leadgen','saas_subscription'].includes(input.business), pricey=b2b?2.5:input.sector==='food_hospitality'?.7:1;
    const forecasts=data.channels.map((c,index)=>{const owned=c.tier==='non_paid_recommendation',managed=/managed|partner|creator/.test(c.purchase),search=c.type==='paid_search'||c.type==='paid_search_commerce';
      let accountReady=input.readiness!=='none' && (!managed || input.readiness==='all');
      let assetReady=!c.assets.some(a=>/^(vertical_video|horizontal_or_vertical_video|vertical_video_or_ar|audio_or_video)$/.test(a))||input.video;
      if(c.id==='google_pmax_shopping')assetReady=input.catalog&&input.tracking;
      if(c.id==='retail_media_marketplace')assetReady=input.catalog&&input.business==='marketplace_seller';
      if(c.id==='owned_crm')accountReady=input.audience==='b2c_existing';
      const cpc=Math.round((search?18:10)*pricey*(1+(index%4)*.15)),cpm=Math.round((b2b?180:70)*(1+(index%5)*.12));
      const cpa=Math.round((b2b?480:100)*(1+(index%4)*.15));
      const clicks=Math.round((c.id==='google_search_maps'?85:c.id==='yandex_search_maps'?35:c.id==='microsoft_search_shopping'?12:55)*local*days);
      const reach=Math.round((c.id==='linkedin'?1800:14000)*local*days);
      const demand=search?clicks*cpc:reach*2*cpm/1000;
      const potentialBudget=Math.floor(c.id==='meta_messages'?demand*.7:managed?demand*.6:demand);
      const radiusSupported=/yarıçap/.test(c.geo);
      return {key:`${hash(JSON.stringify(input))}|${c.id}`,scenario:'authored_interactive',channelId:c.id,accountReady,assetReady,policyPass:true,hasForecast:!owned,
        cpc,cpm:search?0:cpm,cpa,uniqueReach:reach,clicks,cost:potentialBudget,potentialBudget,
        baseUsefulMinimum:c.id==='linkedin'?2500:managed?4000:search?600:700,quality:'authored_simulation_NOT_market_data',updated:new Date().toISOString(),
        radiusSupported,source:version,note:'Yaparo taslağı için hazırlanmış örnek değerler; gerçek hesap, erişim veya performans tahmini değildir.'};
    });
    return {kind:'authored_simulation',version,signature:JSON.stringify(input),forecasts,externalQuery:false};
  }
  function intent(text){const t=norm(text),number=t.match(/(?:butce(?:yi|m|mi|si)?\s*(?:olarak|:)?\s*)([\d.,]+)/);const patch={};
    if(number){const raw=number[1];let n=Number(raw.replace(/\.(?=\d{3}(?:\D|$))/g,'').replace(',','.'));if(Number.isFinite(n)&&n>=0&&n<=1000000)patch.budget=String(n);}
    const duration=t.match(/(\d{1,3})\s*gun/);if(duration&&+duration[1]>=1&&+duration[1]<=365)patch.duration=duration[1];
    const radius=t.match(/(\d{1,3})\s*km/);if(radius&&+radius[1]>=1&&+radius[1]<=800){patch['geo-mode']='radius';patch.radius=radius[1];}
    for(const [city,label] of [['izmir','İzmir'],['ankara','Ankara'],['istanbul','İstanbul'],['antalya','Antalya'],['bursa','Bursa']])if(t.includes(city))patch.region=label;
    if(/turkiye genel|ulke genel/.test(t))patch['geo-mode']='country';
    if(/sade|kisa|minimal/.test(t))return {type:'simplify',patch};
    if(/yeni uclu|yeniden uret|uc alternatif/.test(t))return {type:'regenerate',patch};
    if(/benzer|alternatif/.test(t))return {type:'alternative',patch};
    if(Object.keys(patch).length)return {type:'patch',patch};
    if(/neden|kanal|butce|dagilim|tavan/.test(t))return {type:'explain',patch};
    if(/izin|yardim|saglik|belge/.test(t))return {type:'policy',patch};
    if(/nasil|ne yap|sonraki|devam/.test(t))return {type:'next',patch};
    if(/kafe|kahve|restoran|butik|yazilim|atolye|tesisat|temizlik/.test(t))return {type:'brief',text,profile:profile({description:text}),patch};
    return {type:'question',patch};
  }
  root.YaparoSimulation={version,norm,hash,profiles,profile,cards,alternative,illustration,forecast,intent};
})(typeof window==='undefined'?globalThis:window);
/* Fixed synthetic starting briefs. They never choose usage, budget or readiness. */
(function(root){
  'use strict';
  const version='yaparo-owned-examples-v1';
  const examples={
    cafe:{label:'Kafe açılışı',intent:'promote',outcome:'visit',answers:{
      promote_kind:'brand',promote_name:'Sentetik Örnek Kafe · açılış daveti',
      promote_strength:'other',promote_strength_other:'Mahallede yeni bir kahve ve sohbet noktası',
      promote_audience:'individuals',promote_audience_detail:'everyday',promote_proof:'none',
      action_location_address:'Sentetik adres · Örnek Mahallesi, İzmir. Gerçek bir işletme değildir.'}},
    fashion:{label:'Butik koleksiyonu',intent:'promote',outcome:'visit',answers:{
      promote_kind:'product',promote_name:'Sentetik Örnek Butik · yeni koleksiyon',
      promote_strength:'design',promote_audience:'individuals',promote_audience_detail:'special',promote_proof:'none',
      action_location_address:'Sentetik adres · Örnek Sokak, İstanbul. Gerçek bir mağaza değildir.'}},
    saas:{label:'B2B yazılım',intent:'lead',outcome:'lead_form',answers:{
      lead_service:'Sentetik Örnek Yazılım · ekip görev yönetimi',lead_contact_purpose:'discovery',
      lead_audience:'business',lead_audience_detail:'small',lead_delivery:'online',lead_conditions:'none',
      action_lead_method:'form',action_url:'https://ornek.example/yazilim/tanisma'}},
    home:{label:'Yerel hizmet',intent:'lead',outcome:'call',answers:{
      lead_service:'Sentetik Örnek Ev Hizmeti · bakım talebi',lead_contact_purpose:'quote',
      lead_audience:'individuals',lead_audience_detail:'special',lead_delivery:'customer',lead_conditions:'region',
      lead_condition_note:'Sentetik hizmet bölgesi: Ankara. Gerçek bir hizmet ağı değildir.',action_phone:'+90 555 000 00 00'}},
    event:{label:'Atölye daveti',intent:'event',outcome:'register',answers:{
      event_kind:'workshop',event_name:'Sentetik Örnek Atölye · seramik buluşması',event_mode:'physical',
      event_timing:'unknown',event_location_address:'Sentetik adres · Örnek Sanat Alanı, İzmir. Gerçek bir etkinlik değildir.',
      event_fee:'free',event_eligibility:'open',event_capacity_status:'known',event_capacity:12,
      action_join_method:'page',action_url:'https://ornek.example/atolye/kayit'}}
  };
  function get(id){
    if(typeof id!=='string'||!Object.hasOwn(examples,id))return null;
    const example=examples[id];
    return {id,label:example.label,version,origin:'authored_synthetic_example',
      snapshot:{version:'yaparo-first-stage-v1',intent:example.intent,outcome:example.outcome,answers:structuredClone(example.answers)}};
  }
  const api=Object.freeze({version,ids:()=>Object.keys(examples),get});
  if(typeof module!=='undefined'&&module.exports)module.exports=api;
  root.YaparoOwnedExamples=api;
})(typeof window!=='undefined'?window:globalThis);
