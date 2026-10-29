# Öneri ve bütçe motoru — kabul ve ölçüm planı

Durum: önerilen geliştirme kabul planı; 29 Ekim 2026, Europe/Istanbul.
Bu belge bir test sonucu değildir. Bu araştırma kapsamında hesap, veri tabanı,
kampanya, harcama veya uygulama kodu üzerinde işlem yapılmadı. Aşağıdaki yeni
senaryolar gelecekte uygulanacaktır. Sentetik başarı gerçek hesap yetkisi,
platform geçerliliği veya satış başarısı sayılmaz.

## 1. Mevcut testlerden korunacak sözleşmeler

Depo köküne göre yollar:

| Mevcut dosya / test | Korunacak davranış; yeni kapsam |
|---|---|
| `experiments/decision-studio/brief-analysis.test.cjs` | 46 geçerli yolun tam ilk-aşama bağlamı; bilinmeyenleri sınıf/başarı puanı olarak uydurmama. Yeni sözleşme aynı bağlamdan üretilmeli. |
| `experiments/decision-studio/owned-recommendation.test.cjs` | `evaluateOwned` saklı sınıf/risk/hazırlık girdilerini otorite saymaz; bilinen boyut kapsamı, desteklenmeyen amaç, tarih/konum ve bütçe sınırları. Kapsam ağırlığı tahmin güveni değildir. |
| `experiments/decision-studio/engine.test.cjs` | Eski araştırma örneğinin 20 kanal skoru, 88 bütçe sınırı örneği, minimum/tavan/rezerv. Bunlar piyasa tahmini değil regresyon örnekleridir. |
| `experiments/decision-studio/plan_check.py` | `test_plan_no_invented_budget_location_or_repeated_audience`, `test_plan_same_pair_brief_edit_preserves_manual_bounds`, `test_plan_percentages_selection_reserve_and_stale_guards`, `test_plan_radius_clips_turkey_and_refuses_invalid_centers`, `test_plan_visual_desktop_mobile_and_compact_review`. Yeni veri durumları aynı sade ekranı korumalı. |
| `experiments/decision-studio/test_sources.py` | Tarih/fetch ayrımı, eşzamanlı isteği birleştirme, TTL/force-throttle/yeniden başlama, bağlam/hesap/kalite/zaman değişmesi, rastgele URL/tenant/NaN reddi. Bu testler kamuya açık kur katmanına aittir; reklam tahmin adaptörünün hazır olduğunu kanıtlamaz. |
| `apps/web/growthtwin/modules/campaigns/test_google_draft_payload.py` | `test_every_plan_change_changes_fingerprint`, `test_snapshot_is_canonical_stable_and_immutable`, eski/eksik tercihin reddi. Yeni plan sürümü/kanıt bağlama bunları tamamlamalı. |
| `apps/web/growthtwin/modules/connections/test_total_budget.py` | `test_exact_total_and_validate_only_no_ledger`, `test_rejection_or_timeout_never_falls_back`, `test_source_or_target_change_during_lookup_blocks_request`. Tahmin çağrısı yayın veya ledger mutasyonuna dönüşmemeli. |
| `apps/web/growthtwin/modules/connections/test_campaign_lifecycle.py` | Tekrar denemede çift oluşturma yok, belirsiz timeout sonrası otomatik create yok, TEST hedefi doğrulanmadığında mutasyon yok. Yeni öneri katmanı bu kapıları açamaz. |
| `apps/web/growthtwin/modules/campaigns/test_report_metrics.py` | Mevcut rapor metriklerinin anlamını koru; yeni platform/işletme/atfedilen/artımlı metrikler ayrı eklenmeli. |

Mevcut CI geçmişi için `docs/continuity/STATE.md` ve canlı CI sonucu esas alınır.
Bu listedeki testlerin dosyaları incelendi; bu belgeyi yazmak için yeniden geniş
uygulama testi çalıştırılmadı. Yeni motor tamamlanmış gibi toplam test sayısı verilmez.

## 2. Test katmanları ve kanıt düzeyi

1. Saf sözleşme ve matematik testleri: ağ/DB olmadan her değişmez, sınır ve
   bozuk girdi. Rastgele üretilmiş tekrarlanabilir bütçe/kapasite örnekleri ekle.
2. Adaptör kontratı: resmî cevaplardan kişisel/hesap verisi içermeyen doğrulanmış
   fixture ve hata örnekleri; desteklenmeyen alan/sürüm açık durum döndürür.
3. Uygulama entegrasyonu: geçici test DB'sinde tenant, sürüm, önbellek,
   eşzamanlılık, iptal, izin ve audit; mevcut özel DB'lere dokunma.
4. Tarayıcı: masaüstü ve mobil, klavye, ekran okuyucu adları, kaynak/eksik bilgi,
   plan değişikliği ve taslağı koruyan hata. Ekran görüntüsü gerçekten incelenir.
5. Yetkili salt-okunur hesap kanıtı: ayrı onay, uygun sağlayıcı/hesap/amaç/pazar
   ve gerçek response kanıtı; yalnız kullanılan uç nokta ve kapsam için geçerli.
6. Sınırlı ücretli pilot: ayrı yayın/harcama izni, sert tavan, durdurma ve
   ölçüm kapıları; bu araştırmanın kapsamı dışında.

Her test raporu `synthetic / mocked_provider / authorized_read_only /
controlled_live` düzeyini, commit, kural/adaptör/şema sürümünü, tarih ve gerçek
çalıştırılan kontrolleri taşır. Bir üst düzeye kendiliğinden yükselmez.

## 3. Zorunlu senaryo matrisi

`S` = saf/fixture, `I` = geçici entegrasyon, `B` = tarayıcı,
`R` = ayrıca izinli gerçek salt-okunur doğrulama, `L` = ayrıca izinli pilot.

| ID | Kurulum / eylem | Beklenen sonuç / kabul | Katman |
|---|---|---|---|
| A01 | Yeni hesap, geçmiş yok | Sıfır satış varsayılmaz; geniş belirsizlik/eksik veri ve ölçüm veya sınırlı test önerisi; garanti yok. | S,I,B |
| A02 | OAuth yok, scope eksik, erişim iptal | `unauthorized`/`access_required`; otomatik OAuth, hesap okuma veya yazma yok; taslak korunur. | S,I,B,R |
| A03 | 429, timeout, 5xx | Bütçeli retry/backoff; Retry-After uyumu; circuit state; eski cevabı güncelmiş gibi gösterme; çağrı fırtınası yok. | S,I |
| A04 | Missing/unsupported/unauthorized/stale/zero | Beş durum farklıdır; `value=0,status=available` ile `value=null,status=missing` aynı hesaplamaya girmez. | S,I,B |
| A05 | İki kaynağın aynı metrik için çelişmesi | Bağlam/tarih/örneklem/atıf farkı gösterilir; sessiz ortalama/son yazan kazanır yok; kritikse harcama bekler. | S,I,B |
| A06 | Bütçe 0, organic veya content_only | Medya ayırma/forecast çağrısı yok; içerik/organik yol devam eder; üretim maliyeti ayrı gösterilir. | S,I,B |
| A07 | Teknik minimumdan az bütçe | Kanal tahsisi 0; neden ve kalan bütçe; başka kanala zorla harcama yok. | S,B |
| A08 | Teknik minimum karşılanır, anlamlı test minimumu karşılanmaz | Teknik olarak mümkün ile öğrenmeye yeterli ayrı gösterilir; varsayımsal test minimumu kaynağı/sürümüyle etiketlenir. | S,B |
| A09 | Tüm adaylar tavanda | Artan tutar rezerv kalır; toplamı %100 harcamak için tavan yükseltilmez. | S,I,B |
| A10 | Üç kanal aynı 10 randevu slotunu kullanıyor | Ortak kapasite 30 sayılmaz; toplam planlanan kapasite kullanımı üst sınırda; belirsiz dönüşümde temkinli senaryo ve durdurma. | S,I |
| A11 | Stok/kapasite gün içinde azalır | Kaynak revizyonu değişir; eski onay askıya alınır, yayın öncesi tekrar kontrol; taslak/önceki sürüm kaybolmaz. | S,I,B |
| A12 | İşletme ülkesi TR, hesap ülkesi farklı, hedef pazar çoklu | Üç alan ayrıdır; uygunluk hesap/pazar başına; para/saat/vergi çerçevesi olmadan birleştirilmez. | S,I,B,R |
| A13 | TRY/EUR, farklı saat dilimi/DST ve atıf penceresi | Kur tarihi/yönü/kaynağı, vergi ve yerel gün sınırları sabitlenir; tarihleri saf UTC güne keserek kıyaslama yok. | S,I |
| A14 | Desteklenmeyen konum/radius | Alternatif konum yalnız kullanıcı onayıyla; TR sınırı önizlemesi platform hedefleme ispatı değildir; hedef genişletme sessiz yapılmaz. | S,B,R |
| A15 | Video isteyen kanal, yalnız metin/görsel var | Üretim hazırlığı eksik; ücretli video oluşturma otomatik başlamaz; alternatif format/kanal ve üretim maliyeti ayrı. | S,B |
| A16 | Sağlık/bağış/işe alım veya hassas kategori | Geçerli kanıt ve sağlayıcı/pazar kuralları yoksa bekle; satış karı hedefiyle bağış/erişim optimize edilmez. Yerel yazı cevapları hukuki doğrulama değildir. | S,I,B |
| A17 | Satışlar 14 gün gecikiyor | Olgunlaşmamış cohort provisional; erken sıfırlar nihai başarısızlık sayılmaz; eğitim/kıyas verisine karışmaz. | S,I |
| A18 | Sipariş iptal/iade, kısmi iade | Sipariş kimliğiyle düzeltme/revizyon; brüt/net/katkı ayrımı; mükerrer webhook aynı iadeyi iki düşmez. | S,I |
| A19 | Gerçekten sıfır dönüşüm | MAE/bias tanımlı kalır; sonsuz ROAS/CPA veya yanıltıcı MAPE yok; sıfır örneği rapordan çıkarılmaz. | S,I,B |
| A20 | Meta ve Google aynı satışı sahiplenir | Platform raporu iki ayrı gözlem; işletme satış defteri tek işlem; toplam satış 2 olmaz. Çapraz-platform kişi/erişim de eşsizmiş gibi toplanmaz. | S,I,B |
| A21 | İlk niyet/outcome/teslim modu değişir | Uyumsuz eski yanıtlar etkisiz; risk korunur; tahmin/kanal planı/üretim/onay bağları geçersizleşir; uyumlu manuel sınırlar korunabilir. | S,I,B |
| A22 | API alanı kaldırılır/türü değişir | Şema/özellik bazlı açık `unsupported`/`provider_changed`; yok alan 0 olmaz; adaptör durur, yayın onayı açılmaz; contract alert. | S,I |
| A23 | Onaydan sonra hedef, bütçe, teklif, tarih veya kaynak expiry değişir | Eski onay yeni planı kapsamaz; ilgili tahmin/ekonomi/tahsis/onay yeniden değerlendirilir; tekrarlı onay aynı işi çift başlatmaz. | S,I,B |
| A24 | Cache başka tenant/hesap/scope/pazar/bütçe ile istenir | Hit yok; kimlik/etkin yetki kontrolü cache öncesi ve kullanımda; iptal sonrası cache erişimi yok. | S,I |
| A25 | Aynı anda aynı forecast isteği | Tek outbound request ve sınırlı bekleme; farklı scope/tenant asla birleştirilmez; hata cache'i veri cevabı olmaz. | S,I |
| A26 | Kullanıcı öneri butonuna 20 kez basar | Geçerli değişmeyen gözlem yeniden kullanılır; yeni zaman damgasıyla sahte güncellik veya LLM/API çağrı sayısı artışı yok. | S,I,B |
| A27 | Bütçe gridinde eksik/monoton olmayan tahminler | Aralık dışı ekstrapolasyon veya eğriyi zorla karlılaştırma yok; kaynak belirsizliği korunur; küçük artışın ilave faydası bulunamıyorsa artış önerilmez. | S,I |
| A28 | Çok küçük örnek ve tek büyük satış | Destek/olgun cohort sayısı görünür; nokta oranı kesin işletme CVR'ı sayılmaz; minimum veri kuralı sürümlü. | S,I,B |
| A29 | Kısıtlı hedef kitleye daha çok bütçe | Doygunluk/frekans/belirsizlik kontrolü; yalnız ortalama geçmiş CPA düşük diye bütçe artırılmaz. | S,I,L |
| A30 | Uygun hiçbir kanal yok | “Henüz harcama / ölçüm kur / eksik bilgiyi tamamla” geçerli başarılı ürün çıktısı; sahte öneri uydurma yok. | S,B |
| A31 | Kullanıcı daha düşük/üst manuel yüzde seçer | Uygunluk/minimum/tavan/ortak kapasite korunur; reddedilme gerekçesi; orijinal öneri/sürüm ile manuel değişiklik audit'te ayrı. | S,I,B |
| A32 | Hesap özgü veri yok, yalnız sektör başlangıç varsayımı var | Açık varsayım kaydı ve sürümü; izin olmadan başka müşterinin verisi yok; platform tahmini veya güven düzeyi etiketi yok. | S,I,B |
| A33 | Tahmin-only hesabıyla publish çağrısı | Yetki reddi; öneri rolü yayın/harcama rolüne yükselmez; GET/forecast endpoint'leri kampanya nesnesi oluşturmaz. | S,I,R |
| A34 | Kötücül hedef URL veya kullanıcı metni | Kaynak fetch'i keyfi URL'ye gitmez; SSRF/redirection allowlist, XSS ve prompt injection sınırları; LLM bütçe/izin otoritesi değildir. | S,I,B |
| A35 | Ölçüm durdu veya consent değişti | Veri kalitesi alarmı; eksik dönem sıfır sayılmaz; otomatik artış askıda; yalnız yetkili asgari veri kalır. | S,I,L |
| A36 | Sağlayıcı alt–üst aralık gönderiyor | Kaynak anlamı ve kapsamı korunur; belgelenmedikçe “%95” yazmaz; Yaparo kalibrasyonu ayrı yöntem/sürüm ve out-of-time kanıt ister. | S,I,B |

## 4. Matematiksel değişmezler

Para API sınırında doğru sağlayıcı birimine çevrilir; iç tahsiste currency başına
tam sayı alt birim veya Decimal kullanılır. TRY kuruş ile Google micros eşit
varsayılmaz. NaN, Infinity, taşma, negatif ve kesirli alt birim reddedilir.

- Her kanal için `allocation_i >= 0`; elenmiş kanalda `allocation_i = 0`.
- Aynı para/vergi kapsamındaki `sum(allocation_i) + reserve = media_budget`;
  `reserve >= 0`; bütçe aşımı hiçbir rounding sırasıyla oluşmaz.
- Aktif tahsis teknik minimuma ve seçilen planın anlamlı test şartına uyar;
  kanal tavanı, hesap sınırı ve kullanıcının sert tavanı aşılmaz.
- İçerik üretimi/hizmet/vergi kalemleri açık ve ayrı; medya bütçesine gizlice
  eklenmez. Farklı currency tutarları kur kanıtı olmadan toplanmaz.
- Her ortak kaynak `r` için `sum(resource_usage_i,r) <= available_r`.
  “available” dönem/ürün/lokasyon kimliğiyle tek kaynak olmalı. Beklenen talep
  fiziksel rezervasyon garantisi değildir; gerçekleşen kullanım için atomik stok/
  kapasite kontrolü ve stop kuralları ayrıca gerekir.
- Bilinmeyen değer null+durum taşır; `null -> 0` ile uygunluk/ROI/kapsam iyileşmez.
- Kapasite veya bütçe azalınca geçersiz eski plan geçerli olamaz. Bir kanalı
  yasaklamak diğer kanalların aynı ortak kaynağı sınırsız tüketmesini sağlamaz.
- Veri kalitesi/yaşı kötüleşince “daha kesin” etiket oluşmaz. Skorun ağırlık
  normalizasyonu, olasılık veya sonuç aralığı yerine geçmez.
- Aynı idempotency/event kimliği tekrar geldiğinde satış/adet/iade/harcama
  yinelenmez; tenant ve kaynak kimliği dedup kapsamına dahildir.
- Algoritma izinli sonlu bütçe gridinde deterministik ve açıklanabilir olur;
  greedy veya heuristik yaklaşımın global optimum olduğu iddia edilmez.

Sınır kümeleri: 0/1 kuruş; min-1/min/min+1; cap-1/cap/cap+1; shared-cap;
%0/%100 ve yuvarlama; aynı anda düzenleme; bütçe gridinde son nokta; unsupported
metric; stale source; stok 0 ve bilinmeyen stok; büyük integer/money sınırı.

## 5. Tahmin dondurma ve gerçekleşme kıyaslaması

Öneri anındaki gözlem/sürüm silinmeden saklanır: tenant, plan revision,
snapshot digest, provider/API sürümü, kaynak request parametreleri, zaman/para/
vergi/atıf kapsamı, veri as-of/fetched/expiry, hedef metrik, nokta/aralık,
aralık türü, yöntem/kural sürümü ve bilinen eksikler. Sonradan gerçek sonuçla
aynı satırı güncelleme: ayrı outcome snapshot ve eşleştirme revizyonu oluştur.

Kıyas birimi aynı **metrik + cohort + pazar + currency + dönem + attribution**
olmalı. Örneğin tıklama tahmini ile net satış, lead ile nitelikli lead,
platform conversion ile gerçekleşen randevu karşılaştırılmaz.

### Ölçüler

`p_j` tahmin, `y_j` olgun gerçekleşme, `n` geçerli eşleştirilmiş cohort:

- Bias: `mean(p_j - y_j)`; pozitif = fazla tahmin. İşaret ve mutlak birim açık.
- MAE: `mean(abs(p_j-y_j))`; sıfır gerçekleşmelerde de tanımlıdır.
- RMSE, büyük hataları görmek için ikincil; tek büyük müşterinin etkisi ayrıca.
- WAPE yalnız `sum(abs(y_j)) > 0` ise; aksi `not_defined`. Yüzde hata tek başına
  kullanılmaz; sıfırları çıkartarak iyileştirilmez. MAPE ana gösterge değildir.
- Belirli anlamı olan tahmin aralığı için coverage: `count(L_j <= y_j <= U_j)/n`;
  ortalama/medyan genişlik ve hedef nominal seviye (varsa) yanında gösterilir.
  Çok geniş aralık yüksek coverage ile başarılı ilan edilmez.
- Alt/üst uç yanlılığı ve aralık dışındaki hatanın yönü; kaynak bandı ile
  yerel kalibre predictive interval ayrı seri tutulur.
- `n`, eksik/elenen/provisional cohort sayısı, gözlem dönemi, güncellik,
  olgunluk kesimi ve örneklem yapısı her skorun yanında.
- Kanal × hedef × pazar × müşteri kırılımı; az hücrede kişisel veri sızıntısı
  veya yanıltıcı kesinlik olmaması için minimum raporlama desteği.
- Mikro ağırlıklı ve müşteri başına makro ortalama ayrı: büyük işletme küçük
  işletmedeki hatayı saklamasın. Bir kişinin tekrar tahminleri bağımsız örnek
  sayılmaz; belirsizlik hesapları cohort/tenant kümelenmesini dikkate alır.

Kabul için tek uydurma “%80 doğruluk” eşiği yok. İlk pilotta ileriye dönük
metrik/olgunluk/hata maliyeti tanımlanır; basit “son olgun dönem” ve izinli
başlangıç varsayımı baseline'larıyla rolling/out-of-time karşılaştırılır.
Geçmişe dönük en iyi ay seçilmez; train/test zaman sızıntısı engellenir.
Dar aralık veya otomatik bütçe artışı ancak tanımlı segmente ait yeterli ileri
dönem kanıtı ve başarısızlık halinde geri çekme eşiğiyle açılır.

### İşletme olgunluk yolları

| Yol | Beklenti / değerlendirme |
|---|---|
| Geçmiş yok | Uyumluluk ve ölçüm; varsa platformun kendi metrik bandı ve açık varsayım; satış nokta tahmini gerekmez. Küçük test veya harcamama meşru sonuç. |
| Az veri | Yalnız müşterinin olgun sonuçlarıyla geniş aralık; örneklem/kalite sınırı; basit oran ve duyarlılık senaryosu. Başka müşterinin oranı izinsiz eklenmez. |
| Güçlü geçmiş | Zaman bazlı holdout, kalibrasyon, doygunluk/ilave değer incelemesi ve hata izleme; drift/consent/iş modeli değişince düşük veri yoluna geri dönüş. |

Satış gecikmesi için tenant/olay türü bazlı olgunluk watermark'ı tanımla.
Provisional dönemler ayrı sunulsun; geç gelen/iade edilen sonuç revizyonu yeniden
değerlendirme tetiklesin. Eğitimde kesim anında bilinmeyen gelecekteki sonuç
kullanılmasın. Attribution düzeltmesi gerçek net gelir defterini değiştirmesin.

## 6. Deney, atıf ve ileri modellerin kabulü

Yaratıcı A/B testi ile reklamın **varlığına** ait artımlı etki farklı sorulardır.
Yaratıcı testi, randomizasyon/birim/sızıntı/örneklem uygunluğu varsa kreatifler
arasındaki farkı inceler; tek başına toplam incremental sales kanıtı değildir.
Artımlı etki için uygun holdout/geo deneyinde önceden KPI, analiz birimi,
minimum saptanabilir etki, güç, süre, gecikme, denge ve contamination ölçüsü
tanımlanır. Kontrol yoksa “reklama atfedilen”, “reklamın yarattığı” olmaz.

Meridian/Robyn başlangıç gereksinimi değildir. MMM denemesinin kapısı: tutarlı
zaman serisi, yeterli zaman/geo varyasyonu, doğru KPI, fiyat/sezonsallık gibi
confounder'lar, eksik dönem analizi, privacy kapsamı ve uzman model incelemesi.
Tek müşterinin bir haftalık/tek kampanyalı verisine zorlanmaz. Çalışan model
çıktısı nedensel varsayımları veya kalibrasyon eksikliğini ortadan kaldırmaz.

Resmî kaynaklar 29 Ekim 2026'da açılarak incelendi:

- [Google Meridian — Amount of data needed](https://developers.google.com/meridian/docs/pre-modeling/amount-data-needed):
  veri yeterliliğinin geo/zaman yapısı ve model karmaşıklığıyla değerlendirilmesi
  gerekir; sabit evrensel bir gözlem eşiği uygun değildir. Yaparo için model
  öncesi veri yeterliliği ve çıktı belirsizliği incelemesi öneriyoruz.
- [Meta Robyn — Analyst's guide](https://facebookexperimental.github.io/Robyn/docs/analysts-guide-to-MMM/):
  veri incelemesi ve deneyle kalibrasyon, aynı KPI/dönem/granülerlik ve model
  doğrulaması önemlidir. Bunlar üretici yöntem rehberidir; Yaparo için ölçülmüş
  başarı veya bağımsız müşteri performans kanıtı değildir.

## 7. Faz geçişleri ve canlıya alma engelleri

| Kapı | Gerekli kanıt | Açılmayan yetki |
|---|---|---|
| G0 — sözleşme / sentetik | A01–A36'nın uygulanabilir saf/fixture vakaları, değişmezler, sürüm/binding ve dört-aşama tarayıcı akışı | Hesap bağlantısı/gerçek veri/harcama yok. |
| G1 — uygulama dry-run | Tenant/izin/cache/revocation/idempotency/race testleri, audit ve güvenli hata; geçici DB'de migration/recovery doğrulaması | Dry-run yayın izni değildir. |
| G2 — gerçek salt-okunur forecast | Belirli sağlayıcı/hesap/pazar için açık yetki; scope ve hesap proof; resmî response/schema/metric karşılaştırması; saklama ve veri politikası | Forecast okuma token'ı nesne oluşturma veya medya harcama izni vermez. |
| G3 — kontrollü pilot | Önceki tüm release/security/privacy/staging E2E/backup-restore/rollback kapıları; müşterinin hedef/sert bütçe/tarih/içerik onayı; stop ve belirsiz gönderim uzlaştırması; ölçüm olgunluğu planı | Otomatik tüm-kanal/global rollout yok. |
| G4 — sınırlı öğrenme / büyüme | İleri dönem hata ve aralık kalibrasyonu, kapasite/doğru net sonuç, drift ve rollback; müşteri sınırları içinde yeniden onay kuralları | Kesin satış/ROI garantisi veya izinsiz müşteriler-arası öğrenme yok. |

Gerçek hesap erişimi, API response'u, pazar/amaç desteği, hukuki/politika
uygunluğu, ölçüm yetkisi, saklama/consent koşulları veya hard spend yetkisi eksikse
ilgili kapı kapalı kalır. Taslak ve içerik çalışması korunur; kullanıcı başa
döndürülmez. Bir platformdaki başarılı G2, diğer platforma veya production'a
aktarılmaz. Her kapı kanıtı yeniden kontrol tarihi ve kapsam taşır.

## 8. Ürün kartı ve görsel kabul

Dört aşama korunur. Kanal kartı kısa görünümde durum/hedef/tutar/varsa gerçek
metrik bandı gösterir; ayrıntıda kaynak-as-of, bilgi yeterliliği, gerekçe,
minimum/tavan, eksik hazırlık ve tek sonraki eylem açılır. Bilinmeyen satış
yerine sıfır, uydurma sayı veya loader sonrasında sahte canlı veri gelmez.

Mobil390px/masaüstü1440px görsel inceleme: uzun Türkçe literal, çok-kanal liste,
rezerv, kaynak hatası, stale uyarısı, organik yol ve health/fundraising durumu.
Yatay taşma yok; renk tek bilgi taşıyıcısı değil; yüzde slider'ının sayısal
girişi/klavyesi; durum değişiminde odak korunur. Tekrar sorulan ilk-aşama
bilgisi yok. Kritik stale tahmin yayın onayını durdurabilir, taslağı silmez.

“Temkinli / öğrenme / büyüme” ancak seçilen hedef, bütçe/risk sınırı, veri
yeterliliği ve beklenen ilave sonuç bakımından hesaplanabilir fark varsa sunulur.
Aynı tahsisin üç pazarlama adıyla kopyalanması kabul değildir.
