/* Owned, versioned brief UX policy. Source question visibility is not option filtering. */
(function(root){
  'use strict';
  const version='yaparo-brief-flow-v4';
  const groups={
    communication:[
      {id:'offer',label:'Ürün, hizmet veya satış',values:['product_service_intro','launch','sale_promotion','lead_request']},
      {id:'news',label:'Duyuru, etkinlik veya kutlama',values:['announcement','event','celebration']},
      {id:'knowledge',label:'Eğitim, üyelik veya topluluk',values:['education','membership']},
      {id:'people',label:'İşe alım veya yardım çağrısı',values:['recruitment','fundraising']},
      {id:'public',label:'Kurumsal, toplumsal veya henüz belirsiz',values:['reputation','public_issue','unsure']}
    ],
    business:[
      {id:'shop',label:'Mağaza veya ürün satışı',values:['local_retail','ecommerce_dtc','marketplace_seller']},
      {id:'service',label:'Hizmet veya kurumsal çözüm',values:['local_service','b2b_leadgen']},
      {id:'digital',label:'Yazılım, uygulama veya içerik',values:['saas_subscription','mobile_app','media_creator']},
      {id:'participation',label:'Etkinlik veya sosyal fayda',values:['event','nonprofit_fundraising']},
      {id:'team',label:'İşveren / ekip',values:['employer_recruitment']}
    ],
    sector:[
      {id:'products',label:'Ürün ve perakende',values:['fashion_beauty_lifestyle','retail_ecommerce','automotive']},
      {id:'experience',label:'Yeme içme, seyahat ve etkinlik',values:['food_hospitality','travel_tourism','entertainment_events']},
      {id:'services',label:'Hizmet, ev ve gayrimenkul',values:['professional_services','local_home_services','real_estate']},
      {id:'tech',label:'Teknoloji ve üretim',values:['technology_saas','industrial_b2b']},
      {id:'expert',label:'Eğitim, sağlık ve finans',values:['education_training','health_medical','finance_insurance']},
      {id:'community',label:'Topluluk, işe alım veya başka bir alan',values:['nonprofit_social_cause','recruitment','public_political','other']}
    ]
  };
  const questions={communication:'S1_Q01',business:'S3_Q02',sector:'S3_Q03'};
  const offerJobs=new Set(['product_service_intro','launch','sale_promotion','lead_request']);
  const allBusinesses=groups.business.flatMap(group=>group.values);
  // Owned wording/shortlists describe this work, never inferred ownership or eligibility.
  // Source IDs remain unchanged; the user still explicitly chooses each answer.
  const contextBanks={
    product_service_intro:{business:'Ürününe veya hizmetine nasıl ulaşılıyor?',sector:'Ürün veya hizmet hangi alanda?',title:'Tanıtacağın şeyi netleştirelim'},
    launch:{business:'Yeni ürününe veya hizmetine nasıl ulaşılıyor?',sector:'Yeni ürün veya hizmet hangi alanda?',title:'Lansmanı netleştirelim'},
    sale_promotion:{business:'Satış hangi yoldan yapılıyor?',sector:'Kampanya hangi ürün veya hizmet alanında?',title:'Teklifini netleştirelim'},
    lead_request:{business:'Talep hangi çalışma için toplanacak?',sector:'Talep hangi hizmet veya çözümle ilgili?',title:'Gelecek talebi netleştirelim',values:['local_service','b2b_leadgen','saas_subscription','local_retail','ecommerce_dtc','marketplace_seller','media_creator']},
    event:{business:'Bu etkinlik hangi çalışma kapsamında?',sector:'Etkinliğin konusu ne?',title:'Etkinliğin ayrıntılarını netleştirelim',values:['event','local_retail','b2b_leadgen','media_creator','nonprofit_fundraising'],sectors:['entertainment_events','education_training','food_hospitality','travel_tourism','nonprofit_social_cause','other'],labels:{event:'Etkinlik / buluşma',local_retail:'Mağaza / iş yeri etkinliği',b2b_leadgen:'İşletmelere yönelik etkinlik',media_creator:'Yayın / içerik etkinliği',nonprofit_fundraising:'Sosyal fayda / yardım etkinliği'}},
    recruitment:{business:'Bu iş ilanı hangi çalışma için?',sector:'Pozisyon hangi faaliyet alanında?',title:'Aradığın ekip arkadaşını netleştirelim',values:['employer_recruitment'],labels:{employer_recruitment:'Çalışan / ekip arkadaşı arayışı'}},
    fundraising:{business:'Bu destek çağrısı nasıl yürütülecek?',sector:'Destek hangi alanda kullanılacak?',title:'Yardım çağrını netleştirelim',values:['nonprofit_fundraising','event','media_creator'],sectors:['nonprofit_social_cause','education_training','health_medical','other'],labels:{nonprofit_fundraising:'Yardım / sosyal destek çalışması',event:'Yardım amaçlı etkinlik',media_creator:'Farkındalık / destek yayını'}},
    announcement:{business:'Duyuru hangi çalışma kapsamında?',sector:'Duyurunun ilgili olduğu alan ne?',title:'Paylaşacağın duyuruyu netleştirelim'},
    celebration:{business:'Kutlama hangi çalışma kapsamında?',sector:'Kutlamanın ilgili olduğu alan ne?',title:'Kutlama mesajını netleştirelim'},
    education:{business:'Eğitim içeriğini hangi çalışma kapsamında sunuyorsun?',sector:'Öğrenilecek konu hangi alanda?',title:'Öğrenme amacını netleştirelim',values:['media_creator','event','local_service','saas_subscription','nonprofit_fundraising'],sectors:['education_training','technology_saas','professional_services','health_medical','entertainment_events','nonprofit_social_cause','other'],labels:{media_creator:'Eğitici içerik / yayın',event:'Atölye / eğitim etkinliği',local_service:'Eğitim / danışmanlık hizmeti',saas_subscription:'Dijital eğitim / üyelik hizmeti',nonprofit_fundraising:'Sosyal fayda / ücretsiz eğitim çalışması'}},
    membership:{business:'Katılacakları yapı ne sunuyor?',sector:'Topluluğun veya üyeliğin konusu ne?',title:'Katılımın değerini netleştirelim',values:['saas_subscription','media_creator','event','nonprofit_fundraising'],sectors:['education_training','technology_saas','professional_services','entertainment_events','nonprofit_social_cause','other'],labels:{saas_subscription:'Dijital hizmet / üyelik',media_creator:'İçerik / yayın topluluğu',event:'Buluşma / etkinlik topluluğu',nonprofit_fundraising:'Sosyal fayda / dayanışma topluluğu'}},
    reputation:{business:'Açıklama hangi çalışma adına yapılacak?',sector:'Açıklamanın ilgili olduğu alan ne?',title:'Açıklamanın dayanağını netleştirelim'},
    public_issue:{business:'Mesaj hangi çalışma kapsamında paylaşılacak?',sector:'Toplumsal mesajın konusu hangi alanda?',title:'Toplumsal mesajı netleştirelim',values:['nonprofit_fundraising','media_creator'],sectors:['public_political','nonprofit_social_cause','education_training','health_medical','other'],labels:{nonprofit_fundraising:'Sosyal fayda / sivil toplum çalışması',media_creator:'Kamuoyuna yönelik içerik / yayın'}},
    unsure:{business:'Çalışmanı en iyi hangisi tanımlar?',sector:'Hangi alana daha yakın?',title:'Çalışmayı netleştirelim'}
  };
  function contextBank(communication,action){const bank=contextBanks[communication];if(!bank)return null;return {...bank,...(communication==='fundraising'&&action==='donate'?{values:['nonprofit_fundraising','event'],business:'Bağış çağrısı hangi yolla yapılacak?'}:{})};}
  const sectorChoices={
    local_retail:['fashion_beauty_lifestyle','food_hospitality','automotive','retail_ecommerce','health_medical','other'],
    local_service:['professional_services','local_home_services','health_medical','education_training','automotive','real_estate','travel_tourism','other'],
    ecommerce_dtc:['fashion_beauty_lifestyle','retail_ecommerce','food_hospitality','automotive','technology_saas','health_medical','other'],
    marketplace_seller:['fashion_beauty_lifestyle','retail_ecommerce','food_hospitality','automotive','technology_saas','health_medical','other'],
    b2b_leadgen:['professional_services','industrial_b2b','technology_saas','finance_insurance','real_estate','other'],
    saas_subscription:['technology_saas','finance_insurance','education_training','professional_services','other'],
    mobile_app:['technology_saas','entertainment_events','education_training','finance_insurance','health_medical','other'],
    event:['entertainment_events','education_training','food_hospitality','travel_tourism','other'],
    nonprofit_fundraising:['nonprofit_social_cause','education_training','health_medical','public_political','other'],
    employer_recruitment:['recruitment','professional_services','industrial_b2b','technology_saas','other'],
    media_creator:['entertainment_events','education_training','travel_tourism','fashion_beauty_lifestyle','food_hospitality','public_political','other']
  };
  const offerActions={
    local_retail:['visit_store','message_whatsapp','call','visit_website','remember'],
    local_service:['book_appointment','call','message_whatsapp','visit_website','remember'],
    ecommerce_dtc:['buy_online','visit_website','message_whatsapp','remember'],
    marketplace_seller:['buy_marketplace','visit_website','message_whatsapp','remember'],
    b2b_leadgen:['fill_form','call','message_whatsapp','visit_website','remember'],
    saas_subscription:['join_membership','fill_form','visit_website','message_whatsapp','remember'],
    mobile_app:['download_app','visit_website','remember','follow_engage'],
    event:['register_event','visit_website','message_whatsapp','remember'],
    nonprofit_fundraising:['understand','visit_website','follow_engage'],
    employer_recruitment:['understand','visit_website','remember'],
    media_creator:['follow_engage','visit_website','remember','fill_form']
  };
  const destinationActions={
    physical_store:['visit_store','visit_website','understand','remember'],
    own_website:['buy_online','visit_website','understand'],
    marketplace:['buy_marketplace','visit_website','understand'],
    whatsapp_phone:['message_whatsapp','call','understand'],
    lead_form:['fill_form','book_appointment','visit_website','understand'],
    app:['download_app','visit_website','understand']
  };
  const jobActions={
    announcement:['understand','remember','visit_website','follow_engage'],
    event:['register_event','understand','visit_website','message_whatsapp'],
    recruitment:['apply_job','fill_form','visit_website'],
    education:['understand','visit_website','follow_engage'],
    fundraising:['donate','understand','visit_website'],
    membership:['join_membership','understand','visit_website'],
    reputation:['understand','remember','visit_website','follow_engage'],
    celebration:['remember','follow_engage','understand'],
    public_issue:['understand','remember','visit_website','follow_engage'],
    unsure:['understand','remember','visit_website']
  };
  function families(kind){return (groups[kind]||[]).map(({id,label})=>({id,label}));}
  function familyOf(kind,value){return groups[kind]?.find(group=>group.values.includes(value))?.id||null;}
  function options(data,question,values){return (data?.options||[]).filter(option=>option.questionId===question&&values.includes(option.value));}
  function choices(kind,family,data){const values=groups[kind]?.find(group=>group.id===family)?.values||[];return options(data,questions[kind],values);}
  function businesses(communication,data,action){
    if(!familyOf('communication',communication))return [];
    const bank=contextBank(communication,action),values=bank?.values||(offerJobs.has(communication)?allBusinesses.filter(value=>!['nonprofit_fundraising','employer_recruitment'].includes(value)):allBusinesses);
    return options(data,'S3_Q02',values).map(o=>({...o,label:bank?.labels?.[o.value]||o.label}));
  }
  function sectors(communication,business,data,action){
    // Communication and business model are separate dimensions: a shop may host an event.
    // These are editable UX shortlists, not category eligibility or legal approval.
    if(!familyOf('communication',communication)||!familyOf('business',business))return [];
    const bank=contextBank(communication,action);
    return options(data,'S3_Q03',bank?.sectors||sectorChoices[business]||[]);
  }
  function actions(communication,business,data,destination){
    if(!familyOf('communication',communication)||!familyOf('business',business))return [];
    let values;
    if(offerJobs.has(communication)){
      // Explicit current destination overrides the business shortlist. A shop can also sell online.
      if(destination!==undefined&&destination!==null&&destination!=='')values=destinationActions[destination]||[];
      else values=offerActions[business]||[];
    }else{
      values=[...(jobActions[communication]||[])];
      if(communication==='event'&&business==='local_retail')values.push('visit_store');
      if(communication==='education'&&business==='event')values.push('register_event');
    }
    return options(data,'S1_Q04',values);
  }
  function visible(question,values){
    const conditions=question.showWhen||{};
    if(typeof conditions!=='object'||Array.isArray(conditions))return false;
    return Object.entries(conditions).every(([key,expected])=>{
      if(!Array.isArray(expected))return false;
      const actual=Array.isArray(values[key])?values[key]:[values[key]];
      return actual.some(value=>expected.includes(value));
    });
  }
  function pruneAnswers(answers,questions,base={}){
    const known=new Map((questions||[]).map(question=>[question.id,question]));
    const result=Object.fromEntries(Object.entries(answers||{}).filter(([key])=>known.has(key)).map(([key,value])=>[key,Array.isArray(value)?[...value]:value]));
    for(const key of Object.keys(result))if(Object.hasOwn(base,key))result[key]=Array.isArray(base[key])?[...base[key]]:base[key];
    // Monotonic deletion also clears a descendant whose now-hidden parent had a saved answer.
    let changed=true;
    while(changed){
      changed=false;const values={...result,...base};
      for(const key of Object.keys(result)){
        if(!visible(known.get(key),values)){delete result[key];changed=true;}
      }
    }
    return result;
  }
  function branchApplies(question,communication,action){
    if(['S1_F03','S1_F04'].includes(question.id))return communication==='fundraising'&&action==='donate';
    if(question.id==='S1_E03')return communication==='event'&&action==='register_event';
    if(question.id==='S1_R03')return communication==='recruitment'&&['apply_job','fill_form'].includes(action);
    if(question.id==='S1_B05')return !['remember','understand','visit_website','follow_engage'].includes(action);
    return true;
  }
  function pruneContextAnswers(answers,questions,base={}){return pruneAnswers(answers,questions.filter(q=>branchApplies(q,base.S1_Q01,base.S1_Q04)),base);}
  // Intent is chosen before business/destination. Later detail edits must never
  // silently change what the viewer is being asked to do.
  const intentMap={
    product_service_intro:['remember','understand','visit_store','visit_website','fill_form','call','message_whatsapp','download_app'],
    launch:['remember','understand','visit_store','visit_website','follow_engage','download_app'],
    sale_promotion:['buy_online','buy_marketplace','visit_store','message_whatsapp','visit_website','remember','understand'],
    lead_request:['book_appointment','fill_form','message_whatsapp','call','visit_website'],
    event:['register_event','visit_website','message_whatsapp','understand','visit_store'],
    recruitment:['apply_job','fill_form','visit_website'],
    fundraising:['donate','understand','visit_website'],
    announcement:['understand','remember','visit_website','follow_engage'],
    education:['understand','visit_website','follow_engage','register_event'],
    membership:['join_membership','understand','visit_website','follow_engage'],
    reputation:['understand','remember','follow_engage','visit_website'],
    public_issue:['understand','remember','follow_engage','visit_website'],
    celebration:['remember','follow_engage','understand']
  };
  function intentActions(communication){return [...(intentMap[communication]||[])];}
  function destinations(action,data){
    if(!Object.values(intentMap).some(values=>values.includes(action)))return [];
    const fixed={visit_store:['physical_store'],visit_website:['own_website'],buy_online:['own_website'],buy_marketplace:['marketplace'],message_whatsapp:['whatsapp_phone'],call:['whatsapp_phone'],fill_form:['lead_form','own_website'],book_appointment:['lead_form','own_website','whatsapp_phone'],download_app:['app'],register_event:['lead_form','own_website','physical_store'],apply_job:['lead_form','own_website','whatsapp_phone']};
    // These two entries are owned UI extensions, not invented source enums.
    if(action==='follow_engage')return [{value:'social_profile',label:'Sosyal medya profili / içerik',owned:true}];
    const available=(data?.options||[]).filter(o=>o.questionId==='S1_B02');
    const result=fixed[action]?fixed[action].map(value=>available.find(o=>o.value===value)).filter(Boolean):[...available];
    if(['understand','remember'].includes(action))result.push({value:'none',label:'Yönlendirme yok · mesajı görmesi yeterli',owned:true});
    return result;
  }
  function destinationApplies(communication,action,data){
    if(!intentActions(communication).includes(action))return false;
    const source=data?.questions?.find(q=>q.id==='S1_B02');
    return source?.showWhen?.S1_Q01?.includes(communication)===true ||
      ['visit_store','visit_website','buy_online','buy_marketplace','message_whatsapp','call','fill_form','book_appointment','download_app','register_event','apply_job','follow_engage'].includes(action);
  }
  const urlLabels={own_website:'Web sitesi / sayfa bağlantısı',marketplace:'Ürün / mağaza bağlantısı',lead_form:'Başvuru / kayıt formu bağlantısı',app:'Uygulama / mağaza bağlantısı',social_profile:'Sosyal medya profili / içerik bağlantısı'};
  const knownDestinations=new Set([...Object.keys(urlLabels),'physical_store','whatsapp_phone','none','__other__']);
  function destinationFields(type,action){
    if(Object.hasOwn(urlLabels,type))return [{key:'url',label:urlLabels[type],type:'url',required:true,maxLength:2048,placeholder:'https://ornek.example/'}];
    if(type==='whatsapp_phone')return [{key:'phone',label:action==='call'?'Aranacak telefon numarası':'WhatsApp / telefon numarası',type:'tel',required:true,maxLength:40,placeholder:'+90 555 000 00 00'}];
    if(type==='physical_store')return [
      {key:'address',label:'Açık adres',type:'text',required:false,maxLength:400,placeholder:'Mahalle, sokak, bina ve şehir'},
      {key:'mapUrl',label:'Harita / konum bağlantısı',type:'url',required:false,maxLength:2048,placeholder:'https://harita.example/konum'}
    ];
    return [];
  }
  function validWebUrl(value){
    if(value.length>2048 || /[\u0000-\u0020\u007f-\u009f\\]|\s/.test(value) || !/^https?:\/\//i.test(value))return false;
    try{const parsed=new URL(value);return ['http:','https:'].includes(parsed.protocol)&&!!parsed.hostname&&!parsed.username&&!parsed.password;}catch{return false;}
  }
  function validateDestination(type,values={},action){
    if(!knownDestinations.has(type))return {_form:'Geçerli bir yönlendirme türü seç.'};
    if(values===null)values={};
    if(typeof values!=='object'||Array.isArray(values))return {_form:'Yönlendirme bilgilerini alanlara ayrı ayrı gir.'};
    const fields=destinationFields(type,action),allowed=new Set(fields.map(field=>field.key)),errors={};
    if(Object.keys(values).some(key=>!allowed.has(key)))errors._form='Bu yönlendirmeyle ilgisi olmayan bilgileri kaldır.';
    for(const field of fields){
      const value=values[field.key]===undefined?'':values[field.key];
      if(typeof value!=='string'){errors[field.key]='Bu alanı metin olarak gir.';continue;}
      if(value.length>field.maxLength){errors[field.key]=`En fazla ${field.maxLength} karakter gir.`;continue;}
      if(!value.trim()){if(field.required)errors[field.key]='Bu bilgiyi tamamla.';else if(field.type==='url'&&value)errors[field.key]='http:// veya https:// ile başlayan geçerli bir bağlantı gir.';continue;}
      if(field.type==='url'&&!validWebUrl(value))errors[field.key]='http:// veya https:// ile başlayan, kullanıcı adı veya parola içermeyen geçerli bir bağlantı gir.';
      if(field.type==='tel'){
        const count=value.replace(/\D/g,'').length;
        if(!/^\+?[0-9() .-]+$/.test(value)||count<10||count>15)errors[field.key]='Ülke / alan koduyla birlikte 10–15 rakam içeren telefon numarası gir.';
      }
      if(field.key==='address'&&value.trim().length<5)errors.address='Adresi en az 5 karakterle açıkla.';
    }
    if(type==='physical_store'&&!String(values.address||'').trim()&&!String(values.mapUrl||'').trim())errors.address='Açık adres veya harita / konum bağlantısı ekle.';
    return errors;
  }
  const api={version,families,choices,familyOf,businesses,sectors,actions,contextBank,branchApplies,pruneAnswers,pruneContextAnswers,intentActions,destinations,destinationApplies,destinationFields,validateDestination};
  if(typeof module!=='undefined'&&module.exports)module.exports=api;
  root.YaparoBriefFlow=api;
})(typeof window!=='undefined'?window:globalThis);
