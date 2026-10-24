# Yaparo uygulama sırası ve kabul ölçütleri

23 Ekim 2026. [Ana plan](yaparo-open-source-master-plan.md) ve [ADR-0040](../adr/0040-owned-core-and-open-source-adoption.md) kapsamındadır. Aşağıdaki tablolar kabul ölçütlerini tanımlar; güncel ilerleme aşağıda ayrı belirtilir. Her PR somut müşteri çıktısı veya onun gerekli korumasını teslim eder. Yeni genel amaçlı altyapı, ilk akış onu gerektirmedikçe eklenmez. Gerçek veri/yayın/ödeme/ücretli kaynak kapıları korunur.

Kalıcı iş takibi: [GitHub #328](https://github.com/ugurkbcgl-hub/yaparo/issues/328).

## 23 Ekim uygulama ilerlemesi

- **Y01 tamamlandı:** [kaynak/domain haritası](creative-editor-domain-map.md), iki
  sabit sentetik ürün/hizmet örneği ve tek düzenle/kaydet/aç/PNG görevi tanımlandı.
- **Y02–Y03 yerel seçim kapısı kapandı:** [ADR-0041](../adr/0041-bounded-fabric-and-brand-identity.md)
  güvenlik/derleme kapısında kalan hazır adayı dışlar ve dar yerel dilim için
  Fabric 7.4.0 seçer. Hazır adayın yapılmamış eş görev testi başarılı sayılmaz;
  bu aday için o koşul açıkça değiştirilmiştir. Y06 üretim, yükseltme ve taşınabilirlik
  koşulları devam eder. Y04 ilk dilimi: iki sentetik marka oluşturma/seçme/düzenleme, kimlik sürümleri
  ve sahiplik sınırları uygulandı. Kayıtlı çalışmalar belirli marka kimliği
  sürümüne bağlandı. Logo/font yükleme ve kaynak kanıtları açık; Y04 bütünü
  tamamlanmış değildir.
- **Y06–Y07 ilk görsel bağlantı:** sahip olunan çalışma → Fabric düzenleme →
  sürüm denetimli sunucu kaydı → yeniden aç → 800×800 PNG akışı uygulandı.
  İlk beş odaklı HTTP/tarayıcı testi geçti; dış istek yok. ADR-0042 ile yeni
  tasarımlara marka paleti ve kayıt geçmişinden yeni sürüm olarak dönüş eklendi.
  Eski v1 görünümü korundu. Özel font/varlık, her hareket için undo, yükseltme
  taşınabilirliği ve kampanya bağı açık.
- Kullanıcı 23 Ekim'de kullanım limiti kontrolünü kaldırdı; çalışmayı kullanım
  eşiğine göre durdurma kuralı uygulanmaz. Normal doğrulanmış devir notları korunur.

## A — Marka, materyal ve kendi editörümüz

| ID | İş / bağımlılık | Teslim ve tamamlanma ölçütü |
|---|---|---|
| Y01 | Mevcut domain ve arayüz haritası; başlangıç | Gerçek mevcut marka/asset/creative/campaign modelleri ve yeni ihtiyaçların eşlemesi; sabit sentetik hizmet + ürün örneği; tek kullanıcı görevi ve test dosyası sınırı |
| Y02 | Editör adayını daralt; Y01 | Fabric ve tek hazır MIT editör için sabit sürüm, lisans/bağımlılık/güvenlik ve entegrasyon incelemesi; geçici kısa liste, nihai seçim Y03 sonucuna bağlı |
| Y03 | Uçtan uca geçici editör denemesi; Y02 | Ayrı dal/kapalı yerel sentetik ekran: logo/resim + Türkçe yazı → düzenle → kaydet/aç → PNG; hosted editör/AI bağlantısı gerektirmeyen kanıt; ölçülen görev ve upgrade maliyetiyle gerekçeli nihai seçim |
| Y04 | Çok markalı kimlik ve kaynak gerçekleri; Y01/Y03 | Aynı kullanıcıya iki ayrı sentetik marka; kimlik/karakter/renk/logo/font/teklif/kanıt sürümü ve marka seçici; sunucuda erişim; eski kampanyalar sessizce tahmini markaya bağlanmaz |
| Y05 | Kalıcı materyal kütüphanesi; Y04 | Sentetik JPG/PNG/WebP alımı, özel depo, MIME/byte/piksel sınırı, karantina/işleme, hak ve kaynak/sürüm kayıtları; başka tenant erişemez |
| Y06 | Editör ürünleştirme; Y03/Y05 | Yaparo şeması, metin/logo/crop/katman/undo, kare/dikey export; orijinaller + sahne + asset/font/lisans manifesti yeni çalışma alanına aktarılıp düzenlenir; dış AI/editör/CDN erişimi engelliyken export çalışır; Türkçe/klavye ve desteklenen sürüm upgrade/geri dönüş örneği geçer |
| Y07 | Tek müşteri yolculuğu; Y06 | Mevcut kampanyadan marka → içerik → düzenleme → önizleme → indirme; mobil kullanım, açık ilerleme, örnek/gerçek ayrımı; kayıp düzenleme yok |
| Y08 | Kullanılabilirlik ve kapsam kontrolü; Y07 | Sentetik senaryolarda ölçülmüş hata/süre; izinli katılımcı bulununca 6 gözlem, en az 5 bağımsız tamamlama hedefi; yoksa kullanıcı doğrulaması açık yazılır |

[Markaya özel deneyim](brand-specific-experience.md), Y04–Y14 ve Y30 için ek kabul
ölçütüdür: marka sürümü/izin/varlık/üretim bağı, ayrı yaratıcı hafıza, kural kontrolü
ve eski çalışmaların korunması. Temel çok marka ilk kit diliminde yer alır.

Y01–Y03 yerel seçim kararı ADR-0041 ile kaydedildi; yaratıcı çalışma bağı ve ilk görsel akış uygulandı; marka paleti ve kayıt geçmişi eklendi; sırada sınırlandırılmış sentetik materyal kütüphanesi vardır. Bütün müşteri dosya türlerini açmaz. Y05 gerçek upload servisini ancak ilgili veri/güvenlik kapıları sonrası açar; önce sentetik yerel örneklerle geliştirilir.

## B — Değiştirilebilir AI üretimi ve maliyet

| ID | İş / bağımlılık | Teslim ve tamamlanma ölçütü |
|---|---|---|
| Y09 | Görev/yetenek profili; Y04 | Sürümlü istek/çıktı, kaynaklar, izinli sağlayıcı, maliyet rezervasyonu ve async sonuç sözleşmesi; web formları model adına bağımlı değil |
| Y10 | Tipli AI kütüphanesi denemesi; Y09 | Mevcut adaptör ile PydanticAI aynı sentetik kümede karşılaştırılır; yalnız gerekli paket seçilir; bilinmeyen/bozuk çıktı reddedilir |
| Y11 | Metin üretimini akışa bağla; Y07/Y10 | Yetkili değerlendirme koşullarında kaynak bağlı metin varyantları; kullanıcı düzeltmesi korunur; maliyet/hata açık; üretim sağlayıcı seçimi ayrıca kaydedilir |
| Y12 | Görsel üretim/düzenleme; Y06/Y09 | Tek seçili görsel/katman üzerinde işlem, maske/ölçü/format yeteneği kontrolü; gerçek çıktı dosyası kaydedilir ve açılır; metin/logo ayrı katmanda |
| Y13 | Kalıcı arka plan işi; Y11/Y12 | İşçi/kuyruk ihtiyacı ve maliyeti incelenir; tekrar/crash/timeout ikinci mantıksal iş veya tüketim yaratmaz; iptal ile uzaktaki durumu uzlaştırma ayrı |
| Y14 | Sağlayıcı değişimi ve kalite; Y13 | İki uygun adaptörde aynı görev sözleşmesi; izinli yedek/geri dönüş; mevcut tasarımlar düzenlenebilir; kabul edilen çıktı maliyeti ve kalite raporu |

Ücretli deneyin veri/sağlayıcı koşulları ve mevcut harcama yetkisi işlem öncesi kontrol edilir. Bu belge sınırsız deneme veya yeni abonelik izni değildir. AI kalite kapısı geçmezse temel editör işlevleri yine kullanılabilir.

## C — Hesap, kredi ve hizmet satışı

| ID | İş / bağımlılık | Teslim ve tamamlanma ölçütü |
|---|---|---|
| Y15 | Kayıt ve müşteri/ekip erişimi; Y07 | django-allauth uyumluluk incelemesi; e-posta doğrulama/hesap kurtarma; owner/member rolleri ve izolasyon; gerçek kayıt yalnız yayın kapıları sonrası |
| Y16 | Fiyat ve kredi defteri; Y09/Y13 | Üretim/bonus/rezervasyon/tüketim/serbest bırakma/iade, tekil hareketler; maliyet/TRY/vergi/kur tablosu; örnek hesaplar ve başarısız iş politikası |
| Y17 | Ödeme adaptörü; Y15/Y16 | Uygun Türkiye kuruluşu ve şirket şartları doğrulanır; sandbox checkout, imza/tutar/currency ve tekrar webhook/iade/uzlaştırma; kart verisi tutulmaz |
| Y18 | Ücretsiz başlangıç ve profesyonel temel; Y15/Y16 | Kotalı örnek kredi/kötüye kullanım kontrolü; müşteri kendi içeriğini üretim satın almadan kullanabilir; marka/varlık export'u korunur |

## D — Google Search ve gerçek ölçüm

| ID | İş / bağımlılık | Teslim ve tamamlanma ölçütü |
|---|---|---|
| Y19 | Eski TEST entegrasyonunu eşle; Y01 ile paralel | Mevcut niyet/onay/DAILY-total bütçe/read-stop geçmişini kaynak üzerinden haritala; korunan aday incelemesi ayrı sabit kapsamlı iş; reset/bypass yok |
| Y20 | Üretim kimliği ve hesap yeteneği; Y15/Y19 | Alan adı/işletme/uygulama/API erişimi hazırlığı, tenant token vault/revoke/rotation altyapısı; create/report/forecast yetenekleri ayrı; dış onaylar kaydedilir. Gerçek müşteri hesabına fiilî bağlantı Y26 kapısı ve Y27 yetkisi sonrasıdır |
| Y21 | Plan/tahmin ve kullanıcı onayı; Y07/Y20 | Kaynağı/tazeliği/varsayımı olan tahmin veya açık erişilemez durumu; hedef/hesap/içerik sürümü/harcama/süreye bağlı kesin onay |
| Y22 | Yayın/stop/uzlaştırma; Y21 | Önce PAUSED TEST'te seçilmiş paket; retry/restart/yarım sonuçta mükerrer yok; stop mevcut işten bağımsız çalışır; gerçek serving ayrı yetki ve kapılar sonrası |
| Y23 | Harcama/dönüşüm raporu altyapısı; Y20/Y22 | TEST/sentetik kayıtlarla adaptör ve metrik eşleme, tarih/atıf/gecikme/eksiklik doğrulanır; nitelikli talep ve satış farklı; veri yoksa sıfır uydurulmaz. İlk gerçek performans kanıtı Y27'de alınır |

Platform inceleme süresi geliştirme süresinden ayrıdır. Google erişimi beklerken A–C'nin sentetik işleri ilerler. Search yayını için gerekmeyen video/organik sosyal işleri kritik yola eklenmez.

## E — İşletim ve kontrollü müşteri pilotu

| ID | İş / bağımlılık | Teslim ve tamamlanma ölçütü |
|---|---|---|
| Y24 | Veri, hak ve Türkiye uyumu; A ile paralel | Veri/alıcı/aktarım/saklama/silme, gerçek kimlik/şartlar, AI karakter/iddia/indirim/sektör kuralları ve yetkili inceleme; açık karar sahibi |
| Y25 | Taşınabilir dağıtım ve bakım; Y05/Y13 | App/DB/dosya/işçi envanteri ve gerçek maliyet; sürüm kilidi/SBOM/yama süreci; başka ortamda restore/export; sırlar repo dışında |
| Y26 | Pilot öncesi kampanya release doğrulaması; Y17/Y22/Y23/Y24/Y25 | Staging uçtan uca akış, tenant erişim, ödeme sandbox, timeout/stop, yapılandırılmış DB+dosya restore ve kod/şema kurtarma; izleme/olay müdahalesi. Sentetik rapor kontrolü gerçek performans kanıtı sayılmaz |
| Y27 | 3–5 müşteri pilotu; Y26 ve açık canlı yetki | Önce bir sınırlı hesap/kampanya; gerçek gözlemler ve dönüşüm/atıf platformla karşılaştırılır, tutarlılık kanıtı olmadan genişlenmez. Her hesap/harcama onaylı; fayda/tekrar kullanım/maliyet/destek yükü ölçülür; iade kapsamı açık; başarı yoksa ürün daraltılır |

Pilot kapısı tamamlanmadan gerçek müşteri dosyası, hesap, ödeme veya reklam harcaması açılmaz. Ücretsiz pilot da veri/platform kapılarını ortadan kaldırmaz. Gerçek ödeme testi kart veya gizli bilgi sohbet üzerinden yürütülmez.

## F — Kanıtla genişleme

| ID | İş / bağımlılık | Teslim ve tamamlanma ölçütü |
|---|---|---|
| Y28 | Meta ücretli reklamları; Y27 ve API uygunluğu | Ayrı müşteri izinleri, yerleşim/render, bütçe/stop ve rapor; sosyal post bağlantısı ücretli reklam diye sunulmaz |
| Y29 | Lead iletimi ve profesyonel işler; Y27 | CRM/webhook hedef doğrulama, minimum veri/tekilleştirme/teslim/retention; Y04 temel çok markalı kullanımın üstüne portföy/ekip rolleri/toplu varyant; WhatsApp tıklaması satış sayılmaz |
| Y30 | Video düzenleme/üretim ve TikTok; Y27, ayrı uygunluk | Önce kısa klip/crop/yazı/altyazı/export; sonra marka briefi → senaryo → sahne planı → tutarlı ürün/karakter → ses/kurgu denemesi; codec/model/ses hakları, maliyet ve API izni; tam profesyonel video editörü vaadi yok |
| Y31 | Deney ve kontrollü optimizasyon; Y23/Y27 | Hipotez, örneklem/süre/atıf gecikmesi/kayıp tavanı; önce öneri, sonra izinli otomasyon; yetersiz kanıtta kazanan yok |
| Y32 | İsteğe bağlı organik sosyal ve ileri özellikler; talep kanıtı | Postiz/Mixpost veya başka adaptörün gerçek ek değeri/lisansı/maliyeti; gerektiğinde RAG/çoklu ajan/retail media; çekirdek veriler taşınabilir |

## Gözden geçirme ve ilerleme ölçüsü

- Her tamamlanan dilim için: kullanıcı ne yapabiliyor, sentetik mi/gerçek mi, hangi kanıtla, hangi maliyetle ve hangi sınırla?
- Aşama, PR/test sayısıyla değil yukarıdaki kabul sonuçlarıyla kapanır. Henüz denenmeyen adaylar veya dış onaylar açık kalır.
- Kullanıcı araştırması teknik geliştirmeyle paralel yürür; gerçek kişilerle iletişim/veri toplama için uygun izin alınır. Katılımcı bulunamadıysa pazar doğrulandı denmez.
- İlk Y01–Y03 denemesinden sonra kalan iş büyüklükleri ve takvim ölçülen hızla tahmin edilir. Bugün uçtan uca bitiş tarihi veya tasarruf yüzdesi taahhüt edilmez.
- Üretim sağlayıcı, yeni aylık hizmet, alan adı, gerçek şirket bilgisi ve hukuki/finansal koşullar için gereken kararlar tek açık karar listesinde tutulur. Rutin teknik seçimler mevcut delege yetkisiyle yürütülür.
