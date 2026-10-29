/* Explicit synthetic comparison only. No network, prices, account evidence or authority. */
(function (root) {
  'use strict';
  const version = 'yaparo-synthetic-budget-v1';
  const grid = Object.freeze([100000,200000,300000,500000,800000,1200000,2000000]);
  const maxMoney = 999999999;
  const validMoney = value => value === null || Number.isSafeInteger(value) && value >= 0 && value <= maxMoney;
  const frozen = value => {
    if (value && typeof value === 'object') { Object.values(value).forEach(frozen); Object.freeze(value); }
    return value;
  };
  function compare(input) {
    if (!input || !['paid','hybrid','organic','content_only','unsure'].includes(input.mode)) throw new Error('Kullanım yolunu seç.');
    for (const key of ['ceilingMinor','cashMinor','contributionMinor','productionMinor','serviceMinor']) {
      if (!validMoney(input[key])) throw new Error('Tutarları geçerli kuruş değeriyle belirt.');
    }
    if (input.capacity !== null && (!Number.isSafeInteger(input.capacity) || input.capacity < 0 || input.capacity > 1000000)) throw new Error('Dönem kapasitesini geçerli bir adet olarak belirt.');
    if (!Number.isInteger(input.days) || input.days < 1 || input.days > 365 || typeof input.commercial !== 'boolean' || typeof input.outcome !== 'string' || !input.outcome) throw new Error('Plan dönemi veya sonuç türü eksik.');
    if (!['none','synthetic'].includes(input.evidence)) throw new Error('Tahmin dayanağını seç.');
    if (input.commercial !== ['purchase','ticket'].includes(input.outcome)) throw new Error('Ziyaret, mesaj veya başvuru tamamlanan satış olarak hesaplanamaz.');
    const base = {version, status:'missing', missing:[], candidates:[], reasons:[], publicationEnabled:false, executionAuthorized:false};
    if (['organic','content_only'].includes(input.mode) || input.ceilingMinor === 0) return frozen({...base,status:'no_paid',reasons:['Ücretli medya karşılaştırılmıyor. İçerik ve hizmet maliyetleri ayrı değerlendirilir.']});
    if (input.mode === 'unsure') return frozen({...base,missing:['Ücretli, birlikte veya organik kullanım yolunu seç.']});
    if (input.evidence !== 'synthetic') base.missing.push('Gerçek tahmin bağlantısı yok. İşleyişi görmek için açıkça sentetik örneği seçebilirsin.');
    if (input.capacity === null) base.missing.push('Bu dönemde reklama ayırabileceğin ek kapasiteyi belirt; toplam işletme kapasitesi değil.');
    if (input.commercial && input.contributionMinor === null) base.missing.push('Tamamlanan bir işten doğrudan giderler çıktıktan sonra kalan tutarı belirt.');
    if (base.missing.length) return frozen(base);
    const knownCost = input.productionMinor !== null && input.serviceMinor !== null;
    const candidates = [];
    for (const mediaMinor of grid) {
      if (input.ceilingMinor !== null && mediaMinor > input.ceilingMinor) continue;
      // Deliberately fabricated cost range: 100–200 TL per declared target action.
      // No funnel conversion is inferred from an upstream click/message/visit.
      const resultsLow = Math.floor(mediaMinor / 20000), resultsHigh = Math.ceil(mediaMinor / 10000);
      if (resultsHigh > input.capacity) continue;
      const campaignCostMinor = knownCost ? mediaMinor + input.productionMinor + input.serviceMinor : null;
      if (campaignCostMinor !== null && campaignCostMinor > maxMoney) continue;
      if (input.cashMinor !== null && (campaignCostMinor === null || campaignCostMinor > input.cashMinor)) continue;
      const contributionLowMinor = input.commercial && knownCost ? resultsLow * input.contributionMinor - campaignCostMinor : null;
      if (contributionLowMinor !== null && (!Number.isSafeInteger(contributionLowMinor) || contributionLowMinor <= 0)) continue;
      candidates.push({id:`${version}:${mediaMinor}`,label:'',mediaMinor,productionMinor:input.productionMinor,serviceMinor:input.serviceMinor,campaignCostMinor,peakCashMinor:campaignCostMinor,resultsLow,resultsHigh,contributionLowMinor,capacityLimit:input.capacity,
        resultUnit:input.commercial?'varsayımsal tamamlanan iş':'varsayımsal hedef eylem',
        evidenceLabel:'Sentetik örnek · piyasa veya platform tahmini değil',
        reason:'Örnek yüksek talep dönem kapasitesini aşmıyor'+(input.commercial&&knownCost?'; düşük sonuç varsayımında katkı pozitif.':'.'),
        assumptions:['Örnek hedef eylem maliyeti 100–200 TL; ölçülmüş veri değil.','Girdiğin kapasite tüm dönem için reklama ayrılan ek miktar; günlük dağılım ve ortak kaynak rezervasyonu doğrulanmadı.','Üretim ve hizmet tutarları senin beyanın; vergi dahil karşılaştırılabilir toplam olmalı.','Nakit modeli: kampanya tutarı baştan ödeniyor; teslim gideri ve tahsilat takvimi hesaplanmadı.']});
    }
    if (!candidates.length) return frozen({...base,status:'no_feasible',reasons:['Bu örnek adaylar içinde kapasite, nakit, medya tavanı ve bilinen katkı koşullarını birlikte karşılayan seçenek yok. Tavanı harcamak zorunda değilsin; ücretli test önermiyoruz.']});
    // A finite, deliberately small sample comparison; never claim a global optimum.
    const best = input.commercial && knownCost ? candidates.reduce((a,b)=>b.contributionLowMinor>a.contributionLowMinor?b:a) : candidates[Math.floor((candidates.length-1)/2)];
    const chosen = [...new Set([candidates[0],best,candidates[candidates.length-1]])];
    for (const row of chosen) {
      const labels=[];
      if(row===candidates[0])labels.push('Başlangıç denemesi');
      if(row===best)labels.push('Örnek adaylar içinde önerilen');
      if(row===candidates[candidates.length-1])labels.push('Değerlendirilen örnek üst sınır');
      row.label=labels.join(' · ');
    }
    return frozen({...base,status:'conditional',candidates:chosen,reasons:[knownCost?'Toplamlar beyanına bağlı; fiyat teklifi değildir.':'Üretim veya hizmet bedeli bilinmiyor; toplam maliyet ve nakit teyidi hesaplanamaz.','Tüm seçenekler koşullu yerel taslaktır; günlük darboğazlar, gerçek kaynaklar ve hesap uygunluğu doğrulanmadan uygulanamaz.']});
  }
  const api = Object.freeze({version,compare});
  if (typeof module === 'object' && module.exports) module.exports=api;
  else root.YaparoBudgetPlanner=api;
})(typeof window === 'object' ? window : globalThis);
