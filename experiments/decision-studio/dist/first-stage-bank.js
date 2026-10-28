/* Owned first-stage product schema. No platform rules, source-business mappings or I/O. */
(function (root) {
  'use strict';
  const version = 'yaparo-first-stage-runtime-1';
  const labels = {
    promote: 'Bir marka, ürün veya hizmeti tanıtmak', sell: 'Satış yapmak veya kampanya duyurmak',
    event: 'Bir etkinliğe katılımcı bulmak', lead: 'Talep, teklif veya randevu almak',
    hire: 'İşe alım için başvuru toplamak', fundraise: 'Bağış veya gönüllü destek toplamak',
    announce: 'Bir duyuru veya özel gün mesajı paylaşmak', community: 'Topluluk, üyelik veya eğitim çalışmamı büyütmek',
    reputation: 'Güven oluşturmak veya bir açıklama yapmak'
  };
  const routeOptions = {
    promote: [['remember','Markayı veya mesajı hatırlasın'],['understand','Bilgilensin'],['traffic','Web sitesini ziyaret etsin'],['visit','Mağazaya gelsin'],['contact','İletişime geçsin'],['install','Uygulamayı indirsin']],
    sell: [['purchase','Satın alsın'],['visit','Mağazaya gelsin'],['message','Mesajla sipariş versin'],['call','Telefonla sipariş versin'],['traffic','Web sitesini ziyaret etsin'],['understand','Kampanyayı öğrensin']],
    event: [['register','Kayıt olsun'],['ticket','Bilet alsın'],['visit','Etkinliğe gelsin'],['understand','Etkinlik hakkında bilgi alsın'],['message','Mesajla bilgi istesin']],
    lead: [['lead_form','Form doldursun'],['quote','Teklif istesin'],['book','Randevu alsın'],['call','Telefonla arasın'],['message','Mesaj yazsın'],['meeting','Görüşme ayarlasın']],
    hire: [['apply','İşe başvursun'],['traffic','İlanı incelesin'],['message','Başvuru hakkında mesaj yazsın']],
    fundraise: [['donate','Bağış yapsın'],['materials','Malzeme desteği versin'],['volunteer','Gönüllü olsun'],['understand','Çalışma hakkında bilgilensin'],['traffic','Destek sayfasını ziyaret etsin'],['share','Çağrıyı paylaşsın']],
    announce: [['understand','Bilgilensin'],['remember','Mesajı hatırlasın'],['traffic','Duyuru sayfasını ziyaret etsin'],['share','Mesajı paylaşsın'],['follow','Hesabı takip etsin']],
    community: [['join','Topluluğa katılsın'],['subscribe','Üye veya abone olsun'],['register','Eğitime kayıt olsun'],['traffic','İçeriği incelesin'],['follow','Hesabı takip etsin']],
    reputation: [['understand','Mesajı anlasın'],['remember','Kurumu veya mesajı hatırlasın'],['traffic','Açıklamayı veya dayanağı incelesin'],['share','Mesajı paylaşsın']]
  };
  const opt = values => values.map(([value,label]) => ({value,label}));
  const question = (id,label,type='text',required=true,extra={}) => ({id,label,type,required,group:'Çalışmanın ayrıntıları',maxLength:type==='textarea'?600:160,...extra});
  const select = (id,label,options,required=true,extra={}) => question(id,label,'select',required,{options:opt(options),...extra});
  const multi = (id,label,options,required=true,extra={}) => question(id,label,'multiselect',required,{options:opt(options),...extra});
  const number = (id,label,required=true,extra={}) => question(id,label,'number',required,{min:0,max:1000000000000,step:'any',...extra});
  const other = (list,answers,parent,label='Kendi yanıtını yaz') => { if (answers[parent]==='other' || Array.isArray(answers[parent]) && answers[parent].includes('other')) list.push(question(parent+'_other',label)); };
  const currencies = [['TRY','Türk lirası'],['USD','ABD doları'],['EUR','Euro']];
  const currency = id => select(id,'Para birimi',currencies);
  const yesno = [['yes','Evet'],['no','Hayır']];
  const proofOptions = [['information','Ürün / hizmet bilgisi'],['demo','Gösterim'],['review','İzinli kullanıcı yorumu'],['source','Belge veya kamuya açık kaynak'],['none','Henüz eklemeyeceğim']];
  const audienceOptions = [['individuals','Bireyler'],['families','Aileler'],['business','İşletmeler'],['community','Belirli bir topluluk']];
  function audienceFields(list,a,id,label,options=audienceOptions) {
    list.push(select(id,label,options));
    if (a[id]==='business') list.push(select(id+'_detail','Hangi işletmeler?', [['small','Küçük işletmeler'],['corporate','Kurumsal ekipler'],['professionals','Bağımsız profesyoneller'],['other','Kendi grubum']]));
    if (a[id]==='individuals' || a[id]==='families') list.push(select(id+'_detail','Hangi ihtiyacı karşılıyor?', [['everyday','Günlük ihtiyaç'],['special','Belirli bir ihtiyaç veya ilgi'],['existing','Mevcut kullanıcıların ihtiyacı'],['other','Kendi tanımım']]));
    if (a[id]==='community') list.push(question(id+'_detail','Topluluğu kısa tanımla'));
    other(list,a,id); other(list,a,id+'_detail');
  }
  function dates(list,a,prefix,label='Ne zaman?',allowRecurring=true) {
    list.push(select(prefix+'_timing',label,[['single','Tek tarih'],['range','Tarih aralığı'],...(allowRecurring?[['recurring','Tekrarlayan']]:[]),['unknown','Henüz kesinleşmedi']]));
    if (['single','range','recurring'].includes(a[prefix+'_timing'])) list.push(question(prefix+'_start','Başlangıç tarihi','date'));
    if (a[prefix+'_timing']==='range') list.push(question(prefix+'_end','Bitiş tarihi','date'));
    if (a[prefix+'_timing']==='recurring') list.push(select(prefix+'_recurrence','Ne sıklıkta?', [['daily','Her gün'],['weekly','Her hafta'],['monthly','Her ay'],['other','Kendi düzenim']]));
    other(list,a,prefix+'_recurrence','Tekrarlama düzeni');
  }
  function location(list,prefix,label,extra={}) {
    list.push(question(prefix+'_address',label+' açık adres veya yer adı','text',false,{essential:true,help:'Açık adres veya harita bağlantısından en az birini ekle. Reklam hedefleme bölgesi değildir; platform konumu doğrulanmaz.',...extra}));
    list.push(question(prefix+'_map_url',label+' harita bağlantısı','url',false,{essential:true,maxLength:2048,...extra}));
  }
  function price(list,a,prefix,label='Katılım ücretli mi?',show=true) {
    list.push(select(prefix+'_fee',label,[['free','Ücretsiz'],['paid','Ücretli'],['mixed','Bazı katılımlar ücretli'],['unknown','Henüz belli değil']]));
    if (show && ['paid','mixed'].includes(a[prefix+'_fee'])) {
      list.push(number(prefix+'_amount','Ücret tutarı'),currency(prefix+'_currency'));
      if(a[prefix+'_fee']==='mixed')list.push(question(prefix+'_fee_conditions','Ücret hangi katılımlarda geçerli?'));
    }
  }
  function bankFields(intent,outcome,a) {
    const list = [];
    if (intent==='promote') {
      list.push(select('promote_kind','Neyi tanıtıyoruz?',[['brand','Marka'],['product','Ürün'],['service','Hizmet'],['project','Proje'],['other','Kendi tanımım']]));
      other(list,a,'promote_kind');
      list.push(question('promote_name','Adı veya kısa konu tanımı nedir?'));
      list.push(select('promote_strength','En çok hangi yönü öne çıksın?',[['quality','Kalite'],['ease','Kolaylık'],['innovation','Yenilik'],['expertise','Uzmanlık'],['design','Tasarım'],['social','Sosyal fayda'],['other','Kendi yanıtım']]));
      other(list,a,'promote_strength'); audienceFields(list,a,'promote_audience','Kime fayda sağlıyor?');
      list.push(select('promote_proof','Bunu destekleyen ne var?',proofOptions));
      if (a.promote_proof && a.promote_proof!=='none') list.push(question('promote_proof_note','Kullanılabilir dayanağı kısa açıkla','textarea',false,{help:'Kişisel veri veya özel belge ekleme; bu not doğrulama değildir.'}));
    }
    if (intent==='sell') {
      list.push(select('sell_kind','Ne sunuyorsun?',[['product','Ürün'],['service','Hizmet'],['bundle','Paket'],['subscription','Abonelik'],['other','Kendi tanımım']])); other(list,a,'sell_kind');
      list.push(select('sell_offer','Nasıl bir teklif var?',[['regular','Normal satış'],['discount','İndirim'],['launch','Yeni ürün'],['bundle','Paket avantajı'],['trial','Deneme'],['limited','Sınırlı fırsat']]));
      list.push(question('sell_name','Ürün veya teklifin adı ne?'));
      list.push(select('sell_conditions','Hangi koşullar geçerli?',[['all','Herkese açık'],['selected','Seçili ürünlerde'],['new','Yeni müşterilerde'],['members','Üyelere özel'],['quantity','Adet koşullu'],['other','Kendi koşulum']]));
      other(list,a,'sell_conditions');
      if(a.sell_conditions==='selected')list.push(question('sell_selected','Hangi ürünlerde geçerli?'));
      if(a.sell_conditions==='quantity')list.push(number('sell_min_quantity','En az kaç adet?',true,{min:1,step:1}));
      list.push(select('sell_show_price','Fiyatı içerikte gösterelim mi?',[['yes','Evet'],['no','Hayır'],['unknown','Henüz belli değil']]));
      if(a.sell_show_price==='yes')list.push(number('sell_price','Gösterilecek fiyat'),currency('sell_currency'));
      if(a.sell_offer==='discount')list.push(number('sell_regular_price','İndirim öncesi fiyat'),question('sell_price_evidence','Önceki fiyatın dayanağı nedir?','textarea',true,{help:'Yalnız açıklama; mevzuat veya fiyat doğrulaması sayılmaz.'}));
      list.push(select('sell_timing','Teklifin süresi var mı?',[['ongoing','Sürekli'],['range','Belirli tarihler'],['limited','Kontenjan veya stok bitene kadar']]));
      if(a.sell_timing==='range')list.push(question('sell_start','Başlangıç tarihi','date'),question('sell_end','Bitiş tarihi','date'));
      if(a.sell_timing==='limited')list.push(number('sell_limit','Bilinen adet veya kontenjan',true,{min:1,step:1}));
    }
    if (intent==='event') {
      list.push(select('event_kind','Nasıl bir etkinlik?',[['workshop','Atölye'],['education','Eğitim veya seminer'],['performance','Konser veya gösteri'],['meetup','Buluşma'],['fair','Fuar veya lansman'],['sport','Spor'],['other','Kendi etkinliğim']])); other(list,a,'event_kind');
      list.push(question('event_name','Etkinliğin adı ne?'));
      list.push(select('event_mode','Nasıl yapılacak?',[['physical','Yüz yüze'],['online','Çevrimiçi'],['hybrid','Karma']]));
      dates(list,a,'event');
      if(['physical','hybrid'].includes(a.event_mode))location(list,'event_location','Etkinlik');
      if(['online','hybrid'].includes(a.event_mode)){
        list.push(select('event_online_method','Çevrimiçi katılım nasıl olacak?',[['page','Katılım sayfası'],['invite','Kayıttan sonra davet'],['unknown','Henüz belli değil']]));
        if(a.event_online_method==='page')list.push(question('event_online_url','Çevrimiçi katılım bağlantısı','url',true,{maxLength:2048}));
      }
      price(list,a,'event');
      list.push(select('event_eligibility','Kimler katılabilir?',[['open','Herkese açık'],['application','Başvuru ile'],['members','Üyelere özel'],['conditions','Ön koşullu']]));
      if(a.event_eligibility==='conditions')list.push(question('event_conditions','Katılım ön koşulu nedir?'));
      list.push(select('event_capacity_status','Kontenjan belli mi?', [['known','Evet'],['unlimited','Kontenjan yok'],['unknown','Henüz belli değil']],false));
      if(a.event_capacity_status==='known')list.push(number('event_capacity','Katılımcı kontenjanı',true,{min:1,step:1}));
    }
    if (intent==='lead') {
      list.push(question('lead_service','Hangi hizmet veya çözüm için?'));
      list.push(select('lead_contact_purpose','İlk temas ne için olacak?',[['information','Bilgi alma'],['discovery','İhtiyaç görüşmesi'],['quote','Fiyat teklifi'],['reservation','Rezervasyon'],['appointment','Hizmet randevusu'],['other','Kendi yanıtım']])); other(list,a,'lead_contact_purpose');
      audienceFields(list,a,'lead_audience','Bu hizmet kimler için?',[['individuals','Bireyler'],['business','İşletmeler'],['existing','Mevcut müşteriler'],['community','Belirli bir grup']]);
      list.push(select('lead_delivery','Hizmeti nasıl veriyorsun?',[['onsite','İş yerimde'],['customer','Müşterinin yerinde'],['online','Çevrimiçi'],['mixed','Birden fazla yöntem']]));
      list.push(select('lead_conditions','Önceden bilinmesi gereken koşul var mı?',[['none','Yok'],['region','Hizmet bölgesi'],['eligibility','Uygunluk şartı'],['minimum','Asgari sipariş veya proje'],['other','Kendi koşulum']]));
      if(a.lead_conditions && a.lead_conditions!=='none')list.push(question('lead_condition_note',a.lead_conditions==='region'?'Hizmet verebildiğin bölge':'Koşulu kısa açıkla','textarea',true,{help:'Hizmet bölgesi reklam hedefleme alanı yerine geçmez.'}));
    }
    if (intent==='hire') {
      list.push(question('hire_role','Hangi pozisyon için?'));
      list.push(select('hire_type','Çalışma türü ne?',[['full','Tam zamanlı'],['part','Yarı zamanlı'],['contract','Sözleşmeli'],['seasonal','Dönemsel'],['intern','Staj']]));
      list.push(select('hire_model','Nerede çalışılacak?',[['onsite','İş yerinde'],['remote','Uzaktan'],['hybrid','Karma']]));
      if(['onsite','hybrid'].includes(a.hire_model))location(list,'hire_location','İş yeri');
      list.push(question('hire_duties','Temel görev nedir?','textarea'));
      list.push(multi('hire_qualifications','Hangi işe ilişkin nitelikler gerekli?',[['experience','Deneyim'],['technical','Teknik beceri'],['education','Eğitim veya yetkinlik'],['certificate','İşe özgü belge'],['none','Deneyim şartı yok']]));
      if(Array.isArray(a.hire_qualifications))for(const [key,label] of [['experience','Gerekli deneyim'],['technical','Gerekli teknik beceri'],['education','Gerekli eğitim veya yetkinlik'],['certificate','İşe özgü belge koşulu']])if(a.hire_qualifications.includes(key))list.push(question('hire_'+key,label));
      list.push(select('hire_deadline_status','Başvuru için son tarih var mı?',[['set','Tarih var'],['open','Başvurular açık'],['unknown','Henüz kesinleşmedi']]));
      if(a.hire_deadline_status==='set')list.push(question('hire_deadline','Son başvuru tarihi','date'));
    }
    if (intent==='fundraise') {
      list.push(select('fundraise_organizer_type','Bu çağrıyı kim düzenliyor?',[['association','Dernek'],['foundation','Vakıf'],['institution','Kurum'],['person','Kişi'],['community','Topluluk'],['other','Kendi tanımım']])); other(list,a,'fundraise_organizer_type');
      list.push(question('fundraise_organizer_name','Düzenleyicinin adı'));
      list.push(select('fundraise_purpose','Hangi amaç için destek istiyorsun?',[['education','Eğitim'],['needs','Gıda veya temel ihtiyaç'],['disaster','Afet ve acil destek'],['health','Sağlık desteği'],['animals','Hayvan refahı'],['environment','Çevre'],['culture','Kültür veya topluluk'],['other','Kendi amacım']])); other(list,a,'fundraise_purpose');
      list.push(question('fundraise_goal','Destek neyi gerçekleştirecek?','textarea',true,{help:'Kişi adı, sağlık bilgisi veya özel belge ekleme.'}));
      if(['donate','materials'].includes(outcome))list.push(select('fundraise_permit','İzin veya istisna durumunu biliyor musun?',[['licensed','İzin belgem var'],['exempt','İzin almadan toplama yetkisi veya istisna dayanağım var'],['pending','Süreç devam ediyor'],['unknown','Bilmiyorum']],true,{help:'Bu bir beyan sorusudur; hukuki doğrulama veya yayın izni değildir.'}));
      if(['understand','traffic','share'].includes(outcome))list.push(multi('fundraise_support_types','Çalışmada hangi destek türleri var?',[['money','Para'],['materials','Malzeme'],['volunteer','Gönüllü emek']],false));
      if(outcome==='donate'){
        list.push(select('fundraise_target_status','Parasal hedef belirli mi?',[['set','Belirli'],['unknown','Henüz belli değil']]));
        if(a.fundraise_target_status==='set')list.push(number('fundraise_target','Hedef tutar',true,{min:.01}),currency('fundraise_currency'));
      }
      if(['donate','materials','volunteer'].includes(outcome)){
        list.push(select('fundraise_duration','Destek çağrısının süresi belli mi?',[['range','Belirli tarihler'],['ongoing','Sürekli'],['unknown','Henüz belli değil']],false));
        if(a.fundraise_duration==='range')list.push(question('fundraise_start','Başlangıç tarihi','date'),question('fundraise_end','Bitiş tarihi','date'));
      }
    }
    if (intent==='announce') {
      list.push(select('announce_kind','Nasıl bir duyuru?',[['opening','Açılış'],['hours','Hizmet veya saat değişikliği'],['update','Yeni gelişme'],['celebration','Kutlama veya teşekkür'],['information','Bilgilendirme'],['other','Kendi duyurum']])); other(list,a,'announce_kind');
      list.push(question('announce_identity','Hangi kişi veya kurum adına?'),question('announce_facts','İletilecek kesin bilgi ne?','textarea'));
      list.push(select('announce_timing','Ne zaman geçerli?',[['single','Belirli tarih'],['range','Tarih aralığı'],['ongoing','Sürekli'],['none','Tarih gerekmiyor']]));
      if(['single','range'].includes(a.announce_timing))list.push(question('announce_start','Geçerlilik tarihi','date'));
      if(a.announce_timing==='range')list.push(question('announce_end','Bitiş tarihi','date'));
      if(a.announce_kind==='opening')location(list,'announce_location','Açılış yeri');
      if(a.announce_kind==='hours'){
        list.push(question('announce_hours_start','Yeni başlangıç saati','time'),question('announce_hours_end','Yeni bitiş saati','time'));
        list.push(select('announce_overnight','Bitiş saati ertesi güne mi ait?',yesno));
      }
      audienceFields(list,a,'announce_audience','Kimleri ilgilendiriyor?',[['customers','Müşteriler'],['employees','Çalışanlar'],['members','Üyeler'],['local','Bölge sakinleri'],['public','Genel kamu'],['other','Kendi grubum']]);
    }
    if (intent==='community') {
      list.push(select('community_kind','Neye katılım istiyorsun?',[['community','Topluluk'],['membership','Üyelik veya abonelik'],['course','Kurs veya eğitim'],['meetup','Düzenli buluşma'],['other','Kendi çalışmam']])); other(list,a,'community_kind');
      list.push(question('community_name','Topluluk, program veya eğitimin adı'));
      list.push(select('community_value','Katılımcı ne kazanacak?',[['learn','Öğrenme'],['share','Deneyim paylaşımı'],['create','Birlikte üretim'],['content','İçeriğe erişim'],['solidarity','Dayanışma'],['other','Kendi faydam']])); other(list,a,'community_value');
      list.push(select('community_eligibility','Kimler için uygun?',[['open','Herkese açık'],['beginner','Başlangıç düzeyi'],['experienced','Belirli deneyim düzeyi'],['profession','Meslek veya ilgi alanı'],['conditions','Ön koşullu']]));
      if(['experienced','profession','conditions'].includes(a.community_eligibility))list.push(question('community_conditions','Uygunluk veya katılım koşulunu açıkla'));
      price(list,a,'community','Katılım ücretli mi?', ['join','subscribe','register'].includes(outcome));
      if(['course','meetup'].includes(a.community_kind)){
        list.push(select('community_mode','Nasıl yapılacak?',[['physical','Yüz yüze'],['online','Çevrimiçi'],['hybrid','Karma']]));
        if(['physical','hybrid'].includes(a.community_mode))location(list,'community_location','Katılım yeri');
        dates(list,a,'community','Katılım tarihi belli mi?');
      }
      if(outcome==='subscribe'&&['paid','mixed'].includes(a.community_fee))list.push(select('community_billing','Ücret ne sıklıkla alınır?',[['once','Tek sefer'],['monthly','Aylık'],['yearly','Yıllık'],['other','Kendi dönemim']])); other(list,a,'community_billing');
    }
    if (intent==='reputation') {
      list.push(select('reputation_kind','Nasıl bir çalışma?',[['expertise','Uzmanlığı göstermek'],['experience','Müşteri deneyimini anlatmak'],['statement','Kurumsal açıklama'],['correction','Yanlış bilgiyi düzeltmek'],['public','Toplumsal konuyu açıklamak'],['other','Kendi konum']])); other(list,a,'reputation_kind');
      list.push(question('reputation_identity','Kim adına konuşuyoruz?'),question('reputation_message','Ana mesaj ne?','textarea'));
      list.push(select('reputation_proof','Mesajın dayanağı ne?',[['public','Kamuya açık kaynak'],['document','Belge'],['review','İzinli deneyim veya yorum'],['data','Veriye dayalı açıklama'],['none','Henüz dayanak yok']]));
      if(a.reputation_proof&&a.reputation_proof!=='none')list.push(question('reputation_proof_note','Dayanağı kısa açıkla','textarea',false,{help:'Özel belge veya kişisel veri ekleme; kaynağın doğruluğu ayrıca incelenir.'}));
      audienceFields(list,a,'reputation_audience','Kimlerin bilmesini istiyorsun?',[['customers','Mevcut müşteriler'],['partners','İş ortakları'],['employees','Çalışanlar'],['community','Belirli topluluk'],['public','Genel kamu'],['other','Kendi grubum']]);
      list.push(select('reputation_scope','Özel bir konu kapsamı var mı?',[['ordinary','Genel açıklama'],['political','Politik veya kamusal mesele'],['health','Sağlık'],['finance','Finans'],['unknown','Henüz net değil']],false,{help:'Bu seçim politika onayı değildir; gerekli inceleme sonraki kapıda yapılır.'}));
    }
    return list;
  }
  function methodFields(list,a,id,label,methods) { list.push(select(id,label,methods)); other(list,a,id,'Kullanılacak yöntemi açıkla'); }
  function phone(list,id,label='Telefon numarası') {list.push(question(id,label,'tel',true,{maxLength:24}));}
  function url(list,id,label) {list.push(question(id,label,'url',true,{maxLength:2048}));}
  function messaging(list,a,prefix='action',label='Mesaj hangi yoldan gönderilsin?') {
    methodFields(list,a,prefix+'_message_method',label,[['whatsapp','WhatsApp'],['social','Sosyal medya mesajı'],['email','E-posta']]);
    if(a[prefix+'_message_method']==='whatsapp')phone(list,prefix+'_phone','WhatsApp numarası');
    if(a[prefix+'_message_method']==='social')url(list,prefix+'_profile_url','Mesaj gönderilecek profil bağlantısı');
    if(a[prefix+'_message_method']==='email')list.push(question(prefix+'_email','İletişim e-posta adresi','email',true,{maxLength:254}));
  }
  function outcomeFields(intent,outcome,a) {
    const list=[];
    if(['remember','understand'].includes(outcome) && !['reputation','announce','fundraise'].includes(intent))list.push(question('action_message','Aklında kalmasını istediğin ana mesaj','textarea',false));
    if(outcome==='traffic')url(list,'action_url',({hire:'İlan bağlantısı',fundraise:'Destek veya bilgilendirme sayfası',reputation:'Açıklama veya dayanak bağlantısı',community:'İncelenecek içerik veya program bağlantısı',announce:'Duyuru bağlantısı',sell:'Ürün veya kampanya bağlantısı'})[intent]||'Ziyaret edilecek web sayfası');
    if(outcome==='visit'&&intent!=='event')location(list,'action_location','Ziyaret edilecek yer');
    if(outcome==='purchase'){
      methodFields(list,a,'action_checkout','Satın alma nerede tamamlanacak?',[['website','Web sitesi'],['marketplace','Pazaryeri'],['store','Mağaza'],['message','Mesaj'],['phone','Telefon']]);
      if(['website','marketplace'].includes(a.action_checkout))url(list,'action_url','Ürün veya satış bağlantısı');
      if(a.action_checkout==='store')location(list,'action_location','Satın alınacak yer');
      if(a.action_checkout==='message')messaging(list,a);
      if(a.action_checkout==='phone')phone(list,'action_phone','Sipariş için aranacak numara');
    }
    if(outcome==='call')phone(list,'action_phone',intent==='sell'?'Sipariş için aranacak numara':'Aranacak telefon numarası');
    if(outcome==='message')messaging(list,a);
    if(outcome==='contact'){
      methodFields(list,a,'action_contact','Nasıl iletişime geçsin?',[['phone','Telefon'],['message','Mesaj'],['form','İletişim formu'],['email','E-posta']]);
      if(a.action_contact==='phone')phone(list,'action_phone');
      if(a.action_contact==='message')messaging(list,a);
      if(a.action_contact==='form')url(list,'action_url','İletişim formu bağlantısı');
      if(a.action_contact==='email')list.push(question('action_email','İletişim e-posta adresi','email',true,{maxLength:254}));
    }
    if(['lead_form','quote'].includes(outcome)){
      methodFields(list,a,'action_lead_method',outcome==='quote'?'Teklif talebi nasıl alınacak?':'Form veya talep yöntemi nedir?',[['form','Mevcut form'],['email','E-posta'],['message','Mesaj'],['new','Henüz formum yok']]);
      if(a.action_lead_method==='form')url(list,'action_url','Talep formu bağlantısı');
      if(a.action_lead_method==='email')list.push(question('action_email','Talep e-posta adresi','email',true,{maxLength:254}));
      if(a.action_lead_method==='message')messaging(list,a);
      if(a.action_lead_method==='new')list.push(question('action_form_need','Formda hangi temel ihtiyaç öğrenilmeli?','textarea',true,{help:'Burada müşteri verisi toplanmaz; yeni form henüz oluşturulmaz.'}));
    }
    if(['book','meeting'].includes(outcome)){
      methodFields(list,a,'action_booking','Randevu veya görüşme nasıl ayarlanacak?',[['page','Rezervasyon sayfası'],['phone','Telefon'],['message','Mesaj'],['system','Mevcut rezervasyon sistemi']]);
      if(['page','system'].includes(a.action_booking))url(list,'action_url','Rezervasyon bağlantısı');
      if(a.action_booking==='phone')phone(list,'action_phone');
      if(a.action_booking==='message')messaging(list,a);
    }
    if(['register','ticket','join','subscribe'].includes(outcome)){
      const title={register:'Kayıt nasıl yapılacak?',ticket:'Bilet nereden alınacak?',join:'Topluluğa nasıl katılınacak?',subscribe:'Üyelik veya abonelik nereden başlayacak?'}[outcome];
      methodFields(list,a,'action_join_method',title,[['page','Kayıt / katılım sayfası'],['email','E-posta'],['message','Mesaj'],['other','Kendi yöntemim']]);
      if(a.action_join_method==='page')url(list,'action_url',outcome==='ticket'?'Bilet sayfası bağlantısı':'Kayıt / katılım bağlantısı');
      if(a.action_join_method==='email')list.push(question('action_email','Kayıt e-posta adresi','email',true,{maxLength:254}));
      if(a.action_join_method==='message')messaging(list,a);
    }
    if(outcome==='apply'){
      methodFields(list,a,'action_apply_method','Başvuru hangi yoldan yapılacak?',[['form','Başvuru formu'],['career','Kariyer sayfası'],['email','E-posta'],['message','Mesaj']]);
      if(['form','career'].includes(a.action_apply_method))url(list,'action_url','İş başvurusu bağlantısı');
      if(a.action_apply_method==='email')list.push(question('action_email','Başvuru e-posta adresi','email',true,{maxLength:254}));
      if(a.action_apply_method==='message')messaging(list,a);
    }
    if(outcome==='donate'){
      methodFields(list,a,'action_donation_method','Para desteği hangi yoldan iletilecek?',[['official_page','Düzenleyicinin resmî bağış sayfası'],['platform','Yetkili platform sayfası'],['other','Yöntemi açıklayacağım']]);
      if(['official_page','platform'].includes(a.action_donation_method))url(list,'action_url','Bağış sayfası bağlantısı');
      if(a.action_donation_method==='other'){
        const note=list.find(f=>f.id==='action_donation_method_other');note.help='Hesap numarası, IBAN veya özel bilgi yazma. Yöntem ve yetki ayrıca doğrulanacak.';
      }
    }
    if(outcome==='materials'){
      list.push(question('action_materials','Hangi malzemeler gerekli?','textarea'));
      list.push(number('action_material_quantity','Hedef adet veya miktar',false,{min:0}));
      if(a.action_material_quantity!==undefined)list.push(question('action_material_unit','Miktarın birimi nedir?'));
      methodFields(list,a,'action_delivery','Malzeme nasıl teslim edilecek?',[['dropoff','Teslim noktasına bırakma'],['pickup','Adresten teslim alma'],['contact','Önce iletişim'],['other','Kendi yöntemim']]);
      if(a.action_delivery==='dropoff')location(list,'action_location','Teslim noktası');
      if(['pickup','contact'].includes(a.action_delivery))messaging(list,a);
    }
    if(outcome==='volunteer'){
      list.push(question('action_volunteer_task','Gönüllü hangi işi yapacak?','textarea'));
      list.push(select('action_volunteer_time','Beklenen zaman katkısı nedir?',[['once','Tek seferlik'],['weekly','Düzenli haftalık'],['flexible','Esnek'],['other','Kendi düzenim']])); other(list,a,'action_volunteer_time');
      list.push(question('action_volunteer_skills','Gerekli beceri veya ön koşul varsa açıkla','textarea',false));
      methodFields(list,a,'action_volunteer_apply','Gönüllü başvurusu nasıl yapılacak?',[['form','Başvuru sayfası'],['email','E-posta'],['message','Mesaj']]);
      if(a.action_volunteer_apply==='form')url(list,'action_url','Gönüllü başvuru bağlantısı');
      if(a.action_volunteer_apply==='email')list.push(question('action_email','Gönüllü başvuru e-postası','email',true,{maxLength:254}));
      if(a.action_volunteer_apply==='message')messaging(list,a);
    }
    if(outcome==='follow')url(list,'action_profile_url','Takip edilecek profil bağlantısı');
    if(outcome==='share')list.push(question('action_share_url','Paylaşılacak içerik veya çağrı bağlantısı','url',false,{maxLength:2048,help:'Henüz içerik yoksa boş bırakılabilir; açıklaman ilk aşama taslağında kalır.'}));
    if(outcome==='install'){
      list.push(select('action_app_platform','Uygulama hangi sistemlerde var?',[['android','Android'],['ios','iOS'],['both','Android ve iOS']]));
      if(['android','both'].includes(a.action_app_platform))url(list,'action_android_url','Android mağaza bağlantısı');
      if(['ios','both'].includes(a.action_app_platform))url(list,'action_ios_url','iOS mağaza bağlantısı');
    }
    return list.map(f=>({...f,group:'Seçilen sonucun bilgileri'}));
  }
  function compatible(intent,outcome) {return Object.hasOwn(routeOptions,intent)&&routeOptions[intent].some(([id])=>id===outcome);}
  function cleanInput(answers) {return answers&&typeof answers==='object'&&!Array.isArray(answers)?answers:{};}
  function fields(intent,outcome,answers={}) {
    if(!compatible(intent,outcome))return [];
    const a=cleanInput(answers);
    const result=[...bankFields(intent,outcome,a),...outcomeFields(intent,outcome,a),select('delivery_mode','Bu çalışma nasıl kullanılacak?',[['paid','Ücretli reklam'],['organic','Kendi hesaplarımda paylaşım'],['hybrid','İkisi birlikte'],['content_only','Yalnız içerik hazırlama'],['unsure','Plan aşamasında karar verelim']],true,{group:'Kullanım',help:'İçerik hazırlama seçimi indirme veya dışa aktarma özelliği açmaz.'}),select('risk','Özel bir konu veya kitle kapsamı var mı?',[['normal','Özel kapsam belirtmiyorum'],['fundraising','Yardım veya bağış'],['health','Sağlık'],['finance','Finans'],['political','Politik içerik'],['children','Çocuklara yönelik'],['alcohol_tobacco','Alkol veya tütün'],['gambling','Bahis veya kumar']],false,{group:'Özel koşullar',role:'risk',help:'Bu beyan platform uygunluğu veya yayın izni sağlamaz. Amaçtan doğan koşullar bu seçimle kaldırılmaz.'})];
    if(new Set(result.map(f=>f.id)).size!==result.length)throw new Error('Duplicate owned question');
    const roles={promote_name:'subject',sell_name:'subject',event_name:'subject',lead_service:'subject',hire_role:'subject',fundraise_purpose:'subject',community_name:'subject',fundraise_goal:'message',announce_facts:'message',reputation_message:'message',action_message:'message',announce_identity:'identity',reputation_identity:'identity',fundraise_organizer_name:'identity',promote_audience:'audience',lead_audience:'audience',announce_audience:'audience',reputation_audience:'audience'};
    return result.map(f=>({...f,...(roles[f.id]?{role:roles[f.id]}:{}),...(f.options?{options:f.options.map(o=>({...o}))}:{})}));
  }
  function prune(intent,outcome,answers={}) {
    if(!compatible(intent,outcome))return {};
    const input=cleanInput(answers);
    let result=Object.fromEntries(Object.entries(input).map(([key,value])=>[key,Array.isArray(value)?value.slice(0,30).map(v=>typeof v==='string'?v:null):typeof value==='string'?value.trim():typeof value==='number'?value:null]));
    for(let n=0;n<100;n++){
      const allowed=new Set(fields(intent,outcome,result).map(f=>f.id));
      const next=Object.fromEntries(Object.entries(result).filter(([key,v])=>allowed.has(key)&&v!==''&&!(Array.isArray(v)&&!v.length)));
      if(Object.keys(next).length===Object.keys(result).length)return next;
      result=next;
    }
    throw new Error('Question visibility did not converge');
  }
  function validDate(value) {
    if(typeof value!=='string'||!/^\d{4}-\d{2}-\d{2}$/.test(value))return false;
    const [y,m,d]=value.split('-').map(Number);if(y<1900||y>2200)return false;
    const date=new Date(Date.UTC(y,m-1,d));return date.getUTCFullYear()===y&&date.getUTCMonth()===m-1&&date.getUTCDate()===d;
  }
  function validUrl(value) {
    if(typeof value!=='string'||!/^https?:\/\//i.test(value)||/[\s\u0000-\u001f\u007f\\]/.test(value))return false;
    try {const u=new URL(value);return ['https:','http:'].includes(u.protocol)&&!u.username&&!u.password&&!!u.hostname;}catch{return false;}
  }
  function validate(intent,outcome,input={}) {
    const answers=prune(intent,outcome,input),errors={};
    if(!compatible(intent,outcome))return {valid:false,errors:{_route:'Önce birbiriyle uyumlu amaç ve sonuç seç.'},answers};
    for(const f of fields(intent,outcome,answers)){
      const value=answers[f.id],empty=value===undefined||value===''||Array.isArray(value)&&!value.length;
      if(empty){if(f.required)errors[f.id]='Bu bilgiyi tamamla.';continue;}
      let ok=true;
      if(f.type==='number')ok=typeof value==='number'&&Number.isFinite(value)&&value>=f.min&&value<=f.max&&(f.step!==1||Number.isInteger(value));
      else if(f.type==='select')ok=typeof value==='string'&&f.options.some(o=>o.value===value);
      else if(f.type==='multiselect')ok=Array.isArray(value)&&new Set(value).size===value.length&&value.every(v=>f.options.some(o=>o.value===v));
      else {
        ok=typeof value==='string'&&value.length<=(f.maxLength||600)&&value.trim().length>0;
        if(ok&&f.type==='url')ok=validUrl(value);
        if(ok&&f.type==='date')ok=validDate(value);
        if(ok&&f.type==='time')ok=/^([01]\d|2[0-3]):[0-5]\d$/.test(value);
        if(ok&&f.type==='tel')ok=/^\+?[\d ()-]+$/.test(value)&&value.replace(/\D/g,'').length>=7&&value.replace(/\D/g,'').length<=15;
        if(ok&&f.type==='email')ok=/^[^\s@<>]+@[^\s@<>]+\.[^\s@<>]+$/.test(value)&&!/[\r\n]/.test(value);
      }
      if(!ok)errors[f.id]='Geçerli bir yanıt gir veya seçeneklerden birini seç.';
    }
    for(const prefix of ['sell','event','fundraise','announce','community'])if(answers[prefix+'_start']&&answers[prefix+'_end']&&answers[prefix+'_end']<answers[prefix+'_start'])errors[prefix+'_end']='Bitiş tarihi başlangıçtan önce olamaz.';
    for(const prefix of ['event_location','hire_location','announce_location','community_location','action_location']){
      const active=fields(intent,outcome,answers).some(f=>f.id===prefix+'_address');
      if(active&&!answers[prefix+'_address']&&!answers[prefix+'_map_url'])errors[prefix+'_address']='Açık adres veya harita bağlantısından birini ekle.';
    }
    if(intent==='event'&&outcome==='visit'&&answers.event_mode==='online')errors.event_mode='Doğrudan ziyaret için yüz yüze veya karma etkinlik seç; çevrimiçi etkinlikte kayıt veya bilgi sonucunu kullan.';
    if(answers.sell_offer==='discount'&&typeof answers.sell_price==='number'&&typeof answers.sell_regular_price==='number'&&answers.sell_price>answers.sell_regular_price)errors.sell_price='İndirimli fiyat önceki fiyattan yüksek olamaz.';
    if(Array.isArray(answers.hire_qualifications)&&answers.hire_qualifications.includes('none')&&answers.hire_qualifications.includes('experience'))errors.hire_qualifications='Deneyim şartı yok ile deneyim şartını birlikte seçme.';
    if(answers.announce_hours_start&&answers.announce_hours_end&&answers.announce_overnight==='no'&&answers.announce_hours_end<=answers.announce_hours_start)errors.announce_hours_end='Aynı gün bitiş saati başlangıçtan sonra olmalı.';
    return {valid:!Object.keys(errors).length,errors,answers};
  }
  function summary(intent,outcome,input={}) {
    const answers=prune(intent,outcome,input);
    return fields(intent,outcome,answers).filter(f=>Object.hasOwn(answers,f.id)).map(f=>{
      const value=answers[f.id],names=f.options?new Map(f.options.map(o=>[o.value,o.label])):null;
      return {label:f.label,value:Array.isArray(value)?value.map(v=>names?.get(v)||v).join(', '):names?.get(value)||String(value)};
    });
  }
  const api={version,question:'Bu çalışmayla ne yapmak istiyorsun?',secondQuestion:'Gören kişi ne yapsın?',intents:()=>Object.entries(labels).map(([id,label])=>({id,label})),outcomes:intent=>(routeOptions[intent]||[]).map(([id,label])=>({id,label})),fields,prune,validate,summary};
  if(typeof module!=='undefined'&&module.exports)module.exports=api;
  root.YaparoFirstStage=api;
})(typeof globalThis!=='undefined'?globalThis:this);
