"""Owned Python question bank, ported from first-stage-bank.js; no I/O.

The field resolver describes the active questions. It does not validate answers,
qualify policy/account access or assert that any declared fact is verified.
"""

from dataclasses import dataclass
from types import MappingProxyType

VERSION = "yaparo-server-first-stage-bank-v1"
INTENT_LABELS = MappingProxyType(
    {
        "promote": "Bir marka, ürün veya hizmeti tanıtmak",
        "sell": "Satış yapmak veya kampanya duyurmak",
        "event": "Bir etkinliğe katılımcı bulmak",
        "lead": "Talep, teklif veya randevu almak",
        "hire": "İşe alım için başvuru toplamak",
        "fundraise": "Bağış veya gönüllü destek toplamak",
        "announce": "Bir duyuru veya özel gün mesajı paylaşmak",
        "community": "Topluluk, üyelik veya eğitim çalışmamı büyütmek",
        "reputation": "Güven oluşturmak veya bir açıklama yapmak",
    }
)
OUTCOME_LABELS = MappingProxyType(
    {
        "promote": (
            ("remember", "Markayı veya mesajı hatırlasın"),
            ("understand", "Bilgilensin"),
            ("traffic", "Web sitesini ziyaret etsin"),
            ("visit", "Mağazaya gelsin"),
            ("contact", "İletişime geçsin"),
            ("install", "Uygulamayı indirsin"),
        ),
        "sell": (
            ("purchase", "Satın alsın"),
            ("visit", "Mağazaya gelsin"),
            ("message", "Mesajla sipariş versin"),
            ("call", "Telefonla sipariş versin"),
            ("traffic", "Web sitesini ziyaret etsin"),
            ("understand", "Kampanyayı öğrensin"),
        ),
        "event": (
            ("register", "Kayıt olsun"),
            ("ticket", "Bilet alsın"),
            ("visit", "Etkinliğe gelsin"),
            ("understand", "Etkinlik hakkında bilgi alsın"),
            ("message", "Mesajla bilgi istesin"),
        ),
        "lead": (
            ("lead_form", "Form doldursun"),
            ("quote", "Teklif istesin"),
            ("book", "Randevu alsın"),
            ("call", "Telefonla arasın"),
            ("message", "Mesaj yazsın"),
            ("meeting", "Görüşme ayarlasın"),
        ),
        "hire": (
            ("apply", "İşe başvursun"),
            ("traffic", "İlanı incelesin"),
            ("message", "Başvuru hakkında mesaj yazsın"),
        ),
        "fundraise": (
            ("donate", "Bağış yapsın"),
            ("materials", "Malzeme desteği versin"),
            ("volunteer", "Gönüllü olsun"),
            ("understand", "Çalışma hakkında bilgilensin"),
            ("traffic", "Destek sayfasını ziyaret etsin"),
            ("share", "Çağrıyı paylaşsın"),
        ),
        "announce": (
            ("understand", "Bilgilensin"),
            ("remember", "Mesajı hatırlasın"),
            ("traffic", "Duyuru sayfasını ziyaret etsin"),
            ("share", "Mesajı paylaşsın"),
            ("follow", "Hesabı takip etsin"),
        ),
        "community": (
            ("join", "Topluluğa katılsın"),
            ("subscribe", "Üye veya abone olsun"),
            ("register", "Eğitime kayıt olsun"),
            ("traffic", "İçeriği incelesin"),
            ("follow", "Hesabı takip etsin"),
        ),
        "reputation": (
            ("understand", "Mesajı anlasın"),
            ("remember", "Kurumu veya mesajı hatırlasın"),
            ("traffic", "Açıklamayı veya dayanağı incelesin"),
            ("share", "Mesajı paylaşsın"),
        ),
    }
)
ROLES = MappingProxyType(
    {
        "promote_name": "subject",
        "sell_name": "subject",
        "event_name": "subject",
        "lead_service": "subject",
        "hire_role": "subject",
        "fundraise_purpose": "subject",
        "community_name": "subject",
        "fundraise_goal": "message",
        "announce_facts": "message",
        "reputation_message": "message",
        "action_message": "message",
        "announce_identity": "identity",
        "reputation_identity": "identity",
        "fundraise_organizer_name": "identity",
        "promote_audience": "audience",
        "lead_audience": "audience",
        "announce_audience": "audience",
        "reputation_audience": "audience",
        "risk": "risk",
    }
)
CURRENCIES = (("TRY", "Türk lirası"), ("USD", "ABD doları"), ("EUR", "Euro"))
YESNO = (("yes", "Evet"), ("no", "Hayır"))
PROOFS = (
    ("information", "Ürün / hizmet bilgisi"),
    ("demo", "Gösterim"),
    ("review", "İzinli kullanıcı yorumu"),
    ("source", "Belge veya kamuya açık kaynak"),
    ("none", "Henüz eklemeyeceğim"),
)
AUDIENCES = (
    ("individuals", "Bireyler"),
    ("families", "Aileler"),
    ("business", "İşletmeler"),
    ("community", "Belirli bir topluluk"),
)


@dataclass(frozen=True, slots=True)
class Field:
    id: str
    label: str
    type: str = "text"
    required: bool = True
    max_length: int = 160
    minimum: int | float = 0
    maximum: int | float = 1_000_000_000_000
    integer: bool = False
    options: tuple[tuple[str, str], ...] = ()
    role: str | None = None


def _q(key, label, kind="text", required=True, *, maximum=None):
    return Field(
        key,
        label,
        kind,
        required,
        maximum if maximum is not None else (600 if kind == "textarea" else 160),
        role=ROLES.get(key),
    )


def _s(key, label, options, required=True):
    return Field(
        key,
        label,
        "select",
        required,
        options=tuple(tuple(o) for o in options),
        role=ROLES.get(key),
    )


def _multi(key, label, options, required=True):
    return Field(
        key,
        label,
        "multiselect",
        required,
        options=tuple(tuple(o) for o in options),
        role=ROLES.get(key),
    )


def _n(key, label, required=True, *, minimum=0, integer=False):
    return Field(key, label, "number", required, minimum=minimum, integer=integer)


def _other(result, answers, parent, label="Kendi yanıtını yaz"):
    value = answers.get(parent)
    if value == "other" or isinstance(value, (tuple, list)) and "other" in value:
        result.append(_q(parent + "_other", label))


def _currency(key):
    return _s(key, "Para birimi", CURRENCIES)


def _audience(result, a, key, label, options=AUDIENCES):
    result.append(_s(key, label, options))
    if a.get(key) == "business":
        result.append(
            _s(
                key + "_detail",
                "Hangi işletmeler?",
                (
                    ("small", "Küçük işletmeler"),
                    ("corporate", "Kurumsal ekipler"),
                    ("professionals", "Bağımsız profesyoneller"),
                    ("other", "Kendi grubum"),
                ),
            )
        )
    if a.get(key) in ("individuals", "families"):
        result.append(
            _s(
                key + "_detail",
                "Hangi ihtiyacı karşılıyor?",
                (
                    ("everyday", "Günlük ihtiyaç"),
                    ("special", "Belirli bir ihtiyaç veya ilgi"),
                    ("existing", "Mevcut kullanıcıların ihtiyacı"),
                    ("other", "Kendi tanımım"),
                ),
            )
        )
    if a.get(key) == "community":
        result.append(_q(key + "_detail", "Topluluğu kısa tanımla"))
    _other(result, a, key)
    _other(result, a, key + "_detail")


def _dates(result, a, prefix, label="Ne zaman?"):
    result.append(
        _s(
            prefix + "_timing",
            label,
            (
                ("single", "Tek tarih"),
                ("range", "Tarih aralığı"),
                ("recurring", "Tekrarlayan"),
                ("unknown", "Henüz kesinleşmedi"),
            ),
        )
    )
    if a.get(prefix + "_timing") in ("single", "range", "recurring"):
        result.append(_q(prefix + "_start", "Başlangıç tarihi", "date"))
    if a.get(prefix + "_timing") == "range":
        result.append(_q(prefix + "_end", "Bitiş tarihi", "date"))
    if a.get(prefix + "_timing") == "recurring":
        result.append(
            _s(
                prefix + "_recurrence",
                "Ne sıklıkta?",
                (
                    ("daily", "Her gün"),
                    ("weekly", "Her hafta"),
                    ("monthly", "Her ay"),
                    ("other", "Kendi düzenim"),
                ),
            )
        )
    _other(result, a, prefix + "_recurrence", "Tekrarlama düzeni")


def _location(result, prefix, label):
    result.extend(
        (
            _q(prefix + "_address", label + " açık adres veya yer adı", required=False),
            _q(
                prefix + "_map_url",
                label + " harita bağlantısı",
                "url",
                False,
                maximum=2048,
            ),
        )
    )


def _price(result, a, prefix, label="Katılım ücretli mi?", show=True):
    result.append(
        _s(
            prefix + "_fee",
            label,
            (
                ("free", "Ücretsiz"),
                ("paid", "Ücretli"),
                ("mixed", "Bazı katılımlar ücretli"),
                ("unknown", "Henüz belli değil"),
            ),
        )
    )
    if show and a.get(prefix + "_fee") in ("paid", "mixed"):
        result.extend(
            (_n(prefix + "_amount", "Ücret tutarı"), _currency(prefix + "_currency"))
        )
        if a.get(prefix + "_fee") == "mixed":
            result.append(
                _q(prefix + "_fee_conditions", "Ücret hangi katılımlarda geçerli?")
            )


def _bank(intent, outcome, a):
    result = []
    if intent == "promote":
        result.append(
            _s(
                "promote_kind",
                "Neyi tanıtıyoruz?",
                (
                    ("brand", "Marka"),
                    ("product", "Ürün"),
                    ("service", "Hizmet"),
                    ("project", "Proje"),
                    ("other", "Kendi tanımım"),
                ),
            )
        )
        _other(result, a, "promote_kind")
        result.append(_q("promote_name", "Adı veya kısa konu tanımı nedir?"))
        result.append(
            _s(
                "promote_strength",
                "En çok hangi yönü öne çıksın?",
                (
                    ("quality", "Kalite"),
                    ("ease", "Kolaylık"),
                    ("innovation", "Yenilik"),
                    ("expertise", "Uzmanlık"),
                    ("design", "Tasarım"),
                    ("social", "Sosyal fayda"),
                    ("other", "Kendi yanıtım"),
                ),
            )
        )
        _other(result, a, "promote_strength")
        _audience(result, a, "promote_audience", "Kime fayda sağlıyor?")
        result.append(_s("promote_proof", "Bunu destekleyen ne var?", PROOFS))
        if a.get("promote_proof") and a["promote_proof"] != "none":
            result.append(
                _q(
                    "promote_proof_note",
                    "Kullanılabilir dayanağı kısa açıkla",
                    "textarea",
                    False,
                )
            )
    if intent == "sell":
        result.append(
            _s(
                "sell_kind",
                "Ne sunuyorsun?",
                (
                    ("product", "Ürün"),
                    ("service", "Hizmet"),
                    ("bundle", "Paket"),
                    ("subscription", "Abonelik"),
                    ("other", "Kendi tanımım"),
                ),
            )
        )
        _other(result, a, "sell_kind")
        result.append(
            _s(
                "sell_offer",
                "Nasıl bir teklif var?",
                (
                    ("regular", "Normal satış"),
                    ("discount", "İndirim"),
                    ("launch", "Yeni ürün"),
                    ("bundle", "Paket avantajı"),
                    ("trial", "Deneme"),
                    ("limited", "Sınırlı fırsat"),
                ),
            )
        )
        result.append(_q("sell_name", "Ürün veya teklifin adı ne?"))
        result.append(
            _s(
                "sell_conditions",
                "Hangi koşullar geçerli?",
                (
                    ("all", "Herkese açık"),
                    ("selected", "Seçili ürünlerde"),
                    ("new", "Yeni müşterilerde"),
                    ("members", "Üyelere özel"),
                    ("quantity", "Adet koşullu"),
                    ("other", "Kendi koşulum"),
                ),
            )
        )
        _other(result, a, "sell_conditions")
        if a.get("sell_conditions") == "selected":
            result.append(_q("sell_selected", "Hangi ürünlerde geçerli?"))
        if a.get("sell_conditions") == "quantity":
            result.append(
                _n("sell_min_quantity", "En az kaç adet?", minimum=1, integer=True)
            )
        result.append(
            _s(
                "sell_show_price",
                "Fiyatı içerikte gösterelim mi?",
                (("yes", "Evet"), ("no", "Hayır"), ("unknown", "Henüz belli değil")),
            )
        )
        if a.get("sell_show_price") == "yes":
            result.extend(
                (_n("sell_price", "Gösterilecek fiyat"), _currency("sell_currency"))
            )
        if a.get("sell_offer") == "discount":
            result.extend(
                (
                    _n("sell_regular_price", "İndirim öncesi fiyat"),
                    _q(
                        "sell_price_evidence",
                        "Önceki fiyatın dayanağı nedir?",
                        "textarea",
                    ),
                )
            )
        result.append(
            _s(
                "sell_timing",
                "Teklifin süresi var mı?",
                (
                    ("ongoing", "Sürekli"),
                    ("range", "Belirli tarihler"),
                    ("limited", "Kontenjan veya stok bitene kadar"),
                ),
            )
        )
        if a.get("sell_timing") == "range":
            result.extend(
                (
                    _q("sell_start", "Başlangıç tarihi", "date"),
                    _q("sell_end", "Bitiş tarihi", "date"),
                )
            )
        if a.get("sell_timing") == "limited":
            result.append(
                _n("sell_limit", "Bilinen adet veya kontenjan", minimum=1, integer=True)
            )
    if intent == "event":
        result.append(
            _s(
                "event_kind",
                "Nasıl bir etkinlik?",
                (
                    ("workshop", "Atölye"),
                    ("education", "Eğitim veya seminer"),
                    ("performance", "Konser veya gösteri"),
                    ("meetup", "Buluşma"),
                    ("fair", "Fuar veya lansman"),
                    ("sport", "Spor"),
                    ("other", "Kendi etkinliğim"),
                ),
            )
        )
        _other(result, a, "event_kind")
        result.extend(
            (
                _q("event_name", "Etkinliğin adı ne?"),
                _s(
                    "event_mode",
                    "Nasıl yapılacak?",
                    (
                        ("physical", "Yüz yüze"),
                        ("online", "Çevrimiçi"),
                        ("hybrid", "Karma"),
                    ),
                ),
            )
        )
        _dates(result, a, "event")
        if a.get("event_mode") in ("physical", "hybrid"):
            _location(result, "event_location", "Etkinlik")
        if a.get("event_mode") in ("online", "hybrid"):
            result.append(
                _s(
                    "event_online_method",
                    "Çevrimiçi katılım nasıl olacak?",
                    (
                        ("page", "Katılım sayfası"),
                        ("invite", "Kayıttan sonra davet"),
                        ("unknown", "Henüz belli değil"),
                    ),
                )
            )
            if a.get("event_online_method") == "page":
                result.append(
                    _q(
                        "event_online_url",
                        "Çevrimiçi katılım bağlantısı",
                        "url",
                        maximum=2048,
                    )
                )
        _price(result, a, "event")
        result.append(
            _s(
                "event_eligibility",
                "Kimler katılabilir?",
                (
                    ("open", "Herkese açık"),
                    ("application", "Başvuru ile"),
                    ("members", "Üyelere özel"),
                    ("conditions", "Ön koşullu"),
                ),
            )
        )
        if a.get("event_eligibility") == "conditions":
            result.append(_q("event_conditions", "Katılım ön koşulu nedir?"))
        result.append(
            _s(
                "event_capacity_status",
                "Kontenjan belli mi?",
                (
                    ("known", "Evet"),
                    ("unlimited", "Kontenjan yok"),
                    ("unknown", "Henüz belli değil"),
                ),
                False,
            )
        )
        if a.get("event_capacity_status") == "known":
            result.append(
                _n("event_capacity", "Katılımcı kontenjanı", minimum=1, integer=True)
            )
    if intent == "lead":
        result.append(_q("lead_service", "Hangi hizmet veya çözüm için?"))
        result.append(
            _s(
                "lead_contact_purpose",
                "İlk temas ne için olacak?",
                (
                    ("information", "Bilgi alma"),
                    ("discovery", "İhtiyaç görüşmesi"),
                    ("quote", "Fiyat teklifi"),
                    ("reservation", "Rezervasyon"),
                    ("appointment", "Hizmet randevusu"),
                    ("other", "Kendi yanıtım"),
                ),
            )
        )
        _other(result, a, "lead_contact_purpose")
        _audience(
            result,
            a,
            "lead_audience",
            "Bu hizmet kimler için?",
            (
                ("individuals", "Bireyler"),
                ("business", "İşletmeler"),
                ("existing", "Mevcut müşteriler"),
                ("community", "Belirli bir grup"),
            ),
        )
        result.append(
            _s(
                "lead_delivery",
                "Hizmeti nasıl veriyorsun?",
                (
                    ("onsite", "İş yerimde"),
                    ("customer", "Müşterinin yerinde"),
                    ("online", "Çevrimiçi"),
                    ("mixed", "Birden fazla yöntem"),
                ),
            )
        )
        result.append(
            _s(
                "lead_conditions",
                "Önceden bilinmesi gereken koşul var mı?",
                (
                    ("none", "Yok"),
                    ("region", "Hizmet bölgesi"),
                    ("eligibility", "Uygunluk şartı"),
                    ("minimum", "Asgari sipariş veya proje"),
                    ("other", "Kendi koşulum"),
                ),
            )
        )
        if a.get("lead_conditions") and a["lead_conditions"] != "none":
            result.append(
                _q(
                    "lead_condition_note",
                    "Hizmet verebildiğin bölge"
                    if a["lead_conditions"] == "region"
                    else "Koşulu kısa açıkla",
                    "textarea",
                )
            )
    if intent == "hire":
        result.extend(
            (
                _q("hire_role", "Hangi pozisyon için?"),
                _s(
                    "hire_type",
                    "Çalışma türü ne?",
                    (
                        ("full", "Tam zamanlı"),
                        ("part", "Yarı zamanlı"),
                        ("contract", "Sözleşmeli"),
                        ("seasonal", "Dönemsel"),
                        ("intern", "Staj"),
                    ),
                ),
                _s(
                    "hire_model",
                    "Nerede çalışılacak?",
                    (
                        ("onsite", "İş yerinde"),
                        ("remote", "Uzaktan"),
                        ("hybrid", "Karma"),
                    ),
                ),
            )
        )
        if a.get("hire_model") in ("onsite", "hybrid"):
            _location(result, "hire_location", "İş yeri")
        result.extend(
            (
                _q("hire_duties", "Temel görev nedir?", "textarea"),
                _multi(
                    "hire_qualifications",
                    "Hangi işe ilişkin nitelikler gerekli?",
                    (
                        ("experience", "Deneyim"),
                        ("technical", "Teknik beceri"),
                        ("education", "Eğitim veya yetkinlik"),
                        ("certificate", "İşe özgü belge"),
                        ("none", "Deneyim şartı yok"),
                    ),
                ),
            )
        )
        if isinstance(a.get("hire_qualifications"), (tuple, list)):
            for key, label in (
                ("experience", "Gerekli deneyim"),
                ("technical", "Gerekli teknik beceri"),
                ("education", "Gerekli eğitim veya yetkinlik"),
                ("certificate", "İşe özgü belge koşulu"),
            ):
                if key in a["hire_qualifications"]:
                    result.append(_q("hire_" + key, label))
        result.append(
            _s(
                "hire_deadline_status",
                "Başvuru için son tarih var mı?",
                (
                    ("set", "Tarih var"),
                    ("open", "Başvurular açık"),
                    ("unknown", "Henüz kesinleşmedi"),
                ),
            )
        )
        if a.get("hire_deadline_status") == "set":
            result.append(_q("hire_deadline", "Son başvuru tarihi", "date"))
    if intent == "fundraise":
        result.append(
            _s(
                "fundraise_organizer_type",
                "Bu çağrıyı kim düzenliyor?",
                (
                    ("association", "Dernek"),
                    ("foundation", "Vakıf"),
                    ("institution", "Kurum"),
                    ("person", "Kişi"),
                    ("community", "Topluluk"),
                    ("other", "Kendi tanımım"),
                ),
            )
        )
        _other(result, a, "fundraise_organizer_type")
        result.append(_q("fundraise_organizer_name", "Düzenleyicinin adı"))
        result.append(
            _s(
                "fundraise_purpose",
                "Hangi amaç için destek istiyorsun?",
                (
                    ("education", "Eğitim"),
                    ("needs", "Gıda veya temel ihtiyaç"),
                    ("disaster", "Afet ve acil destek"),
                    ("health", "Sağlık desteği"),
                    ("animals", "Hayvan refahı"),
                    ("environment", "Çevre"),
                    ("culture", "Kültür veya topluluk"),
                    ("other", "Kendi amacım"),
                ),
            )
        )
        _other(result, a, "fundraise_purpose")
        result.append(_q("fundraise_goal", "Destek neyi gerçekleştirecek?", "textarea"))
        if outcome in ("donate", "materials"):
            result.append(
                _s(
                    "fundraise_permit",
                    "İzin veya istisna durumunu biliyor musun?",
                    (
                        ("licensed", "İzin belgem var"),
                        (
                            "exempt",
                            "İzin almadan toplama yetkisi veya istisna dayanağım var",
                        ),
                        ("pending", "Süreç devam ediyor"),
                        ("unknown", "Bilmiyorum"),
                    ),
                )
            )
        if outcome in ("understand", "traffic", "share"):
            result.append(
                _multi(
                    "fundraise_support_types",
                    "Çalışmada hangi destek türleri var?",
                    (
                        ("money", "Para"),
                        ("materials", "Malzeme"),
                        ("volunteer", "Gönüllü emek"),
                    ),
                    False,
                )
            )
        if outcome == "donate":
            result.append(
                _s(
                    "fundraise_target_status",
                    "Parasal hedef belirli mi?",
                    (("set", "Belirli"), ("unknown", "Henüz belli değil")),
                )
            )
            if a.get("fundraise_target_status") == "set":
                result.extend(
                    (
                        _n("fundraise_target", "Hedef tutar", minimum=0.01),
                        _currency("fundraise_currency"),
                    )
                )
        if outcome in ("donate", "materials", "volunteer"):
            result.append(
                _s(
                    "fundraise_duration",
                    "Destek çağrısının süresi belli mi?",
                    (
                        ("range", "Belirli tarihler"),
                        ("ongoing", "Sürekli"),
                        ("unknown", "Henüz belli değil"),
                    ),
                    False,
                )
            )
            if a.get("fundraise_duration") == "range":
                result.extend(
                    (
                        _q("fundraise_start", "Başlangıç tarihi", "date"),
                        _q("fundraise_end", "Bitiş tarihi", "date"),
                    )
                )
    if intent == "announce":
        result.append(
            _s(
                "announce_kind",
                "Nasıl bir duyuru?",
                (
                    ("opening", "Açılış"),
                    ("hours", "Hizmet veya saat değişikliği"),
                    ("update", "Yeni gelişme"),
                    ("celebration", "Kutlama veya teşekkür"),
                    ("information", "Bilgilendirme"),
                    ("other", "Kendi duyurum"),
                ),
            )
        )
        _other(result, a, "announce_kind")
        result.extend(
            (
                _q("announce_identity", "Hangi kişi veya kurum adına?"),
                _q("announce_facts", "İletilecek kesin bilgi ne?", "textarea"),
                _s(
                    "announce_timing",
                    "Ne zaman geçerli?",
                    (
                        ("single", "Belirli tarih"),
                        ("range", "Tarih aralığı"),
                        ("ongoing", "Sürekli"),
                        ("none", "Tarih gerekmiyor"),
                    ),
                ),
            )
        )
        if a.get("announce_timing") in ("single", "range"):
            result.append(_q("announce_start", "Geçerlilik tarihi", "date"))
        if a.get("announce_timing") == "range":
            result.append(_q("announce_end", "Bitiş tarihi", "date"))
        if a.get("announce_kind") == "opening":
            _location(result, "announce_location", "Açılış yeri")
        if a.get("announce_kind") == "hours":
            result.extend(
                (
                    _q("announce_hours_start", "Yeni başlangıç saati", "time"),
                    _q("announce_hours_end", "Yeni bitiş saati", "time"),
                    _s("announce_overnight", "Bitiş saati ertesi güne mi ait?", YESNO),
                )
            )
        _audience(
            result,
            a,
            "announce_audience",
            "Kimleri ilgilendiriyor?",
            (
                ("customers", "Müşteriler"),
                ("employees", "Çalışanlar"),
                ("members", "Üyeler"),
                ("local", "Bölge sakinleri"),
                ("public", "Genel kamu"),
                ("other", "Kendi grubum"),
            ),
        )
    if intent == "community":
        result.append(
            _s(
                "community_kind",
                "Neye katılım istiyorsun?",
                (
                    ("community", "Topluluk"),
                    ("membership", "Üyelik veya abonelik"),
                    ("course", "Kurs veya eğitim"),
                    ("meetup", "Düzenli buluşma"),
                    ("other", "Kendi çalışmam"),
                ),
            )
        )
        _other(result, a, "community_kind")
        result.append(_q("community_name", "Topluluk, program veya eğitimin adı"))
        result.append(
            _s(
                "community_value",
                "Katılımcı ne kazanacak?",
                (
                    ("learn", "Öğrenme"),
                    ("share", "Deneyim paylaşımı"),
                    ("create", "Birlikte üretim"),
                    ("content", "İçeriğe erişim"),
                    ("solidarity", "Dayanışma"),
                    ("other", "Kendi faydam"),
                ),
            )
        )
        _other(result, a, "community_value")
        result.append(
            _s(
                "community_eligibility",
                "Kimler için uygun?",
                (
                    ("open", "Herkese açık"),
                    ("beginner", "Başlangıç düzeyi"),
                    ("experienced", "Belirli deneyim düzeyi"),
                    ("profession", "Meslek veya ilgi alanı"),
                    ("conditions", "Ön koşullu"),
                ),
            )
        )
        if a.get("community_eligibility") in (
            "experienced",
            "profession",
            "conditions",
        ):
            result.append(
                _q("community_conditions", "Uygunluk veya katılım koşulunu açıkla")
            )
        _price(
            result, a, "community", show=outcome in ("join", "subscribe", "register")
        )
        if a.get("community_kind") in ("course", "meetup"):
            result.append(
                _s(
                    "community_mode",
                    "Nasıl yapılacak?",
                    (
                        ("physical", "Yüz yüze"),
                        ("online", "Çevrimiçi"),
                        ("hybrid", "Karma"),
                    ),
                )
            )
            if a.get("community_mode") in ("physical", "hybrid"):
                _location(result, "community_location", "Katılım yeri")
            _dates(result, a, "community", "Katılım tarihi belli mi?")
        if outcome == "subscribe" and a.get("community_fee") in ("paid", "mixed"):
            result.append(
                _s(
                    "community_billing",
                    "Ücret ne sıklıkla alınır?",
                    (
                        ("once", "Tek sefer"),
                        ("monthly", "Aylık"),
                        ("yearly", "Yıllık"),
                        ("other", "Kendi dönemim"),
                    ),
                )
            )
        _other(result, a, "community_billing")
    if intent == "reputation":
        result.append(
            _s(
                "reputation_kind",
                "Nasıl bir çalışma?",
                (
                    ("expertise", "Uzmanlığı göstermek"),
                    ("experience", "Müşteri deneyimini anlatmak"),
                    ("statement", "Kurumsal açıklama"),
                    ("correction", "Yanlış bilgiyi düzeltmek"),
                    ("public", "Toplumsal konuyu açıklamak"),
                    ("other", "Kendi konum"),
                ),
            )
        )
        _other(result, a, "reputation_kind")
        result.extend(
            (
                _q("reputation_identity", "Kim adına konuşuyoruz?"),
                _q("reputation_message", "Ana mesaj ne?", "textarea"),
                _s(
                    "reputation_proof",
                    "Mesajın dayanağı ne?",
                    (
                        ("public", "Kamuya açık kaynak"),
                        ("document", "Belge"),
                        ("review", "İzinli deneyim veya yorum"),
                        ("data", "Veriye dayalı açıklama"),
                        ("none", "Henüz dayanak yok"),
                    ),
                ),
            )
        )
        if a.get("reputation_proof") and a["reputation_proof"] != "none":
            result.append(
                _q("reputation_proof_note", "Dayanağı kısa açıkla", "textarea", False)
            )
        _audience(
            result,
            a,
            "reputation_audience",
            "Kimlerin bilmesini istiyorsun?",
            (
                ("customers", "Mevcut müşteriler"),
                ("partners", "İş ortakları"),
                ("employees", "Çalışanlar"),
                ("community", "Belirli topluluk"),
                ("public", "Genel kamu"),
                ("other", "Kendi grubum"),
            ),
        )
        result.append(
            _s(
                "reputation_scope",
                "Özel bir konu kapsamı var mı?",
                (
                    ("ordinary", "Genel açıklama"),
                    ("political", "Politik veya kamusal mesele"),
                    ("health", "Sağlık"),
                    ("finance", "Finans"),
                    ("unknown", "Henüz net değil"),
                ),
                False,
            )
        )
    return result


def _method(result, a, key, label, methods):
    result.append(_s(key, label, methods))
    _other(result, a, key, "Kullanılacak yöntemi açıkla")


def _phone(result, key, label="Telefon numarası"):
    result.append(_q(key, label, "tel", maximum=24))


def _url(result, key, label):
    result.append(_q(key, label, "url", maximum=2048))


def _email(result, key, label):
    result.append(_q(key, label, "email", maximum=254))


def _messaging(result, a, prefix="action", label="Mesaj hangi yoldan gönderilsin?"):
    _method(
        result,
        a,
        prefix + "_message_method",
        label,
        (
            ("whatsapp", "WhatsApp"),
            ("social", "Sosyal medya mesajı"),
            ("email", "E-posta"),
        ),
    )
    if a.get(prefix + "_message_method") == "whatsapp":
        _phone(result, prefix + "_phone", "WhatsApp numarası")
    if a.get(prefix + "_message_method") == "social":
        _url(result, prefix + "_profile_url", "Mesaj gönderilecek profil bağlantısı")
    if a.get(prefix + "_message_method") == "email":
        _email(result, prefix + "_email", "İletişim e-posta adresi")


def _outcome(intent, outcome, a):
    result = []
    if outcome in ("remember", "understand") and intent not in (
        "reputation",
        "announce",
        "fundraise",
    ):
        result.append(
            _q(
                "action_message",
                "Aklında kalmasını istediğin ana mesaj",
                "textarea",
                False,
            )
        )
    if outcome == "traffic":
        label = {
            "hire": "İlan bağlantısı",
            "fundraise": "Destek veya bilgilendirme sayfası",
            "reputation": "Açıklama veya dayanak bağlantısı",
            "community": "İncelenecek içerik veya program bağlantısı",
            "announce": "Duyuru bağlantısı",
            "sell": "Ürün veya kampanya bağlantısı",
        }.get(intent, "Ziyaret edilecek web sayfası")
        _url(result, "action_url", label)
    if outcome == "visit" and intent != "event":
        _location(result, "action_location", "Ziyaret edilecek yer")
    if outcome == "purchase":
        _method(
            result,
            a,
            "action_checkout",
            "Satın alma nerede tamamlanacak?",
            (
                ("website", "Web sitesi"),
                ("marketplace", "Pazaryeri"),
                ("store", "Mağaza"),
                ("message", "Mesaj"),
                ("phone", "Telefon"),
            ),
        )
        if a.get("action_checkout") in ("website", "marketplace"):
            _url(result, "action_url", "Ürün veya satış bağlantısı")
        if a.get("action_checkout") == "store":
            _location(result, "action_location", "Satın alınacak yer")
        if a.get("action_checkout") == "message":
            _messaging(result, a)
        if a.get("action_checkout") == "phone":
            _phone(result, "action_phone", "Sipariş için aranacak numara")
    if outcome == "call":
        _phone(
            result,
            "action_phone",
            "Sipariş için aranacak numara"
            if intent == "sell"
            else "Aranacak telefon numarası",
        )
    if outcome == "message":
        _messaging(result, a)
    if outcome == "contact":
        _method(
            result,
            a,
            "action_contact",
            "Nasıl iletişime geçsin?",
            (
                ("phone", "Telefon"),
                ("message", "Mesaj"),
                ("form", "İletişim formu"),
                ("email", "E-posta"),
            ),
        )
        if a.get("action_contact") == "phone":
            _phone(result, "action_phone")
        if a.get("action_contact") == "message":
            _messaging(result, a)
        if a.get("action_contact") == "form":
            _url(result, "action_url", "İletişim formu bağlantısı")
        if a.get("action_contact") == "email":
            _email(result, "action_email", "İletişim e-posta adresi")
    if outcome in ("lead_form", "quote"):
        _method(
            result,
            a,
            "action_lead_method",
            "Teklif talebi nasıl alınacak?"
            if outcome == "quote"
            else "Form veya talep yöntemi nedir?",
            (
                ("form", "Mevcut form"),
                ("email", "E-posta"),
                ("message", "Mesaj"),
                ("new", "Henüz formum yok"),
            ),
        )
        if a.get("action_lead_method") == "form":
            _url(result, "action_url", "Talep formu bağlantısı")
        if a.get("action_lead_method") == "email":
            _email(result, "action_email", "Talep e-posta adresi")
        if a.get("action_lead_method") == "message":
            _messaging(result, a)
        if a.get("action_lead_method") == "new":
            result.append(
                _q(
                    "action_form_need",
                    "Formda hangi temel ihtiyaç öğrenilmeli?",
                    "textarea",
                )
            )
    if outcome in ("book", "meeting"):
        _method(
            result,
            a,
            "action_booking",
            "Randevu veya görüşme nasıl ayarlanacak?",
            (
                ("page", "Rezervasyon sayfası"),
                ("phone", "Telefon"),
                ("message", "Mesaj"),
                ("system", "Mevcut rezervasyon sistemi"),
            ),
        )
        if a.get("action_booking") in ("page", "system"):
            _url(result, "action_url", "Rezervasyon bağlantısı")
        if a.get("action_booking") == "phone":
            _phone(result, "action_phone")
        if a.get("action_booking") == "message":
            _messaging(result, a)
    if outcome in ("register", "ticket", "join", "subscribe"):
        title = {
            "register": "Kayıt nasıl yapılacak?",
            "ticket": "Bilet nereden alınacak?",
            "join": "Topluluğa nasıl katılınacak?",
            "subscribe": "Üyelik veya abonelik nereden başlayacak?",
        }[outcome]
        _method(
            result,
            a,
            "action_join_method",
            title,
            (
                ("page", "Kayıt / katılım sayfası"),
                ("email", "E-posta"),
                ("message", "Mesaj"),
                ("other", "Kendi yöntemim"),
            ),
        )
        if a.get("action_join_method") == "page":
            _url(
                result,
                "action_url",
                "Bilet sayfası bağlantısı"
                if outcome == "ticket"
                else "Kayıt / katılım bağlantısı",
            )
        if a.get("action_join_method") == "email":
            _email(result, "action_email", "Kayıt e-posta adresi")
        if a.get("action_join_method") == "message":
            _messaging(result, a)
    if outcome == "apply":
        _method(
            result,
            a,
            "action_apply_method",
            "Başvuru hangi yoldan yapılacak?",
            (
                ("form", "Başvuru formu"),
                ("career", "Kariyer sayfası"),
                ("email", "E-posta"),
                ("message", "Mesaj"),
            ),
        )
        if a.get("action_apply_method") in ("form", "career"):
            _url(result, "action_url", "İş başvurusu bağlantısı")
        if a.get("action_apply_method") == "email":
            _email(result, "action_email", "Başvuru e-posta adresi")
        if a.get("action_apply_method") == "message":
            _messaging(result, a)
    if outcome == "donate":
        _method(
            result,
            a,
            "action_donation_method",
            "Para desteği hangi yoldan iletilecek?",
            (
                ("official_page", "Düzenleyicinin resmî bağış sayfası"),
                ("platform", "Yetkili platform sayfası"),
                ("other", "Yöntemi açıklayacağım"),
            ),
        )
        if a.get("action_donation_method") in ("official_page", "platform"):
            _url(result, "action_url", "Bağış sayfası bağlantısı")
    if outcome == "materials":
        result.extend(
            (
                _q("action_materials", "Hangi malzemeler gerekli?", "textarea"),
                _n("action_material_quantity", "Hedef adet veya miktar", False),
            )
        )
        if "action_material_quantity" in a:
            result.append(_q("action_material_unit", "Miktarın birimi nedir?"))
        _method(
            result,
            a,
            "action_delivery",
            "Malzeme nasıl teslim edilecek?",
            (
                ("dropoff", "Teslim noktasına bırakma"),
                ("pickup", "Adresten teslim alma"),
                ("contact", "Önce iletişim"),
                ("other", "Kendi yöntemim"),
            ),
        )
        if a.get("action_delivery") == "dropoff":
            _location(result, "action_location", "Teslim noktası")
        if a.get("action_delivery") in ("pickup", "contact"):
            _messaging(result, a)
    if outcome == "volunteer":
        result.extend(
            (
                _q("action_volunteer_task", "Gönüllü hangi işi yapacak?", "textarea"),
                _s(
                    "action_volunteer_time",
                    "Beklenen zaman katkısı nedir?",
                    (
                        ("once", "Tek seferlik"),
                        ("weekly", "Düzenli haftalık"),
                        ("flexible", "Esnek"),
                        ("other", "Kendi düzenim"),
                    ),
                ),
            )
        )
        _other(result, a, "action_volunteer_time")
        result.append(
            _q(
                "action_volunteer_skills",
                "Gerekli beceri veya ön koşul varsa açıkla",
                "textarea",
                False,
            )
        )
        _method(
            result,
            a,
            "action_volunteer_apply",
            "Gönüllü başvurusu nasıl yapılacak?",
            (("form", "Başvuru sayfası"), ("email", "E-posta"), ("message", "Mesaj")),
        )
        if a.get("action_volunteer_apply") == "form":
            _url(result, "action_url", "Gönüllü başvuru bağlantısı")
        if a.get("action_volunteer_apply") == "email":
            _email(result, "action_email", "Gönüllü başvuru e-postası")
        if a.get("action_volunteer_apply") == "message":
            _messaging(result, a)
    if outcome == "follow":
        _url(result, "action_profile_url", "Takip edilecek profil bağlantısı")
    if outcome == "share":
        result.append(
            _q(
                "action_share_url",
                "Paylaşılacak içerik veya çağrı bağlantısı",
                "url",
                False,
                maximum=2048,
            )
        )
    if outcome == "install":
        result.append(
            _s(
                "action_app_platform",
                "Uygulama hangi sistemlerde var?",
                (("android", "Android"), ("ios", "iOS"), ("both", "Android ve iOS")),
            )
        )
        if a.get("action_app_platform") in ("android", "both"):
            _url(result, "action_android_url", "Android mağaza bağlantısı")
        if a.get("action_app_platform") in ("ios", "both"):
            _url(result, "action_ios_url", "iOS mağaza bağlantısı")
    return result


def fields_for(intent, outcome, answers):
    """Return immutable active fields for one compatible route and bounded answers."""
    if (
        type(intent) is not str
        or type(outcome) is not str
        or outcome not in dict(OUTCOME_LABELS.get(intent, ()))
    ):
        return ()
    result = _bank(intent, outcome, answers) + _outcome(intent, outcome, answers)
    result.append(
        _s(
            "delivery_mode",
            "Bu çalışma nasıl kullanılacak?",
            (
                ("paid", "Ücretli reklam"),
                ("organic", "Kendi hesaplarımda paylaşım"),
                ("hybrid", "İkisi birlikte"),
                ("content_only", "Yalnız içerik hazırlama"),
                ("unsure", "Plan aşamasında karar verelim"),
            ),
        )
    )
    result.append(
        _s(
            "risk",
            "Özel bir konu veya kitle kapsamı var mı?",
            (
                ("normal", "Özel kapsam belirtmiyorum"),
                ("fundraising", "Yardım veya bağış"),
                ("health", "Sağlık"),
                ("finance", "Finans"),
                ("political", "Politik içerik"),
                ("children", "Çocuklara yönelik"),
                ("alcohol_tobacco", "Alkol veya tütün"),
                ("gambling", "Bahis veya kumar"),
            ),
            False,
        )
    )
    if len({field.id for field in result}) != len(result):
        raise ValueError("Duplicate owned question")
    return tuple(result)


def outcome_label(intent, outcome):
    return dict(OUTCOME_LABELS.get(intent, ())).get(outcome)
