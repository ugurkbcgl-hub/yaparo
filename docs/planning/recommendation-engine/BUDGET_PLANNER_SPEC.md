# İşletmeye uygun bütçe ve anlık senaryo karşılaştırması

Ürün kararı ve uygulama onayı:29Ekim2026, Europe/Istanbul. Mevcut araştırma, kabul
edilmiş46-yol doğrulayıcısı ve dört aşama korunur. Bu belgede anlatılan bütçe
planlayıcı henüz çalışmıyor. İlk WP01 uygulaması yalnız saf keşif/seçim/nakit
metadata sözleşmesidir; [ADR0076](../../adr/0076-budget-optional-discovery-contract.md).
Sayısal öneri, ortak kapasite, kalıcı kayıt ve UI bağlantısı henüz yoktur.
Migration, paket, hesap, kampanya, harcama veya sunucu ayarı değiştirilmedi.

[Mevcut denetim](AUDIT.md), [uygulama işleri](IMPLEMENTATION_PLAN.md),
[sağlayıcı kanıtları](PROVIDER_CAPABILITIES.md) ve
[kabul planı](ACCEPTANCE_TESTS.md) bu tanımla birlikte okunur. Bu belge, bütçenin
başlangıçta zorunlu müşteri girdisi sayıldığı eski plan maddelerini değiştirir;
mevcut uygulamanın harcama korumalarını veya gerçekleşmiş testlerini değiştirmez.

## 1. Ne değişiyor, ne korunuyor?

Önce: müşteri medya bütçesini girer → motor bu tutarı kanallara dağıtır.

Yeni: istenen sonuç → işletmenin ekonomik koşulları ve ek kapasitesi → uygun
kanal/veri → sınırlı bütçe adayları → sonuç/katkı/iş yükü → nakit uygunluğu →
seçilmiş plan → ayrı harcama yetkisi.

Başlangıçta bütçe bilgisi gerekmez. Zaten bütçesi olan kişi **isteğe bağlı medya
tavanı** verebilir. `unknown/null`, bilinçli0 ve pozitif tavan ayrı anlamlardır.
0 ücretli harcamama tercihidir; boş alanı0 veya örnek3000TL yapma. Sistem bütçeyi
“sonuna kadar kullanma” hedefiyle çalışmaz. Kullanıcı tavanı, nakit uygunluğu,
ekonomik verim ve kapasite birbirinin yerine geçmez.

Korunanlar: iki ilk soru, amaca özel form, tekrar sormama, ücretli/organik/
birlikte/yalnız içerik ayrımı, plan önce içerik sonra, seçilmiş kanalların
yüzdeleri, kuruş hassasiyeti, ayrılmamış bakiye, sahiplik/sürüm/tekrar işlem
sınırları. Organik ve yalnız içerikte medya karşılaştırıcısı açılmaz; varsa
üretim bedeli kendi onay akışında kalır. Yeni keşif taslağı mevcut
`PlanBounds.media_budget_minor` veya yayın tavanını nullable yapmayacak.

“Canlı karşılaştırma” **ekranda anlık hesaplama** demektir; canlı piyasa verisi,
anlık stok bağlantısı veya reklam hesabında değişiklik anlamına gelmez.

## 2. Dört aşamada sade kullanıcı akışı

### İsteğini netleştir

“Bu çalışma için ne yapmak istiyorsun?” ve “Gören kişi ne yapsın?” korunur.
İlgili kısa formun mevcut ad, ürün/hizmet, tarih, fiyat, yönlendirme ve risk
yanıtları kullanılır. Mevcut sorunun daha teknik bir kopyası eklenmez. Eksik iş
modeli gerektiğinde kısa seçimle sorulur; metinden sektör/kapasite uydurulmaz.

### Planını kur

Tek kısa panel, sırayla yalnız eksik bilgiyi gösterir:

1. “Bu çalışmadan ne zamana kadar sonuç bekliyorsun?” Sonuç beklenen dönem,
   reklamın yayın dönemiyle aynı olmak zorunda değildir. Satış gecikmesi uzunsa
   bunu açıkla; ilk formdaki etkinlik/teklif tarihiyle çelişkiyi çözmeden ilerleme.
2. “Bu dönemde kaç ek sipariş / randevu / yeni işi rahatlıkla karşılayabilirsin?”
   Birim ve dönemi yanına yaz. “Bilmiyorum, birlikte hesaplayalım” ek alanları açar.
3. Gelir hedefinde: “Bir satıştan, o işe bağlı giderler çıktıktan sonra yaklaşık
   ne kadar kalıyor?” Hazır fiyatı tekrar sorma. “Bilmiyorum” seçeneğinde gerekli
   giderleri kısa kalemlerle aç; kullanıcıya marj/CPA terminolojisi dayatma.
4. İsteğe bağlı: “Aşmamamızı istediğin bir reklam tutarı var mı?” Medya tavanı
   olduğunu ve üretimin ayrı gösterileceğini belirt. İsterse toplam nakit tavanı
   da verebilir; iki alanı aynı para gibi iki kere düşme.

İlk adaylarda, veri yeterliyse: “İşletmene uygun bir başlangıç bulduk.”
Eksik veri varsa: “Planını karşılaştırabiliriz; güvenilir tutar için şu bilgi
eksik.” Kullanılamayan metrikte sıfır veya temsili getiri gösterilmez.

Kartın hap bilgileri: önerilen medya tutarı, üretim/hizmet dahil **kampanya
maliyeti**, hedef sonuç ve varsa aralığı, iş yükü/kapasite, hesaplanabiliyorsa
koşullu katkı, tek cümle neden. Alt açıklamada kaynak tarihleri, maliyet kapsamı,
nakit ihtiyacı, belirsizlik ve önceki seçeneğe göre fark bulunur.

Sonra nakit sorusu: “Kampanya maliyeti XTL. Sonuçlar düşük kalsa da bu harcama
işletmeni zorlar mı?” Gerekli modelde ayrıca: “Sipariş/hizmet giderleri için,
tahsilata kadar YTL daha gerekebilir; en yüksek nakit ihtiyacı ZTL.”
Yanıtlar: “Karşılayabilirim”, “Daha düşük bir sınır belirleyeyim”, “Henüz emin
değilim”. Sonuncu durumda koşullu taslak korunur; harcama izni oluşmaz.

### İçeriğini oluştur

Seçilen planın kanal/format gereksinimleriyle üret. Üç farklı yaklaşım, editör ve
yardımcı korunur. Yeni kanal/video gerekiyorsa ek maliyet ve plan revizyonunu
önce göster; sessiz ücretli üretim yok. Var olan müşteriye ait materyalin hakkı,
kullanılabilirliği ve uyarlama maliyeti ayrıca kontrol edilir.

### Kontrol et ve yayınla

Medya, üretim, hizmet/vergi kapsamı ve nakit ihtiyacı ayrı gösterilir. Sonuç
ölçütü, hedefleme, tarih, hesap, içerik, sert harcama limitleri ve güncel kapasite
yeniden kontrol edilir. “Bu senaryoyu seçtim”, “nakdim uygun” ve “bu reklam
hesabında bu sınırlarla harcama yap” **üç ayrı karar**dır.

## 3. İş modeline özel kısa soru ve yardımcı alanlar

| Yol | Ana yanıt | “Birlikte hesaplayalım” alanları | Önemli ayrım |
| --- | --- | --- | --- |
| Ürün / sipariş | Dönemde karşılanabilecek ek sipariş, birim başına kalan tutar | Mevcut fiyat, doğrudan ürün/ambalaj/komisyon/gönderim gideri; satılabilir stok; sipariş başına adet; hazırlama ve gönderim/gün | Stok adedi sipariş sayısı değildir; önceden ödenmiş stok ekonomik gider olsa da yeniden nakit çıkışı olmayabilir |
| Randevulu hizmet | Ek randevu, gerçekleşen hizmet başına kalan tutar | Boş slot, süre, personel saati, oda/ekipman, doğrudan sarf/hizmet gideri; iptal/gelmeme | Rezerve edilen slot ile gerçekleşen hizmet ayrı; gelmeyen kişi de kapasiteyi tutabilir |
| Kurumsal / proje | Karşılanabilecek yeni talep ve teslim edilebilir yeni iş | İlk görüşme, teklif hazırlama süresi/sayısı, uzman saatleri, eşzamanlı proje; iş başına değişken gider ve tahsilat koşulu | Talep/görüşme/teklif/iş birbirine eşitlenmez; uzun satış döngüsü kısa dönemde kâr kanıtı olmaz |
| Etkinlik / eğitim | Ek katılımcı ve kayıt/yer sınırı | Koltuk/oturum/personel, bilet bedeli ve doğrudan katılım gideri varsa; kayıt/katılım ayrımı | Ücretsiz etkinlikte satış kârı zorunlu değil; son tarih ve bekleme listesi gerekir |
| Bağış / gönüllülük | Geçerli bağış veya uygun gönüllü başvurusu | Beyan edilen yetki/dayanak, işleme/yanıt kapasitesi, kabul edilebilir toplama/başvuru gideri | Bağış tutarı şirket kârı değildir; izin/politika kapıları korunur |
| İşe alım | Nitelikli başvuru ve görüşme kapasitesi | Açık pozisyon, işe ilişkin ölçütler, değerlendirme/görüşme zamanı, kabul edilebilir başvuru gideri | İşe alınan kişi sayısı başvuru sayısı değildir; hassas hedefleme otomatik açılmaz |
| Farkındalık / duyuru | Desteklenen erişim/frekans/hatırlama hedefi | Dönem, uygun kitle, gerekiyorsa yanıt kapasitesi ve kabul edilebilir iletişim maliyeti | Gösterimden satış veya kârlılık türetme; araştırma yoksa hatırlama ölçümü yok |

Her kritik bilinmeyen alanın durumu ayrı: verilmedi, bilmiyor, tahmini beyan,
bağlantıdan gözlendi, eski, çelişkili. Yardımcı alanı doldurmak doğruluk onayı
değildir. Alanlarda kaynak/tarih/birim/kapsam saklanır. İlk aşamadaki fiyatı
“bu işte beklenen fiyat” olarak yeniden kullanmadan kapsam uyumu sorulur.

## 4. Ortak kapasite: kanaldan ve kampanyadan bağımsız

Kaynak kimliği `workspace + işletme/tesis + ürün/personel/oda/grup + birim +
zaman dilimi` ile tanımlanır. Bir marka birden fazla kampanyada aynı çalışanı
kullanıyorsa farklı kaynak kopyaları yaratılmaz. Farklı işletmelerin kaynağı
yetkisiz birleşmez. Adet, slot ve saat birbirine doğrudan toplanmaz.

İki ayrı hat: **talebi karşılama** (mesaj/arama/görüşme/teklif) ve **işi teslim**
(stok/üretim/hizmet/gönderim). Sonuç başına kaynak tüketimi açık matristir:
`demand_r,t = sum_k(result_k,t × units_per_result_k,r)`.
Bir üründen2adet ve30dakika gerekiyorsa iki ayrı kaynak satırını tüketir.

Kapasite gözleminin üç türü ve uygulanan kesintiler kaydedilir:

- `total`: dönemin toplamı; mevcut kesin iş/rezervasyonlar, henüz dahil olmayan
  organik talep, başka kampanyaların açık yükü/taahhüdü ve güvenlik payı düşülür.
- `free_after_commitments`: mevcut işler zaten düşülmüştür; yeniden düşme.
  Yalnız henüz kapsanmayan organik/diğer kampanya/güvenlik kalemleri düşülür.
- `advertisable_incremental`: reklama ayrılabilir ek kapasite verilmiştir.
  Hangi yük/güvenlik payını zaten içerdiğini sor/kaydet; yalnız sonradan oluşmuş,
  henüz dahil olmayan yükü düş. Aynı organik işi veya rezervasyonu tekrar düşme.

Genel hesap: `yeni plana kalan = kaynak değeri − henüz uygulanmamış benzersiz
kesintiler`. Kaynak değeri/kesinti durumu bilinmiyorsa sonucu0 varsayma.
Yük kimliği, kaynak dönemi ve included/excluded bilgisi olmadan aynı yükü bir
platform tahmini, CRM kaydı ve rezervasyon olarak üç kez sayma.

Güvenlik payı değişmez%20 değildir. Güncellik, dönüşüm/stop gecikmesi, dalgalanma,
kullanıcı tercihi ve kaynak esnekliğine göre sürümlü gerekçesi vardır. Veri yoksa
güvenlik payının yeterliliği de bilinmiyor demektir; büyüme onayı verilmez.

Ekonomiyi düşük sonuç/düşük değer senaryosuyla, kapasiteyi yüksek talep ve
gecikmeli yük senaryosuyla sınayacağız. Dönem toplamı kadar günlük/saatlik
darboğazlar gerekir. Günlük dağılım kaynağı yoksa toplamı günlere eşit bölmek
kapasite kanıtı sayılmaz; küçük aşama, fiziksel kontenjan veya koşullu plan gerekir.

Onayda tüm ilgili kaynak revizyonları tekrar okunur. Taslak seçimi fiziksel stok
rezervasyonu değildir. Süreli plan taahhüdü tutulacaksa kaynaklar kararlı sırayla
kilitlenir; aynı request/revision kendi taahhüdünü ikinci kez düşmez. Eşzamanlı
iki plan aynı son slotu alamaz. Haricî takvim/stok sisteminin atomik rezervasyonu
yoksa yerel DB kilidi uzaktaki kaynağı garanti etmez; belirsiz rezervasyon bekler,
otomatik tekrar veya “kesin boş” sonucu üretmez. Migration/servis burada kurulmadı.

## 5. Ekonomi, nakit ve üç seviye

### Karşılaştırılabilir maliyet

`M(b)` medya, `P(b)` üretim, `S(b)` ilgili ek kampanya/hizmet gideri;
`C(b)=M(b)+P(b)+S(b)`. Vergi/para birimi/kur tarihi açık ve eşleşir.
Kampanya maliyeti, ürünleri/hizmeti teslim etmenin tüm maliyetiyle aynı değildir.
İşlem başına kalan `m`, tanımlı net gelirden o işlemin doğrudan giderleri
çıktıktan sonraki değerdir; gerçek muhasebe net kârı değildir.

Uygun gelir hedefinde koşullu katkı senaryosu:
`K(b,q)=sum_k(q_incremental_k(b) × m_k) − C(b)`.
Ek etki ölçülmemişse q'nun artımlılığı bir **model varsayımıdır**; platforma
atfedilen satışın tamamı ek satış sayılmaz. Bu durumda kart “artımlılık varsayımıyla
koşullu katkı” der. q/m yoksa K yoktur; sıfır değil hesaplanamıyor gösterilir.

Her giderin tek `cost_component_id`si ve nerede düşüldüğü olur. Birim m içinde
gönderim/komisyon varsa C'den yeniden düşülmez. İade/gelmeme/hazırlık kaybı,
tamamlanmış işlemin giderine dahil değilse ayrı olay gideri olarak bir kez sayılır.
Sabit gider, gelir vergisi, KDV/kur etkisi ve finansman kapsam dışıysa kart bunu
yazar. LTV veya tekrar satın alma verisiz eklenmez. Çok ürünün marjı/tüketimi
ayrı ele alınır; ürün karması bilinmiyorsa tek ortalama marjla kapasite garantisi yok.

### Nakit ayrı bir zaman hesabıdır

Kârlı görünen planın finansmanı mümkün olmayabilir. İzinli beyana dayanarak
harcama, üretim/teslim gideri, tahsilat/iadelerin zaman çizgisini kur:

`peak_cash_need = max_t(max(0, cumulative_outflows(t) − conservative_receipts(t)))`.

Düşük sonuçta giderlerin batması ve yüksek talepte tahsilata kadar üretim yükü
ayrı, tutarlı stres senaryolarıdır. Ödenmiş stok yeniden ödeme sayılmaz; gideri
m içinde kalabilir. Kullanıcının belirttiği “ayırabileceğim nakit”, mevcut
yükümlülükler sonrası tutarsa aynı borç ikinci kez düşülmez. Vergi/tahsilat
zamanı bilinmiyorsa nakit teyidi koşullu kalır. Nakit hesabında işletme giderini
göstermek, katkıdan aynı gideri yeniden düşmek değildir.

### Seviye tanımları

| Seviye | Hesap yaklaşımı | Gösterilmeyecek iddia |
| --- | --- | --- |
| Başlangıç testi | Teknik olarak mümkün ve bu amacın ölçüm/öğrenme planına yeterli görülen en küçük **incelenmiş** aday; kapasite/nakit/riskle uyumlu | Her işletmeye aynı tutar, kesin satış, otomatik istatistiksel güç |
| Önerilen | Uygulanabilir incelenmiş adaylar arasında, seçilen amaç ve temkinli senaryoda anlamlı sonuç/katkı, iş yükü, belirsizlik ve nakit dengesi; eşit faydada daha düşük maliyet/yük | Global optimum, kesin ideal bütçe veya garanti ROI |
| Mevcut koşullarda üst | İncelenen kanıt aralığında tüm sınırları geçen en yüksek **planlama** seviyesi; hangi sınırın daralttığı açıklanır | Harcama hedefi, aşılmadıkça her tutarın eşit verimli olduğu iddiası |

Nakit bilinmiyorken seviyeler “nakit teyidine bağlı” görünür, operasyonel üst
sınır gibi kullanılamaz. Nakit yanıtı sonrası adaylar yeniden süzülür. Üst=öneri
veya test=öneri ise kartlar birleştirilir. Hiç aday kalmazsa ücretli test önerme;
organik, başka kanal/kapsam veya hazırlık yolu ver. Teknik minimum ile test
minimumu ayrı, kaynaklı ve tarihli; kural tabanlı test miktarı “istatistiksel
olarak yeterli” diye sunulmaz.

İsteğe bağlı medya tavanı ile adayın medya tutarı da ayrıdır. Aday içinde
`kanal payları + aday içi ayrılmamış tutar = aday medya tutarı`; tavan verilmişse
`aday medya tutarı <= isteğe bağlı tavan`. Tavan−aday farkı **kullanılmayan tavan**
olarak gösterilir, gider veya aday içi rezerv diye ikinci kez sayılmaz. Girilmiş
yüksek tavan, farkı sonradan harcama yetkisi vermez; aşamalı aggregate izin ayrıca
açıkça verilmelidir. Seçilmiş ilk aşama tutarı bu yüzden toplam izinle aynı şey değildir.

## 6. En küçük güvenilir algoritma ve anlık karşılaştırma

Yeni bağımlılık/ML/MMM zorunlu değil. Mevcut saf sözleşme, Decimal/minor-unit,
güncellik ve kanal uygunluk kurallarıyla, küçük sonlu aday karşılaştırması:

1. Kullanım/amaç/konum/politika/hesap/ölçüm/içerik uygunluğunu süz. Bilinen ilk
   form bilgilerini yeniden isteme. Gelir dışı hedefi ayrı objective strategy'ye bağla.
2. İlk bütçe olmadan, kaynaklı teknik/test minimumları ve işletmenin kaynak/değer
   zarfından **sınırlı planlama sorgu ızgarası** üret. Sorgu sayısı ve aralığına
   sürümlü teknik arama sınırı koy; bu müşteri harcama yetkisi değildir. Yeterli
   zarf/veri yoksa rasgele tutarla ızgarayı büyütme; eksik bilgi sonucunu ver.
3. Aynı bağlamda geçerli hesap tahmini/işletme geçmişi veya açık sentetik fixture
   ile adayları değerlendir. Gerektiğinde farklı bütçe uçları için yetkili salt
   okuma sorgusu yapılır; müşterinin para harcaması gerekmez. Gerçek erişim yoksa
   canlı tahmin etiketi veya gizli demo fallback yoktur.
4. Her adayda kanal dağılımı, P/S maliyet eşiği, sonuç metriği ve koşullu K,
   yüksek talepte tüm ortak kaynaklar ve günlük yoğunluk, ardından nakit hesabı.
   Toplam bütçe izinli olsa da günlük yük taşarsa aday elenir/koşullu kalır.
5. Bütün uygulanabilir adayları koru; öneriyi amaç bazında etkin seçeneklerden
   seç, üst seviyeyi ise **tüm uygulanabilir incelenmiş adaylar** içinde bul.
   Katkıda daha zayıf ama kapasiteye sığan üst adayı filtreyle kaybetme; neden
   önerilmediğini açıkla. Ek C artışının ek sonuç/K karşılığını hesapla; daha
   pahalı ama daha düşük katkılı planı önerilen yapma. Farklı amaç metriklerini
   keyfî tek skorda toplama.
6. Test/öneri/üst seç, somut gerekçeler ve eksik kanıtla göster. Bu sezgisel,
   sonlu seçenek yöntemidir; gerçek global optimum iddiası yoktur.

İlk sürümde kaydırıcı **hesaplanmış adaylara oturur**; tutar girişi en yakın
adayları farklarıyla gösterir, sessiz yuvarlayıp onaylamaz. Böylece doğrulanmamış
ara değer uydurulmaz. Sonraki sürümde yalnız aynı kanal/format/teklif/maliyet
rejiminde, iki geçerli uç arasında açık etiketli parçalı doğrusal önizleme
değerlendirilebilir. İstatistiksel aralık garantisi değildir. Aralık dışında
ekstrapolasyon yok; rejim değişiminde tekrar fiyat ve kaynak kontrolü gerekir.

Slider hareketi yerel saf hesaplama yapar; API/LLM, medya bütçe düzenleme, stok
rezervasyonu, ücretli içerik veya onay çağrısı **0**. Yeni bağlam/aralık istenirse
önce “yeniden hesapla” ve gerekiyorsa açık kaynak yenileme yapılır. Geçerli
değişmeyen veri önbellekten kullanılır. Kaynak gecikmesi olan eski yanıtlar son
seçimi ezemez. Platform kaynağı tarihi ve kapasite tarihi yan yana ayrıdır.

Plan tutarı/kanal/format/içerik değiştiğinde yalnız etkilenen kaynaklar ve üretim
maliyeti, dağılım, nakit ve onay bağları eski sayılır. İlk form ve uyumlu yanıtlar
silinmez. Üst tavan onayı tamamını baştan kullanma izni değildir; aşama tutarı,
toplam tavan, kanal/tarih/içerik sınırları ayrı açık olmalıdır.

## 7. Veri sözleşmeleri ve mevcut dosyalara yerleşim

İsimler öneridir; her kavram için yeni SQL tablosu kararı verilmedi.

| Kavram / önerilen kayıt | Alanlar ve geçerlilik | Mevcut yerle ilişkisi |
| --- | --- | --- |
| `BudgetDiscoveryDraft` | Owner/brand/draft/revision, AcceptedBrief/analysis binding, sonuç dönemi, opsiyonel medya tavanı, bilinmeyen durumları; başlangıçta tahsis yok | Yeni keşif payload'ı; `contracts.py::PlanBounds` mevcut çözülmüş bütçeyi tutmaya devam eder |
| `BusinessEconomics` | Ürün/hizmet, price/cost-component IDs, birim, para/vergi kapsamı, beyan/gözlem, tarih; katsayı/tutar? | İlk aşama bankasındaki fiyat/ücret/ürün bilgisiyle eşleme; yeni sorular ancak onaylı bank sürümünde |
| `CapacityResource` | Kaynak kimliği/birim/tesis/period+timezone, total/free/incremental türü, deductions_applied, değer/durum/as-of/expiry, kaynak revizyonu | Çalışma alanı düzeyinde ortak kaynak; plan payload'ında immutable referans, her kanala kopya tablo yok |
| Yük ve taahhüt | Benzersiz order/booking/lead/plan kimliği, kaynak tüketimi, zaman aralığı, pending/committed/released/uncertain, expiry | Mevcut append-only/replay desenleri; sadece fiziksel rezervasyon varsa garanti, bekleyen iş asla sessiz silinmez |
| Varsayımlar | Organik yük, güvenlik, dönüşüm/tahsilat gecikmesi, iş başına tüketim, gerekçe/sürüm/beyan | Kural/varsayım kaydı; ortak müşterilerden izinsiz veri yok |
| `BudgetCandidate` / karşılaştırma kümesi | Grid/context ID, M/P/S/C, channel allocations+reserve, metric?range, K? ve varsayımı, resource/load?risk, peak cash?, sources, sürümler | Önerilen saf decision/allocation modülleri; tüm adaylar plan revizyonuna bağlı tek payload olabilir |
| Seçilmiş öneri/üst | Test/öneri/üst aday ID'leri, neden/sınır, unavailable/conditional durumu; seçim kendi başına izin değil | `CampaignPlanRevision` benzeri immutable metadata, eski v1 değerleri yerinde yorumlama yok |
| `CashFit` | Seçilmiş aday/context revizyonu, nakit tavanı ve kapsamı, takvim/stres varsayımları, yanıt/as-of/expiry | Ayrı bağlanan sürümlü payload; kullanıcı cevabı banka/ödeme yetkisi değildir |
| Harcama yetkisi | Hesap/generation, kampanya/aggregate cap, dönem, içerik, kanal, güncel kaynak/cash/decision bağları, request/consent | Mevcut ayrı onay/dispatch/reconcile/stop; keşif taslağı doğrudan publisher'a bağlanmaz |
| Yeniden değerlendirme | Stok/takvim/outcome/cash/policy/expiry tetikleyicisi, etkilenen kaynak/plan revizyonu ve izinli eylem | WP08 gözlem/worker sınırı; yeni mali servis veya scheduler bu belgede açılmaz |

Geçerlilik: tenant/actor servis tarafından çözülür; tarayıcı scope/“ready” bayrağı
otorite olamaz. Unknown miktar null+reason; available0 geçerli değerdir. Karma
currency, tarih, vergi veya birim uyumsuzsa toplayıp tek sonuç üretme. Yeni planın
analysis/capacity/cash sürümü eski onayı karşılayamaz. Eski taslaklar bozulmadan
review-required kalır; mevcut sıkı `PlanBounds`/Google/AI geçmişi değiştirilmez.

### Onay ve onay sonrası kontrol

Durumlar: `discovery → conditional_candidates → scenario_selected →
cash_confirmed → separately_spend_authorized`. Eksik kritik kaynak durumunda
`needs_information` veya `stale_review`; taslak kaybolmaz. Organic/content-only
ücretli durum zincirine zorlanmaz. `cash_confirmed` publisher yetkisi değildir.

Sipariş/randevu/stok bağlantısı varsa izinli webhook/API; yoksa “son güncelleme”
gösteren kısa manuel durum güncellemesi. Yeni tarih damgası eski gözlemi taze
yapmaz. Ölçüm veya kapasite kaynağı koptuğunda otomatik büyüme durur; kayıtlı
reklamın durdurulması ayrıca güvenli consent/stop politikası gerektirir.

Stop sonrası önceki gösterimlerden yeni talep gelebilir; raporlama ve sağlayıcı
durdurma gecikmesi hesaba katılır. Bekleme listesi, gün/slot kontenjanı ve gerçekten
rezervasyon yapan işletme sistemi gerekir. Ortalama günlük medya bütçesi sert
günlük limit değildir; [resmî davranış matrisi](PROVIDER_CAPABILITIES.md#işletmeye-uygun-bütçe-harcama-ve-durdurma-semantiği)
günlük/total tiplerini ayırır. Bu araştırma durdurma SLA'sı veya hesapta aşım
koruması doğrulamadı.

Büyüme: sınırlı aşama → hedef sonucun olgunlaşması → güncel kapasite/nakit →
onay kapsamı içindeyse sonraki aşama. Her işletmeye7gün veya sabit%20 harcama
zorunlu değil. Önceden verilmiş izin aşama koşulunu/tutarını/kanalını kapsamıyorsa
yeni onay gerekir. Gerçekleşen+bekleyen+yeni harcama yetkili toplamı aşmaz;
aynı gerçekleşmiş taahhüt yeniden bekleyen olarak sayılmaz.

## 8. Tamamen sentetik örnekler ve aritmetik

**Bütün fiyatlar, maliyetler, talepler, aralıklar, minimumlar ve kanallar bu
belgede uydurulmuş test girdisidir; gerçek sağlayıcı veya müşteri tahmini değildir.**
Aralıklar güven aralığı değildir. Sırf aritmetik açıklığı için vergi/kur farkı0,
iptal/iade0 varsayılmıştır; Türkiye'de vergi0 veya iade yok demek değildir.
Gerçek maliyet/nakit onayında vergi/ücret/iade kapsamı tamamlanmadan geçiş yoktur.
“Katkı” satırlarında q'nun ek sonuç olması yalnız koşullu model varsayımıdır.

### Örnek1 — stok ve gönderim sınırlı ürün

14gün. Bir sipariş1ürün; fiyat800TL, doğrudan gider500TL (önceden ödenmiş stok460,
gönderim40), işlem başına kalan300TL. Mevcut80üründen kesin sipariş20,
henüz dahil olmayan organik10, güvenlik5 düşülür: reklama45ürün kalır.
Gönderim kapasitesi90sipariş; kesin35, organik10 ve güvenlik10 sonrası35ek
gönderim. Ortak darboğaz **35sipariş**; dönem ve her günün yüksek profili ayrıca
kontrol edilmiş varsayılır, günlük en çok3ek gönderim. Kaynak her kanalda35 değildir.

| Aday | Medya | Üretim | C kampanya maliyeti | Koşullu ek sipariş | Koşullu katkı q×300−C | Yüksek sipariş /35 | Tahsilata kadar nakit |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Başlangıç testi | 1.500 | 300 | 1.800 | 8–12 | 600–1.800 | 12/35 | 2.280 |
| Önerilen | 3.000 | 300 | 3.300 | 16–24 | 1.500–3.900 | 24/35 | 4.260 |
| İncelenen üst | 5.000 | 900 | 5.900 | 22–32 | 700–3.700 | 32/35 | 7.180 |
| Elenen sonraki aday | 7.000 | 900 | 7.900 | 25–42 | −400–4.700 | **42/35** | 9.580 |

5.000TL adayı yeni kanal/video istediği için üretim600TL artar. Önerilenden üst
adaya kampanya maliyeti2.600TL artarken sonuç yalnız6–8sipariş artar; düşük
katkı800TL, yüksek katkı200TL azalır. Daha pahalı adayı “daha iyi” yapmıyoruz.
7.000TL adayında yüksek yük kapasiteyi aşar; ortalama33,5sipariş35'in altında
olsa bile aday elenir. Üst5.000, incelenen ızgaranın üstüdür; arada ölçülmemiş
her bütçe için matematiksel en yüksek tutar iddiası değildir.

Nakit varsayımı: stok zaten ödenmiş; medya/üretim ve tüm yüksek senaryo
gönderimleri, pazaryeri tahsilatından önce ödeniyor. Peak cash=C+40×q_H.
Önceden ödenmiş460TL stok yeniden finansman ihtiyacı değildir; m içinde ekonomik
gider olmaya devam eder. Kullanıcı daha sonra8.000TL serbest nakit teyit ederse
ilk üç aday nakit açısından sığar; üst harcanması gereken hedef olmaz.

### Örnek2 — randevu ve personel sınırlı hizmet

28gün. Mevcut işler sonrası boş25slot; henüz dahil olmayan organik5 ve güvenlik4
sonrası16ek slot. Personel32ek saat ve2saat/hizmet de16hizmete izin verir;
talep yanıtlama kapasitesi60. Slotu onaylamak ile hizmetin gerçekleşmesi ayrı.
Fiyat1.000, gerçekleşen hizmetin doğrudan gideri400, kalan600TL. Yüksek günlük
profilde en çok2hizmet ve yeterli oda/personel bulunduğu varsayılmıştır. Yanıt
ekibi günlük5yeni talebi karşılayabilir; ilk dört adayın sentetik günlük yüksek
talep profili bu sınırda kalıyor varsayılmıştır. Bu dağılım bilinmeseydi dönem
toplamı60 tek başına günlük uygunluk kanıtı olmazdı.

| Aday | Medya | Üretim | C | Talepler | Rezerve slot | Gerçekleşen hizmet | Koşullu katkı q×600−C | Peak nakit |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Başlangıç | 1.200 | 200 | 1.400 | 12–20 | 5–8 | 4–7 | 1.000–2.800 | 2.200 |
| Ara seçenek | 1.800 | 200 | 2.000 | 18–30 | 7–11 | 6–10 | 1.600–4.000 | 2.800 |
| İlk öneri | 2.400 | 200 | 2.600 | 24–40 | 10–15 | 8–13 | 2.200–5.200 | 3.400 |
| İlk üst | 3.000 | 200 | 3.200 | 30–50 | 12–16 | 9–14 | 2.200–5.200 | 4.000 |
| Elenen | 3.600 | 400 | 4.000 | 40–65 | 16–21 | 13–18 | 3.800–6.800 | 4.800 |

3.000TL daha çok yük getirirken2.400TL'ye göre katkı aralığını artırmıyor;
2.400TL önerilir.3.600TL, yüksek slot21>16 ve talep65>60 nedeniyle elenir.
Randevuya gelmeme gerçekleşen hizmeti azaltabilir fakat rezerve slotu otomatik
boşaltmaz. Bu örnekte ek gelmeme hazırlık gideri0 varsayılmış; varsa ayrıca eklenir.

Nakit varsayımı: medya/üretim önceden, en yoğun gündeki2hizmetin800TL gideri
tahsilattan önce; hizmet bedelleri gün sonunda gelir ve sonraki günleri fonlar.
Peak cash=C+800; dönem giderlerinin tamamını bir anda fonlama varsayılmamış.
Müşteri **3.300TL** serbest nakit sınırı verirse ilk öneri3.400TL gerektirdiğinden
uymaz. Yeniden hesapta1.800TL medya önerilir; uygulanabilir en yüksek incelenmiş
aday da aynı olduğundan iki ayrı “öneri/üst” kartı üretilmez.2.400TL planın
kârlı görünmesi, nakit olarak karşılanabilir olduğu anlamına gelmez.

### Örnek3 — geçmişi az kurumsal talep

30günlük pilotta reklama ayrılabilir30ilk görüşme,12teklif,2yeni proje kapasitesi
beyan edilmiş; bu değerlerde mevcut işler zaten düşülmüş. Tekrar düşmüyoruz.
Proje satış döngüsü90gün, talep→proje dönüşümü ve iş başına gider sonrası değer
bilinmiyor. Satış/ek katkı üretmek doğru değil.

Sentetik kaynak yalnız1.500TL medyada40–60tıklama örneği sağlıyor. Teknik minimum
ile operasyonel öğrenme testi ayrı; test medya1.500, üretim500, C=2.000TL.
Bu tutarlar platform kuralı veya50tıklamanın istatistiksel yeterliliği değildir.
Beklenen nitelikli talep, proje, gelir ve katkı **hesaplanamıyor** gösterilir.

Yalnız talep toplama testi, kampanyaya özel formda ilk5başvuru/uygun günlük kotayı
zorlayan kontenjan ve bekleme listesiyle, yeni proje/teslim taahhüdü otomatik
verilmeden düşünülebilir. Bu işletme entegrasyonu doğrulanmadıysa test koşullu
kalır. Bu örnekte mevcut maaşı ödenmiş personel en çok5başvuruyu ek nakit gideri
olmadan karşılıyor; ücretli görüşme/teklif hazırlama veya proje teslimi otomatik
başlamıyor varsayılmıştır. Bu koşul bilinmiyorsa2.000TL nakit hesabı da koşullu
kalmalıdır. Kullanıcı2.500TL pilot kaybını karşılayabildiğini teyit ederse, başka
yetki/ölçüm kapıları da geçtiğinde2.000TL maliyetli sınırlı öğrenme adayı vardır.
Kanıt ve teslim finansmanı olmadan daha yüksek “büyüme” veya “ideal bütçe” yok.
Tek uygulanabilir test varsa üç kart zorlanmaz; modelin satış çıktısı yoktur.

### Örnek4 — sayısal öneri vermemek doğru sonuç

Kişi kaç ek iş karşılayabileceğini ve doğrudan giderlerini bilmiyor; stok/takvim
bağlı değil, platform kaynağı eski, nakit uygunluğu bilinmiyor. Motor “başlangıç
3.000TL” yazmaz. “Önce karşılayabileceğin ek işi birlikte belirleyelim; güncel
veri olmadan güvenilir reklam tutarı hesaplayamıyorum” der. Organik/yalnız
içerik taslağı devam edebilir. Başka örnek müşterinin kapasitesi veya varsayımsal
kârı bu kişiye aktarılmaz. Bu, motorun geçerli ve güvenli sonucudur.

## 9. Uygulama sırası, kabul ve açık kararlar

En küçük güvenilir sürüm **yerel sentetik, sonlu adaylı karşılaştırıcıdır**:
isteğe bağlı tavan + kısa iş-modeli yardımcıları + kaynaklı ortak kapasite +
ayrı maliyet/nakit + üçü zorunlu olmayan seçenek + adaylara oturan slider.
Satış/kapasite verisi yoksa gerekçeli hesaplanamıyor/test yolu da tamamlanmış
ürün davranışıdır. Gerçek API, ML veya yeni servis bu ilk dilimin şartı değildir.

İlk üç uygulama işi, onaydan sonra:

1. **WP01 keşif sözleşmesi:** AcceptedBrief/analysis yanında bütçe bilinmiyor/0/
   tavan, sonuç dönemi, aday/seçim/nakit/onay sürümleri. PlanBounds ve mevcut
   yürütme bütçesi değişmez. Saf test: bütçesiz keşif, unknown≠0, eski onay reddi.
2. **WP02 ekonomi ve kapasite:** toplam/boş/ek kaynak, birim tüketimi ve maliyet
   kapsamı; bir kez kesinti, çok kampanya/günlük darboğaz, sıfır ve bilinmeyen.
3. **WP06+WP03 sahte kaynak:** geçerli sonlu bütçe ızgarası, maliyet eşikleri,
   temkinli ekonomi/yüksek kapasite/nakit senaryoları, slider ve gerekçeler;
   hiçbir hareket gerçek harcamaya dönüşmez. Ardından WP07 sade UI/görsel kabul.

| Mevcut bileşen / iş | Yeni değişiklik ve kabul | Bağımlılık, risk ve geri dönüş |
| --- | --- | --- |
| `plan-ui.js`, `first-stage-bridge.js`, `bank.py`, `validation.py` / WP01,WP07 | Zorunlu bütçe yerine kısa keşif, mevcut yanıtları bir kez kullan; bilgi yok yolu | Yeni bank/validator sürümü ve diferansiyel fixture incelemesi; eski46-yol sözleşmesi yerinde değiştirilmez, feature flag ile önceki akış korunur |
| `contracts.py`, `CampaignPlanRevision`, `brand_settings.py` / WP01 | Keşif ile çözülmüş/onaylı planı ayrı bağla; sahip/revizyon/replay | Kalıcı owner servisi henüz yok; kapalı sentetik geliştirme, eski plan/Google/AI geçmişine dönüşüm yok |
| `report_metrics.py`, WP02/WP08 | Net outcome, iptal/iade/gelmeme, kaynak/olgunluk/günlük zaman; event dedupe | Kaynak izni ve veri sözlüğü; bozuk veri karantinada, geçmiş silinmez |
| `engine.js`, `plan-summary.js`, WP05/WP06 | Tek bütçe paylaştırmanın yanında aday üret/karşılaştır, reserve, ortak kapasite/nakit | Saf yeni karşılaştırıcı ve küçük exhaustive referans örnekleri; kanıt yoksa eski demo yalnız etiketiyle kalır, gerçek veriye fallback olmaz |
| `sources.py`, WP03/WP04/WP09 | Grid/geo/tarih/account/strategy/model/cost rejimi cache; source-as-of ve kapasite-as-of ayrı | Gerçek salt okuma özel yetki/terms/kota testi; hata taslağı korur, kaynak kapatılır |
| WP08/WP10 mevcut consent/dispatch/stop | Olay/manuel güncelleme, cash/capacity yeniden kontrol, concurrency/taahhüt, izin içi aşama | Geçici DB/race/recovery testleri sonra; gerçek yürütme tüm launch kapılarıyla, stop/reconcile bağımsız; restore ile tüketilmiş hak yenilenmez |

Göreli efor ve diğer paket ayrıntıları [güncellenen uygulama planında](IMPLEMENTATION_PLAN.md).
Özellikle WP01,02,03,05,06,07,08,10 değişir; gerçek platform bağlama WP04/09 ve
ileri model WP11 ayrı kalır. İlk iki soru ve teknoloji/tedarikçi kararı değişmedi.

Kabul: [B01–B30](ACCEPTANCE_TESTS.md) yeni davranışın test planıdır; bu görevde
çalıştırılmış uygulama testi değildir. Negatif harcama yok, onaylı sınır aşılmaz,
pay+reserve eşitliği, unknown≠0, aynı kaynak/yük iki kez sayılmaz; negatif katkı
meşru sonuçtur. Örnek aritmetiği ayrıca kontrol edilir, müşteri doğrulaması sayılmaz.

Gerçek hesap/API kanıtı gerekenler: gerçek teknik minimum ve budget/pacing tipi,
forecast bütçe ızgarası/metric desteği, ülke/hesap/sürüm, günlük teslim profili,
erişim/terms/kota; işletme stok/takvim/sonuç bağlantısının freshness ve rezervasyon
semantiği; stop gecikmesi, gerçek+bekleyen harcama ve onay bağları. Belgelenen
servis özelliği veya bir TEST başarısı bu kanıtların hepsi değildir.

Kullanıcı bu bütçe planının uygulamasını onayladı. İlk sentetik dilimler için
parola/anahtar, yeni ücret veya gerçek veri gerekmez. Gerçek pilot öncesi hangi
işletme kaynağının bağlanacağı, risk/güvenlik
tercihi, nakit/test kaybı tavanı, veri/hukuk ve hesap/medya izinleri ayrıca gerekir;
bu kararlar varsayımla alınmayacak. İlk sözleşmenin varlığını tam planlayıcı
veya gerçek harcama yetkisi gibi yorumlama.
