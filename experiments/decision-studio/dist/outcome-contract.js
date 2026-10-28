/* Owned outcome semantics and authored local concepts. No network, inference or platform approval. */
(function (root, factory) {
  'use strict';
  const api = factory(typeof module !== 'undefined' && module.exports ? require('./first-stage-bank.js') : root.YaparoFirstStage);
  if (typeof module !== 'undefined' && module.exports) module.exports = api;
  root.YaparoOutcomeContract = api;
})(typeof globalThis !== 'undefined' ? globalThis : this, function (M) {
  'use strict';
  const version = 'yaparo-owned-outcome-v1', snapshotVersion = 'yaparo-first-stage-v1';
  const freeze = value => {if (value && typeof value === 'object') {Object.values(value).forEach(freeze); Object.freeze(value);} return value;};
  function canonical(value) {
    if (value === null || typeof value === 'string' || typeof value === 'boolean') return JSON.stringify(value);
    if (typeof value === 'number' && Number.isFinite(value)) return JSON.stringify(value);
    if (Array.isArray(value)) return '[' + value.map(canonical).join(',') + ']';
    if (value && Object.getPrototypeOf(value) === Object.prototype) return '{' + Object.keys(value).sort().map(k => JSON.stringify(k) + ':' + canonical(value[k])).join(',') + '}';
    throw new TypeError('Snapshot must contain plain JSON values.');
  }
  // Full canonical value rather than a collision-prone short hash; not a cryptographic signature.
  function signature(snapshot) {try {return version + ':' + canonical(snapshot);} catch {return version + ':invalid_snapshot';}}
  const definitions = {
    remember:['remember_message','Mesaj hatırlanması','Mesajı hatırla'], understand:['understand_message','Mesajın anlaşılması','Bilgileri incele'],
    traffic:['destination_visits','Hedef sayfa ziyaretleri','Sayfayı ziyaret et'], visit:['physical_visits','Fiziksel ziyaretler','Ziyaret bilgilerini gör'],
    contact:['contact_requests','İletişim talepleri','İletişime geç'], install:['app_installs','Uygulama indirmeleri','Uygulamayı indir'],
    purchase:['completed_purchases','Tamamlanan satın almalar','Satın al'], message:['message_requests','Başlatılan mesaj görüşmeleri','Mesaj gönder'],
    call:['phone_calls','Telefon aramaları','Telefonla ara'], register:['completed_registrations','Tamamlanan kayıtlar','Kayıt ol'],
    ticket:['completed_ticket_purchases','Tamamlanan bilet alımları','Bilet al'], lead_form:['submitted_lead_requests','İletilen talep formları','Talebini ilet'],
    quote:['quote_requests','Teklif talepleri','Teklif iste'], book:['confirmed_appointments','Onaylanan randevular','Randevu al'],
    meeting:['scheduled_meetings','Planlanan görüşmeler','Görüşme ayarla'], apply:['job_applications','İş başvuruları','Başvur'],
    donate:['completed_monetary_donations','Tamamlanan para bağışları','Bağış bilgilerini incele'],
    materials:['received_material_contributions','Teslim alınan malzeme destekleri','Malzeme desteği ver'],
    volunteer:['volunteer_applications','Gönüllü başvuruları','Gönüllü başvurusu yap'],
    share:['content_shares','İçerik paylaşımları','Çağrıyı paylaş'], follow:['new_followers','Yeni takipçiler','Hesabı takip et'],
    join:['community_memberships','Topluluk katılımları','Topluluğa katıl'], subscribe:['started_subscriptions','Başlatılan üyelik veya abonelikler','Üyeliği başlat']
  };
  const communication = {promote:'product_service_intro',sell:'sale_promotion',event:'event',lead:'lead_request',hire:'recruitment',fundraise:'fundraising',announce:'announcement',community:'membership',reputation:'reputation'};
  function projection(s) {
    const a=s.answers,o=s.outcome; let action=null,goal=null;
    if(o==='remember'){action='remember';goal='awareness';}
    if(o==='understand'){action='understand';goal='awareness';}
    if(o==='traffic'){action='visit_website';goal='traffic';}
    if(o==='visit'&&s.intent!=='event'){action='visit_store';goal='store_visits';}
    if(o==='purchase'&&['website','marketplace'].includes(a.action_checkout)){action=a.action_checkout==='website'?'buy_online':'buy_marketplace';goal='ecommerce_purchase';}
    if(o==='message'&&a.action_message_method==='whatsapp'){action='message_whatsapp';goal='calls_messages';}
    if(o==='call'){action='call';goal='calls_messages';}
    if(o==='contact'){
      if(a.action_contact==='phone'){action='call';goal='calls_messages';}
      if(a.action_contact==='form'){action='fill_form';goal='lead_generation';}
      if(a.action_contact==='message'&&a.action_message_method==='whatsapp'){action='message_whatsapp';goal='calls_messages';}
    }
    if(o==='lead_form'&&a.action_lead_method==='form'){action='fill_form';goal='lead_generation';}
    if(o==='book'&&a.action_booking==='page'){action='book_appointment';goal='appointment';}
    if(o==='register'&&s.intent==='event'){action='register_event';goal='event_registration';}
    if(o==='apply'&&['form','career'].includes(a.action_apply_method)){action='apply_job';goal='job_application';}
    if(o==='donate'){action='donate';goal='donation';}
    if(o==='install'){action='download_app';goal='app_install';}
    return action?{communication:communication[s.intent],action,goal,scope:'taxonomy_only',qualified:false}:null;
  }
  function destination(s) {
    const a=s.answers,o=s.outcome;
    const d={kind:'none',channel:null,method:null,url:null,phone:null,email:null,address:null,mapUrl:null,required:false,missing:[],verified:false};
    const link=(field='action_url',kind='web')=>{d.kind=kind;d.channel='web';d.url=a[field]||null;d.required=true;if(!d.url)d.missing.push(field);};
    const phone=()=>{d.kind='phone';d.channel='phone';d.phone=a.action_phone||null;d.required=true;if(!d.phone)d.missing.push('action_phone');};
    const email=()=>{d.kind='email';d.channel='email';d.email=a.action_email||null;d.required=true;if(!d.email)d.missing.push('action_email');};
    const place=prefix=>{d.kind='location';d.channel='physical';d.address=a[prefix+'_address']||null;d.mapUrl=a[prefix+'_map_url']||null;d.required=true;if(!d.address&&!d.mapUrl)d.missing.push(prefix+'_address_or_map');};
    const message=()=>{d.method=a.action_message_method||null;if(d.method==='whatsapp'){phone();d.kind='message';d.channel='whatsapp';}else if(d.method==='social'){link('action_profile_url','message');d.channel='social';}else if(d.method==='email'){email();d.kind='message';}else{d.kind='unresolved';d.required=true;d.missing.push('action_message_method');}};
    const method=value=>{d.method=value||null;if(['page','system','form','career','website','marketplace','official_page','platform'].includes(value))link();else if(value==='phone')phone();else if(value==='email')email();else if(value==='message')message();else if(value==='store'||value==='dropoff')place('action_location');else if(value==='other'||value==='new'){d.kind='unresolved';d.required=true;d.missing.push(value==='new'?'form_not_created':'custom_destination_not_verified');}};
    if(o==='traffic')link();
    else if(o==='visit')place(s.intent==='event'?'event_location':'action_location');
    else if(o==='call')phone();
    else if(o==='message')message();
    else if(o==='contact')method(a.action_contact);
    else if(o==='purchase')method(a.action_checkout);
    else if(['lead_form','quote'].includes(o))method(a.action_lead_method);
    else if(['book','meeting'].includes(o))method(a.action_booking);
    else if(['register','ticket','join','subscribe'].includes(o))method(a.action_join_method);
    else if(o==='apply')method(a.action_apply_method);
    else if(o==='donate')method(a.action_donation_method);
    else if(o==='materials'){if(a.action_delivery==='dropoff')place('action_location');else if(['pickup','contact'].includes(a.action_delivery))message();else method(a.action_delivery);d.deliveryMethod=a.action_delivery||null;}
    else if(o==='volunteer')method(a.action_volunteer_apply);
    else if(o==='follow')link('action_profile_url','profile');
    else if(o==='share'){d.kind='share';d.url=a.action_share_url||null;d.channel='user_selected';if(!d.url)d.missing.push('share_content_not_created');}
    else if(o==='install'){d.kind='app_store';d.channel='app';d.method=a.action_app_platform;d.required=true;d.androidUrl=a.action_android_url||null;d.iosUrl=a.action_ios_url||null;if(['android','both'].includes(d.method)&&!d.androidUrl)d.missing.push('action_android_url');if(['ios','both'].includes(d.method)&&!d.iosUrl)d.missing.push('action_ios_url');}
    return d;
  }
  function resolve(snapshot) {
    const bindingSignature=signature(snapshot), errors={};
    let checked=null;
    if(bindingSignature===version+':invalid_snapshot'||!snapshot||typeof snapshot!=='object'||Array.isArray(snapshot)||snapshot.version!==snapshotVersion)errors._snapshot='Desteklenen ilk aşama kaydı gerekli.';
    else if(!snapshot.answers||Object.getPrototypeOf(snapshot.answers)!==Object.prototype)errors._answers='Yanıtlar düz bir nesne olmalı.';
    else if(!M||!M.intents().some(i=>i.id===snapshot.intent)||!M.outcomes(snapshot.intent).some(o=>o.id===snapshot.outcome))errors._route='Amaç ve sonuç yolu tanınmıyor.';
    else {
      checked=M.validate(snapshot.intent,snapshot.outcome,snapshot.answers);
      Object.assign(errors,checked.errors);
      const active=new Set(M.fields(snapshot.intent,snapshot.outcome,checked.answers).map(f=>f.id));
      if(Object.keys(snapshot.answers).some(k=>!active.has(k)))errors._hidden='Gizli veya tanınmayan yanıtlar kayıttan çıkarılmalı.';
    }
    const valid=!Object.keys(errors).length;
    const base={version,snapshotVersion,binding:{signature:bindingSignature,snapshot:bindingSignature!==version+':invalid_snapshot'?JSON.parse(canonical(snapshot)):null},valid,errors,
      authoredSimulation:true,authorship:{kind:'authored_local_simulation',externalQuery:false,model:null},
      policy:{status:'not_evaluated',publishReady:false,platformQualified:false},legacyProjection:null};
    if(!valid)return freeze({...base,action:null,destination:null,kpi:null,requirements:[],usage:{mode:null,resolved:false,contentOnly:false}});
    const s={...snapshot,answers:checked.answers},def=definitions[s.outcome],d=destination(s),mode=s.answers.delivery_mode;
    const intentLabel=M.intents().find(i=>i.id===s.intent).label,outcomeLabel=M.outcomes(s.intent).find(o=>o.id===s.outcome).label;
    const secondary={install:{id:'activated_app_users',label:'Uygulamayı etkin kullanmaya başlayanlar'},subscribe:{id:'active_subscriptions',label:'Etkin üyelik veya abonelikler'},volunteer:{id:'participating_volunteers',label:'Fiilen katılan gönüllüler'}}[s.outcome]||null;
    const requirements=[{id:'outcome_measurement',label:def[1]+' için gerçek ölçüm bağlantısı doğrulanmalı.',status:'unverified'},...d.missing.map(id=>({id,label:'Yönlendirme veya başvuru noktası henüz hazır değil; yayın öncesinde tamamlanmalı.',status:'missing'}))];
    if(mode==='unsure')requirements.push({id:'usage_choice',label:'İçeriğin kullanım yolunu seç.',status:'unresolved'});
    if(mode==='content_only')requirements.push({id:'independent_draft',label:'Kanaldan bağımsız içerik taslağı; yayın, indirme veya reklam izni içermez.',status:'draft_only'});
    else requirements.push({id:'channel_permissions',label:'Hesap, kanal, izin, politika ve bütçe sınırları ayrıca doğrulanmalı.',status:'unverified'});
    if(s.intent==='fundraise')requirements.push({id:'fundraising_authority',label:'Yardımın yetkisi, belge kapsamı ve koşulları ayrıca doğrulanmalı.',status:'unverified'});
    return freeze({...base,intent:s.intent,outcome:s.outcome,intentLabel,outcomeLabel,
      action:{id:s.intent+'/'+s.outcome,label:outcomeLabel,cta:def[2]},destination:d,
      kpi:{id:def[0],label:def[1],secondary,measurementVerified:false,forecast:null},
      usage:{mode,resolved:mode!=='unsure',contentOnly:mode==='content_only'},requirements,legacyProjection:projection(s),
      facts:M.summary(s.intent,s.outcome,s.answers)});
  }
  function analyze(snapshot) {
    const c=resolve(snapshot),analysisVersion='yaparo-owned-brief-analysis-v1';
    const base={version:analysisVersion,valid:c.valid,errors:c.errors,signature:c.binding.signature,binding:c.binding,
      externalQuery:false,model:null,authorship:c.authorship,
      policy:{status:'not_evaluated',publishReady:false,platformQualified:false},
      sourceBusiness:null,sourceSector:null,sourceAudience:null};
    if(!c.valid)return freeze({...base,intent:null,outcome:null,subject:null,identity:null,message:null,audienceLabel:null,
      ownedAudience:null,delivery:null,destination:null,goal:null,communication:null,action:null,risk:null,riskDeclared:null,
      risks:[],legacyProjection:null,scoringDimensions:{},known:[],unknown:[],reason:'İlk aşamadaki geçerli bilgileri tamamla.'});
    const a=c.binding.snapshot.answers,fields=M.fields(c.intent,c.outcome,a);
    const role=key=>{
      const f=fields.find(field=>field.role===key&&a[field.id]!==undefined);
      if(!f)return null;
      const value=a[f.id],label=value==='other'&&typeof a[f.id+'_other']==='string'?a[f.id+'_other']:
        f.options?.find(option=>option.value===value)?.label||(Array.isArray(value)?value.map(item=>f.options?.find(option=>option.value===item)?.label||item).join(', '):String(value));
      return {id:f.id,value,label};
    };
    const subject=role('subject'),identity=role('identity'),message=role('message'),audience=role('audience');
    const declared=typeof a.risk==='string'?a.risk:null,risk=c.intent==='fundraise'?'fundraising':declared;
    const risks=[...new Set([risk,declared].filter(Boolean))];
    const known=[{id:'intent',label:'Çalışmanın amacı',value:c.intentLabel},{id:'outcome',label:'Beklenen adım',value:c.outcomeLabel},
      ...c.facts.map((row,index)=>({id:fields.find(field=>field.label===row.label)?.id||'declared_'+index,label:row.label,value:row.value}))]
      .map(row=>({...row,source:'first_stage',verified:false}));
    const unknown=[
      {id:'business_model',label:'İşletme modeli otomatik sınıflandırılmadı.',status:'unclassified'},
      {id:'sector',label:'Faaliyet alanı metinden tahmin edilmedi.',status:'unclassified'},
      {id:'source_audience',label:'Kitle beyanı reklam platformunun doğrulanmış hedef kitlesi değildir.',status:'unverified'},
      {id:'account_permissions',label:'Gerçek reklam hesabı ve izinleri doğrulanmadı.',status:'unverified'},
      {id:'measurement',label:'Gerçek sonuç ölçümü doğrulanmadı.',status:'unverified'},
      {id:'platform_forecast',label:'Güncel platform erişim ve maliyet tahmini yok.',status:'unverified'},
      ...c.requirements.map(requirement=>({id:requirement.id,label:requirement.label,status:requirement.status}))
    ];
    if(!audience)unknown.push({id:'declared_audience',label:'İlk aşamada ayrı bir hedef kitle beyanı bulunmuyor.',status:'not_declared'});
    if(!declared)unknown.push({id:'declared_risk',label:'Özel koşul beyanı bulunmuyor; politika uygunluğu varsayılmaz.',status:'not_declared'});
    if(!c.legacyProjection)unknown.push({id:'paid_outcome',label:'Bu sonucun ücretli kanal eşleştirmesi henüz bağlı değil.',status:'unsupported'});
    const description=[subject?.label||identity?.label,c.outcomeLabel,audience?.label].filter(Boolean).join(' · ');
    return freeze({...base,intent:c.intent,outcome:c.outcome,subject:subject?.label||null,identity:identity?.label||null,
      message:message?.label||null,audienceLabel:audience?.label||null,ownedAudience:typeof audience?.value==='string'?audience.value:null,
      delivery:c.usage.mode,destination:c.destination,goal:c.legacyProjection?.goal||null,
      communication:communication[c.intent],action:c.legacyProjection?.action||null,risk,riskDeclared:declared,risks,
      legacyProjection:c.legacyProjection,scoringDimensions:c.legacyProjection?{objective:c.legacyProjection.goal}:{},known,unknown,
      reason:description+'. İlk aşamadaki bu beyanlar planın bölge, tarih ve bütçe seçimleriyle birlikte değerlendirilir; hesap, ölçüm veya yayın onayı değildir.'});
  }
  function buildConcepts(snapshot,options={}) {
    const c=resolve(snapshot);if(!c.valid)return [];
    const revision=Number.isInteger(options.revision)&&options.revision>0?options.revision:1;
    const notes=typeof options.notes==='string'?options.notes.trim().slice(0,600):'';
    const a=c.binding.snapshot.answers,fields=M.fields(c.intent,c.outcome,a);
    const fact=role=>{const f=fields.find(f=>f.role===role&&a[f.id]!==undefined);if(!f)return '';const value=a[f.id];return a[f.id+'_other']||f.options?.find(o=>o.value===value)?.label||(Array.isArray(value)?value.join(', '):String(value));};
    const subject=fact('subject')||fact('identity')||c.intentLabel;
    const message=fact('message');
    const support=c.outcome==='materials'?a.action_materials:c.outcome==='volunteer'?a.action_volunteer_task:'';
    const purpose=[subject,message,support].filter(Boolean).join(' · ');
    const direction=c.outcomeLabel;
    const variants=[
      {angle:'Somut bilgi',hook:'Ne, neden, nasıl?',title:subject,message:purpose+' — '+direction+'.',tone:'Açık ve güven veren'},
      {angle:'İnsana yakın anlatım',hook:'İhtiyaçtan başlayan hikâye',title:'Birlikte anlam kazanan bir adım',message:'Bu çalışmanın odağı: '+purpose+'. Beklenen adım: '+direction+'.',tone:'Sıcak ve sade'},
      {angle:'Doğrudan davet',hook:'Tek bir sonraki adım',title:c.action.cta,message:subject+' için davet: '+direction+'. '+(support||message||'Ayrıntıları değerlendir; sana uygunsa sonraki adımı seç.'),tone:'Net ve harekete çağıran'}
    ];
    // Revisions rotate three authored approaches; they do not pretend to query or invent new evidence.
    return variants.map((_,i)=>({...variants[(i+revision-1)%variants.length],id:c.intent+'-'+c.outcome+'-'+revision+'-'+i,kind:i,cta:c.action.cta,format:'static_image',theme:c.intent==='event'?'event':'product',x:10,y:14,revision,edits:[],claims:[],proof:'Kullanıcının beyan ettiği bilgiler; bağımsız doğrulama yok',channelAffinity:'Kanal uygunluğu henüz doğrulanmadı',briefLine:purpose,
      context:{subject,audience:fact('audience'),identity:fact('identity'),outcome:c.outcome,communication:c.intent,action:c.action.id,branch:{}},
      binding:{version,signature:c.binding.signature},outcomeSignature:c.binding.signature,outcome:c.outcome,destination:JSON.parse(JSON.stringify(c.destination)),kpi:JSON.parse(JSON.stringify(c.kpi)),
      provenance:{kind:'authored_local_simulation',version,externalQuery:false,model:null,fictional:true},notes,
      disclaimer:'Hazırlanmış yerel taslak örneği; gerçek AI üretimi, platform onayı, performans tahmini veya yayın değildir.'}));
  }
  return freeze({version,snapshotVersion,resolve,analyze,buildConcepts,signature});
});
