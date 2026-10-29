# Sağlayıcı yetenekleri ve erişim kanıtı

Kontrol tarihi: **29 Ekim 2026, Europe/Istanbul**. Araştırma/plan; hesap çağrısı,
OAuth, taslak reklam nesnesi, rezervasyon, yayın veya harcama yapılmadı.

## Kanıt düzeyleri

`documented` resmî sayfada/sağlayıcının kendi SDK'sında görüldü;
`app_access_unverified` Yaparo uygulamasının bu yeteneğe güncel erişimi denenmedi;
`account_test_unverified` gerçek hesaba sorgu yapılmadı;
`production_unverified` üretim güvenilirliği kanıtlanmadı. Bu dosyadaki bütün
sağlayıcılar son üç durumda kalır. Eski Google TEST kimlik/izin çalışmalarının
varlığı üretim tahmini hakkı değildir; korunan aday veya izin geçmişi değiştirilmez.

Resmî dokümantasyon da eski özet, güncel ana metin ve SDK arasında çelişebilir.
Bir sürümü sabitlemek, sunucu tarafı alan kaldırılmalarını önlemez. Belgede görülen
özellik yalnızca uygulanacak adaptör için adaydır; hesap/pazar/amaç bazında kabul
testi geçmeden arayüzde kullanılabilir sayılmaz.

## Öncelikli yetenek matrisi

| Yüzey | Yayın öncesi belgelenen veri | Bütçe eğrisi ve amaç | Yan etki sınırı / Yaparo kararı |
|---|---|---|---|
| Google Search | KeywordPlanIdeaService.GenerateKeywordForecastMetrics; maliyet ve teklif stratejisine bağlı tıklama/CPC veya dönüşüm/CPA | Ayrı bütçe/teklif senaryoları sorgulanabilir; bütün metrikler bütün stratejilerde yok | Inline CampaignToForecast, hizmet veren kampanya oluşturmayı gerektirmeyen hesaplama; POST tek başına mutation demek değildir. İlk aday |
| YouTube / Google Video Partners | ReachPlanService erişim ve ilgili video medya planı metrikleri | Bütçe/ürün karması üzerinden erişim eğrisi; satış tahmini değildir | Özel allowlist + veri lisansı; standart Google erişimi yetmez. Erişim kanıtı olmadan kapalı |
| Meta Facebook / Instagram | Güncel resmî SDK'da aylık hedef kitle alt/üst sınırı ve estimate_ready | Güncel SDK, günlük sonuç/bütçe eğrisi sağlamıyor; kitle boyutunu ücretli erişim veya satışa dönüştürme | Salt sorgu adaptörü ad/adset yaratmaz. Önce kitle uygunluğu + geçmiş sonuç; eski eğri varsayımı kaldırılacak |
| LinkedIn | adSupplyForecasts: amaç/format uyumuna göre gösterim, harcama, tıklama, video, lead, conversion, reach türleri | criteriaV2 günlük/toplam bütçe ve teklif/optimizationTarget alır; dönen metrikler koşullu | GET; kampanya URN opsiyonel. Uygun hesap/ürün erişimiyle yeni kampanya yaratmadan aday |
| TikTok | API kataloğunda audience estimate, potential-audience insights, R&F inventory estimate; UI Reach Estimator ve EDR ayrı | UI Reach Estimator reach/video-view + cost-cap koşullu; EDR yayındaki adgroup güncellemelerine bağlı | UI özelliği API erişimi sayılmaz. R&F estimate ile order/create ayrılacak; yayınsız genel satış eğrisi doğrulanmadı |
| Microsoft Search | Ad Insight GetKeywordTrafficEstimates; min/max CPC, clicks, CTR, impressions, total cost | Teklif/dil/konum/network ve opsiyonel DailyBudget; ayrı senaryolar; satış tahmini yok | Inline CampaignEstimators ile hesaplama; campaign save çağrılmaz. Google'dan bağımsız ikinci Search aday |
| Yandex Search | Resmî bütçe tahmini aracı ve Live4 forecast raporları | Kelime/konum/teklif bazlı maliyet/tıklama planlaması; güncel tam cevap şeması ayrıca doğrulanmalı | CreateNewForecast sunucuda rapor yaratır; reklam yayını değildir ama katı salt-okunur da değildir. İlk faz manuel doğrulanmış giriş; API ayrı izin paketi |

### Google: güncel erişim ve sürüm riski

Güncel ana metin, **9 Eylül 2026'da developer token modelinin sonlandığını**,
erişimin Cloud projesine taşındığını söylüyor. Explorer'ın planning servisleri
kapalı; Basic başvurusu marka doğrulaması gerektiriyor. Sayfanın eski özeti hâlâ
üç seviye/token anlatıyor: ana metni esas alıp gerçek proje erişimini ayrı kontrol
etmeliyiz. Bu bulgu uygulamada otomatik kimlik değişikliği yetkisi vermez.
[Resmî erişim sayfası, son güncelleme 2026-10-28](https://developers.google.com/google-ads/api/docs/api-policy/access-levels).

v24+ forecast şemasında impressions/CTR/conversion_rate kaldırılmış; clicks/CPC
Manual CPC veya Maximize Clicks, conversions/CPA Maximize Conversions koşullu.
v23 örneklerini yeni şemaya taşıyıp eksik alanları sıfır doldurmak hatalıdır.
Geo/language/date/strategy ve anahtar kelimeler istek bağlamıdır; varsayılan hesap
saat dilimi veya dönem sessizce alınmamalı.
[Forecast yöntemi ve sürüm farkları](https://developers.google.com/google-ads/api/docs/keyword-planning/generate-forecast-metrics),
[resmî v24 değişiklik duyurusu](https://ads-developers.googleblog.com/2026/04/simplifying-keyword-forecast-metrics-in.html).

Keyword planning yöntemleri CID başına 1QPS sınırına tabi. Günlük erişim kotaları
ve servis sınırları farklıdır; yanlış istekler de kota tüketebilir. Kuyruk/cache ve
sınırlı senaryo ızgarası gerekir. Yeni offline conversion yüklemeleri için aynı
sayfa Data Manager geçişini işaret ediyor: eski UploadClickConversions tasarımını
yeni entegrasyona varsaymayın.
[Kota ve yeni benimseyenler için kısıtlar](https://developers.google.com/google-ads/api/docs/best-practices/quotas).

ReachPlanService ayrı allowlist, ön değerlendirme ve veri-lisans koşulları ister.
ListPlannableLocations/Products sonucu hedef pazar/para birimi/ürün destek kanıtı
olmalıdır; Türkiye/TRY veya bütün YouTube formatları varsayılmaz.
[YouTube erişim tahmini](https://developers.google.com/google-ads/api/docs/reach-forecasting).

### Meta: eski örnekten sonuç eğrisi türetmeyin

Birincil referans/changelog sayfaları bu araştırmada 429/erişim hatası verdi;
güncel canlı cevap doğrulanmadı. Buna karşılık Meta'nın kendi güncel Python SDK
AdAccountDeliveryEstimate şeması `estimate_mau_lower_bound`,
`estimate_mau_upper_bound`, `estimate_ready`, `targeting_optimization_types` içeriyor;
DAU veya daily_outcomes_curve içermiyor. Bu, mevcut SDK yüzeyinin kanıtıdır,
hesabın döndüreceği cevabın kanıtı değildir.
[Resmî SDK şeması](https://raw.githubusercontent.com/facebook/facebook-python-business-sdk/main/facebook_business/adobjects/adaccountdeliveryestimate.py).

Meta'nın eski incubator rehberi hâlâ günlük eğri anlatıyor; güncel SDK ile
çeliştiği için operasyonel sözleşme olarak alınmayacak. Alan kaldırılmasının tam
tarihi ve geçerli Graph sürümü erişilemeyen ana changelogdan ayrıca doğrulanmalı;
üçüncü taraf tarih iddiaları burada doğrulanmış gerçek sayılmadı.
[Eski resmî örnek](https://github.com/facebookincubator/catalogue-of-api-solutions/blob/main/solutions/miscellaneous/targeting-reach-estimate.md),
[erişilemeyen v26 changelog](https://developers.facebook.com/docs/marketing-api/changelog/version26.0/).

Meta'nın resmî API koleksiyonu, diğer işletmelerin hesapları için Advanced Access
ve uygun ads_read/ads_management izinlerini ayırıyor. Öneri adaptörü minimum okuma
izni hedeflemeli; gerçekten gerekli scope güncel endpoint ile doğrulanacak.
[Meta tarafından yayımlanan koleksiyon](https://www.postman.com/meta/facebook-marketing-api/collection/0zr4mes/facebook-marketing-api-mapi).
IG ve Facebook ayrı medya yüzeyleri olsa da aynı hesabın tahmini kitlelerini
toplayıp tekil toplam erişim üretemeyiz. Kesin kota, saklama şartı ve mevcut
inceleme gereklilikleri güncel ana referansa erişilmeden açık kalır.

### LinkedIn

criteriaV2; bütçe, hedefleme, tarih, amaç/format ve teklif bağlamından koşullu
metricType/timeSeries/adForecastRange üretir. Forecast aralığı istatistiksel %95
güven aralığı değildir. Belgede r_ads ile VIEWER dâhil rol listesi ve rw_ads
alternatifi var; mümkün olan minimum okuma izni kullanılacak. Günlük bütçenin
1.2 katı tahmini harcama üst sınırı örneği Yaparo'nun sert onay tavanının yerine
geçmez. Sayfa 202511 sürümü için 16 Kasım 2026 sonlanma uyarısı içeriyor;
uygulamada aktif YYYYMM açıkça sabitlenecek.
[Ad Supply Forecasts](https://learn.microsoft.com/en-us/linkedin/marketing/integrations/ads/advertising-targeting/ad-supply-forecasts).

Audience Counts hedeflenebilir üye sayısıdır; teslim edilmiş erişim değildir.
[Audience Counts, 2026-10 görünümü](https://learn.microsoft.com/en-us/linkedin/marketing/integrations/ads/advertising-targeting/audience-counts?view=li-lms-2026-10).
Advertising API ürün başvurusu/incelemesi gerekir; Development ve Standard hesap
erişim sınırları farklıdır. Development adı güvenli sentetik sandbox kanıtı değildir:
resmî sayfa çağrıların production data kullandığını belirtir.
[Program seviyeleri](https://learn.microsoft.com/en-us/linkedin/marketing/integrations/marketing-tiers?view=li-lms-2026-03),
[başvuru süreci](https://www.linkedin.com/help/linkedin/answer/a524477).

### TikTok

v1.3 resmî SDK hedef bölgeleri advertiser ID ile arayabiliyor; ülke ve hedefleme
uyumu hesap bazında okunmalı. İşletme ülkesinden Türkiye hedeflenebilirliği veya
1km yarıçap desteği çıkartılamaz.
[Resmî SDK ToolApi](https://github.com/tiktok/tiktok-business-api-sdk/blob/main/js_sdk/docs/ToolApi.md).
API kataloğu Audience estimate ve R&F inventory estimate ile create-order yollarını
ayrı listeler. Detaylı estimator request/response ve salt-okunur niteliği için
güncel endpoint referansı/izinleri tamamlanmadan adaptör açılmaz.
[Business API kataloğu](https://business-api.tiktok.com/portal/docs?id=1739318962329602),
[Audience insights ve R&F kataloğu](https://business-api.tiktok.com/gateway/docs/index?doc_id=1797016417934337&language=ENGLISH).

Ads Manager Reach Estimator reach/video-view + cost-cap, yeni kampanya/adgroup
bağlamında koşullu çalışır; bazı hedefleme/dönem ayarları tahmini kaldırır. UI'da
görüldüğü için genel API'ye taşınmış sayılmaz.
[Resmî Reach Estimator](https://ads.tiktok.com/resources/help/article/reach-estimator-for-brand-auction?lang=en).
EDR ise yayındaki install/web-conversion/lead adgroup değişiklikleri için koşullu
bid/budget tahminidir; sıfırdan yayın öncesi satış tahmini gibi sunulamaz.
[Resmî EDR açıklaması, Ağustos 2026](https://ads-useast2a.tiktok.com/resources/help/article/estimated-delivery-results?lang=en).

Business API kotası uygulama ve endpoint düzeyindedir; tüketici TikTok API limitleri
buraya kopyalanmaz. Basic genel sınırı10QPS/600QPM; endpoint daha dar olabilir.
40100 throttle, QPM bekleme ve UTC günlük reset semantiği adaptörde ayrı ele alınır.
[Resmî Business rate limits](https://business-api.tiktok.com/gateway/docs/index?doc_id=1740029171730433).

### Microsoft

Ad Insight v13 GetKeywordTrafficEstimates, CampaignEstimators ile bid/location/
language/network ve isteğe bağlı daily budget alır; min/max gösterim, tıklama,
CPC/CTR/maliyet döndürür. OAuth, yetkili account/customer ve DeveloperToken başlıkları
belgelenmiştir. Google'ın token değişikliği Microsoft'a genellenemez. Min/max'ın
kapsama olasılığı belgelenmiş sayılmaz; lead/satış üretmez.
[İşlem ve cevap şeması](https://learn.microsoft.com/en-us/advertising/ad-insight-service/getkeywordtrafficestimates?view=bingads-13).

Keyword Planner UI teklif/bütçe senaryosu ve dosyadan kelime girişi sağlar;
**Save to account** kampanya yaratma yoludur ve araştırma/okuma paketine alınmaz.
[Resmî UI yolu](https://help.ads.microsoft.com/apex/index/3/en-us/50902).
Türkiye/TRY/dil/geo granülerliği, kesin hesap kotası ve saklama şartları bu görevde
hesapla doğrulanmadı; adapter qualification ön koşuludur.

### Yandex

Direct v5 rapor servisi ile budget forecast farklıdır: resmî rehber forecast için
Live4 CreateNewForecast/GetForecast yöntemlerini işaret ediyor; v5 genel endpoint
listesine forecast eklemek hatalı olur. CreateNewForecast rapor nesnesi yaratır.
[Resmî istatistik/tahmin ayrımı](https://yandex.com/dev/direct/doc/en/best-practice/statistics),
[sürüm eşlemesi](https://www.yandex.ru/dev/direct/doc/en/concepts/methods).
Yetkili UI Budget Forecast kelime ve display-region üzerinden yaklaşık bütçe/CPC
verir; önce tarih/bağlamı saklanan manuel belge girişi tercih edilebilir.
[Resmî bütçe aracı](https://yandex.ru/support/direct/en/impressions/budget-estimation).

Uygulama erişim başvurusu ve kullanıcı OAuth yetkisi ayrı gerekir. Debug token
dahi gerçek reklam içeriğini yönetebilir; token türü salt-okunur güvence değildir.
[Başvuru](https://www.yandex.ru/dev/direct/doc/en/troubleshooting/register),
[OAuth sınırları](https://yandex.ru/dev/direct/doc/en/concepts/auth-token).
API puanları para/bakiye değildir; başarılı okuma ve hatalar da tüketebilir.
[Puan/kısıt modeli](https://yandex.com/dev/direct/doc/en/concepts/units).
Türkiye'ye mevcut ticari hesap açılışı/ödeme, TRY, hedef konumlar ve Live4 endpoint
hesap erişimi açık kalır; genel doküman mevcudiyeti bunları kanıtlamaz.

## Diğer mevcut katalog yüzeyleri ve öncelik

`experiments/decision-studio/dist/data.js` içindeki20 ürün **uygulanmış API
bağlantısı değil araştırma kataloğudur**. Search+Maps, PMax+Shopping veya
Display+DemandGen birleşik satırları ayrı yetenek kaydına bölünmeli; birine ait
tahmin diğerine taşınmaz. Meta messages da social ile aynı performans eğrisi olamaz.

Snapchat, Pinterest, X, Reddit, Spotify, retail/marketplace, creator/influencer ve
programmatic/native/video için bu görevde tam endpoint/ülke/yetki doğrulaması
tamamlanmadı. `not_researched` görünür kalsın; otomatik medya payı/pazar aktifliği
iddiası verilmesin. Talep kanıtına göre ayrı araştırma paketi. Retail stok/merchant,
creator teklif/teslimat, programmatic partner sözleşmesi ayrı maliyet ve veri
modelleri gerektirir. Owned CRM ve organic local profile medya bütçesi dağıtımından
ayrılır; teslimat/abonelik/üretim maliyeti ve izinler ayrıca değerlendirilir.

## Kota, maliyet, kullanım ve saklama karar kaydı

| Kaynak | Belgelenmiş / bilinmeyen maliyet | Kullanım ve saklama ön koşulu |
|---|---|---|
| Google Search | Bu incelemede çağrı başına fiyat doğrulanmadı; ücretsiz varsayılmaz. Kota belgeli; altyapı/bakım ayrı | Genel Ads API terms/data-use ve müşteri yetkisi incelenecek; saklama için evrensel süre uydurulmaz |
| YouTube Reach | Rehber non-exclusive royalty-free data license diyor; ortaklık/işletim masrafı bundan çıkmaz | İmzalı veri lisansı, audit ve aracın kullanım koşulları; allowlist kanıtı |
| Meta | Fiyat, hesap kotası ve güncel access-tier detayları bu araştırmada tamamlanmadı | App review/business izinleri, güncel platform terms, silme/revocation yükümlülükleri doğrulanmalı |
| LinkedIn | Genel API terms mevcutta API kullanım ücreti almadığını, ileride alabileceğini söylüyor; marketing özel anlaşması ayrıca | Genel self-serve şartları reklam yetkisi değildir; özel Marketing Program Terms erişimi burada doğrulanamadı |
| TikTok | Çağrı fiyatı ve sözleşmeye özgü R&F maliyeti bilinmiyor; genel/endpoint kota belgeli | App permissions + advertiser consent; Business sözleşmesi/saklama kısıtı incelenecek |
| Microsoft | Per-call ücret doğrulanmadı; hesap/servis quota ve bakım maliyeti açık | Sözleşme, yetkili müşteri kapsamı ve retention onayı olmadan kalıcı ham veri toplama yok |
| Yandex | API puanı belgeli; parasal maliyet/TRY ticari koşulları doğrulanmadı | OAuth/app access, hesabın şartları ve rapor saklama/silme koşulları ayrı kontrol |

[LinkedIn genel fiyat hükmü ve program ayrımı](https://developer.linkedin.com/legal).
Önerilen Yaparo politikası: adaptör başına doğrulanmış terms_version,
allowed_purposes, raw_retention, derived_retention, deletion_trigger ve reviewed_at
olmadan persistent ham müşteri verisi alma. Bu bir tasarım önerisidir; sağlayıcının
verdiği hukuki izin veya KVKK uygunluk kararı değildir.

## Alternatif yollar ve bozulma davranışı

| Yol | Kalite / hesap özgüllüğü | Erişim ve bakım | Kullanım kararı |
|---|---|---|---|
| Resmî forecast API | Bağlamı eşleşen hesap/amaç için güçlü başlangıç, satış doğruluğu garanti değil | İzin, sürüm, kota ve deprecation takibi | Google Search, erişim varsa Microsoft; Meta kitle sadece uygunluk |
| Resmî export / kontrollü manuel giriş | Doğru dönem/ayar dosyasıyla denetlenebilir; güncellik insan adımına bağlı | Daha az entegrasyon; hash, export tarihi, schema ve metrik eşleme gerekir | API başvurusu sürerken başlangıç; sessiz canlı etiketleme yok |
| Aynı işletmenin geçmişi | Net sipariş/iadeye bağlanırsa işletme özgüllüğü yüksek; selection bias ve gecikme var | Consent/olay sözleşmesi; düzenli güncelleme | Platform tahminiyle eşleştir, bağımsız gerçek sonuç otoritesi |
| Üçüncü taraf | Kapsama göre değişir; çoğu hesap sonucu yerine genel talep/rekabet verir | Teklif, sözleşme, provenance ve alt sağlayıcı bağımlılığı | İlk fazda satın alma yok; eksik sorunu ölçmeden ekleme |
| Kontrollü pilot | O işletmede gerçekleşme üretir; her pilot nedensel etki değildir | Ayrı sert harcama/onay/ölçüm kapısı | Belirsizlik yüksekken limitli öğrenme; bu görevde çalıştırılmaz |
| MMM | Yeterli geçmiş/variation ile üst düzey bütçe içgörüsü | Veri, model doğrulama, uzman bakım | Başlangıç bağımlılığı değil; veri yeterliliği kapısından sonra |

API outage/missing field/permission revoked durumunda capability durumu düşürülür;
aynı metriğe stale/unsupported/unauthorized işareti verilir, sıfır yazılmaz.
Önceden kaydedilmiş taslak korunur; eski kanıt yeni tarihliymiş gibi gösterilmez.
Kritik hedefleme/izin/bütçe koşulu değişirse onay yenilenir. Alternatif kaynak
kullanımı provenance ve yöntem farkıyla görünür olur; sessiz provider fallback yok.

## Kanıt örnekleri ve sınırlılık

Bu araştırmada bağımsız denetlenmiş, Türkiye'de aynı müşteri/aynı ürün için
genellenebilir başarı yüzdesi bulunmuş sayılmıyor. İncelenen somut örnekler resmî
API örnekleridir: Google inline plan, Microsoft inline estimator ve LinkedIn
criteriaV2 örnekleri **tahmin hesaplar**, gerçekleşmiş artımlı satış kanıtlamaz.
Öğrenilecek ders ortak bir conversion alanı uydurmak yerine yöntemin desteklediği
metriği ve bağlamı korumaktır. Platform pazarlama hikâyesi, başka müşterinin ROI'si
ve SDK örnek çıktısı Yaparo müşterisine sonuç garantisi değildir.

Sonraki doğrulama: sözleşme/maliyet/retention incelemesi → açık yetkili minimum
okuma erişimi → tek bağlamda safe response/schema testi → kontrollü senaryo bütçe
ızgarası → olgun gerçekleşmeyle kalibrasyon. Bu dosya bu adımların yapıldığını
iddia etmez.

### Resmî uygulama hikâyeleri: sonuç türünü ayırma

29 Ekim2026'da okunan
[Google'ın Haziran2026 Meridian incelemesi](https://business.google.com/en-all/think/measurement/google-meridian-marketing-mix-modelling/)
bir sağlayıcı/partner yayınıdır; bağımsız etki denetimi değildir.

| Örnek | Yöntem ve ölçülen konu | Sonuç türü / sınırlılık | Yaparo dersi |
| --- | --- | --- | --- |
| Ngern Tid Lor | Meridian + Google Ads; dönüşüm ve yatırım ölçeği | Yayın artan dönüşüm bildiriyor; sayısal holdout/karşılaştırma ayrıntısı yok, bağımsız nedensel kanıt sayılmaz | İşletme sonucunu ve karşılaştırma tasarımını birlikte tut |
| ITC Dark Fantasy | Google/NielsenIQ Meridian çalışması; YouTube frekansı | Planlamada kullanılacak model önerisi; gerçekleşmiş satış artışı olarak sunulmuyor | Daha fazla bütçeden önce doygunluk ve frekansı incele |
| APAC partner projeleri | Bütçe yeniden dağılımı/gelir veya dönüşüm | Yayındaki14% artış ifadesi, partnerlerin25projeye dayanan potansiyel beyanıdır; uygulanmış ve bağımsız doğrulanmış artış kabul edilmeyecek | Senaryo önerisi ile sonradan ölçülen gerçekleşmeyi ayrı kaydet |

[Robyn resmî vaka dizini](https://facebookexperimental.github.io/Robyn/docs/case-studies/)
Resident ve BARK örneklerini listeliyor. Ayrıntı bağlantıları bu araştırmada
Facebook giriş ekranına yönlendi; yöntem/karşılaştırma ayrıntısı okunamadı.
Bu yüzden Resident başlığındaki artış iddiası doğrulanmış gerçekleşme olarak
aktarılmıyor. Erişilemeyen başarı hikâyesi yerine tahmin doğrulama testleri esas
alınmalı; başka işletmenin sonucu Yaparo müşterisine garanti değildir.

## İşletmeye uygun bütçe: harcama ve durdurma semantiği

**Resmî sayfa kontrolü:29Ekim2026, Europe/Istanbul.** Bu ek yalnız araştırmadır;
hesap/API çağrısı, bütçe düzenleme, nesne oluşturma, yayın veya harcama yapılmadı.
İlgili tasarım [bütçe planlayıcı şartnamesinde](BUDGET_PLANNER_SPEC.md) bulunur.
Belge erişimi gerçek hesaptaki ürün/para birimi/ülke davranışının kanıtı değildir.

| Sağlayıcı / bütçe tipi | Resmî belgede görülen davranış | Yaparo için sonuç / açık doğrulama |
| --- | --- | --- |
| Google ortalama günlük | Çoğu kampanyada bir günün ücretlendirilen limiti ortalamanın2katı; aylık limit30,4katı. Ortalama günlük bütçe katı günlük tavan değildir. [Ortalama günlük bütçe](https://support.google.com/google-ads/answer/6385083), [harcama limitleri](https://support.google.com/google-ads/answer/10486637/about-spending-limits) | Tahmini günlük ortalamayı operasyonel kapasite sınırı gibi kullanma. Dönem/ayar değişikliği, istisna kampanya tipi ve hesabın gerçek bütçe profilini ayrı doğrula. Served cost ile billed cost farklı olabilir; sağlayıcı kredisi/refund anlık nakit telafisi varsayılmaz. |
| Google kampanya toplamı | Yeni kampanyada belirli başlangıç/bitiş ve toplam tutar; günlük harcama limiti yok, toplamdan fazla ücretlendirme yok. Tür sonradan değiştirilemiyor; uygun kampanya türleri ve3–90gün / bazı video-Demand Gen yollarında1yıla kadar dönem koşulları var. [Kampanya toplam bütçesi](https://support.google.com/google-ads/answer/10486938/about-campaign-total-budgets) | Toplam medya tavanı günlük iş yükünü korumaz. Günü gününe stok/randevu/yanıt yükü için ayrıca kaynak kontrolü ve gerekiyorsa sınırlı aşama gerekir. Tür/sürüm/hesap desteği kabul testinden geçmeden mevcut TEST profilini gerçek hesaba genelleme. |
| Meta | Güncel resmî bütçe, günlük bütçe, değişiklik ve account-limit sayfaları bu araştırmada giriş/erişim engeline yönlendi; güncel sayısal aşım oranı ve uygulama gecikmesi doğrulanamadı. [Günlük bütçe](https://www.facebook.com/business/help/190490051321426), [bütçe türleri](https://www.facebook.com/business/help/214319341922580), [bütçe değişikliği](https://www.facebook.com/business/help/196976447912140), [hesap limiti](https://www.facebook.com/business/help/141820733085330) | Üçüncü tarafların aktardığı yüzde/gecikmeler onaylı kural yapılmaz. Güncel resmî semantik ve hesabın ayarları doğrulanana kadar katı nakit/günlük kapasite garantisi verilmez; canlı yürütme kapısı kapalı kalır. |
| TikTok standart günlük / lifetime | Günlük ortalama ve tüm dönem toplamı ayrılıyor; lifetime günlere eşit dağılmayabilir. Bütçe tipi yayın sonrası değiştirilemiyor; minimumlar kampanya/adgroup/dönem düzeyinde. [Bütçe rehberi, Temmuz2026](https://ads.tiktok.com/resources/help/article/budget) | Belgedeki USD minimumu TRY hesabına körlemesine çevrilmez; teknik minimum ile anlamlı test ayrı kalır. Güncel hesap/amaç/ürün profilini kontrol et. |
| TikTok Dynamic Daily | Yedi günlük ortalama; bazı günler25% fazla, Pazar–Cumartesi hafta toplamı günlük tutarın7katıyla sınırlı. Amaçlara göre kullanılabilirlik ve sınırlı erişim koşulları var. [Dynamic Daily, Şubat2025 güncellemesi](https://ads.tiktok.com/resources/help/article/about-dynamic-daily-budget?lang=en) | “Daily” etiketine bakarak sabit tavan varsayma; gerçekten kullanılan pacing türünü kaydet. Kaynak eski diye kontrol tarihi yeniymiş gibi yayın tarihi değiştirilmez. |
| LinkedIn | Günlük bütçe ortalama; gün içinde50% fazla olabilir. Sürekli planda Pazartesi–Pazar haftalık toplam7kat; sabit tarihte günlük×gün toplamı. Lifetime bütçe tüm süre toplamıdır; kampanya/adset hiyerarşisi ve Dynamic Group Budget ayrı. [Güncel bütçe yardımı](https://www.linkedin.com/help/lms/answer/a420155), [API campaign/pacing açıklaması](https://learn.microsoft.com/en-us/linkedin/marketing/integrations/ads/account-structure/create-and-manage-campaigns?view=li-lms-2026-05) | Tek campaign budget alanını bütün yüzeylere kopyalama. Aktif API sürümü, kampanya/adset, pacingStrategy ve gerçek hesabın bütçe tipini birlikte sınayarak eşle. Tahsis ile sağlayıcının optimize ettiği günlük dağılım ayrı. |
| Microsoft Advertising | Günlük tutar hedef; aylık bütçe günlük×30,4. Ay içi değişiklikte geçmiş harcama+günlük×kalan gün hesabı. Günlük aşımın genellikle100%'den az tutulduğu ifadesi kesin garanti değil. Lifetime pacing güncel kalan tutar/günlerle yenilenir; aşım halinde iade anlatılır. [Resmî bütçe seçenekleri](https://help.ads.microsoft.com/apex/index/3/en/51006/) | “Genellikle” bir güvenlik tavanı değildir. İade olasılığını eldeki nakit sayma. Lifetime/API desteğini seçilen kampanya/hesap için ayrıca kanıtla. |
| Yandex | Haftalık bütçe Pazartesi–Pazar dağıtılır; haftalık bütçe değişikliği harcama sayacını sıfırlayabilir, hafta ortasında önceki harcama yeni limite dahil olmayabilir. Günlük pay zaman planına ve devreden bütçeye bağlı. [Resmî haftalık bütçe](https://yandex.ru/support/direct/en/strategies/week-budget) | Bütçe azaltmak her zaman kalan harcamayı aynı ölçüde azaltmaz. Yaparo'nun dönemi kapsayan harcama+bekleyen taahhüt defteri korunur; provider reset güvenlik defterini sıfırlamaz. Mevcut Türkiye hesabı/para koşulları hâlâ doğrulanmamış. |

### Ortak uygulama ön koşulu — öneri ile gerçek harcama ayrı

Kaydırıcının yerel senaryo hesabı hiçbir platform bütçesini değiştirmez. Salt
okunur forecast kotası/çağrı maliyeti, reklam medya bütçesinden farklıdır; forecast
bütçe ızgarası seçmek ödeme/yayın yetkisi değildir. Öneri, nakit uygunluğu,
plan seçimi ve operasyonel harcama onayı ayrı sürümlü kayıtlar olmalıdır.

Yayın adaptöründen önce doğrulanacak alanlar: provider/API sürümü, budget_type,
budget_level, pacing tipi, hesap timezone'u, dönem/gün kapsamı, birim/para/vergi,
değişiklikte limit-reset davranışı, gerçekleşen/bekleyen harcama tanımı ve
hesapta kullanılabilir sert toplam limit. Bu kontrol tamamlanmadıysa taslak
karşılaştırma yapılabilir; yürütme açılmaz. Hiçbir sağlayıcıda anlık bütçe kesme
veya durdurma SLA'sı bu araştırmada hesapla test edilmiş sayılmıyor.

Durdurma onayı, önceden oluşmuş gösterim/ziyaret/talep ve sonradan kaydedilecek
satışın sona erdiğini göstermez. Planın kapasite güvenlik payı ve günlük yoğunluk
kontrolü bu gecikmeli yükü dikkate almalı; gerçek stok/randevu rezervasyonu ve
bekleme listesi ayrı işletme kontrolüdür. Kaynak koptuğunda eski sayılar gerçek
zamanlı etiketlenmez. Otomatik büyüme yalnız açık izinli tutar/kanal/tarih/içerik
sınırları içinde ve güncel kapasiteyle olabilir; sözleşmedeki sınırı aşan artış
yeni kullanıcı onayı gerektirir.
