/* Owned demo production recipes. Not current platform specifications or execution. */
(function(root){
  'use strict';
  const version='prototype-production-v1';
  const disclaimer='Sabit demo üretim reçetesi; güncel platform şartnamesi, hesap/politika onayı veya fiyat teklifi değildir. Gerçek AI, video üretimi ve yayın yapılmaz.';
  const recipes={
    google_search_maps:[['search','Arama reklamı','text','Arama niyetine yanıt veren başlıklar, açıklamalar ve doğrulanacak yönlendirme']],
    google_pmax_shopping:[['commerce-image','Ürün görseli','image','Ürün odaklı mesaj'],['catalog','Katalog / açılış noktası','task','Feed, ürün bilgisi ve yönlendirme doğrulaması']],
    youtube:[['video','YouTube video','video','Açılış, anlatı ve aksiyon çağrısı']],
    google_display_demandgen:[['display','Display / Demand Gen görsel taslağı','image','Görsel keşif mesajı; gerçek yerleşimler ayrıca seçilir']],
    meta_social:[['feed','Instagram / Facebook Feed','image','Ürün / fayda odaklı görsel ve açıklama']],
    meta_messages:[['lead-image','Meta mesaj reklamı','image','Sohbete davet eden görsel ve metin'],['message-flow','Mesaj / form akışı','task','İletişim akışı, izinler ve yönlendirme doğrulaması']],
    tiktok:[['video','TikTok video','video','Platforma uyarlanacak doğal anlatım ve açılış']],
    linkedin:[['feed','LinkedIn akış görseli','image','Profesyonel fayda ve iş sonucu']],
    yandex_search_maps:[['search','Yandex arama metni','text','Arama niyetine ve konuma yanıt']],
    microsoft_search_shopping:[['search','Microsoft arama metni','text','Bu reçetede yalnız Search; Shopping/feed ayrı planlanır']],
    snapchat:[['video','Snapchat video','video','Dikey anlatım; AR bu reçetede yok']],
    pinterest:[['pin','Pinterest görseli','image','Keşif ve ürün ilhamı; partner/bağlantı doğrulaması ayrıca']],
    x_ads:[['feed','X akış taslağı','image','Kısa mesaj, görsel ve aksiyon çağrısı']],
    reddit:[['feed','Reddit yerel anlatım taslağı','image','Topluluk bağlamına uygun görsel ve açıklama']],
    spotify:[['audio-video','Spotify ses / video işi','task','Ses/video prodüksiyonu ve yayın formatı ayrıca belirlenmeli']],
    retail_media_marketplace:[['catalog','Pazaryeri katalog işi','task','Satıcı hesabı, feed, stok ve ürün bilgisi doğrulanmalı']],
    influencer_creator:[['creator','Üretici iş birliği brief’i','task','Üretici seçimi, kullanım hakları ve reklam açıklaması ayrıca doğrulanmalı']],
    programmatic_native_video:[['native','Native görsel taslağı','image','Yerleşime uyarlanacak başlık ve görsel'],['placement','Partner yerleşim gereksinimleri','task','Satın alma biçimi ve gerçek yerleşim şartnamesi doğrulanmalı']],
    owned_crm:[],organic_local_profile:[]
  };
  const organic={
    instagram:[['feed','Instagram organik paylaşım','image','Organik paylaşım için görsel ve açıklama']],
    facebook:[['feed','Facebook organik paylaşım','image','Organik paylaşım için görsel ve açıklama']],
    linkedin:[['feed','LinkedIn organik paylaşım','image','Profesyonel organik paylaşım']],
    tiktok:[['video','TikTok organik video','video','Organik kısa video anlatımı']],
    youtube:[['video','YouTube organik video','video','Organik video anlatımı']]
  };
  function build(options={}){
    if(!['paid','organic','both'].includes(options.mode))throw new Error('Çalışma türünü seç.');
    const videoAllowed=options.videoAllowed===true,videoAvailable=options.videoAvailable===true;
    const destinations=[...new Set(options.organicPlatforms||[])].sort();
    const selected=options.mode==='organic'?[]:(options.plan?.rows||[]).filter(r=>!r.owned&&r.channel?.tier!=='non_paid_recommendation'&&Number.isFinite(r.amount)&&r.amount>0).map(r=>({id:r.channel.id,amount:r.amount})).sort((a,b)=>a.id.localeCompare(b.id));
    const requirements=[];
    function add(channelId,items,kind){
      for(const [key,placement,medium,purpose] of items){
        const status=medium==='video'?(!videoAllowed||!videoAvailable?'blocked_material':'production_pending'):['text','image'].includes(medium)?'preview_ready':'production_pending';
        requirements.push({id:`${kind}:${channelId}:${key}`,channelId,placement,medium,quantity:1,purpose,status,label:status==='preview_ready'?'Hazırlanmış metin/görsel önizlemesi':status==='blocked_material'?'Video tercihi veya kullanılabilir materyal eksik':'Üretim / doğrulama bekliyor',usage:kind});
      }
    }
    selected.forEach(row=>{
      if(!Object.hasOwn(recipes,row.id)){add(row.id,[['unknown','Tanımsız ürün','task','Bu ürün için güvenilir üretim reçetesi yok']],'paid');return;}
      add(row.id,recipes[row.id],'paid');
      if(row.id==='meta_social'&&videoAllowed&&videoAvailable)add(row.id,[['reels','Instagram / Facebook Reels','video','Seçilen ortak fikrin hareketli uyarlaması; video render bağlı değil']],'paid');
    });
    if(options.mode!=='paid')destinations.forEach(id=>add(id,organic[id]||[['unknown','Tanımsız organik hedef','task','Bu hedef için üretim reçetesi yok']],'organic'));
    const signature=JSON.stringify({version,mode:options.mode,selected,destinations:options.mode==='paid'?[]:destinations,videoAllowed,videoAvailable});
    const blocked=requirements.filter(r=>r.status!=='preview_ready').length;
    return {version,signature,requirements,ready:requirements.length>0&&blocked===0,blocked,disclaimer,publishable:false};
  }
  function adapt(core,requirements){
    if(!core||typeof core.id!=='string'||!Number.isInteger(core.revision)||core.revision<1)throw new Error('Seçilmiş yaratıcı fikir ve revizyonu gerekli.');
    return requirements.filter(r=>r.status==='preview_ready'&&['text','image'].includes(r.medium)).map(r=>{
      const common={id:`${r.id}:${core.id}:r${core.revision}`,requirementId:r.id,channelId:r.channelId,placement:r.placement,medium:r.medium,status:'preview_ready',coreId:core.id,coreRevision:core.revision,quality:'authored_demo',publishable:false};
      if(r.medium==='text')return {...common,title:core.title||'',headlines:[core.title||'',core.angle||'',core.cta||''],descriptions:[core.message||'',`${core.cta||''} · ${r.purpose}`],destination:null,notice:'Arama metni taslağı; yönlendirme, uzunluk ve iddialar ayrıca doğrulanmalı. Görsel üretilmez.'};
      return {...common,title:core.title||'',message:core.message||'',caption:`${core.message||''} ${core.cta||''}`.trim(),cta:core.cta||'',theme:core.theme,kind:core.kind,x:core.x,y:core.y,notice:'Ortak fikirden hazırlanmış görsel yerleşim örneği; kanal şartnamesi doğrulanmadı.'};
    });
  }
  const api={version,disclaimer,build,adapt};
  if(typeof module!=='undefined'&&module.exports)module.exports=api;
  root.YaparoProduction=api;
})(typeof window!=='undefined'?window:globalThis);
