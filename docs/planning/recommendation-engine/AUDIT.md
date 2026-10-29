# Reklam önerisi ve bütçe motoru: mevcut durum denetimi

Kontrol tarihi: **29 Ekim 2026, Europe/Istanbul**. Bu belge araştırma ve
planlamadır; uygulama, veritabanı, hesap veya yayın değişikliği değildir.
İncelenen temel: PR373 sonrası `cba8fba` ve yerel devir kaydı `87fa86d`.
Mevcut dört aşama korunur: isteği netleştir → planı kur → içeriği oluştur →
kontrol et ve yayınla. Aşağıdaki yollar depo köküne göredir.

## 1. Sonuç

Yaparo'da korunmaya değer çalışan form, bağlama, açıklama, mali sınır ve sahiplik
bileşenleri var. Buna karşılık8014'te görülen medya önerisi **piyasa tahmini
değil, açıkça etiketli yerel senaryo**. Gerçek hesap tahmini, işletme sonuçları,
kalibrasyon ve marjinal bütçe optimizasyonu bu akışa bağlı değil. Yeni mimari bu
sınırı kaldırılmış gibi göstermemeli; kaynak sözleşmesiyle kontrollü biçimde
genişletmeli. Mevcut sistemi yeniden yazmak gerekli değil.

## 2. Çalışan, örnek, tasarım ve belirsizlik ayrımı

| Bileşen | Gerçekte bulunan | Sınır / yeni iş |
|---|---|---|
| İlk iki soru ve kısa form | `dist/first-stage-bank.js`, `first-stage-ui.js`:9 banka/46 uyumlu yol, tip/koşul/eksik alan denetimi, görünmeyen cevabı budama | Hukuki uygunluk ve gerçek belge doğrulaması değil |
| Tam bağlama | `dist/outcome-contract.js`: `resolve`, `analyze`, `signature`, `buildConcepts`; asıl niyet, beklenen davranış, literal hedef ve riskler | Bilinmeyen iş/sektör sınıfı tahmin edilmiyor; ücretli eski taksonomide karşılığı olmayan sonuç bekletiliyor |
| Kısa plan ekranı | `dist/plan-ui.js`, `first-stage-bridge.js`: ilk aşama tekrarlanmıyor; bölge/tarih/bütçe, isteğe bağlı ekonomi | Müşteri beyanı ölçülmüş kapasite/hesap hazırlığı sayılmaz |
| Kanal sıralaması | `dist/engine.js`: `evaluateOwned` yeniden doğrulanmış snapshot'tan türetiyor; bilinen boyutlara göre kısmi puan, ayrı coverage | Normal durumda40/100 kapsama üzerinden normalize puan; başarı olasılığı veya gerçek uzman kapsamı değil |
| Tahmin ve içerik | `dist/simulation.js`: `forecast`, `cards`, `alternative`, hazırlanmış yardımcı yanıtlar | CPC/CPM/CPA/erişim ve3 konsept kurgu; LLM veya reklam platformu çağrısı yok |
| Bütçe | `engine.js`: `evaluate`, `manual`; `plan-summary.js`: `check`, `bounds`, `limits`, `redistribute` | Tam kuruş, ortak tavan, minimumlar, bakiye çalışıyor; score² dağıtımı ekonomik optimum kanıtı değil |
| Konum | `dist/plan-geo.js`: `calculate`, pinlenmiş Türkiye geometrisi | Yaklaşık çevrimdışı1–800km önizlemesi; platform konum kimliği veya kesin teslim sınırı değil |
| Kaynak/güncellik | `sources.py`: `make_snapshot`, `snapshot_status`, `SourceService`; TCMB/ECB ayrımı | Gerçek genel kur kaynağı altyapısı; reklam forecast satırları halen `access_required` |
| Kanal/üretim bağı | `dist/production.js`, `app.js`: seçilen kanala göre metin/görsel tarifleri, revizyonla geçersizleşme | Sürüm onayı üretim/yayın izni değildir; gerçek video/hesap/placement doğrulaması eksik |
| Kalıcı uygulama | Django workspace/marka/kampanya/tasarım ve plan revizyonları | Ayrı uygulama;8014 bellek içi brief doğrudan kalıcı kampanyaya dönüşmüyor |
| Gerçek sonuç öğrenmesi | `campaigns/report_metrics.py` veri sözleşmeleri | Mevcut rapor alanları kaynaksızken unavailable; gerçek çok kanallı sonuç/kalibrasyon hattı bağlı değil |

`dist/` tablosundaki yollar `experiments/decision-studio/` altındadır.

## 3. Karar motorunun mevcut matematiği

`experiments/decision-studio/dist/engine.js::evaluateOwned`:

1. İlk aşamayı yeniden analiz eder, ücretli/hibrit yol ve tam hedef eşleştirmesi ister.
2. Konum, başlangıç tarihi ve sayı sınırlarını denetler; eski gizli kontrollerden
   gelen sınıf, risk ve hazırlık iddialarını yetki kabul etmez.
3. `YaparoSimulation.forecast` ile **yeni kurgusal** gözlemler oluşturur; eski
   SC01 gözlemini başka koşullara bağlamaz.
4. Ortak `evaluate` hesabına özel kapalı bağlamla girer. Politika, amaç, hesap,
   varlık, tahmin, minimum, yarıçap/kitle ve bütçe koşulları adayları süzer.
5. Hedef25/coğrafya10/bütçe5 gibi bilinen ağırlıkları normalize eder; bilinmeyen
   sektör, iş modeli, ölçüm vb. boyutları puanlamaz. Coverage güven değildir.
6. Anlamlı test minimumlarını yerleştirir; sınırlı portföy seçer, puan karesi
   ağırlıklı tavanlı water filling uygular; kuruş farkını deterministik tamamlar.

Korunacak değişmezler: negatif tutar yok; seçilen kanallar minimum/tavan içinde;
toplam ortak bütçe/tavanı aşmıyor; kalan bütçe açık; manuel dağıtım da aynı sınırda.

**Gerçek öneriye taşınmaması gereken varsayımlar:**

- `simulation.js::forecast`: indeks/kanal türü/yarıçap/gün ve açık B2B rolüne göre
  sabit maliyet/kitle çarpanları. Yerel oluşturulma zamanı pazar gözlem zamanı değil.
- Simülasyonun `accountReady`, `policyPass`, `radiusSupported` değerleri gerçek
  hesap yeteneği/uygunluğu sayılmaz. `readiness:'core'` kurgu girdisidir.
- `engine.js` içinde test minimumu için CPM×10, CPC×40, CPA×8 ve araştırma tabanı;
  bunlar ürün varsayımıdır, sağlayıcı minimumu veya istatistiksel güç hesabı değil.
- Kanal başına `potentialBudget` kurgusal talep tavanı; kârlı harcama kapasitesi değil.
- Ortak ekonomik tavan `capacity × days × min(cpa, value×margin/100)` bir defa
  sayılıyor. Bu iyi muhasebe sınırı olsa da kanal bazlı satış kalitesi, gecikme,
  iade, stok SKU'su, maliyet ve artımlılık içermiyor. Bağış/itibar/işe alıma ortak
  kâr amacı uygulanmamalı.
- Araştırma kuru49.7627 yalnız etiketli örnek fallback. Gerçek mali kararda sessiz
  güncel kur gibi kullanılamaz; FX dönüşümü reklam maliyeti tahmini değildir.
- Normalize uygunluk puanının karesini bütçeye çevirmek bugünkü kurgu algoritması;
  beklenen marjinal getiriyi ölçmez. Gerçek modda kaldırılacak dağıtım otoritesi,
  korunacak kısım ise açıklanabilir aday ön filtresidir.

Tarih/pazar kapsamı: owned ekranda Türkiye sabit; `nationwide` Türkiye'ye çevrilir.
İşletme ülkesi, hesap ülkesi, hedef pazar, yerel para ve saat dilimi ayrı ilk sınıf
nesneler değil. Çok ülke desteği iddia edilemez. Eski SC01 ise2026-10-27,
Kadıköy/7gün/mağaza ziyareti vb. tam örnek bağlamına kilitlidir; genel öneri değildir.

## 4. Kaynak ve önbellek incelemesi

`experiments/decision-studio/sources.py`:

- Sabit HTTPS TCMB/ECB XML, TLS doğrulaması, boyut/zaman aşımı, entity yasağı,
  tarih ve Decimal kur denetimi mevcut.
- `make_snapshot` şema/kaynak/kapsam/bağlam hash'i, kaynak tarihi, çekim/son kullanım,
  kalite ve ham kaynak SHA256 taşır. `snapshot_status` farklı bağlamı, kaliteyi,
  gelecekteki ve süresi dolmuş veriyi reddeder.
- `SourceService` yalnız genel FX'yi özel yerel dosyada saklar;1saat TTL,
  en çok4gün gözlem yaşı ve60saniye tekrar deneme aralığı yerel politikalardır.
  Kilit süreç içi; çok worker için dağıtık kota/önbellek garantisi yok.
- `describe/_description` her reklam kanalı için snapshot:null, usable:false,
  `access_required`, advertising_api_calls:0 verir. Reklam veri adaptörü yoktur.
- `dist/app.js` genel kur isteğinde ham firstStage/ownedAudience göndermiyor;
  `sources.js` güncellik ve kaynak durumunu gösterir. FX ve reklam verisinin
  kalite etiketi ayrılır.

Korunacaklar: kaynak zamanını çekim zamanından ayırma, sabit hedef URL, kapalı
girdi, içerik hash'i, kalite/context doğrulaması, kaynak kesildiğinde taslağı koruma.
Eksikler: tenant/account/grant-generation kapsamı, sağlayıcı yetenek/sürüm kaydı,
metric başına TTL ve veri saklama şartı, pagination/completeness,429/backoff,
request deduplication, devre kesici ve reklam tahmini izin kanıtı. FX cache anahtarı
genel kaynak için yeterli; reklam cache'i için aynen kullanılamaz.

## 5. Django'ya geçişte korunacaklar ve uyumsuzluklar

Kök: `apps/web/growthtwin/modules/`.

`apps/web/pyproject.toml`: Python>=3.13,<3.14; Django>=5.2,<5.3;
psycopg/PostgreSQL, Gunicorn ve WhiteNoise. Prototip bağımsız sade JS/Python HTTP
katmanıdır. Yeni servis veya veri tabanı gerektirdiğine dair kanıt yok; mevcut
Django+PostgreSQL ile başlamak makul tasarım varsayımıdır.

| Dosya / sembol | Korunacak işlev | Sınır |
|---|---|---|
| `campaigns/models.py::WorkspaceCampaignDraft`, `WorkspaceCampaignDraftQuerySet.owned_by`; `campaigns/services.py` owner servisleri | Workspace sahibine bağlı erişim, kuruş bütçe, marka ilişki kontrolü | Tek enum Google Search/lead_generation; pozitif bütçe zorunlu. Organik veya46 niyeti bu modele sessizce sıkıştırma |
| `campaigns/models.py::CampaignPlanRevision`; `campaigns/brand_settings.py::save`, `_checked`, `_scope` | Append-only revizyon, fingerprint, request_id idempotency, beklenen sürüm ve sahiplik | Mevcut ayarlar sözleşmesi tam owned brief+evidence+allocation sözleşmesi değil; kontrollü yeni sürüm gerekli |
| `campaigns/planning.py::build_google_search_campaign_plan` | Kaynak alanlarına izlenebilir metin taslağı; `publication_enabled=False` | forecast ve keyword ideas açıkça unavailable. Pazarlama tahmini üretmiyor |
| `campaigns/report_metrics.py::CampaignReportMetric`, `MetricObservation`, `classify_metric_freshness` | Gerçek sıfır ile unavailable ayrımı; tam dönem/satır/pagination ve kaynak güncelliği | Nitelikli lead, gerçekleşen randevu, net gelir/katkı, atıf ve dedup kapsamı henüz ortak uçtan uca hat değil |
| `connections/backend.py`, `scoped_oauth_candidate.py`, `models.py` | Şifreli/ayrı yerel kimlik, default-off sınır, sahiplik/generation ve belirsiz işlem geçmişi | Yerel özel akış çok kiracılı üretim secret store yerine geçmez; adayın varlığı aktif grant/tahmin yetkisi değil |
| `connections/draft_dispatch.py::perform`, `total_budget.py::validate` | TEST onay/fingerprint ve belirsiz dış işlem geçmişi | `validateOnly:true` ad-mutasyon doğrulamasıdır; forecast değildir. Diğer eylemler gerçekten paused TEST nesnesi yaratabilir; öneri adaptörüne bağlanamaz |

`report_metrics.py` iyi başlangıçtır: eksik satır/eksik dönem/eski kaynak gerçek0
sayılmaz. Ancak kaynaklar arası aynı satış için evrensel order_id/dedup,
attribution window ve event-time/ingestion-time, iptal/iade revizyonu, sonuç olgunluğu,
kalıcı tahmin sürümü ve gerçekleşme eşleştirmesi ayrıca tasarlanmalıdır.

Somut tarih uyumsuzluğu: `campaigns/planning.py` günlük ortalama için
`(end-start).days` kullanıyor; `brand_settings.validate/summary` her iki günü
dahil edip `+1` kullanıyor. Gerçek pacing adaptöründen önce provider timezone,
gün dahil etme ve aynı-gün uç durumunu tek sözleşmede çözmek gerekir; bu raporda
hesap değiştirilmedi.

Korunan Google adayı/izin tüketimleri, özel DB, credential dosyaları ve mevcut
migration geçmişi bu araştırmada açılmadı veya değiştirilmedi. Kaynak incelemesi
gerçek hesabın erişilebilir olduğunun kanıtı değildir.

## 6. Sahip dosyaları ve türetilmiş kaynaklar

Salt okunur erişimle doğrulanan mevcut dosyalar:

- `C:\Users\ugrkb\OneDrive\Masaüstü\Yaparo Araştırma\Yaparo_V2_Dinamik_Akis_Veri_Seti.xlsx`
  (130194byte); importer `--check` ile mevcut `dist/v2-data.js` aynı.
  SHA256 `3a1a0b117902d35bda23acb9c56a7e6ba7552b8c012d2a02b81f269c3cf5817d`.
- Aynı klasörde `Yaparo_V2_Urun_Ve_Entegrasyon_Plani.docx` (52784byte):
  XML metin incelemesi dört aşama, niyet/sonuç ayrımı,
  değişmez KPI, ülke/hesap/pazar ayrımı, kaynak tarihi ve null/0 ayrımını destekliyor.
  Bu dokümanın metni tasarım girdisidir; canlı yetki veya başarı kanıtı değildir.
- `Yaparo_V2_Dinamik_Karar_Paketi.zip` adı kontrol edilen araştırma klasörü ve
  eski dataset kökünde bulunamadı; tüm bilgisayarda yokluğu iddia edilmiyor.
- Eski `C:\Users\ugrkb\OneDrive\Belgeler\Yaparo_TR_Karar_Motoru_Dataset\yaparo_package\`
  mevcut: JSON/CSV, şema, reason_codes, `engine_reference.js`, doğrulama raporu.
  `package_version.json`: `tr-rule-engine-v1.0.0`, research_prototype,
  2026-10-27. Bu paket V2 ZIP'le özdeş sayılmadı.
- Referans motorun `forecastFor` fonksiyonu senaryo yoksa kanal-only fallback
  yapıyor; `demandCapTry` son çare toplam bütçeyi tavan sayabiliyor. Bu davranışları
  üretime alma. Test raporunun iddiaları bu oturumda yeniden doğrulanmış değil.

`import_v2.py` yedi bildirime dayalı kataloğu ithal ediyor:10 niyet,20 sonuç,
200 yol,131 soru,161 seçenek,43 modül,10 kural. Formül/bozuk referans/hash
değişikliği reddediliyor. `dist/v2-flow.js` ve `/v2.html` ayrı inceleme akışı;
default46-yol renderer ile aynı ontoloji değil. İki modeli sessizce birleştirmek
yerine açık enum eşleştirmesi ve sürüm geçişi gerekir. Türetilen kataloglar canlı
forecast, hesap doğrulaması veya400 skorun doğruluğunu ithal etmiş sayılmaz.

Mevcut README/PROJECT/ROADMAP bazı eski tarihli bölümleri koruyor: örneğin README
sonlarındaki “yeni tasarımda radius yalnız not” ifadesi güncel `plan-geo.js` ile
eskimiş; üstteki güncel açıklama doğru. Belgelerdeki eski sonraki işler uygulama
kanıtı yerine kullanılmamalı. Bu araştırma üretim kodunu düzeltmedi.

## 7. En kritik eksikler ve korunacak sınır

1. **Kurgu ile hesap kanıtı arasında kalıcı sözleşme yok.** Önce owner/account,
   gerçek metric türü, kalite, context, sürüm ve tarihe bağlı evidence/forecast
   sözleşmesi. Kullanıcı beyanı ve unknown state korunmalı.
2. **Puan bütçe otoritesi.** Gerçek modda skor yalnız aday sıralaması olmalı;
   veri yokken ölçüm/test/harcama yapma sonucu, veri varken marjinal sınır ve ortak
   kapasite kullanan açıklanabilir dağıtım gereklidir.
3. **İşletme gerçekleşmesi ve tahmin doğrulaması yok.** İlk yetkili kaynak
   reklam metrikleri kadar sipariş/nitelikli talep/randevu sonucudur. Platformlar
   arası dönüşüm toplamı satış veya artımlılık sayılmamalı.
4. **Sürüm/izin değişimi yönetimi eksik.** Sağlayıcı dokümanındaki endpoint
   uygulamanın erişimi sayılmaz; yetki kesilmesi/alan kalkması/onay eskimesi planı
   koruyarak durdurmalı. Öneri izni dış mutasyon izninden ayrı tutulmalı.

Korunacaklar: iki soru+kısa form, tekrar sormama, exact outcome/destination/risk
bağı, first-stage pruning, literal render, dört aşama, organik/yalnız içerik yolları,
tam kuruş ve ortak tavan, bakiye, revizyon/idempotence/owner kapıları, mevcut
Google belirsizlik geçmişi. Yeni belgeler bu korumaları kaldırma onayı değildir.

## 8. Bu denetimde gerçekten çalıştırılan kontroller

29 Ekim2026 yerel salt okunur/pure kontrolleri:

- `brief-analysis.test.cjs`:46 exact yol, literal/unknown/risk ve immutable
  analiz sözleşmesi geçti.
- `owned-recommendation.test.cjs`: ilk aşama bağı, gizli alan enjeksiyonunun
  etkisizliği, risk/hedef/coğrafya ve tavanlı sentetik dağıtım geçti.
- `import_v2.py <owner-workbook> --check`: yedi katalog/hash ve mevcut çıktı
  eşleşti; kaynak veya türetilmiş kod yazılmadı.

Bu üç kontrol gerçek hesap, platform tahmini, finansal sonuç veya yayın kanıtı
değildir. Bu belge paketi için yeni görsel akış/DB/provider testi yapılmadı;
UI değişikliği olmadığı için önceki görsel sonuçlar yeniymiş gibi tekrarlanmadı.
