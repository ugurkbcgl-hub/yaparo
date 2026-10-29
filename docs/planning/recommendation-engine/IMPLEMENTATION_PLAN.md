# Yaparo reklam önerisi ve bütçe motoru — uygulama planı

Durum: **29 Ekim2026'da kullanıcı tarafından onaylandı**. Araştırma tarihi:
29 Ekim 2026, Europe/Istanbul. Bu paket ürün kodu, migration, hesap nesnesi,
kampanya, paket sürümü, ücret veya yayın değişikliği içermez.

Uygulama kaydı: ilk WP01 dilimi sağlayıcısız, immutable ve daima
`declared_unqualified` sözleşmeler olarak başladı; tam form doğrulaması/kalıcı
kayıt/gerçek tahmin tamamlanmadı. Güncel sınır ve testler
[ADR0074](../../adr/0074-unqualified-recommendation-contracts.md) içindedir.
Aşağıdaki mimari hedef planıdır, tamamlanmış özellik listesi değildir.

Bu plan [denetim](AUDIT.md), [sağlayıcı matrisi](PROVIDER_CAPABILITIES.md) ve
[kabul planıyla](ACCEPTANCE_TESTS.md) birlikte okunur. Mevcut ADR0072/0073,
hesap sahipliği, nesil/revizyon, tekrar çalıştırmama, bütçe ve yayın kapıları
korunur. Metin, sağlayıcı erişimi veya hukuki uygunluk kararı değildir.

## 1. Sonuç ve ilk üç iş

Mevcut sistemi yeniden yazmayalım. İki sorulu dinamik formu, dört aşamayı,
editörü, kuruş hassasiyetindeki sınırları, ayrılmamış bütçeyi, açık kaynak
güncellik yapısını ve Django sahiplik/geçmiş desenlerini koruyalım.
Değişmesi gereken, **örnek kanal puanından gerçek sonuç beklentisine geçişteki
kanıt zinciri**. Kur uygunluğu, hesap erişimi veya satış tahmini değildir.

İlk üç bağımsız geliştirme paketi:

1. **WP01 — Sürümlü plan/kanıt sözleşmesi.** İlk aşama ve plan sınırlarını
   sunucunun doğruladığı, sahibine bağlı, değişiklikte eskiyen bir taslak olarak
   tanımla. Demo, platform tahmini, gerçekleşme ve işletme varsayımını ayır.
2. **WP02 — Metrik ve işletme sonucu alımı.** Önce sentetik dosya ile test edilen
   yetkili dışa aktarım yolu; satış, nitelikli talep, iptal/iade ve kapasiteyi ayrı
   kaydet. Ortak satışları platform toplamından türetme.
3. **WP03 — Yetenek/güncellik kaydı ve yalnız okuma adaptör sınırı.** Gerçek
   hesap erişmeden erişimsizlik, desteklenmeme ve eskimeyi işle; Google Search
   adayını güncel sürüm/izin kanıtıyla daha sonra bağla.

Bu üçü bitmeden gerçek tahmine dayanan otomatik dağılım veya satış beklentisi
etiketi eklenmez. Şu anda başka kullanıcı bilgisi gerekmiyor. Plan onaylandı;
gerçek veri/hesap denemesi için ayrıca aşağıdaki kapılar gerekir.

## 2. Korunan kullanıcı deneyimi

**İsteğini netleştir → Planını kur → İçeriğini oluştur → Kontrol et ve yayınla.**

- İlk iki seçim ve uygun kısa form, niyet/istenen eylem için tek giriş kaynağı.
  `OutcomeContract.analyze` sonucunu sunucu tekrar doğrular; tarayıcıya güvenmez.
- Plan aşaması yalnız eksik bölge, tarih, medya bütçesi ve amaca gerekli bir
  işletme bilgisini sorar. Bilinen kitle/link/telefon/risk tekrar sorulmaz.
  İşletme katsayıları yoksa kullanıcıyı uzun bir finans formuna zorlamak yerine
  satış beklentisi gösterilmez veya küçük test yolu sunulur.
- Ücretli, organik, birlikte ve yalnız içerik ayrı yollardır. Organik/yalnız
  içerikte medya bütçesi sıfır olabilir; üretim maliyeti yine ayrı kalır.
  Eski `WorkspaceCampaignDraft` pozitif bütçe şartı sessizce kaldırılmaz.
- Kanalların uygun içerik/ölçüm gereksinimi üretimden önce bulunur. Video yoksa
  video kanalına pay verilmez; izinli üretim seçilirse maliyet ve plan yeniden
  değerlendirilir. Her içerik düzenlemesi gereksiz yere bütün formu sıfırlamaz.
- Kullanıcının taslağı API hatasında korunur. Yeni öneri mevcut manuel payların
  üzerine sessizce yazılmaz; değişiklik ve gerekçesi gösterilerek uygulanır.
- Türkiye ilk uygulama pazarıdır. `business_country`, `ad_account_country` ve
  `target_markets[]` birbirinden ayrılır. Çok ülke sözleşmesi tasarlanır; bu
  çalışma uluslararası yayını açmaz. Sabit Kadıköy/İstanbul merkezi yoktur.

### Kanal kartı, kısa görünüm

`Durum · hedeflenen metrik · önerilen tutar/ayrılmamış tutar · varsa aralık`.
Altında bir cümle neden, kaynak tarihi ve **sonraki adım**. Açılabilir ayrıntıda
kaynak türü/kanıt durumu, kısıtlar, teknik/test minimumları, ekonomik/ortak tavan,
veri eksikleri ve içerik/hesap hazırlıkları bulunur. Desteklenmeyen metrik çizgi
ve gerekçe ile gösterilir; sıfır yazılmaz. Yalnız gösterim tahmini varsa satış
kartı oluşmaz. Örnek sayılar gerçek tahmin kartına taşınmaz.

Öneri durumları: `eksik_bilgi`, `ölçüm_gerekli`, `erişim_gerekli`,
`veri_eskimiş`, `sınırlı_test`, `karşılaştırılabilir_tahmin`, `uygun_değil`.
Hiçbiri yayın izni değildir. Hukuk/hesap/medya yetkisi ayrıca değerlendirilir.

“Temkinli/öğrenme/büyüme” ancak farklı hesaplanmış sınırları varsa gösterilir:
temkinli açık risk sınırı ve korunacak rezerv; öğrenme açıkça izinli test tutarı
ve durdurma kuralı; büyüme olgun veri ve pozitif marjinal değer şartı. Verisiz
işletmeye üç farklı isimle aynı yüzde tablosu sunulmaz.

## 3. Mevcut yığına yerleşim

Python 3.13 + Django 5.2 modüler monolit + PostgreSQL korunur. Prototip JS,
üretim finans otoritesi olmaz. İlk çekirdek `dataclass`, `Enum`, `Decimal`,
standart kütüphane ve mevcut ORM desenleriyle kurulabilir; yeni vektör veri tabanı,
ajan çerçevesi, mikroservis veya ML servisi gerekmiyor.

Önerilen bileşen adları **henüz mevcut dosya değildir**:

| Yeni sınır | Mevcut karşılık / değişim |
| --- | --- |
| `campaigns/recommendations/contracts.py` | `outcome-contract.js`, `WorkspaceCampaignDraft`, `CampaignPlanRevision` arasında sürümlü sahiplik eşlemesi |
| `campaigns/recommendations/capabilities.py` | `sources.py` içindeki sabit reklam kaynak listesini gerçek yetenek/kanıt kaydına ayırma |
| `campaigns/recommendations/evidence.py` | `report_metrics.py` açık eksiklik/güncellik desenini tahmine genişletme |
| `campaigns/recommendations/decision.py` | `engine.js` uygunluk/gerekçe kurallarını saf fonksiyon olarak taşıma; örnek tahmini gerçek yolun dışında tutma |
| `campaigns/recommendations/allocation.py` | `engine.js::evaluate/manual`, `plan-summary.js::redistribute/check` sınırlarını koruyup skor² yerine desteklenen tepki eğrilerini kullanma |
| `campaigns/recommendations/calibration.py` | Olgun sonuçlardan işletme düzeltmesi; yeterli veri yoksa çalışmayan ayrı modül |
| `connections` içindeki ayrı forecast adaptörleri | Mevcut dispatch/OAuth backend'inden ayrı çağrı listesi; yayın metoduna erişemez |
| `campaigns/recommendations/evaluation.py` | Dondurulmuş tahmin–olgun gerçekleşme karşılaştırması; bugünkü raporu geçmiş tahmin yerine koymaz |

Yerel prototip davranışı kabul edilene kadar8014 korunur; uygulama eşlemesi
özellik anahtarı arkasında ve sentetik yapılır. Yeni anahtar/izin istemeden
sözleşme/sahte adaptör/algoritma testleri tamamlanabilir.

## 4. Önerilen sürümlü veri sözleşmeleri

Alanlar tasarım önerisidir; şema/migration bu görevde uygulanmadı.

### Sahiplik ve taslak

`RecommendationDraftV1`: sunucudan `workspace_id`, kullanıcıya yetkili
`brand_id?`, `draft_id`, artan `revision`, `request_id`, `expected_revision`,
`first_stage_schema`, doğrulanmış snapshot ve digest, `analysis_version`,
`delivery_mode`, `goal_metric`, literal CTA/destination; ayrı risk ve hazırlık
durumları. `PlanBoundsV1`: ülke/pazarlar, hedefleme türü ve sağlayıcıya uygun
konum kimlikleri, dil, tarih/saat dilimi, kampanya para birimi, toplam medya
minor-unit bütçesi, üretim/hizmet kalemleri, test izni ve rezerv tercihi.

Digest bütünlük/bağlama içindir, kimlik doğrulaması veya imza değildir. Scope
tarayıcıdan kabul edilmez. Eski kayıtlar yerinde yeniden yorumlanmaz; yeni
versiyon olarak içe alma önizlemesi gerekir. Eksik alanlı eski taslak, kaybolmadan
`migration_review_required` durumunda açılır. Brand ve workspace çapraz bağları
sunucuda reddedilir. Yeni revizyon eski yayın onayı değildir.

### Yetenek ve erişim kanıtı

`CapabilityRecordV1`: provider/product/API sürümü, endpoint/metot, amaç/teklif
stratejisi/pazar/para birimi kısıtları, metrik listesi, çok bütçeli sorgu desteği,
`read_only`/`creates_draft`/`mutates_account`, izin kapsamları, resmî kaynak,
kontrol tarihi, sona erme/yeniden kontrol kuralı, kota ve saklama koşulu sürümü.

Ayrı `AccessEvidenceV1`: yetkili workspace/account/connector generation,
ürün/sürüm, `documented | app_approved | account_tested | production_observed`,
kanıt referansı ve zamanı. Bu seviyeler birbirinin yerine geçmez. Güncel bir
izin bile bütün metrik/pazarları onaylamaz. Bilinmeyen alan nullable ve gerekçeli.
Google'daki korunmuş TEST adayı bu kayda kendiliğinden taşınmaz/etkinleşmez.

### Tahmin isteği ve cevap

`ForecastRequestV1`: sahip scope'u, hesap/nesil, hedef pazar+dil+para birimi+
timezone, amaç+optimizasyon metriği, tarih aralığı, teklif stratejisi, keyword/
match/negative kısıtlarının sürüme uygun hali, audience/placement/geo tanımı,
creative/material digest gerekiyorsa, `budget_grid_minor[]`, conversion-action
tanımı, attribution pencere tanımı, capability/policy/model sürümleri.

`EvidenceSnapshotV1`: immutable ID, request hash, provider/API sürümü, kaynak
sınıfı (`official_forecast`, `platform_actual`, `business_actual`,
`declared_assumption`, `manual_export`, `authored_demo`), publication/source-as-of,
fetch zamanı, expiry, geçerlilik bağlamı, birim/vergi/currency/timezone,
provenance ve response completeness; ham yanıtı saklamak zorunlu değildir.
Saklama hakkı yoksa normalize yeterli özet+kanıt; payload politikasını ayrıca uygula.

Her metrik `value?`, `lower?`, `upper?`, `interval_kind`, `status`,
`reason`, `definition_version` taşır. Durumlar en az `available`, `missing`,
`unsupported`, `unauthorized`, `stale`, `partial`, `conflicting`, `error`,
`not_applicable`. **Available0**, eksik değer değildir. Provider aralığında
`interval_kind=provider_range_unspecified`; otomatik95% etiketi yoktur.

`DecisionSnapshotV1`: input/source IDs, rule/model/assumption sürümleri,
adayların kabul/red nedenleri, karşılaştırılabilir metrikler, tahmin/işletme
düzeltme ayrımı, kısıtlar ve rezerv. `AllocationV1`: channel, account, market,
minor units, öngörülen sonuç metriği/aralığı?, min/max gerekçesi, shared resource
grubu. `ApprovalV1` ayrı exact decision/source/content/scope/budget binding'i
ister; öneri üretmek onay üretmez. Değişmiş koşul eski onayı çalıştıramaz.

## 5. Metrik sözlüğü ve veri önceliği

| Metrik | Tanım / birincil kayıt | Özellikle ayrılacak durum |
| --- | --- | --- |
| Gösterim | Platformdaki reklam gösterimi | İnsan veya tekil erişim değildir |
| Erişim | Platformun tanımına göre tekil tahmini kişi/hesap | Kanallar arasında toplanıp tekil kişi denmez |
| Bağlantı tıklaması | Platformun dış bağlantı tıklaması | Bütün etkileşim/tıklama türleriyle aynı değil |
| Açılış sayfası ziyareti | İzinli analytics/site ölçümü | Tıklamadan farklı; izleme kaybı/engelleme olabilir |
| Talep | CRM/formun dedupe edilmiş talebi | Her platform lead sayımı nitelikli değildir |
| Nitelikli talep | İşletmenin sürümlü kalite kuralını sağlayan talep | Kalite kuralı değişirse tarihsel karşılaştırma işaretlenir |
| Randevu / gerçekleşen randevu | Ayrı booking ve attendance olayları | Rezervasyon, hizmetin gerçekleşmesi değildir |
| Satış | İşletme sipariş/ödeme kimliğiyle tanımlı durum | Oluşturulan, ödenen ve iptal edilen sipariş ayrı |
| Net gelir | Tanımlı vergi bazında ödeme eksi iade/iptal düzeltmesi | Brüt ciro, kâr veya reklamın ek etkisi değildir |
| Katkı | Uyumlu net gelir eksi değişken maliyetler ve belirtilen giderler | Medya/üretim/hizmet iki kez düşülmez; LTV varsayılmaz |

`BusinessOutcomeV1`: tenant, kaynak ve kaynak olay kimliği, order/lead/booking
referansı (minimum gerekli takma kimlik), occurred_at/received_at, durum,
amount/currency/tax basis, consent/purpose, düzeltme ilişkisi. İade eski satırı
silmez; yeni düzeltme olayıyla netleştirilir. Aynı satışın Meta/Google'a atıfları
ayrı `AttributionClaim` kayıtlarıdır; işletme satış olayı bir tanedir. Eşleme yoksa
atıfları zorla birleştirme; birleşik satış toplamını unavailable göster.

Öncelik tek global sıralama değildir:

- Gelecek arama talebi: uygun yetkili hesap+tarihli Search tahmini; işletme
  sonuçları tahminin yerine değil ticari dönüşümüne kanıt olur.
- Geçmiş medya maliyeti/tıklama: tamamlanmış platform raporu; faturanın vergi/
  ücret kapsamı farklıysa ayrı tut.
- Satış/gelir/iade: izinli işletme muhasebe/sipariş kaydı; platform atıfı ayrı.
- Stok/randevu kapasitesi: ilgili günün işletme kaynağı; eski kampanya ortalaması
  güncel kapasiteyi geçersiz kılamaz.
- Veri yokluğu: açık etiketli başlangıç varsayımı yalnız izinli test tasarımında;
  sayısal gerçek tahminin yerine sessizce kullanılamaz.

Birleştirme öncesinde pazar, amaç, metrik tanımı, tarih aralığı, saat dilimi,
para birimi, vergi kapsamı, attribution penceresi ve sonuç olgunluğu eşleştirilir.
Kur gözlemi kaynak/tarihiyle sabitlenir; FX çevirisi metrik bağlamını düzeltmez.
Güvenilir kaynaklar çatışıyorsa ortalama alıp gizlemek yerine iki değer ve
uyuşmazlık gösterilir. Organik/ücretli katkılar etiketli ayrı kalır.

## 6. Açıklanabilir karar ve dağıtım algoritması

### A — Uygunluk

Niyet/eylem/usage → ülke/hesap/policy/konum → içerik/ölçüm gereksinimi.
Uygunsuz veya kritik bilinmeyen aday elenir ya da “hazırlık gerekli” kalır.
Bir platformun tahmin API'sinin güçlü olması uygunluk puanı değildir.
Hassas kategori beyanı, kanıtlanmış yasal izin sayılmaz. Sağlayıcı coğrafyası
prototip Türkiye poligonundan türetilmez; gerçek endpoint desteği doğrulanır.

### B — Adaylar

Mevcut bilinen-boyut puanı başlangıç sıralaması/gerekçesi olarak korunabilir;
başarı olasılığına ve otomatik bütçe yüzdesine dönüşmez. Amaç eşlemesi olmayan
kanal, daha zengin verisi olduğu için seçilemez. Pazar payı medya payı değildir.

### C — Veri

Yalnız uygun ve izinli adaylara, açık “öneri oluştur” işleminde küçük bir bütçe
ızgarası iste. Her slider/tuş/LLM mesajı API çağrısı yapmaz. Endpoint bütçe eğrisi
vermiyorsa kitle büyüklüğünden bir eğri uydurma. Sonuç tahminlenemiyorsa kanal
“sınırlı test” veya niteliksel aday olarak kalır; bütçe harcanmayabilir.

### D — İşletmeye uyarlama

Yeni işletme: platformun desteklediği metrikler ve belirsizlik; satış tahmini yok.
Az veri: aynı işletme/bağlamdaki olgun örneklerde açıkça sürümlü oranlar ve geniş
aralık; komşu müşteriden izinsiz prior yok. Güçlü geçmiş: zaman bazlı backtesti
geçen işletme düzeltmesi; mevsim/pazar/creative değişimi ve drift kontrolü.

Tıklama→talep→nitelikli talep→ödenmiş satış çarpımı ancak her aşama için bağlamı
uyumlu, yeterli ve olgun kayıt varsa kurulur. Nokta oranları kesin kabul edilmez;
bağımlı oranların alt/üstlerini çarpmak doğrulanmış güven aralığı vermez.
Başlangıçta basit kohort oranı ve açık senaryo aralığı; istatistiksel kapsama
iddiası ancak kabul planındaki zamansal doğrulamadan sonra.

Ticari amaçta marjinal net katkı değerlendirilebilir; bağışta geçerli bağış/başvuru
maliyeti, işe alımda nitelikli başvuru, farkındalıkta tanımlı erişim/frekans gibi
ayrı objective strategy gerekir. Kâr fonksiyonunu hepsine dayatma. İşletme talebi
ve kapasitesi bilinmiyorsa “kârlı büyüme” planı sunulmaz.

### E — Sınırlı dağıtım

İlk yöntem: küçük, denetlenebilir bütçe ızgarası + kısıtlı marjinal artış seçimi.
Bu **sezgisel yöntemdir; global optimum veya nedensel fayda kanıtı değildir**.

1. Tüm tutarlar currency-aware minor unit; USD micros ayrı ölçektir. Teknik
   minimum, anlamlı test minimumu ve ekonomik/operasyonel maksimum ayrı kayıtlar.
2. Toplam medya bütçesinden açık rezerv/test sınırını ve kesin gider ayrımlarını
   belirle. Medya bütçesinden üretim kredisi kendiliğinden düşme.
3. Uygun başlangıç alt kümeleri için minimumları kontrol et. Bütün kanalları az
   tutarla bölmek yerine anlamlı testin mümkün olduğu küçük aday kümesini karşılaştır.
4. Uyumlu kanalda desteklenen eğriden `Δsonuç/Δbütçe` veya ticari modda
   `Δnet_katkı` hesapla. Kullanıcı risk stratejisi, belirsizlik ve shared-cap altında
   sıradaki artışı seç. Ortak bir hedef tanımı yoksa sonuçları tek puanda toplama.
5. Min/max, izinli hesap/kanal, toplam, kapasite veya kanıt sınırında dur.
   Sonraki adım desteklenmiyor/olumsuz/çok belirsizse kalan para **ayrılmamış**.
   Bütçeyi doldurmak için tahmin uzatma veya ucuz kanal icat etme.
6. Kullanıcının yüzde değişikliği aynı sınır fonksiyonundan geçer. Nokta tahmini
   bozulan manuel pay için eski performans aralığı aynen korunmaz. Tutar ve rezerv
   tam eşitlikle bağlanır; yuvarlama en son kontrollü yapılır.

Talep eğrisi ölçüm gürültüsünde monoton olmayabilir. Çelişen/eşleşmeyen noktaları
sessiz düzleştirip kesin getiri sunma; inceleme/test gerekçesi üret. Kanalların
birbirini etkilemediği varsayımı açıkça yazılır; cross-channel etki öğrenilmeden
elde edilen dağılım bağımsızlık yaklaşımıdır.

Tek stok/randevu grubu tüm kanallarda ortak tüketilir. Beklenen sonuç üst sınırıyla
yapılan tahsis **gerçek stok garantisi değildir**; sert operasyon sınırı için
işletme sistemi rezervasyonu, satış durumu ve yayın durdurma entegrasyonu gerekir.
Bilinmeyen kaynak durumunda büyüme kapalıdır. Aynı para/dönem/vergi kapsamında
`gerçekleşen_harcama + henüz_gerçekleşmemiş_taahhütler + önerilen_yeni_tutar
<= yetkili_medya_tavanı` sağlanmadan yeni harcama izni verilemez. Gerçekleşmiş
bir taahhüt ikinci kez bekleyen sayılmaz; toplam bütçe harcama üstüne eklenmez.
Platform günlük bütçesi, uygulamanın toplam sert limiti yerine geçmez.

### F — Açıklama ve öğrenme

Gerekçe makine tarafından üretilen reason-code ve kanıt ID'lerinden oluşur.
İsteğe bağlı LLM bunları sadeleştirebilir; eksik metrik, neden veya sayı ekleyemez,
kanal seçemez, limit değiştiremez ve yayın yetkisi oluşturamaz. Bu plan için
hiç LLM çağrısı veya sağlayıcı değişikliği gerekmiyor.

Tahmin üretildiği haliyle dondurulur; gerçekleşme sonradan ayrı bağlanır.
Olgunlaşmamış satış dönemleri eğitim/teste tamamlanmış gibi girmez. Hata,
kalibrasyon ve drift ayrıntıları [kabul planında](ACCEPTANCE_TESTS.md).

## 7. Önbellek, değişiklik ve güvenlik

Cache key: server tenant/account/connector-generation, API+capability version,
market/language/currency/timezone, objective/conversion action/attribution,
dates, bid strategy, bütçe ızgarası, geo/keywords/audience/placement/material
digest ve gerçek yanıtı etkileyen diğer parametrelerin canonical digest'i.
Ham token, client secret, parola veya kişisel kimlik bilgisi cache key/log içinde
yer almaz; sunucunun opaque tenant/account/generation kapsamı anahtarda bulunur.
Public FX ayrı public cache'tir;
hesap tahminleri bu cache'e veya tarayıcı localStorage'a yazılmaz.

Her metrik/kaynak için gerekçeli TTL, as-of maksimum yaşı, kaynak gecikmesi ve
yeniden kontrol politikası tanımlanır. Prototip FX TTL'si reklam verisine kopyalanmaz.
Kota üst sınırı, küçük batch, single-flight, timeout, bounded retry+jitter,
Retry-After ve circuit breaker; yalnız kanıtlı idempotent okumada retry.
Taslak nesne yaratan forecast API yolu, salt okuma sayılmaz ve başlangıçta kapalı.
Yetki iptali/401/403 refresh fırtınası yaratmaz; account/generation cache'i kullanımdan
çıkarır. Başka müşterinin verisine veya demo'ya otomatik fallback yapılmaz.

| Değişiklik | Yenilenecek hesap/onay | Korunacak taslak |
| --- | --- | --- |
| Niyet/eylem/usage/risk | Analiz, uygunluk, ilgili tahmin, dağılım ve yayın onayı | Uyumlu literal alanlar; gizli dal cevapları kullanılmaz |
| Konum/pazar/dil/tarih/teklif/bütçe | İlgili forecast cache key, dağılım, maliyet ve yayın onayı | Önceki karar tarihsel olarak saklanır |
| İçerik/format/destination | İçerik/policy; ilgili forecast creative-sensitive ise o tahmin; yayın onayı | Bağlamdan bağımsız geçerli tahminler |
| Yeni outcome/iade/stok | İşletme düzeltmesi/kapasite/dağılım; yürütmeden önce limit kontrolü | İlk form ve önceki sonuçlar |
| Veri eskimesi/şema kalkması | İlgili kanıt ve tahsis stale; kritik yürütme kapalı | Form/editor/salt okunur geçmiş |
| Hesap/connector nesli/izin iptali | Tüm bağlı okumalar/onaylar geçersiz; yeni yetki gerekir | Kullanıcının sahip olduğu taslak |
| Sadece kart açma/etiket yazımı | Hiçbir dış sorgu veya yeni onay yok | Her şey |

Öneri servisi en az yetkiyle, publisher çağrı listesi olmadan çalışır. Gerçekte
sağlayıcı OAuth kapsamı yazmaya da izin veriyorsa uygulama işlem allowlist'i bunu
telafi eder; scope adı tek başına salt okuma kanıtı değildir. Cache okumasında da
ownership kontrol edilir. Secret store referansı dışında hiçbir sır kaydı yoktur.
Silme/iptalde şahsi veriyi kaldırma ile tekrar-yayın güvenliğini koruyan asgari
denetim izinin saklanması mevcut ADR'lerle tasarlanır; sınırsız geçmiş önerilmez.

Türkiye hukuki kapısı: veri sorumlusu/işleyen rolleri, aydınlatma, amaç/minimum
veri, hukuki dayanak, saklama/silme ve gerekiyorsa yurt dışı aktarım mekanizması
uzman incelemesi ister. [KVKK'nın güncel aktarım açıklaması](https://www.kvkk.gov.tr/Icerik/2053/Yurtdisina-Aktarim)
uygun güvence yollarını anlatır; hesabın bağlanması tek başına hukuki uygunluk
sağlamaz. Sağlık/bağış/işe alım gibi alanlarda ayrı politika kontrolü korunur.
Müşteriler arası öğrenme varsayılan kapalı; izin, anonimleştirme ve yeniden
kimliklendirme testinden geçmeden ortak havuz yoktur.

## 8. Kaynak yolları ve öncelik

| Yol | Kalite/hesap özgüllüğü | Erişim, güncellik, maliyet/bakım | Kullanım kararı |
| --- | --- | --- | --- |
| Resmî API | Metrik ve hesaba göre yüksek bağlam; garanti değil | Ürün/izin/sürüm/kota; bakım ve çalışma maliyeti var | Google Search adayından başlayıp kanıtlanan kapsamı aç |
| Üçüncü taraf | Üst kaynağa bağlı; normalize etmek kaybı gizleyebilir | Sözleşme, fiyat, tenant/transfer/retention ve taşınabilirlik incelemesi | İlk fazda satın alma yok; yalnız kendi adaptörü karşılıyorsa aday |
| Resmî export + doğrulanmış giriş | Hesap/pencere/ayar/dosya kanıtı korunursa yararlı | Elle hata/eski veri; değişiklik tarihi/tekrar içe alma/dedupe gerekir | İlk işletme sonucu ve erişim bekleme alternatifi |
| İşletme geçmişi | Kendi net sonucu/kalitesinde güçlü | Olgunluk/örneklem/bağlam/drift; üretim ingest maliyeti | Erken kur; tek başına gelecek medya talebi veya nedensellik değil |
| Kontrollü pilot/deney | Uygun tasarımda öğrenme; her A/B nedensel satış etkisi değil | Açık medya/test yetkisi, süre, örneklem ve kayıp limiti | Veri yokluğunda etiketi açık sınırlı öğrenme |
| MMM (Meridian/Robyn) | Yeterli geçmiş/coğrafya/variation ve model varsayımlarına bağlı | Veri hazırlama/uzmanlık/backtest/bakım yüksek | Veri yeterliliği kanıtlandığında; başlangıç motoru değil |

İlk kaynak sırası: **işletmenin izinli sipariş/CRM/randevu dışa aktarımı**
(gerçek değer ve kapasite), **yetkili Google Search forecast + geçmiş rapor**
(ilk kanal adayına uygun gelecek talep ve medya gerçekleri), sonra **Meta geçmiş
rapor/izinli tahmin yetenekleri**. Bu sıra erişimi garanti etmez; Google erişimi
bekliyorsa sentetik veya doğrulanmış export ile sözleşme çalışması sürer.
GA4 landing-page ölçümü varsa salt okunur alım yararlı ek kaynaktır; satışın
birincil defteri değildir. [Data API kota modeli](https://developers.google.com/analytics/devguides/reporting/data/v1/quotas)
istek karmaşıklığına/özelliğe bağlıdır; slider başına sorgu tasarlanmaz.

Meta/LinkedIn/TikTok/YouTube/Microsoft/Yandex sırası amaç ve erişime göre açılır;
belgelenmiş API zenginliği veya pazar büyüklüğü tek başına bütçe üstünlüğü yaratmaz.
Diğer katalog kanalları kayıt olarak kalır, kanıt yoksa otomatik yatırım almaz.

## 9. Sıralı, bağımsız iş paketleri

Her paket ayrı geri alınabilir PR ve ilgili kabul testleriyle ilerler. Aşağıdaki
dosya adları mevcut değilse önerilen hedef olarak okunmalıdır. Kodlama ilk
araştırmadan sonraki kullanıcı onayıyla başladı. Göreli efor,
takvim/sağlayıcı onay süresi taahhüdü değildir.

### WP01 — Taslak ve kanıt sözleşmesi · şimdi · orta

- Problem/değer: geçici prototip bağlamını kaybetmeden sahipli ve sürümlü plana
  dönüştürmek; örneği gerçek tahmin gibi göstermemek.
- Bileşen: `outcome-contract.js`, `first-stage-bridge.js`, campaign models ve
  önerilen contracts; mevcut plan revision/owner/idempotence desenleri.
- Veri/yetki: sentetik snapshot, kullanıcı sahibi ve context; dış erişim yok.
- Bağımlılık: ADR0071–0073 ve audit eşlemesi; WP02/03'ün ortak zemini.
- Kabul:46 route/delivery, unknown≠zero, cross-tenant refusal, stale revision,
  stable replay; eski Google/AI/plan kayıtlarına dokunulmaz. `planning.py` ile
  `brand_settings.py` arasındaki exclusive/inclusive gün farkı, aynı-gün ve
  timezone örnekleriyle karara bağlanır; gerçek pacing'e belirsizlik taşınmaz.
- Risk/dönüş: iki domain'i yanlış birleştirme; yeni şema/anahtar kapalı,
  önce saf sözleşme, gerçek migration daha sonra ayrı inceleme.

### WP02 — İşletme sonuçları ve metrik sözlüğü · şimdi · orta

- Problem/değer: platform conversion'ını satış sanmamak, net değer ve kapasiteyi
  kanıtla ilişkilendirmek.
- Bileşen: `report_metrics.py`, rapor testleri; yeni outcome import/evidence sınırı.
- Veri/yetki: sentetik CSV önce; gerçek export için hesap sahibi izin/dayanak,
  alan/saklama/minimizasyon kararı. Başlangıçta e-posta/telefon gerekmez.
- Bağımlılık: WP01; mapping preview ve idempotent import.
- Kabul: ödeme/iptal/iade/attendance, duplicate sale, timezone/currency/tax,
  partial/mature window testleri; satış atıfları ayrı.
- Risk/dönüş: mükerrer/kişisel veri alımı; importer kapalı, batch quarantine ve
  geçmişi bozmadan yeni düzeltme olayı; izin yoksa sadece sentetik.

### WP03 — Capability ve freshness katmanı · şimdi · orta

- Problem/değer: bulunmayan/eskimiş endpoint'in hayali sonuç üretmesini önlemek.
- Bileşen: prototype `sources.py` deseni, yeni capability/evidence kayıtları,
  connection sahiplik/generation kontrolleri.
- Veri/yetki: resmî doküman + sahte cevap; canlı yetki gerektirmez.
- Bağımlılık: WP01; kaynak matrisindeki belirsizlikler kapalı varsayılır.
- Kabul: schema/version/metric-specific TTL, stale/unsupported/unauthorized,
  context/tenant key, no demo fallback, schema removal ve late-response testleri.
- Risk/dönüş: doküman kanıtını hesap izni sanmak; adapter default-off,
  yalnız test kayıtlarını kullan; eski public FX bozulmaz.

### WP04 — Google Search yalnız okuma kanıtı · sonra · orta

- Problem/değer: ilk desteklenen amaçta yayın öncesi hesap-bağlamlı veri.
- Bileşen: yeni forecast adapter; mevcut Google TEST publisher/backend'ini
  bağlamak veya yeniden yetkilendirmek yerine ayrı allowlist ve generation binding.
- Veri/yetki: güncel Cloud API erişimi, OAuth/user/account yetkisi, pazar/
  currency/strategy proof; gerçek salt okuma testine açık izin. Hiç reklam nesnesi yok.
- Bağımlılık: WP01/03; sürüm ve negatif keyword/konum ifade kaybı incelenmiş.
- Kabul: desteklenen bütçe ızgarası ve metrik alanları; yazma çağrısı0,
  hesap/sürüm/kota/expiry kanıtı, eksik metrik null, test hesabı≠production proof.
- Risk/dönüş: mevcut erişim yeni ürüne yetmeyebilir; salt okuma kapalı bırak,
  manuel export/sentetik yola dön; korunan adayı tekrar üretme/resetleme yok.

### WP05 — İşletmeye özgü basit kalibrasyon · sonra · orta

- Problem/değer: tıklamayı otomatik satışa çevirmek yerine gerçekten gözlenen
  dönüşüm aşamalarını kullanmak.
- Bileşen: yeni calibration/evaluation; rapor MetricObservation sözleşmesi.
- Veri/yetki: aynı işletmenin izinli olgun kohortları; yeterlilik eşiği backtestle.
- Bağımlılık: WP02 ve karşılaştırılabilir kaynak WP04 veya export.
- Kabul: cold-start/az veri/olgun veri ayrımı, zero outcome, gecikme/iade,
  time split/no leakage, bias/MAE/coverage; yetersiz veride satış yok.
- Risk/dönüş: sahte kesinlik/drift; model sürümünü kapat, platform metriği veya
  açık sınırlı test moduna dön; geçmiş tahmin silinmez.

### WP06 — Kısıtlı marjinal bütçe motoru · sonra · büyük

- Problem/değer: puan² dağıtımı yerine desteklenen ilave değer ve ortak sınırlar.
- Bileşen: yeni saf allocation + mevcut engine allocation/share/min/max davranışı;
  medya/üretim/hizmet finans ayrımı.
- Veri/yetki: karşılaştırılabilir eğri veya açık pilot sınırı; harcama yetkisi yok.
- Bağımlılık: WP01/03/05; teknik/test minimum kayıtları ve shared-cap tanımı.
- Kabul: tam kuruş bütçe=paylar+rezerv, eksik/sıfır ayrımı, min/max, ortak kapasite,
  noncommercial objective, no extrapolation; exhaustive küçük problem referansı.
- Risk/dönüş: heuristiğin optimum sanılması; shadow comparison, yayımlanamaz
  sonuç, eski demo yalnız etiketiyle kalır; gerçek tahsis otomatik çalışmaz.

### WP07 — Dört aşamada açıklama/plan sürümü · sonra · orta

- Problem/değer: veri ayrıntısını kullanıcıya yüklemeden neden ve eksikleri göstermek.
- Bileşen: `plan-ui.js`, `app.js`, `sources.js`, owned summary/review; sonra Django UI.
- Veri/yetki: WP01 decision/source snapshot'ları; LLM zorunlu değil.
- Bağımlılık: WP03/06; UI prototipi sentetik kanıtla paralel hazırlanabilir.
- Kabul: tekrar form yok, plan hatada korunur, kaynak/tarih/metric/null nedenleri,
  keyboard/mobile visual, stale approval; API çağrısı slider başına artmaz.
- Risk/dönüş: örnek/gerçek karışması; feature flag ve önceki kabul edilmiş8014
  görüntüsü korunur; eski onay yeni sürüme taşınmaz.

### WP08 — Forecast–actual kayıt ve öğrenme · sonra · orta

- Problem/değer: gerçekleşen kötü sonucu geçmiş tahmini değiştirerek gizlememek.
- Bileşen: yeni evaluation kayıtları, reporting view ve scheduler sınırı.
- Veri/yetki: frozen forecasts, olgun gerçekler, mevcut iş kuyruğu/komut altyapısı.
- Bağımlılık: WP02/05; ayrı attributable vs incremental labels.
- Kabul: matured cohort/time split, error/bias/interval genişliği ve kapsama,
  channel/market/goal segmenti, late conversion revision; no pooling by default.
- Risk/dönüş: otomatik yanlış öğrenme; shadow-only sürüm, driftte son doğrulanmış
  sürüme dön; kötü veri geçmişi korunur, canlı bütçe değişmez.

### WP09 — Ek platformlar ve export adaptörleri · sonra · büyük

- Problem/değer: tek platforma kilitlenmeden gerçek uygun kanalları karşılaştırmak.
- Bileşen: capability kaydı, forecast/report adaptörleri, typed imports.
- Veri/yetki: her platformun ayrı app/account/market/retention onayı; ücretli
  tedarikçi varsa ayrıca teklif ve kullanıcı bütçe kararı.
- Bağımlılık: WP03 ve ilk adaptör acceptance deseni; amaç bazlı sıra.
- Kabul: her kanalın desteklenmeyen metriği null; mutation-needed yöntem kapalı;
  API sürüm kaldırma/429/degraded/manual provenance ve tenant testleri.
- Risk/dönüş: en zayıf kanala göre her şeyi tekleştirmek; küçük versioned adapter,
  yalnız o sağlayıcıyı kapat; hiçbir satış/erişim garantisi verme.

### WP10 — Kontrollü gerçek pilot ve yayın kapıları · sonra · büyük

- Problem/değer: güvenli öneri ile gerçek medya yürütmesini ayrı kanıtlamak.
- Bileşen: mevcut consent/dispatch/stop/reconcile/recovery ve plan binding'leri.
- Veri/yetki: staging E2E, recovery/backup/privacy/platform kapıları, gerçek hesap,
  advertiser bütçe/kanal/tarih/content izni ve özel pilot harcama onayı.
- Bağımlılık: WP01–08 ve ilgili platform kanıtı; onay beklentileri açık.
- Kabul: operation-time revalidation, stale consent refusal, no resend,
  actual+reserved spend cap, stop/reconcile, data deletion ve rollback kanıtı.
- Risk/dönüş: aşım/çift yayın; fail closed ve bağımsız stop; DB restore ile
  tüketilmiş yetkiyi geri açma veya geçmişi sıfırlama yok.

### WP11 — İleri deney/karma modeller · veri yeterli olduğunda · büyük

- Problem/değer: uygun deneyle artımlı etki ve kanallar arası etkileşimi araştırmak.
- Bileşen: ayrı experiment/MMM değerlendirmesi; çalışma motorunu değiştirmez.
- Veri/yetki: hacim/geçmiş/geo variation, açık deney/mahremiyet/medya izni;
  yeterlilik ve güç analizi problem bazlıdır.
- Bağımlılık: WP08, olgun geçmiş ve uzman model incelemesi.
- Kabul: holdout veya geo test tasarımı, backtest, priors/sensitivity,
  model varsayımları ve gerçekleşmiş sonuç/model önerisi ayrımı.
- Risk/dönüş: overfit/nedensellik iddiası; shadow advisory ve basit modele dönüş;
  Meridian/Robyn ilk bağımlılık değildir.

## 10. Maliyet ve sürdürülebilirlik

Bu araştırmada maliyetli çağrı/servis açılmadı. Bağımlılık yükseltme önerisi yok.

| Kalem | Bilgi sınıfı | Plan |
| --- | --- | --- |
| Mevcut staging | Repo kaydı yaklaşık12USD/ay vergi öncesi; güncel fatura bu görevde doğrulanmadı | Yeni kaynak ekleme; onayı genişletme |
| Resmî API kullanımı | Kota/erişim ürüne bağlı; ayrı ücret açıkça doğrulanmamışsa **bilinmiyor** | Ücretsiz varsayma; account/product şartını doğrula |
| API developer/access/partner incelemesi | Hesap/ürün onayı ve zaman gerektirir | Efor, garanti onay/süre olarak yazılmaz |
| İşletme export/import | Yeni lisans satın almadan prototiplenebilir; işçilik/bakım vardır | Mevcut Python/DB ile ilk dilim |
| Üçüncü taraf veri | **Teklif/sözleşme gerekir**, fiyat bilinmiyor | İlk fazda satın alma yok |
| Cache/worker/storage/alerts | **Tahmini tasarım maliyeti**, ölçülmüş kaynak ihtiyacı yok | Önce mevcut monolit/komutlar; ihtiyaç ölçülmeden Redis/Celery/servis ekleme |
| LLM açıklaması | Zorunlu değil; birim/tekrar/saklama maliyeti seçilmeden bilinmiyor | Reason-code şablonu başlangıç çözümü |
| Medya pilotu/üretim | Ürün bazlı ayrı özel onay gerekir | Araştırma ve öneri hesabına medya harcaması ekleme |

PROJECT.md'deki100USD/ay çalışma tavanı,80USD uyarı ve20USD tek harcama
onay eşiği yeni ücret onayı sayılmaz. Mevcut12USD staging onayı dışında
yeni abonelik yoktur; OpenRouter bakiyesini kullanıcı yönetir. Operasyon için
ölçülecekler: karar başına çağrı, cache hit, quota429, p95 gecikme, hatalı/eski
kanıt yüzdesi, depolama artışı ve bakım süresi. Tekrarlanan tarihli provider
kontrolü görevini bu plan otomatik açmaz.

## 11. Henüz kesin olmayanlar ve karar kapıları

1. Google Cloud projesinin güncel planning erişimi ve uygun gerçek hesabın
   capability kanıtı yok; önceki TEST başarısı bunu kanıtlamaz. OAuth veya
   korunmuş aday üzerinde tekrar işlem bu araştırmanın parçası değil.
2. Meta dahil bazı güncel doküman/sürüm alanları erişim sınırlı; matris bu
   belirsizlikleri kapalı tutar. Türkiye'de hesap, amaç ve konum bazlı uygunluk
   katalogda var olmaktan çıkarılamaz.
3. Hangi işletme sistemi/CRM/sipariş/randevu export'unun ilk kaynak olacağı gerçek
   pilot müşteriye bağlı; şu an seçilmesi geliştirmeyi durdurmaz.
4. Test kaybı/bütçe rezervi, anlamlı iş sonucu tanımı ve iade/garanti koşulu ticari
   karardır. Tahmin aralığına dayanarak performans garantisi verilmeyecek.
5. Veri saklama/yurt dışı aktarım/sözleşme ve platform şartları gerçek veri
   öncesi kararlaştırılmalı; belge kontrolü hukuki onay değildir.
6. Eşikleri sayıyla uydurmuyoruz: minimum örneklem, model hata toleransı,
   kalibrasyon coverage ve tazelik SLO'ları pilot amacına göre önce kaydedilip
   backtestte sınanacak. Kalite kanıtı yoksa büyüme yerine ölçüm/test önerilecek.

**Sonraki tek iş:** WP01'in tam sunucu form doğrulaması ve kabul edilmiş analiz
sözleşmesini46 yol için tamamla; ilk unqualified dilimi kabul edilmiş müşteri
analizi gibi kullanma. Kalıcı servis/şema ve gerçek kaynaklar ayrı kapılardır.
