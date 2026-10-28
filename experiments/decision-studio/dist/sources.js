/* Same-origin public-source status. No advertising account or arbitrary URL input. */
(function(root){
  'use strict';
  const stable=value=>JSON.stringify(Object.fromEntries(Object.entries(value).sort(([a],[b])=>a.localeCompare(b))));
  const labels={available:'Güncel kayıt',missing:'Henüz alınmadı',expired:'Süresi dolmuş',invalid:'Doğrulanamadı',refresh_failed:'Yenileme başarısız',context_invalid:'Plan bilgileri eksik / geçersiz',context_mismatch:'Koşullar eşleşmiyor',unqualified:'Kaynak uygun değil'};
  const money=n=>Number(n).toLocaleString('tr-TR',{minimumFractionDigits:4,maximumFractionDigits:4});
  let config=null,element=null,bundle=null,sequence=0,timer=null,busy=false,expiresTimer=null,provider='ecb';
  const providerName=()=>provider==='tcmb'?'TCMB gösterge satış':'ECB çapraz referans';
  function node(tag,text){const n=document.createElement(tag);if(text!==undefined)n.textContent=text;return n;}
  function dateTime(s){if(!s)return '—';const d=new Date(s);return Number.isFinite(d.getTime())?d.toLocaleString('tr-TR',{timeZone:'Europe/Istanbul'}):'Geçersiz';}
  function currentKey(){return stable(config.readContext());}
  function fx(context){
    // FX is public USD/TRY data: shared across plan contexts. Account forecasts
    // remain exact-context snapshots and are currently unavailable.
    if(!bundle || bundle.source_provider!==provider || bundle.fx?.status!=='available' || !bundle.fx.usable)return null;
    const r=bundle.fx.snapshot,rate=Number(r?.payload?.rate),expires=Date.parse(r?.expires_at);
    if(r?.source!==provider||r.kind!=='fx'||r.scope!=='public'||r.quality!=='official_public'||r.payload?.base!=='USD'||r.payload?.quote!=='TRY'||!(rate>0&&rate<100000)||!Number.isFinite(expires)||expires<=Date.now())return null;
    return {rate,snapshot:r};
  }
  function render(){
    element.replaceChildren();element.dataset.contextHash=bundle?.context_hash||'';const heading=node('div');heading.className='source-heading';heading.append(node('strong','Veri kaynakları ve güncellik'));
    const refresh=node('button',busy?'Kaynak kontrol ediliyor…':'↻ Kaynakları yenile');refresh.type='button';refresh.id='source-refresh';refresh.className='secondary';refresh.disabled=busy;refresh.addEventListener('click',()=>request(true,true));heading.append(refresh);element.append(heading);
    const sourceLabel=node('label','Kur kaynağı');sourceLabel.htmlFor='fx-provider';const selector=node('select');selector.id='fx-provider';for(const [v,t] of [['ecb','ECB · EUR üzerinden USD/TRY çapraz referans'],['tcmb','TCMB · USD döviz satış göstergesi']]){const o=node('option',t);o.value=v;selector.append(o);}selector.value=provider;selector.disabled=busy;selector.addEventListener('change',()=>{provider=selector.value;bundle=null;changed();config.onChange();});element.append(sourceLabel,selector);
    const fxState=bundle?.fx;const line=node('p');line.id='source-status';line.setAttribute('role','status');
    line.textContent=config.canRequest&&!config.canRequest()?'Kur kontrolü için plan bilgilerini tamamla.':busy?`${providerName()} kaynağı kontrol ediliyor. Reklam platformlarına istek gönderilmez.`:`${providerName()} USD/TRY · ${labels[fxState?.status]||'Durum okunuyor'}`;element.append(line);
    const record=fxState?.snapshot;
    if(record?.payload?.rate){const value=node('p',`Son kayıt: 1 USD = ${money(record.payload.rate)} TRY · ${fxState.usable?providerName():'Güncel hesapta kullanılmıyor'}`);value.className='source-rate';element.append(value);
      const dates=node('p',`Kaynak tarihi: ${record.source_as_of} · Alındı: ${dateTime(record.fetched_at)} · Geçerlilik: ${dateTime(record.expires_at)}`);dates.className='hint';element.append(dates);
    }
    if(bundle?.refresh_result==='cooldown')element.append(node('p','Çok sık yenileme önlendi. Bir dakika dolunca tekrar deneyebilirsin.'));
    if(fxState?.status==='refresh_failed')element.append(node('p','Kaynağa erişilemedi. Önceki kayıt varsa tarihini gösteriyoruz; güncel kur olarak kullanmıyoruz.'));
    const available=fx(config.readContext());element.append(node('p',available?'Bu kur yalnız para birimi dönüşümünü günceller. Kanal erişimi / maliyet tahmini sağlamaz.':'Simülasyon hesapları tarihli örnek kur kullanabilir; bu gerçek ve güncel bir fiyat teklifi değildir.'));
    const details=node('details'),summary=node('summary','Reklam tahmin kaynakları · bağlantı bekliyor');details.append(summary);
    for(const f of bundle?.forecasts||[]){const row=node('p',`${config.channelName(f.channel_id)}: ${f.reason}`);row.className='hint';details.append(row);}
    if(!bundle?.forecasts?.length)details.append(node('p','Henüz seçili ücretli kanal yok. Google/Meta ve diğer hesapların tahmin erişimi bağlanmadı.'));
    details.append(node('p','Gerçek hesap tahmini olmadan simülasyon sonuçları canlı tahmine dönüştürülmez. Hesap erişimi, ülke/konum, hedef, kreatif, tarih ve bütçe bağlamı ayrıca doğrulanır.'));
    element.append(details);const foot=node('p','Seçilen resmî kaynağın son yayını kullanılır; otomatik kaynak değişimi yoktur. ECB çapraz kuru TCMB satış kuru değildir. Sorgu tarihi yayın tarihi değildir. İşlem kuru / performans garantisi sunulmaz.');foot.className='hint';element.append(foot);
  }
  async function request(refresh=false,force=false){
    if(config.canRequest&&!config.canRequest()){sequence++;busy=false;bundle=null;render();return;}
    const own=++sequence,context=config.readContext(),key=stable(context),channels=config.readChannels(),requestedProvider=provider;
    if(refresh){busy=true;render();}
    try{
      const response=await fetch(refresh?'/api/sources/refresh':'/api/sources/status',{method:'POST',headers:{'Content-Type':'application/json','X-Yaparo-Source':'local-synthetic'},body:JSON.stringify({context,channels,force,source:requestedProvider})});
      if(!response.ok)throw new Error(response.status===400?'context_invalid':'source_unavailable');
      const result=await response.json();
      if(own!==sequence||key!==currentKey())return;
      if(result.schema!=='yaparo-source-status-v1'||result.source_provider!==requestedProvider||provider!==requestedProvider||stable(result.context)!==key||result.scope!=='local-synthetic')throw new Error('context_mismatch');
      const prior=fx(context)?.snapshot.id;bundle=result;busy=false;render();
      clearTimeout(expiresTimer);const expires=Date.parse(bundle.fx?.snapshot?.expires_at);
      if(Number.isFinite(expires)&&expires>Date.now())expiresTimer=setTimeout(()=>{if(bundle?.fx){bundle.fx.status='expired';bundle.fx.usable=false;render();config.onChange();request(true,false);}},Math.min(expires-Date.now()+5,2147483647));
      if(prior!==fx(context)?.snapshot.id)config.onChange();
    }catch(error){
      if(own!==sequence||key!==currentKey())return;
      bundle={schema:'yaparo-source-status-v1',source_provider:requestedProvider,context,scope:'local-synthetic',fx:{status:error.message==='context_invalid'?'context_invalid':'refresh_failed',usable:false,snapshot:bundle?.fx?.snapshot||null},forecasts:[]};busy=false;render();config.onChange();
    }finally{if(own===sequence){busy=false;render();}}
  }
  function changed(){sequence++;busy=false;clearTimeout(timer);clearTimeout(expiresTimer);render();timer=setTimeout(()=>request(!fx(config.readContext()),false),350);}
  function configure(options){config=options;element=node('section');element.id='source-panel';element.className='source-panel';options.mount.append(element);render();document.getElementById('plan-form').addEventListener('input',changed);document.getElementById('plan-form').addEventListener('change',changed);document.getElementById('brief-form').addEventListener('input',changed);document.getElementById('brief-form').addEventListener('change',changed);request(true,false);}
  root.YaparoSources={configure,getFx:fx,contextChanged:changed,isCurrent:context=>!!bundle&&bundle.source_provider===provider&&stable(bundle.context)===stable(context),status:()=>bundle?structuredClone(bundle):null};
})(window);
